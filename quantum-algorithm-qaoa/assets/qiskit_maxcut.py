"""Small, local Qiskit Max-Cut reference: library QAOA plus independent evidence.

This is a per-instance solver, not a trained model. The exhaustive evaluator is
only a small-instance reference; production quantum optimization is delegated
to Qiskit Optimization's maintained QAOA and MinimumEigenOptimizer.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

SCHEMA = "qiskit_maxcut_result_v1"
WORKER_TIMEOUT_SECONDS = 120
WORKER_QUEUE_TIMEOUT_SECONDS = 5
_WORKER_SLOTS = threading.BoundedSemaphore(2)


def _validate_settings(reps: int, shots: int, maxiter: int, seed: int) -> None:
    for name, value, low, high in (
        ("reps", reps, 1, 3),
        ("shots", shots, 64, 4096),
        ("maxiter", maxiter, 5, 120),
        ("seed", seed, 0, 2**32 - 1),
    ):
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{name} must be an integer in {low}..{high}")
    if maxiter < 2 * reps + 2:
        raise ValueError("maxiter must allow at least 2 * reps + 2 COBYLA evaluations")


def solve_maxcut_isolated(
    num_nodes: int,
    edges: list,
    *,
    reps: int = 1,
    shots: int = 2048,
    maxiter: int = 60,
    seed: int = 42,
) -> dict[str, Any]:
    """Run one real solve in a bounded fresh process for long-lived HTTP servers.

    This contains native SDK failures; it does not fix upstream native memory
    behavior or substitute cached results. Two workers per imported module are
    allowed; queued callers wait at most five seconds. Offline scripts may keep
    calling ``solve_maxcut`` directly.
    """
    started = time.perf_counter()
    normalized = normalize_graph(num_nodes, edges)
    _validate_settings(reps, shots, maxiter, seed)
    payload = {
        "num_nodes": num_nodes,
        "edges": normalized,
        "reps": reps,
        "shots": shots,
        "maxiter": maxiter,
        "seed": seed,
    }
    if not _WORKER_SLOTS.acquire(timeout=WORKER_QUEUE_TIMEOUT_SECONDS):
        raise RuntimeError("QAOA solver is busy; retry after the current solve")
    try:
        try:
            completed = subprocess.run(
                [sys.executable, "-I", str(Path(__file__).resolve()), "--solve-worker"],
                input=json.dumps(payload, allow_nan=False),
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=WORKER_TIMEOUT_SECONDS,
                check=False,
                **(
                    {"creationflags": subprocess.CREATE_NO_WINDOW}
                    if os.name == "nt"
                    else {}
                ),
            )
        except subprocess.TimeoutExpired as error:
            # subprocess.run kills and waits for its direct worker on timeout.
            raise RuntimeError(
                "QAOA worker exceeded its 120-second solve budget"
            ) from error
        if completed.returncode != 0:
            raise RuntimeError(f"QAOA worker failed (exit code {completed.returncode})")
        if len(completed.stdout) > 4 * 1024 * 1024:
            raise RuntimeError("QAOA worker result exceeds the supported size")
        try:
            result = json.loads(completed.stdout)
            if not isinstance(result, dict):
                raise ValueError("worker result must be an object")
            validate_result_evidence(result)
            if result["input"] != {"num_nodes": num_nodes, "edges": normalized}:
                raise ValueError("worker returned a different graph")
            if any(
                result["settings"][key] != payload[key]
                for key in ("reps", "shots", "maxiter", "seed")
            ):
                raise ValueError("worker returned different solver settings")
        except (TypeError, KeyError, ValueError, OverflowError) as error:
            raise RuntimeError(
                "QAOA worker returned invalid result evidence"
            ) from error
        # HTTP latency includes queueing and interpreter startup, not just the
        # optimization loop measured by the direct, offline solver.
        result["latency_ms"] = (time.perf_counter() - started) * 1000
        return result
    finally:
        _WORKER_SLOTS.release()


def normalize_graph(num_nodes: int, edges: list) -> list[list]:
    if type(num_nodes) is not int or not 2 <= num_nodes <= 10:
        raise ValueError("num_nodes must be an integer in 2..10")
    if not isinstance(edges, (list, tuple)) or not 1 <= len(edges) <= 45:
        raise ValueError("edges must contain 1..45 weighted edges")
    normalized = []
    seen = set()
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3:
            raise ValueError("each edge must be [source, target, weight]")
        source, target, weight = edge
        if (
            type(source) is not int
            or type(target) is not int
            or not 0 <= source < num_nodes
            or not 0 <= target < num_nodes
            or source == target
        ):
            raise ValueError("invalid vertex or self-loop")
        key = tuple(sorted((source, target)))
        if key in seen:
            raise ValueError("duplicate undirected edge")
        seen.add(key)
        if (
            type(weight) not in (int, float)
            or not math.isfinite(weight)
            or not 0 <= weight <= 100
        ):
            raise ValueError("edge weights must be finite numbers in 0..100")
        if weight > 0:
            normalized.append([*key, float(weight)])
    if not normalized:
        raise ValueError("at least one positive-weight edge is required")
    return sorted(normalized)


def cut_value(partition: list[int], edges: list[list]) -> float:
    return math.fsum(weight for u, v, weight in edges if partition[u] != partition[v])


def exact_reference(num_nodes: int, edges: list[list]) -> dict[str, Any]:
    """Enumerate complementary partitions once, independently of Qiskit."""
    candidates = (
        [0, *tail] for tail in itertools.product((0, 1), repeat=num_nodes - 1)
    )
    best = max(candidates, key=lambda bits: cut_value(bits, edges))
    return {
        "partition": best,
        "cut_value": cut_value(best, edges),
        "method": "exhaustive_2^(n-1)",
    }


def greedy_reference(num_nodes: int, edges: list[list]) -> dict[str, Any]:
    partition = [0] * num_nodes
    while True:
        value = cut_value(partition, edges)
        candidates = [
            [*partition[:node], 1 - partition[node], *partition[node + 1 :]]
            for node in range(num_nodes)
        ]
        best = max(candidates, key=lambda bits: cut_value(bits, edges))
        if cut_value(best, edges) <= value + 1e-12:
            return {
                "partition": partition,
                "cut_value": value,
                "method": "deterministic_single_flip",
            }
        partition = best


def _finite_real(value: Any) -> float:
    number = complex(value)
    if abs(number.imag) > 1e-10 or not math.isfinite(number.real):
        raise ValueError("SDK returned a non-finite or non-real value")
    return float(number.real)


def verify_ising(
    problem, operator, offset: float, num_nodes: int, edges: list[list]
) -> float:
    """Validation-only oracle, exhaustively checking sign/offset/endianness."""
    terms = operator.to_list()
    maximum_error = 0.0
    for raw in itertools.product((0, 1), repeat=num_nodes):
        bits = list(raw)
        energy = 0.0
        for paulis, coefficient in terms:
            sign = 1
            for q, pauli in enumerate(reversed(paulis)):
                if pauli == "Z":
                    sign *= 1 - 2 * bits[q]
                elif pauli != "I":
                    raise ValueError(
                        "Max-Cut cost operator must be diagonal in the Z basis"
                    )
            energy += _finite_real(coefficient) * sign
        original = cut_value(bits, edges)
        error = max(
            abs(problem.objective.evaluate(bits) - original),
            abs(energy + offset + original),
        )
        maximum_error = max(maximum_error, error)
    if maximum_error > 1e-8:
        raise ValueError(
            "QUBO/Ising objective, offset, or bit order disagrees with direct cut"
        )
    return maximum_error


def solve_maxcut(
    num_nodes: int,
    edges: list,
    *,
    reps: int = 1,
    shots: int = 2048,
    maxiter: int = 60,
    seed: int = 42,
) -> dict[str, Any]:
    """Run the maintained library solver and return JSON-safe result evidence."""
    import numpy as np
    from qiskit.primitives import StatevectorSampler
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_optimization.applications import Maxcut
    from qiskit_optimization.minimum_eigensolvers import QAOA
    from qiskit_optimization.optimizers import COBYLA

    started = time.perf_counter()
    normalized = normalize_graph(num_nodes, edges)
    _validate_settings(reps, shots, maxiter, seed)
    adjacency = np.zeros((num_nodes, num_nodes))
    for u, v, weight in normalized:
        adjacency[u, v] = adjacency[v, u] = weight
    problem = Maxcut(adjacency).to_quadratic_program()
    operator, offset = problem.to_ising()
    offset = _finite_real(offset)
    oracle_error = verify_ising(problem, operator, offset, num_nodes, normalized)
    trace = []

    def callback(evaluation, parameters, energy, _metadata):
        value = _finite_real(energy)
        trace.append(
            {
                "evaluation": int(evaluation),
                "parameters": [_finite_real(p) for p in parameters],
                "ising_energy": value,
                "expected_cut": -value - offset,
            }
        )

    initial_point = np.random.default_rng(seed).uniform(-np.pi / 2, np.pi / 2, 2 * reps)
    qaoa = QAOA(
        StatevectorSampler(default_shots=shots, seed=seed),
        COBYLA(maxiter=maxiter),
        reps=reps,
        initial_point=initial_point,
        callback=callback,
    )
    solver = MinimumEigenOptimizer(qaoa)
    compatibility = solver.get_compatibility_msg(problem)
    if compatibility:
        raise ValueError(compatibility)
    solved = solver.solve(problem)
    if not solved.samples:
        raise ValueError("QAOA returned no sampled solution")
    samples = []
    for sample in solved.samples:
        partition = [int(bit) for bit in sample.x]
        probability = _finite_real(sample.probability)
        samples.append(
            {
                "partition": partition,
                "bitstring": "".join(map(str, reversed(partition))),
                "probability": probability,
                "cut_value": cut_value(partition, normalized),
            }
        )
    samples.sort(
        key=lambda item: (-item["cut_value"], -item["probability"], item["partition"])
    )
    best = samples[0]
    most_probable = min(
        samples, key=lambda item: (-item["probability"], item["partition"])
    )
    expected = math.fsum(item["probability"] * item["cut_value"] for item in samples)
    exact = exact_reference(num_nodes, normalized)
    sdk_result = solved.min_eigen_solver_result
    bound = sdk_result.optimal_circuit.assign_parameters(sdk_result.optimal_parameters)
    if bound.num_parameters:
        raise ValueError("optimal SDK circuit still has unbound parameters")
    gates = []
    for instruction in bound.data:
        if instruction.operation.name == "barrier":
            continue
        gates.append(
            {
                "gate": instruction.operation.name.upper(),
                "stage": "qaoa_bound_execution",
                "qubits": [bound.find_bit(qubit).index for qubit in instruction.qubits],
                "params": [
                    _finite_real(value) for value in instruction.operation.params
                ],
            }
        )
    result = {
        "schema": SCHEMA,
        "input": {"num_nodes": num_nodes, "edges": normalized},
        "settings": {
            "reps": reps,
            "shots": shots,
            "maxiter": maxiter,
            "seed": seed,
            "initial_point": initial_point.tolist(),
        },
        "quantum_runtime": {
            "sdk": "qiskit",
            "execution_mode": "local_simulator",
            "solver": "qiskit_optimization.minimum_eigensolvers.QAOA",
            "optimizer": "qiskit_optimization.optimizers.COBYLA",
            "sampler": "qiskit.primitives.StatevectorSampler",
            "versions": {
                name: version(name)
                for name in ("qiskit", "qiskit-optimization", "numpy", "scipy")
            },
        },
        "bit_order": "partition[q] is qubit q; bitstring displays q(n-1)..q0",
        "best_sample": best,
        "most_probable_sample": most_probable,
        "expected_cut": expected,
        "exact": exact,
        "greedy": greedy_reference(num_nodes, normalized),
        "best_sample_ratio": best["cut_value"] / exact["cut_value"],
        "expected_ratio": expected / exact["cut_value"],
        "samples": samples,
        "trace": trace,
        "ising_offset": offset,
        "ising_basis_max_error": oracle_error,
        "optimal_parameters": {
            str(key): _finite_real(value)
            for key, value in sdk_result.optimal_parameters.items()
        },
        "quantum": {
            "qubits": num_nodes,
            "depth": int(bound.depth()),
            "backend": "Qiskit StatevectorSampler (seeded finite shots)",
            "gates": gates,
        },
        "graph": {
            "num_nodes": num_nodes,
            "edges": normalized,
            "partition": best["partition"],
            "cut_value": best["cut_value"],
            "partition_source": "best_sample",
        },
        "latency_ms": (time.perf_counter() - started) * 1000,
        "limitations": [
            "Local simulator; no quantum advantage claim.",
            "Best observed sample is distinct from the distribution-weighted expected cut.",
            "Fixed seeds describe the recorded installed SDK versions, not cross-version bitwise reproducibility.",
        ],
    }
    validate_result_evidence(result)
    return result


def validate_result_evidence(result: dict[str, Any]) -> None:
    """Recheck saved numeric evidence without loading any executable model."""
    if result.get("schema") != SCHEMA:
        raise ValueError("unsupported Max-Cut result schema")
    num_nodes = result["input"]["num_nodes"]
    edges = normalize_graph(num_nodes, result["input"]["edges"])
    samples = result["samples"]
    if not samples or not math.isclose(
        math.fsum(s["probability"] for s in samples), 1.0, abs_tol=1e-9
    ):
        raise ValueError("sample probabilities must sum to one")
    seen = set()
    for sample in samples:
        bits = sample["partition"]
        if len(bits) != num_nodes or any(
            type(bit) is not int or bit not in (0, 1) for bit in bits
        ):
            raise ValueError("invalid saved partition")
        if not 0 <= sample["probability"] <= 1 or sample["bitstring"] != "".join(
            map(str, reversed(bits))
        ):
            raise ValueError("invalid saved probability or bit order")
        if sample["bitstring"] in seen:
            raise ValueError("saved sample distribution repeats a bitstring")
        seen.add(sample["bitstring"])
        if not math.isclose(cut_value(bits, edges), sample["cut_value"], abs_tol=1e-9):
            raise ValueError("saved cut disagrees with the graph")
    exact = exact_reference(num_nodes, edges)
    best = result["best_sample"]
    expected = math.fsum(s["probability"] * s["cut_value"] for s in samples)
    if (
        best not in samples
        or best["cut_value"] != max(s["cut_value"] for s in samples)
        or result["most_probable_sample"] not in samples
        or result["most_probable_sample"]["probability"]
        != max(s["probability"] for s in samples)
        or not math.isclose(expected, result["expected_cut"], abs_tol=1e-9)
        or not math.isclose(
            exact["cut_value"], result["exact"]["cut_value"], abs_tol=1e-9
        )
        or not math.isclose(
            best["cut_value"] / exact["cut_value"],
            result["best_sample_ratio"],
            abs_tol=1e-9,
        )
        or not math.isclose(
            expected / exact["cut_value"], result["expected_ratio"], abs_tol=1e-9
        )
        or result["graph"]["partition"] != best["partition"]
        or result["graph"]["cut_value"] != best["cut_value"]
        or result["graph"]["num_nodes"] != num_nodes
        or result["graph"]["edges"] != edges
        or result["graph"]["partition_source"] != "best_sample"
    ):
        raise ValueError("saved aggregate result disagrees with sampled evidence")
    for name in ("exact", "greedy"):
        baseline = result[name]
        bits = baseline["partition"]
        if (
            len(bits) != num_nodes
            or any(type(bit) is not int or bit not in (0, 1) for bit in bits)
            or not math.isclose(
                cut_value(bits, edges), baseline["cut_value"], abs_tol=1e-9
            )
        ):
            raise ValueError("saved baseline partition disagrees with its cut")


def save_result(path: str | Path, result: dict[str, Any]) -> None:
    validate_result_evidence(result)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        prefix=target.name + ".",
        suffix=".part",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def load_result(path: str | Path) -> dict[str, Any]:
    result = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_result_evidence(result)
    return result


if __name__ == "__main__":
    if sys.argv[1:] != ["--solve-worker"]:
        raise SystemExit(
            "Use the imported solver API or the internal --solve-worker entry"
        )
    raw = sys.stdin.read(65537)
    if len(raw) > 65536:
        raise ValueError("worker input exceeds the supported size")
    worker_result = solve_maxcut(**json.loads(raw))
    validate_result_evidence(worker_result)
    print(json.dumps(worker_result, ensure_ascii=True, allow_nan=False))
