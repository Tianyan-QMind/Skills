"""Bounded Qiskit VQE for the bundled fixed LiH CAS(2e,2o) instance.

This is an SDK adapter, not a chemistry driver or a learned model. Qiskit Nature
provides the Hartree-Fock/UCCSD circuit and Qiskit Algorithms owns optimization.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import time
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np

_INSTANCE = Path(__file__).with_name("lih_sto3g_2e2o.json")
_INSTANCE_DIGEST = "86559d22fbb5f4a57ac3f8a30d928443dd906ff8534acff681547f5c4f4417fd"
_SECTOR = [5, 6, 9, 10]  # alpha wires 0,1; beta wires 2,3; one of each
_PAULI = {
    "I": np.eye(2),
    "X": np.array([[0, 1], [1, 0]]),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.diag([1, -1]),
}


def load_instance(path: str | Path = _INSTANCE) -> dict[str, Any]:
    """Read the declared fixed instance and verify its scientific contract."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _validate_instance(data)


def _validate_instance(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema_version") != 1 or data.get("num_qubits") != 4:
        raise ValueError("Expected the version 1 four-qubit LiH fixture")
    if data.get("num_particles") != [1, 1] or data.get("active_orbitals") != [1, 2]:
        raise ValueError("Expected the declared LiH CAS(2e,2o) particle sector")
    for label, value in data["paulis"]:
        if len(label) != 4 or any(p not in _PAULI for p in label):
            raise ValueError("Invalid four-qubit Pauli label")
        if type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("Pauli coefficients must be real and finite")
    if set(data["offsets"]) != {"nuclear_repulsion_energy", "ActiveSpaceTransformer"}:
        raise ValueError("Both separate energy offsets are required")
    if not all(math.isfinite(v) for v in data["offsets"].values()):
        raise ValueError("Non-finite energy offset")
    scientific = {key: value for key, value in data.items() if key != "generation"}
    digest = hashlib.sha256(
        json.dumps(
            scientific, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()
    if digest != _INSTANCE_DIGEST:
        raise ValueError("Fixed LiH instance content differs from its verified source")
    return data


def independent_matrix(data: dict[str, Any]) -> np.ndarray:
    """Evaluation oracle: Pauli q3..q0 Kronecker matrix, independent of Qiskit."""
    matrix = np.zeros((16, 16), dtype=complex)
    for label, value in data["paulis"]:
        term = np.array([[1.0]], dtype=complex)
        for symbol in label:
            term = np.kron(term, _PAULI[symbol])
        matrix += value * term
    if not np.allclose(matrix, matrix.conj().T, atol=1e-12):
        raise ValueError("Hamiltonian is not Hermitian")
    outside = sorted(set(range(16)) - set(_SECTOR))
    if np.max(np.abs(matrix[np.ix_(_SECTOR, outside)])) > 1e-10:
        raise ValueError("Hamiltonian does not conserve the declared particle sector")
    return matrix


def _ansatz():
    from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
    from qiskit_nature.second_q.mappers import JordanWignerMapper

    mapper = JordanWignerMapper()
    return UCCSD(2, (1, 1), mapper, initial_state=HartreeFock(2, (1, 1), mapper))


def evaluate_parameters(
    parameters: list[float], *, instance: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Evaluate persisted parameters; never invoke an optimizer on reload."""
    from qiskit.quantum_info import Statevector

    data = load_instance() if instance is None else _validate_instance(instance)
    ansatz = _ansatz()
    if len(parameters) != ansatz.num_parameters or not all(
        type(v) in (int, float) and math.isfinite(v) for v in parameters
    ):
        raise ValueError("Expected three finite UCCSD parameters in circuit order")
    state = Statevector.from_instruction(ansatz.assign_parameters(parameters)).data
    matrix = independent_matrix(data)
    active = float(np.vdot(state, matrix @ state).real)
    reference = float(np.linalg.eigvalsh(matrix[np.ix_(_SECTOR, _SECTOR)])[0])
    offset = sum(data["offsets"].values())
    leakage = max(0.0, float(1 - sum(abs(state[i]) ** 2 for i in _SECTOR)))
    if leakage > 1e-9 or active < reference - 1e-9:
        raise ValueError("State violates particle-sector or variational-bound contract")
    return {
        "active_electronic_energy": active,
        "total_energy": active + offset,
        "reference_total_energy": reference + offset,
        "absolute_error": abs(active - reference),
        "particle_sector_leakage": leakage,
        "statevector": [[float(x.real), float(x.imag)] for x in state],
    }


def bound_circuit_metadata(parameters: list[float]) -> dict[str, Any]:
    """Extract the actual evaluated UCCSD circuit, with explicit Qiskit wires."""
    circuit = _ansatz().assign_parameters(parameters).decompose(reps=10)
    gates = []
    for instruction in circuit.data:
        if instruction.operation.name == "barrier":
            continue
        gates.append(
            {
                "gate": instruction.operation.name.upper(),
                "qubits": [circuit.find_bit(q).index for q in instruction.qubits],
                "params": [float(value) for value in instruction.operation.params],
                "stage": "ansatz",
                "detail": "Final bound UCCSD circuit including Hartree-Fock preparation",
            }
        )
    return {
        "qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "backend": "Qiskit StatevectorEstimator (local exact simulation)",
        "gates": gates,
        "global_phase": float(circuit.global_phase),
        "wire_order": "q0 at top; little-endian statevector basis indices",
    }


def _trace_estimator(parameter_order):
    """Observe public primitive inputs; delegate every quantum evaluation to Qiskit.

    Algorithms 0.4.0 flattens callback parameters to one scalar per energy.
    Capture copied, ordered parameter rows before dispatch instead of inventing
    missing values or replacing the SDK's VQE/optimizer implementation.
    """
    from qiskit.primitives import StatevectorEstimator
    from qiskit.primitives.containers import EstimatorPub

    class ObservedStatevectorEstimator(StatevectorEstimator):
        def __init__(self):
            super().__init__(seed=42)
            self.pending_parameters = deque()

        def run(self, pubs, *, precision=None):
            if self.pending_parameters:
                raise ValueError(
                    "Previous estimator rows were not consumed by VQE callbacks"
                )
            batch = [EstimatorPub.coerce(pub, precision) for pub in pubs]
            if len(batch) != 1 or batch[0].observables.shape != ():
                raise ValueError("LiH trace requires one scalar Hamiltonian per batch")
            rows = (
                batch[0]
                .parameter_values.as_array(parameter_order)
                .reshape(-1, len(parameter_order))
            )
            if not np.all(np.isfinite(rows)):
                raise ValueError("Estimator parameters must be finite")
            self.pending_parameters.extend(np.array(row, copy=True) for row in rows)
            return super().run(batch, precision=precision)

    return ObservedStatevectorEstimator()


def solve_lih(max_iterations: int = 100) -> dict[str, Any]:
    """Run actual bounded local VQE and return a JSON-safe reproducible result."""
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_algorithms import VQE
    from qiskit_algorithms.optimizers import SLSQP

    if type(max_iterations) is not int or not 1 <= max_iterations <= 200:
        raise ValueError("max_iterations must be an integer from 1 to 200")
    data = load_instance()
    ansatz = _ansatz()
    matrix = independent_matrix(data)
    operator = SparsePauliOp.from_list(data["paulis"])
    if not np.allclose(operator.to_matrix(), matrix, atol=1e-12):
        raise ValueError("SDK Pauli ordering differs from the independent oracle")
    trace = []
    started = time.perf_counter()
    offset = sum(data["offsets"].values())
    estimator = _trace_estimator(list(ansatz.parameters))

    def callback(count, parameters, energy, metadata):
        if count != len(trace) + 1 or not estimator.pending_parameters:
            raise ValueError(
                "VQE callback count does not match estimator parameter rows"
            )
        actual_parameters = estimator.pending_parameters.popleft()
        reported = np.asarray(parameters).reshape(-1)
        if reported.size == actual_parameters.size and not np.array_equal(
            reported, actual_parameters
        ):
            raise ValueError("VQE callback parameters disagree with estimator inputs")
        trace.append(
            {
                "evaluation": int(count),
                "parameters": [float(v) for v in actual_parameters],
                "callback_parameter_count": int(reported.size),
                "active_electronic_energy": float(energy),
                "total_energy": float(energy) + offset,
                "elapsed_seconds": time.perf_counter() - started,
            }
        )

    result = VQE(
        estimator,
        ansatz,
        SLSQP(maxiter=max_iterations, ftol=1e-11),
        initial_point=np.zeros(ansatz.num_parameters),
        callback=callback,
    ).compute_minimum_eigenvalue(operator)
    if estimator.pending_parameters or result.cost_function_evals != len(trace):
        raise ValueError("VQE trace is incomplete for the executed estimator inputs")
    parameters = [float(result.optimal_parameters[p]) for p in ansatz.parameters]
    evaluated = evaluate_parameters(parameters, instance=data)
    delta = abs(evaluated["active_electronic_energy"] - float(result.eigenvalue.real))
    if delta > 1e-9:
        raise ValueError("Solver result differs from final-parameter recomputation")
    iterations = result.optimizer_result.nit
    return {
        "schema_version": 1,
        "instance": data["instance_id"],
        "instance_sha256": hashlib.sha256(_INSTANCE.read_bytes()).hexdigest(),
        "scope": "fixed_geometry_active_space",
        "energy_unit": "hartree",
        "offsets": data["offsets"],
        "pauli_order": "q3 q2 q1 q0; little-endian basis indices",
        "parameters": parameters,
        "parameter_order": [str(p) for p in ansatz.parameters],
        "quantum": bound_circuit_metadata(parameters),
        **evaluated,
        "solver_recompute_delta": delta,
        "exact_reference_tolerance_met": evaluated["absolute_error"] <= 1e-6,
        "optimizer": {
            "class": "qiskit_algorithms.optimizers.SLSQP",
            "max_iterations": max_iterations,
            "iterations": iterations,
            "energy_evaluations": len(trace),
            "iteration_limit_reached": iterations is not None
            and iterations >= max_iterations,
            "success_reported": getattr(result.optimizer_result, "success", None),
        },
        "solver": "qiskit_algorithms.VQE",
        "ansatz": "qiskit_nature.second_q.circuit.library.UCCSD",
        "primitive": "qiskit.primitives.StatevectorEstimator",
        "versions": {
            p: importlib.metadata.version(p)
            for p in ("qiskit", "qiskit-algorithms", "qiskit-nature", "numpy", "scipy")
        },
        "elapsed_seconds": time.perf_counter() - started,
        "convergence_trace": trace,
        "trace_parameter_source": "copied EstimatorPub parameter bindings in ansatz order",
        "limitations": data["limitations"],
    }
