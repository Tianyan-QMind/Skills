"""Standalone runtime shared by the canonical QML adapter matrix."""

from __future__ import annotations

import json
import math
import os
import tempfile
from collections.abc import Mapping
from functools import lru_cache
from hashlib import file_digest, sha256
from pathlib import Path
from threading import RLock
from types import MappingProxyType
from typing import Any

VQC_MAX_FEATURE_WIDTH = 8
VQC_MAX_TRAINING_ROWS = 256
VQC_MAX_BATCH_ROWS = 256
VQC_MAX_CLASSES = 10
VQC_MAXITER = 60
VQC_SEED = 12345

MAX_MODEL_BYTES = 8 * 1024 * 1024
# Statevector cost grows exponentially with feature-map width. Twelve qubits is
# a fail-closed local ceiling; generated one-hour applications target ten or less.
MAX_FEATURE_WIDTH = 12
MAX_SUPPORT_VECTORS = 4096
MAX_BATCH_ROWS = 4096
MAX_KERNEL_PAIRS = 2_000_000

_QISKIT_CACHE_LOCK = RLock()


@lru_cache(maxsize=1)
def _descriptor() -> dict[str, Any]:
    return json.loads(Path(__file__).with_name("adapter.json").read_text())


def _application_root() -> Path:
    """Return the generated application root for this materialized runtime."""

    return Path(__file__).resolve().parents[2]


def _models_root() -> Path:
    models_dir = _application_root() / "models"
    if models_dir.is_symlink():
        raise ValueError("application models directory must not be a symbolic link")
    return models_dir.resolve()


def _trusted_model_path(model_path: str | Path) -> Path:
    """Resolve a model path inside the generated application's models directory."""

    application_root = _application_root()
    models_root = _models_root()
    candidate = Path(model_path).expanduser()
    if not candidate.is_absolute():
        candidate = application_root / candidate
    resolved = candidate.resolve()
    if resolved == models_root or models_root not in resolved.parents:
        raise ValueError("model_path must resolve to a file under application models/")
    return resolved


def _atomic_write_json_model(model_path: Path, state: dict[str, Any]) -> None:
    """Replace a JSON model only after its complete inert state is durable."""

    rendered = json.dumps(state, sort_keys=True, allow_nan=False)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=model_path.parent,
            prefix=f".{model_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(model_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _reject_unsafe_qiskit_native_persistence() -> None:
    raise ValueError(
        "Qiskit native model persistence is unavailable because Dill "
        "deserialization can execute arbitrary code; select a route with a "
        "non-executable JSON or weights-only model format"
    )


def _is_qiskit_vqc(descriptor: dict[str, Any]) -> bool:
    return (
        descriptor["sdk"] == "qiskit"
        and descriptor["profile"] == "variational_supervised"
        and descriptor.get("selected_variant") == "vqc"
    )


def _reject_unsupported_qiskit_variational(descriptor: dict[str, Any]) -> None:
    if (
        descriptor["sdk"] == "qiskit"
        and descriptor["profile"] == "variational_supervised"
        and not _is_qiskit_vqc(descriptor)
    ):
        _reject_unsafe_qiskit_native_persistence()


def _expectation(sdk: str, angle: float) -> float:
    if sdk == "cqlib":
        from cqlib import Circuit
        from cqlib.simulator import SimpleSimulator

        circuit = Circuit(1)
        circuit.ry(0, angle)
        probabilities = SimpleSimulator(circuit).probs(dict_format=False)
        return float(probabilities[0] - probabilities[1])
    if sdk == "qiskit":
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        circuit = QuantumCircuit(1)
        circuit.ry(angle, 0)
        probabilities = Statevector.from_instruction(circuit).probabilities()
        return float(probabilities[0] - probabilities[1])
    if sdk == "pennylane":
        import pennylane as qml

        device = qml.device("default.qubit", wires=1, shots=None)

        @qml.qnode(device)
        def circuit(value):
            qml.RY(value, wires=0)
            return qml.expval(qml.Z(0))

        return float(circuit(angle))
    raise ValueError(f"unsupported SDK: {sdk}")


def _features(sdk: str, rows: list[list[float]]) -> list[float]:
    return [
        sum(_expectation(sdk, float(value)) for value in row) / len(row) for row in rows
    ]


def _fit_linear(features: list[float], targets: list[float]) -> dict[str, float]:
    mean_x = sum(features) / len(features)
    mean_y = sum(targets) / len(targets)
    variance = sum((value - mean_x) ** 2 for value in features)
    slope = (
        sum(
            (value - mean_x) * (target - mean_y)
            for value, target in zip(features, targets, strict=True)
        )
        / variance
        if variance > 1e-12
        else 0.0
    )
    return {"slope": slope, "intercept": mean_y - slope * mean_x}


def _route_smoke_training_fixture(
    descriptor: dict[str, Any],
) -> tuple[list[list[float]], list[float]]:
    """Return deterministic data used only by the framework route smoke."""
    profile = descriptor["profile"]
    if descriptor["sdk"] in {"qiskit", "cqlib"} and (
        profile == "quantum_kernel"
        or _is_qiskit_vqc(descriptor)
        or _is_cqlib_vqc(descriptor)
    ):
        return (
            [[0.1, 0.2], [0.2, 0.1], [1.1, 1.2], [1.2, 1.1]],
            [0.0, 0.0, 1.0, 1.0],
        )
    rows = [[0.1], [0.4], [1.2], [1.5]]
    if profile in {"quantum_kernel", "variational_supervised", "hybrid_neural"}:
        return rows, [0.0, 0.0, 1.0, 1.0]
    return rows, [0.1, 0.4, 1.2, 1.5]


def _build_qiskit_torch_layer():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter, ParameterVector
    from qiskit_machine_learning.connectors import TorchConnector
    from qiskit_machine_learning.neural_networks import EstimatorQNN

    feature = Parameter("feature")
    weights = ParameterVector("weight", 2)
    circuit = QuantumCircuit(1)
    circuit.ry(feature, 0)
    circuit.ry(weights[0], 0)
    circuit.rz(weights[1], 0)
    qnn = EstimatorQNN(
        circuit=circuit,
        input_params=[feature],
        weight_params=list(weights),
        input_gradients=True,
    )
    return TorchConnector(
        qnn,
        initial_weights=[0.1, -0.2],
    )


def _build_pennylane_torch_layer():
    import pennylane as qml
    import torch

    device = qml.device("default.qubit", wires=1, shots=None)

    @qml.qnode(device, interface="torch")
    def circuit(inputs, weights):
        qml.RY(inputs[..., 0], wires=0)
        qml.RY(weights[0], wires=0)
        qml.RZ(weights[1], wires=0)
        return qml.expval(qml.Z(0))

    return qml.qnn.TorchLayer(
        circuit,
        {"weights": (2,)},
        init_method=lambda tensor: torch.nn.init.constant_(tensor, 0.1),
    )


def _train_hybrid_native(
    descriptor: dict[str, Any],
    model_path: Path,
    rows: list[list[float]],
    targets: list[float],
) -> dict[str, Any]:
    import torch

    torch.manual_seed(7)
    layer = (
        _build_qiskit_torch_layer()
        if descriptor["sdk"] == "qiskit"
        else _build_pennylane_torch_layer()
    )
    optimizer = torch.optim.SGD(layer.parameters(), lr=0.1)
    inputs = torch.tensor(rows, dtype=torch.float32)
    labels = torch.tensor(targets, dtype=torch.float32)
    for _ in range(2):
        optimizer.zero_grad()
        predictions = layer(inputs).reshape(-1)
        loss = torch.mean((predictions - labels) ** 2)
        loss.backward()
        optimizer.step()
    torch.save(layer.state_dict(), model_path)
    return {
        "backend": type(layer).__name__,
        "training_samples": len(rows),
        "model_file": model_path.as_posix(),
        "final_loss": float(loss.detach()),
    }


def _train_framework_adapter(
    descriptor: dict[str, Any],
    model_path: Path,
    rows: list[list[float]],
    targets: list[float],
) -> dict[str, Any]:
    profile = descriptor["profile"]
    state: dict[str, Any] = {
        "adapter_id": descriptor["adapter_id"],
        "adapter_version": descriptor["adapter_version"],
    }
    if profile in {
        "quantum_kernel",
        "variational_supervised",
        "hybrid_neural",
        "quantum_reservoir",
    }:
        state["linear"] = _fit_linear(_features(descriptor["sdk"], rows), targets)
    elif profile == "quantum_generative":
        state["probability"] = sum(targets) / len(targets)
    elif profile == "quantum_representation":
        state["center"] = sum(_features(descriptor["sdk"], rows)) / len(rows)
    elif profile == "quantum_reinforcement":
        state["action_values"] = targets[:2]
    else:
        raise ValueError(f"unsupported profile: {profile}")
    _atomic_write_json_model(model_path, state)
    return {
        "backend": "framework_official_primitives",
        "training_samples": len(rows),
        "model_file": model_path.as_posix(),
    }


def _qiskit_statevector_kernel(feature_width: int):
    if feature_width < 2:
        raise ValueError("Qiskit ZZ feature map requires at least two features")
    from qiskit.circuit.library import zz_feature_map
    from qiskit_machine_learning.kernels import FidelityStatevectorKernel

    feature_map = zz_feature_map(
        feature_dimension=feature_width,
        reps=1,
        entanglement="linear",
    )
    return FidelityStatevectorKernel(feature_map=feature_map)


def _kernel_feature_map(sdk: str) -> dict[str, Any]:
    return {
        "factory": (
            "cqlib.Circuit.ry_rz_cx"
            if sdk == "cqlib"
            else "qiskit.circuit.library.zz_feature_map"
        ),
        "reps": 1,
        "entanglement": "linear",
    }


class _CqlibStatevectorKernel:
    """Fidelity kernel from Cqlib states; sklearn supplies only the SVM solver."""

    def __init__(self, feature_width: int):
        if not 2 <= feature_width <= MAX_FEATURE_WIDTH:
            raise ValueError("Cqlib kernel requires 2 to 12 features")
        self.feature_width = feature_width

    def _state(self, row):
        import numpy as np
        from cqlib import Circuit
        from cqlib.simulator import StatevectorSimulator

        circuit = Circuit(self.feature_width)
        for index, value in enumerate(row):
            circuit.ry(index, float(value))
            circuit.rz(index, float(value) ** 2)
        for index in range(self.feature_width - 1):
            circuit.cx(index, index + 1)
        amplitudes = StatevectorSimulator(circuit, omp_threads=1).statevector()
        state = np.asarray(
            [
                amplitudes[format(i, f"0{self.feature_width}b")]
                for i in range(2**self.feature_width)
            ],
            dtype=complex,
        )
        if not np.isfinite(state).all() or not np.isclose(np.vdot(state, state), 1):
            raise ValueError("Cqlib returned an invalid or unnormalized statevector")
        return state

    def evaluate(self, x_vec, y_vec=None):
        import numpy as np

        def states(rows):
            rows = np.asarray(rows, dtype=float)
            if rows.ndim != 2 or rows.shape[1] != self.feature_width:
                raise ValueError("Cqlib kernel feature width mismatch")
            if not np.isfinite(rows).all():
                raise ValueError("Cqlib kernel features must be finite")
            return np.stack([self._state(row) for row in rows])

        left = states(x_vec)
        right = left if y_vec is None else states(y_vec)
        return np.clip(np.abs(left.conj() @ right.T) ** 2, 0.0, 1.0)


@lru_cache(maxsize=4)
def _cached_cqlib_kernel(model_content_hash: str, feature_width: int):
    del model_content_hash
    return _CqlibStatevectorKernel(feature_width), RLock()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _bounded_model_bytes(model_path: Path) -> bytes:
    size = model_path.stat().st_size
    if size > MAX_MODEL_BYTES:
        raise ValueError(f"model file exceeds the {MAX_MODEL_BYTES}-byte safety limit")
    content = model_path.read_bytes()
    if len(content) > MAX_MODEL_BYTES:
        raise ValueError(f"model file exceeds the {MAX_MODEL_BYTES}-byte safety limit")
    return content


@lru_cache(maxsize=4)
def _validated_qiskit_model_from_bytes(
    adapter_id: str,
    adapter_version: str,
    selected_variant: str,
    content: bytes,
) -> Mapping[str, Any]:
    """Validate inert Qiskit state once per exact model content."""

    try:
        state = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("model state must be valid UTF-8 JSON") from exc
    if not isinstance(state, dict):
        raise ValueError("model state must be a JSON object")
    if (
        state.get("adapter_id") != adapter_id
        or state.get("adapter_version") != adapter_version
    ):
        raise ValueError("model state does not belong to the materialized adapter")
    sdk = "cqlib" if adapter_id == "cqlib.quantum_kernel" else "qiskit"
    if state.get("model_kind") != f"{sdk}_statevector_kernel_svm":
        raise ValueError("model state is not a safe Qiskit kernel SVM")
    if state.get("variant") != selected_variant:
        raise ValueError("Qiskit kernel model variant does not match the adapter")

    feature_width = state.get("feature_width")
    if (
        not isinstance(feature_width, int)
        or isinstance(feature_width, bool)
        or not 2 <= feature_width <= MAX_FEATURE_WIDTH
    ):
        raise ValueError("Qiskit kernel model has an invalid feature width")
    if state.get("feature_map") != _kernel_feature_map(sdk):
        raise ValueError("Qiskit kernel model has an unsupported feature map")

    support_vectors = state.get("support_vectors")
    dual_coefficients = state.get("dual_coefficients")
    if (
        not isinstance(support_vectors, list)
        or not support_vectors
        or len(support_vectors) > MAX_SUPPORT_VECTORS
        or not isinstance(dual_coefficients, list)
        or len(support_vectors) != len(dual_coefficients)
    ):
        raise ValueError("Qiskit kernel model has invalid support-vector state")
    numeric_support_vectors: list[tuple[float, ...]] = []
    for row_index, row in enumerate(support_vectors):
        if not isinstance(row, list) or len(row) != feature_width:
            raise ValueError("Qiskit kernel support-vector width is invalid")
        numeric_support_vectors.append(
            tuple(
                _finite_number(
                    value,
                    f"support_vectors[{row_index}][{column_index}]",
                )
                for column_index, value in enumerate(row)
            )
        )
    numeric_coefficients = tuple(
        _finite_number(value, f"dual_coefficients[{index}]")
        for index, value in enumerate(dual_coefficients)
    )
    intercept = _finite_number(state.get("intercept"), "intercept")

    output_mapping: tuple[float, float, float] | None
    if selected_variant == "qsvc":
        mapping = state.get("output_mapping")
        if not isinstance(mapping, dict):
            raise ValueError("Qiskit kernel model has invalid output mapping")
        output_mapping = (
            _finite_number(mapping.get("decision_threshold"), "decision_threshold"),
            _finite_number(mapping.get("negative"), "negative class"),
            _finite_number(mapping.get("positive"), "positive class"),
        )
    elif selected_variant == "qsvr":
        if state.get("output_mapping") != {"kind": "continuous"}:
            raise ValueError("Qiskit kernel regressor has invalid output mapping")
        output_mapping = None
    else:
        raise ValueError(f"unsupported safe Qiskit kernel variant: {selected_variant}")

    return MappingProxyType(
        {
            "feature_width": feature_width,
            "support_vectors": tuple(numeric_support_vectors),
            "dual_coefficients": numeric_coefficients,
            "intercept": intercept,
            "output_mapping": output_mapping,
        }
    )


def _load_validated_qiskit_model(
    descriptor: dict[str, Any], model_path: Path
) -> tuple[str, Mapping[str, Any]]:
    content = _bounded_model_bytes(model_path)
    content_hash = sha256(content).hexdigest()
    with _QISKIT_CACHE_LOCK:
        state = _validated_qiskit_model_from_bytes(
            str(descriptor["adapter_id"]),
            str(descriptor["adapter_version"]),
            str(descriptor["selected_variant"]),
            content,
        )
    return content_hash, state


@lru_cache(maxsize=4)
def _cached_qiskit_kernel(model_content_hash: str, feature_width: int):
    del model_content_hash
    return _qiskit_statevector_kernel(feature_width), RLock()


def _validated_inference_rows(
    requests: list[dict[str, Any]],
) -> list[list[float]]:
    if not isinstance(requests, list) or not requests:
        raise ValueError("requests must be a non-empty list")
    if len(requests) > MAX_BATCH_ROWS:
        raise ValueError(f"batch exceeds the {MAX_BATCH_ROWS}-row safety limit")
    rows: list[list[float]] = []
    for row_index, request in enumerate(requests):
        if not isinstance(request, dict):
            raise ValueError(f"requests[{row_index}] must be an object")
        raw_features = request.get("features")
        if not isinstance(raw_features, list) or not raw_features:
            raise ValueError(f"requests[{row_index}].features must be a non-empty list")
        if len(raw_features) > MAX_FEATURE_WIDTH:
            raise ValueError(
                f"requests[{row_index}].features exceeds the "
                f"{MAX_FEATURE_WIDTH}-feature safety limit"
            )
        rows.append(
            [
                _finite_number(
                    value,
                    f"requests[{row_index}].features[{column_index}]",
                )
                for column_index, value in enumerate(raw_features)
            ]
        )
    return rows


def _infer_qiskit_kernel_many(
    descriptor: dict[str, Any],
    model_path: Path,
    rows: list[list[float]],
) -> list[dict[str, Any]]:
    model_content_hash, state = _load_validated_qiskit_model(descriptor, model_path)
    feature_width = state["feature_width"]
    if any(len(row) != feature_width for row in rows):
        raise ValueError("inference features do not match the trained feature width")
    kernel_pairs = len(rows) * len(state["support_vectors"])
    if kernel_pairs > MAX_KERNEL_PAIRS:
        raise ValueError(
            f"batch exceeds the {MAX_KERNEL_PAIRS}-kernel-pair safety limit"
        )

    # Keep dependency-free validation ahead of the optional numerical stack.
    # Core installs can still reject malformed or over-budget model inputs;
    # successful QML inference requires the documented qml-data/qml-qiskit extra.
    import numpy as np

    with _QISKIT_CACHE_LOCK:
        kernel_factory = (
            _cached_cqlib_kernel
            if descriptor["sdk"] == "cqlib"
            else _cached_qiskit_kernel
        )
        kernel, evaluation_lock = kernel_factory(model_content_hash, feature_width)
    with evaluation_lock:
        kernel_values = np.asarray(
            kernel.evaluate(
                x_vec=rows,
                y_vec=state["support_vectors"],
            ),
            dtype=float,
        )
    expected_shape = (len(rows), len(state["support_vectors"]))
    if kernel_values.shape != expected_shape or not np.isfinite(kernel_values).all():
        raise ValueError("Qiskit kernel inference produced invalid kernel values")
    decisions = (
        kernel_values @ np.asarray(state["dual_coefficients"], dtype=float)
        + state["intercept"]
    )
    if not np.isfinite(decisions).all():
        raise ValueError("Qiskit kernel inference produced a non-finite value")

    results: list[dict[str, Any]] = []
    for raw_decision in decisions:
        decision = float(raw_decision)
        result: dict[str, Any] = {"operation": "predict", "value": decision}
        if descriptor["selected_variant"] == "qsvc":
            threshold, negative, positive = state["output_mapping"]
            result["label"] = positive if decision >= threshold else negative
        results.append(result)
    return results


def _train_qiskit_kernel(
    descriptor: dict[str, Any],
    model_path: Path,
    rows: list[list[float]],
    targets: list[float],
) -> dict[str, Any]:
    """Fit a real statevector quantum kernel and persist inert SVM state."""
    variant = descriptor["selected_variant"]
    feature_width = len(rows[0])
    if any(len(row) != feature_width for row in rows):
        raise ValueError(
            "Qiskit kernel training rows must have one fixed feature width"
        )
    if not 2 <= feature_width <= MAX_FEATURE_WIDTH:
        raise ValueError(
            "Qiskit kernel training exceeds the "
            f"{MAX_FEATURE_WIDTH}-feature statevector safety limit"
        )
    if len(rows) * len(rows) > MAX_KERNEL_PAIRS:
        raise ValueError(
            "Qiskit kernel training exceeds the "
            f"{MAX_KERNEL_PAIRS}-kernel-pair safety limit"
        )

    import numpy as np

    numeric_rows = np.asarray(rows, dtype=float)
    numeric_targets = np.asarray(targets, dtype=float)
    if not np.isfinite(numeric_rows).all() or not np.isfinite(numeric_targets).all():
        raise ValueError("Qiskit kernel training data must contain finite numbers")

    sdk = descriptor["sdk"]
    if sdk == "cqlib":
        from sklearn.svm import SVC, SVR

        kernel = _CqlibStatevectorKernel(feature_width)
        model_factory = SVC if variant == "qsvc" else SVR
        model_options = {"kernel": "precomputed"}
        fit_rows = kernel.evaluate(numeric_rows)
    else:
        from qiskit_machine_learning.algorithms import QSVC, QSVR

        kernel = _qiskit_statevector_kernel(feature_width)
        model_factory = QSVC if variant == "qsvc" else QSVR
        model_options = {"quantum_kernel": kernel}
        fit_rows = numeric_rows
    if variant == "qsvc":
        classes = sorted({float(value) for value in numeric_targets})
        if len(classes) != 2:
            raise ValueError("QSVC training requires exactly two target classes")
        model = model_factory(
            **model_options,
            class_weight="balanced",
            C=1.0,
            probability=False,
        )
        model.fit(fit_rows, numeric_targets)
        output_mapping: dict[str, Any] = {
            "negative": float(model.classes_[0]),
            "positive": float(model.classes_[1]),
            "decision_threshold": 0.0,
        }
    elif variant == "qsvr":
        model = model_factory(**model_options, C=1.0, epsilon=0.1)
        model.fit(fit_rows, numeric_targets)
        output_mapping = {"kind": "continuous"}
    else:
        raise ValueError(f"unsupported safe Qiskit kernel variant: {variant}")

    support_indices = [int(index) for index in model.support_]
    state = {
        "adapter_id": descriptor["adapter_id"],
        "adapter_version": descriptor["adapter_version"],
        "model_kind": f"{sdk}_statevector_kernel_svm",
        "variant": variant,
        "feature_width": feature_width,
        "feature_map": _kernel_feature_map(sdk),
        "support_vectors": [
            [float(value) for value in numeric_rows[index]] for index in support_indices
        ],
        "dual_coefficients": [float(value) for value in model.dual_coef_[0]],
        "intercept": float(model.intercept_[0]),
        "output_mapping": output_mapping,
    }
    _atomic_write_json_model(model_path, state)
    return {
        "backend": (
            "cqlib.simulator.StatevectorSimulator+"
            f"sklearn.svm.{type(model).__name__}(precomputed fidelity kernel)"
            if sdk == "cqlib"
            else "qiskit_machine_learning.kernels.FidelityStatevectorKernel+"
            f"qiskit_machine_learning.algorithms.{type(model).__name__}"
        ),
        "training_samples": len(rows),
        "support_vectors": len(support_indices),
        "model_file": model_path.as_posix(),
        "persistence_format": "json_support_vector_state",
    }


def _vqc_circuit_spec(sdk: str = "qiskit") -> dict[str, Any]:
    # These are identifiers checked for equality, never dynamically imported code.
    if sdk == "cqlib":
        return {
            "feature_map": {"factory": "cqlib_ry_rz_squared", "reps": 1},
            "ansatz": {
                "factory": "cqlib_ry_cx_ry",
                "reps": 1,
                "entanglement": "linear",
            },
            "interpret": "basis_index_mod_class_count",
            "basis_order": "q0_least_significant",
            "primitive": "cqlib.simulator.StatevectorSimulator",
            "shots": None,
        }
    return {
        "feature_map": {
            "factory": "zz_feature_map",
            "reps": 1,
            "entanglement": "linear",
        },
        "ansatz": {"factory": "real_amplitudes", "reps": 1, "entanglement": "linear"},
        "interpret": "basis_index_mod_class_count",
        "primitive": "qiskit_machine_learning.primitives.QMLSampler",
        "shots": None,
    }


def _vqc_library_versions(sdk: str = "qiskit") -> dict[str, str]:
    from importlib.metadata import version

    packages = (
        ("cqlib", "numpy", "scipy")
        if sdk == "cqlib"
        else ("qiskit", "qiskit-machine-learning")
    )
    return {name: version(name) for name in packages}


def _vqc_components(feature_width: int, class_count: int):
    from qiskit.circuit.library import real_amplitudes, zz_feature_map
    from qiskit_machine_learning.primitives import QMLSampler

    feature_map = zz_feature_map(feature_width, reps=1, entanglement="linear")
    ansatz = real_amplitudes(feature_width, reps=1, entanglement="linear")

    def interpret(basis_index: int) -> int:
        return basis_index % class_count

    return feature_map, ansatz, QMLSampler(shots=None), interpret


def _vqc_number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be a finite JSON number")
    return _finite_number(value, field)


def _vqc_rows(rows: list[list[float]], max_rows: int) -> list[list[float]]:
    if not isinstance(rows, list) or not 1 <= len(rows) <= max_rows:
        raise ValueError(f"VQC rows must contain 1 to {max_rows} samples")
    if not isinstance(rows[0], list) or not 2 <= len(rows[0]) <= VQC_MAX_FEATURE_WIDTH:
        raise ValueError(f"VQC requires 2 to {VQC_MAX_FEATURE_WIDTH} features")
    width = len(rows[0])
    if any(not isinstance(row, list) or len(row) != width for row in rows):
        raise ValueError("VQC rows must have the same feature width")
    return [[_vqc_number(value, "VQC feature") for value in row] for row in rows]


def _vqc_request_rows(requests):
    if not isinstance(requests, list) or not 1 <= len(requests) <= VQC_MAX_BATCH_ROWS:
        raise ValueError("VQC batch must contain 1 to 256 requests")
    if any(
        not isinstance(request, dict) or set(request) != {"features"}
        for request in requests
    ):
        raise ValueError("VQC requests must contain only features")
    return _vqc_rows([request["features"] for request in requests], VQC_MAX_BATCH_ROWS)


@lru_cache(maxsize=4)
def _validated_vqc_state(adapter_id: str, adapter_version: str, content: bytes):
    sdk = "cqlib" if adapter_id == "cqlib.variational_supervised" else "qiskit"
    try:
        state = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("VQC model must be valid UTF-8 JSON") from exc
    required = {
        "schema",
        "adapter_id",
        "adapter_version",
        "model_kind",
        "feature_width",
        "circuit",
        "input_parameters",
        "weight_parameters",
        "weights",
        "classes",
        "library_versions",
    }
    if not isinstance(state, dict) or set(state) != required:
        raise ValueError("VQC model has invalid JSON fields")
    if (
        state["schema"] != f"{sdk}_vqc_json_v1"
        or state["model_kind"] != f"{sdk}_vqc"
        or state["adapter_id"] != adapter_id
        or state["adapter_version"] != adapter_version
    ):
        raise ValueError("VQC model does not match the adapter/schema")
    width = state["feature_width"]
    if type(width) is not int or not 2 <= width <= VQC_MAX_FEATURE_WIDTH:
        raise ValueError("VQC model has invalid feature width")
    if state["circuit"] != _vqc_circuit_spec(sdk):
        raise ValueError("VQC model has unsupported circuit/execution settings")
    classes = state["classes"]
    if not isinstance(classes, list) or not 2 <= len(classes) <= min(
        VQC_MAX_CLASSES, 2**width
    ):
        raise ValueError("VQC model has invalid class count")
    classes = tuple(_vqc_number(value, "VQC class") for value in classes)
    if tuple(sorted(set(classes))) != classes:
        raise ValueError("VQC classes must be unique and sorted")
    weights = state["weights"]
    if not isinstance(weights, list) or len(weights) != 2 * width:
        raise ValueError("VQC model has invalid weight count")
    weights = tuple(_vqc_number(value, "VQC weight") for value in weights)
    # Standard factories give these names and order; check before numerical imports.
    inputs = [f"x[{index}]" for index in range(width)]
    parameters = [f"θ[{index}]" for index in range(2 * width)]
    if state["input_parameters"] != inputs or state["weight_parameters"] != parameters:
        raise ValueError("VQC model parameter order is incompatible")
    if state["library_versions"] != _vqc_library_versions(sdk):
        raise ValueError(
            "VQC model library versions differ; use the training environment"
        )
    return width, classes, weights, tuple(inputs), tuple(parameters)


@lru_cache(maxsize=4)
def _cached_vqc_network(feature_width: int, class_count: int):
    from qiskit import QuantumCircuit
    from qiskit_machine_learning.neural_networks import SamplerQNN

    feature_map, ansatz, sampler, interpret = _vqc_components(
        feature_width, class_count
    )
    circuit = QuantumCircuit(feature_width)
    circuit.compose(feature_map, inplace=True)
    circuit.compose(ansatz, inplace=True)
    network = SamplerQNN(
        circuit=circuit,
        sampler=sampler,
        input_params=list(feature_map.parameters),
        weight_params=list(ansatz.parameters),
        interpret=interpret,
        output_shape=class_count,
    )
    return network, RLock()


def _infer_qiskit_vqc_many(descriptor, model_path, rows):
    numeric_rows = _vqc_rows(rows, VQC_MAX_BATCH_ROWS)
    content = _bounded_model_bytes(model_path)
    with _QISKIT_CACHE_LOCK:
        width, classes, weights, inputs, parameters = _validated_vqc_state(
            descriptor["adapter_id"], descriptor["adapter_version"], content
        )
        if len(numeric_rows[0]) != width:
            raise ValueError("VQC inference features do not match the model")
        network, lock = _cached_vqc_network(width, len(classes))
    if (
        tuple(str(p) for p in network.input_params) != inputs
        or tuple(str(p) for p in network.weight_params) != parameters
    ):
        raise ValueError("VQC SDK parameter order differs from the saved model")
    import numpy as np

    with lock:
        probabilities = np.asarray(network.forward(numeric_rows, weights), dtype=float)
    if (
        probabilities.shape != (len(numeric_rows), len(classes))
        or not np.isfinite(probabilities).all()
        or np.any(probabilities < -1e-12)
        or np.any(probabilities > 1 + 1e-12)
        or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-10, rtol=0)
    ):
        raise ValueError("VQC inference returned invalid class probabilities")
    results = []
    for row in probabilities:
        index = int(np.argmax(row))  # First class wins ties, like the SDK classifier.
        results.append(
            {
                "operation": "predict",
                "label": classes[index],
                "value": float(row[index]),
                "probabilities": row.tolist(),
                "classes": list(classes),
            }
        )
    return results


def _train_qiskit_vqc(descriptor, model_path, rows, targets):
    numeric_rows = _vqc_rows(rows, VQC_MAX_TRAINING_ROWS)
    numeric_targets = [_vqc_number(value, "VQC target") for value in targets]
    classes = sorted(set(numeric_targets))
    width = len(numeric_rows[0])
    if not 2 <= len(classes) <= min(VQC_MAX_CLASSES, 2**width):
        raise ValueError("VQC requires 2 to min(10, 2**feature_width) target classes")
    import numpy as np
    from qiskit_machine_learning.algorithms import VQC
    from qiskit_machine_learning.optimizers import COBYLA

    feature_map, ansatz, sampler, interpret = _vqc_components(width, len(classes))
    initial = np.random.default_rng(VQC_SEED).uniform(
        -np.pi, np.pi, ansatz.num_parameters
    )
    trace = []

    def record_loss(_weights, loss):
        trace.append(_finite_number(loss, "VQC training loss"))

    model = VQC(
        feature_map=feature_map,
        ansatz=ansatz,
        sampler=sampler,
        optimizer=COBYLA(maxiter=VQC_MAXITER),
        initial_point=initial,
        interpret=interpret,
        output_shape=len(classes),
        callback=record_loss,
    )
    # Keep the native encoder deterministic; the original numeric labels live in JSON.
    indices = np.asarray([classes.index(value) for value in numeric_targets])
    model.fit(np.asarray(numeric_rows), indices)
    state = {
        "schema": "qiskit_vqc_json_v1",
        "adapter_id": descriptor["adapter_id"],
        "adapter_version": descriptor["adapter_version"],
        "model_kind": "qiskit_vqc",
        "feature_width": width,
        "circuit": _vqc_circuit_spec(),
        "input_parameters": [str(p) for p in feature_map.parameters],
        "weight_parameters": [str(p) for p in ansatz.parameters],
        "weights": [float(value) for value in model.weights],
        "classes": classes,
        "library_versions": _vqc_library_versions(),
    }
    # Validate the complete state before replacing a previous successful model.
    rendered = json.dumps(state, allow_nan=False).encode("utf-8")
    _validated_vqc_state(
        descriptor["adapter_id"], descriptor["adapter_version"], rendered
    )
    _atomic_write_json_model(model_path, state)
    evidence_path = _trusted_model_path(model_path.with_suffix(".training.json"))
    evidence = {
        "schema": "qiskit_vqc_training_v1",
        "model_file": model_path.relative_to(_application_root()).as_posix(),
        "model_sha256": sha256(
            json.dumps(state, sort_keys=True, allow_nan=False).encode("utf-8")
        ).hexdigest(),
        "loss": trace,
        "parameter_names": state["weight_parameters"],
        "initial_weights": initial.tolist(),
        "trained_weights": state["weights"],
        "optimizer": "COBYLA",
        "maxiter": VQC_MAXITER,
        "seed": VQC_SEED,
        "training_samples": len(rows),
    }
    _atomic_write_json_model(evidence_path, evidence)
    return {
        "backend": "qiskit_machine_learning.algorithms.VQC+QMLSampler(exact)",
        "training_samples": len(rows),
        "model_file": model_path.as_posix(),
        "persistence_format": "json_vqc_weights",
        "class_count": len(classes),
        "initial_weights": initial.tolist(),
        "training_loss": trace,
        "training_evidence_file": evidence_path.relative_to(
            _application_root()
        ).as_posix(),
        "optimizer": "COBYLA",
        "maxiter": VQC_MAXITER,
        "seed": VQC_SEED,
        "weights_changed": not np.allclose(model.weights, initial, atol=1e-12, rtol=0),
    }


def _is_cqlib_vqc(descriptor):
    return (
        descriptor["sdk"] == "cqlib"
        and descriptor["profile"] == "variational_supervised"
        and descriptor["selected_variant"] == "vqc"
    )


def _cqlib_vqc_probabilities(rows, weights, class_count):
    """Exact Cqlib circuit probabilities, with q0 the rightmost bit in SDK keys."""
    import numpy as np
    from cqlib import Circuit
    from cqlib.simulator import StatevectorSimulator

    width = len(rows[0])
    probabilities = np.zeros((len(rows), class_count), dtype=float)
    for row_index, row in enumerate(rows):
        circuit = Circuit(width)
        for qubit, value in enumerate(row):
            circuit.ry(qubit, float(value))
            circuit.rz(qubit, float(value) ** 2)
            circuit.ry(qubit, float(weights[qubit]))
        for qubit in range(width - 1):
            circuit.cx(qubit, qubit + 1)
        for qubit in range(width):
            circuit.ry(qubit, float(weights[width + qubit]))
        state = StatevectorSimulator(circuit, omp_threads=1).statevector()
        for basis in range(2**width):
            probabilities[row_index, basis % class_count] += (
                abs(state[format(basis, f"0{width}b")]) ** 2
            )
    if (
        not np.isfinite(probabilities).all()
        or np.any(probabilities < 0)
        or np.any(probabilities > 1 + 1e-12)
        or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-10, rtol=0)
    ):
        raise ValueError("Cqlib VQC returned invalid class probabilities")
    return probabilities


def _infer_cqlib_vqc_many(descriptor, model_path, rows):
    import numpy as np

    numeric_rows = _vqc_rows(rows, VQC_MAX_BATCH_ROWS)
    width, classes, weights, _inputs, _parameters = _validated_vqc_state(
        descriptor["adapter_id"],
        descriptor["adapter_version"],
        _bounded_model_bytes(model_path),
    )
    if len(numeric_rows[0]) != width:
        raise ValueError("VQC inference features do not match the model")
    probabilities = _cqlib_vqc_probabilities(numeric_rows, weights, len(classes))
    return [
        {
            "operation": "predict",
            "label": classes[int(np.argmax(row))],
            "value": float(np.max(row)),
            "probabilities": row.tolist(),
            "classes": list(classes),
        }
        for row in probabilities
    ]


def _train_cqlib_vqc(descriptor, model_path, rows, targets):
    """Framework VQC on Cqlib primitives; scipy supplies derivative-free optimization."""
    import numpy as np
    from scipy.optimize import minimize

    numeric_rows = _vqc_rows(rows, VQC_MAX_TRAINING_ROWS)
    numeric_targets = [_vqc_number(value, "VQC target") for value in targets]
    classes = sorted(set(numeric_targets))
    width = len(numeric_rows[0])
    if not 2 <= len(classes) <= min(VQC_MAX_CLASSES, 2**width):
        raise ValueError("VQC requires 2 to min(10, 2**feature_width) target classes")
    indices = np.asarray([classes.index(value) for value in numeric_targets])
    initial = np.random.default_rng(VQC_SEED).uniform(-np.pi, np.pi, 2 * width)
    trace = []

    def objective(weights):
        probabilities = _cqlib_vqc_probabilities(numeric_rows, weights, len(classes))
        loss = float(
            -np.log(
                np.clip(probabilities[np.arange(len(rows)), indices], 1e-12, 1)
            ).mean()
        )
        trace.append(_finite_number(loss, "VQC training loss"))
        return loss

    optimized = minimize(
        objective, initial, method="COBYLA", options={"maxiter": VQC_MAXITER}
    )
    state = {
        "schema": "cqlib_vqc_json_v1",
        "adapter_id": descriptor["adapter_id"],
        "adapter_version": descriptor["adapter_version"],
        "model_kind": "cqlib_vqc",
        "feature_width": width,
        "circuit": _vqc_circuit_spec("cqlib"),
        "input_parameters": [f"x[{index}]" for index in range(width)],
        "weight_parameters": [f"θ[{index}]" for index in range(2 * width)],
        "weights": [float(value) for value in optimized.x],
        "classes": classes,
        "library_versions": _vqc_library_versions("cqlib"),
    }
    _validated_vqc_state(
        descriptor["adapter_id"],
        descriptor["adapter_version"],
        json.dumps(state, allow_nan=False).encode("utf-8"),
    )
    _atomic_write_json_model(model_path, state)
    evidence_path = _trusted_model_path(model_path.with_suffix(".training.json"))
    evidence = {
        "schema": "cqlib_vqc_training_v1",
        "model_file": model_path.relative_to(_application_root()).as_posix(),
        "model_sha256": sha256(
            json.dumps(state, sort_keys=True, allow_nan=False).encode("utf-8")
        ).hexdigest(),
        "loss": trace,
        "parameter_names": state["weight_parameters"],
        "initial_weights": initial.tolist(),
        "trained_weights": state["weights"],
        "optimizer": "COBYLA",
        "optimizer_converged": bool(optimized.success),
        "optimizer_message": str(optimized.message),
        "maxiter": VQC_MAXITER,
        "seed": VQC_SEED,
        "training_samples": len(rows),
    }
    _atomic_write_json_model(evidence_path, evidence)
    return {
        "backend": "cqlib.simulator.StatevectorSimulator+scipy.optimize.minimize(COBYLA)",
        "implementation_level": "official_primitives",
        "training_samples": len(rows),
        "model_file": model_path.as_posix(),
        "persistence_format": "json_vqc_weights",
        "class_count": len(classes),
        "initial_weights": initial.tolist(),
        "training_loss": trace,
        "training_evidence_file": evidence_path.relative_to(
            _application_root()
        ).as_posix(),
        "optimizer": "COBYLA",
        "optimizer_converged": bool(optimized.success),
        "optimizer_message": str(optimized.message),
        "maxiter": VQC_MAXITER,
        "seed": VQC_SEED,
        "weights_changed": not np.allclose(optimized.x, initial, atol=1e-12, rtol=0),
    }


def _pennylane_variational_circuit():
    import pennylane as qml
    from pennylane import numpy as np

    device = qml.device("default.qubit", wires=1, shots=None)

    @qml.qnode(device, interface="autograd")
    def circuit(input_angle, weights):
        qml.RY(input_angle, wires=0)
        qml.Rot(weights[0], weights[1], weights[2], wires=0)
        return qml.expval(qml.Z(0))

    return qml, np, circuit


def _train_pennylane_variational(
    descriptor: dict[str, Any],
    model_path: Path,
    rows: list[list[float]],
    targets: list[float],
) -> dict[str, Any]:
    qml, np, circuit = _pennylane_variational_circuit()
    variant = descriptor["selected_variant"]
    input_width = len(rows[0])
    if any(len(row) != input_width for row in rows):
        raise ValueError("variational training rows must have one fixed feature width")
    if variant == "vqc":
        classes = sorted({float(target) for target in targets})
        if len(classes) != 2:
            raise ValueError("VQC training requires exactly two target classes")
        low, high = classes
        mapped_targets = [-1.0 if float(target) == low else 1.0 for target in targets]
        output_mapping: dict[str, Any] = {
            "negative": low,
            "positive": high,
            "decision_threshold": 0.0,
        }
    elif variant == "vqr":
        mapped_targets = [float(target) for target in targets]
        output_mapping = {"kind": "continuous"}
    else:
        raise ValueError(f"unsupported PennyLane variational variant: {variant}")

    inputs = np.array(rows, requires_grad=False)
    input_angles = np.mean(inputs, axis=1)
    expected = np.array(mapped_targets, requires_grad=False)
    weights = np.array([0.1, -0.2, 0.3], requires_grad=True)

    def loss(trainable_weights):
        predictions = circuit(input_angles, trainable_weights)
        return np.mean((predictions - expected) ** 2)

    optimizer = qml.GradientDescentOptimizer(stepsize=0.2)
    initial_loss = float(loss(weights))
    for _ in range(12):
        weights = optimizer.step(loss, weights)
    final_loss = float(loss(weights))
    state = {
        "adapter_id": descriptor["adapter_id"],
        "adapter_version": descriptor["adapter_version"],
        "model_kind": "pennylane_variational",
        "variant": variant,
        "weights": [float(value) for value in weights],
        "input_width": input_width,
        "feature_reduction": "row_mean_angle",
        "output_mapping": output_mapping,
    }
    _atomic_write_json_model(model_path, state)
    return {
        "backend": "pennylane.QNode",
        "training_samples": len(rows),
        "model_file": model_path.as_posix(),
        "initial_loss": initial_loss,
        "final_loss": final_loss,
    }


def train_and_save(
    model_path: str | Path,
    rows: list[list[float]],
    targets: list[float],
) -> dict[str, Any]:
    descriptor = _descriptor()
    profile = descriptor["profile"]
    if len(rows) != len(targets) or not rows or any(not row for row in rows):
        raise ValueError("training rows and targets must be non-empty and aligned")
    path = _trusted_model_path(model_path)
    _reject_unsupported_qiskit_variational(descriptor)
    path.parent.mkdir(parents=True, exist_ok=True)
    if _is_qiskit_vqc(descriptor):
        result = _train_qiskit_vqc(descriptor, path, rows, targets)
    elif _is_cqlib_vqc(descriptor):
        result = _train_cqlib_vqc(descriptor, path, rows, targets)
    elif profile == "quantum_kernel" and descriptor["sdk"] in {"qiskit", "cqlib"}:
        result = _train_qiskit_kernel(descriptor, path, rows, targets)
    elif profile == "variational_supervised" and descriptor["sdk"] == "pennylane":
        result = _train_pennylane_variational(descriptor, path, rows, targets)
    elif profile == "hybrid_neural" and descriptor["sdk"] in {
        "qiskit",
        "pennylane",
    }:
        result = _train_hybrid_native(descriptor, path, rows, targets)
    else:
        result = _train_framework_adapter(descriptor, path, rows, targets)
    # Only the actual successful training path writes this receipt. Inference
    # and model-loading calls leave it untouched, including deterministic reruns.
    receipt_path = path.with_suffix(".training-receipt.json")
    with path.open("rb") as stream:
        model_hash = file_digest(stream, "sha256").hexdigest()
    _atomic_write_json_model(
        receipt_path,
        {
            "schema": "qml_training_receipt_v1",
            "run_id": os.environ.get("QMIND_TRAINING_RUN_ID"),
            "model_file": path.relative_to(_application_root()).as_posix(),
            "model_sha256": model_hash,
            "training_samples": len(rows),
            "adapter_id": descriptor["adapter_id"],
            "adapter_version": descriptor["adapter_version"],
        },
    )
    return {
        **result,
        "training_receipt_file": receipt_path.relative_to(
            _application_root()
        ).as_posix(),
    }


def _load_hybrid_native(
    descriptor: dict[str, Any], model_path: Path, features: list[float]
) -> float:
    import torch

    layer = (
        _build_qiskit_torch_layer()
        if descriptor["sdk"] == "qiskit"
        else _build_pennylane_torch_layer()
    )
    layer.load_state_dict(torch.load(model_path, weights_only=True))
    with torch.no_grad():
        return float(
            layer(torch.tensor([features], dtype=torch.float32)).reshape(-1)[0]
        )


def describe_circuit(model_path: str | Path, request: dict[str, Any]) -> dict[str, Any]:
    """Export the validated Qiskit runtime circuit without training or SDK imports in apps.

    VQC binds the same cached SamplerQNN circuit used for inference. Kernel
    routes expose only the input feature map, not a fictitious SVM circuit.
    Returned objects are fresh numeric data; cached SDK objects stay immutable.
    """
    descriptor = _descriptor()
    if descriptor["sdk"] != "qiskit":
        raise ValueError("circuit export is unavailable for this SDK")
    path = _trusted_model_path(model_path)
    if _is_qiskit_vqc(descriptor):
        rows = _vqc_rows(_vqc_request_rows([request]), 1)
        with _QISKIT_CACHE_LOCK:
            width, classes, weights, inputs, parameters = _validated_vqc_state(
                descriptor["adapter_id"],
                descriptor["adapter_version"],
                _bounded_model_bytes(path),
            )
            if len(rows[0]) != width:
                raise ValueError("VQC inference features do not match the model")
            network, lock = _cached_vqc_network(width, len(classes))
        if (
            tuple(str(p) for p in network.input_params) != inputs
            or tuple(str(p) for p in network.weight_params) != parameters
        ):
            raise ValueError("VQC SDK parameter order differs from the saved model")
        bindings = dict(zip(network.input_params, rows[0], strict=True))
        bindings.update(zip(network.weight_params, weights, strict=True))
        with lock:
            circuit = network.circuit.assign_parameters(bindings, inplace=False)
        stage = "trained VQC: bound input and saved weights"
    elif descriptor["profile"] == "quantum_kernel":
        rows = _validated_inference_rows([request])
        model_hash, state = _load_validated_qiskit_model(descriptor, path)
        width = state["feature_width"]
        if len(rows[0]) != width:
            raise ValueError("inference features do not match the model")
        with _QISKIT_CACHE_LOCK:
            kernel, lock = _cached_qiskit_kernel(model_hash, width)
        with lock:
            feature_map = kernel.feature_map
            circuit = feature_map.assign_parameters(
                dict(zip(feature_map.parameters, rows[0], strict=True)),
                inplace=False,
            )
        stage = "input feature map; classical kernel decision is not a quantum gate"
    else:
        raise ValueError("circuit export is unavailable for this QML profile")
    gates = []
    for instruction in circuit.data:
        operation = instruction.operation
        gate = {
            "gate": operation.name.upper(),
            "stage": stage,
            "qubits": [circuit.find_bit(qubit).index for qubit in instruction.qubits],
        }
        if operation.params:
            gate["params"] = [
                _finite_number(float(value), "circuit parameter")
                for value in operation.params
            ]
        gates.append(gate)
    return {
        "qubits": int(circuit.num_qubits),
        "depth": int(circuit.depth()),
        "backend": "local_simulator",
        "gates": gates,
    }


def load_and_infer(model_path: str | Path, request: dict[str, Any]) -> dict[str, Any]:
    descriptor = _descriptor()
    path = _trusted_model_path(model_path)
    profile = descriptor["profile"]
    _reject_unsupported_qiskit_variational(descriptor)
    if not path.is_file():
        raise ValueError(f"model file does not exist: {path}")
    if _is_qiskit_vqc(descriptor):
        return _infer_qiskit_vqc_many(descriptor, path, _vqc_request_rows([request]))[0]
    if _is_cqlib_vqc(descriptor):
        return _infer_cqlib_vqc_many(descriptor, path, _vqc_request_rows([request]))[0]
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    raw_features = request.get("features")
    if not isinstance(raw_features, list) or not raw_features:
        raise ValueError("request.features must be a non-empty list")
    values = [
        _finite_number(value, f"request.features[{index}]")
        for index, value in enumerate(raw_features)
    ]
    if len(values) > MAX_FEATURE_WIDTH:
        raise ValueError(
            f"request.features exceeds the {MAX_FEATURE_WIDTH}-feature safety limit"
        )
    if profile == "quantum_kernel" and descriptor["sdk"] in {"qiskit", "cqlib"}:
        return _infer_qiskit_kernel_many(descriptor, path, [values])[0]
    if profile == "hybrid_neural" and descriptor["sdk"] in {
        "qiskit",
        "pennylane",
    }:
        value = _load_hybrid_native(descriptor, path, values)
        return {"operation": "predict", "value": value}

    state = json.loads(path.read_text())
    if not isinstance(state, dict):
        raise ValueError("model state must be a JSON object")
    if (
        state.get("adapter_id") != descriptor["adapter_id"]
        or state.get("adapter_version") != descriptor["adapter_version"]
    ):
        raise ValueError("model state does not belong to the materialized adapter")
    if profile == "variational_supervised" and descriptor["sdk"] == "pennylane":
        if state.get("model_kind") != "pennylane_variational":
            raise ValueError("model state is not a PennyLane variational model")
        if len(values) != int(state["input_width"]):
            raise ValueError(
                "inference features do not match the trained feature width"
            )
        _qml, np, circuit = _pennylane_variational_circuit()
        weights = np.array(state["weights"], requires_grad=False)
        score = float(circuit(float(sum(values) / len(values)), weights))
        result: dict[str, Any] = {"operation": "predict", "value": score}
        if descriptor["selected_variant"] == "vqc":
            mapping = state["output_mapping"]
            result["label"] = (
                mapping["positive"]
                if score >= float(mapping["decision_threshold"])
                else mapping["negative"]
            )
        return result
    quantum_features = [_expectation(descriptor["sdk"], value) for value in values]
    mean = sum(quantum_features) / len(quantum_features)
    if profile in {
        "quantum_kernel",
        "variational_supervised",
        "hybrid_neural",
        "quantum_reservoir",
    }:
        linear = state["linear"]
        return {
            "operation": "predict",
            "value": linear["slope"] * mean + linear["intercept"],
        }
    if profile == "quantum_generative":
        shots = int(request.get("shots", 8))
        probability = min(1.0, max(0.0, float(state["probability"])))
        samples = [
            1 if ((index + 0.5) / shots) <= probability else 0 for index in range(shots)
        ]
        return {"operation": "sample", "samples": samples}
    if profile == "quantum_representation":
        return {
            "operation": "transform",
            "embedding": [value - state["center"] for value in quantum_features],
        }
    if profile == "quantum_reinforcement":
        action_values = state["action_values"]
        return {
            "operation": "act",
            "action": max(range(len(action_values)), key=action_values.__getitem__),
            "action_values": action_values,
        }
    raise ValueError(f"unsupported profile: {profile}")


def load_and_infer_many(
    model_path: str | Path, requests: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Infer a bounded batch while reusing immutable validated runtime state."""

    descriptor = _descriptor()
    path = _trusted_model_path(model_path)
    profile = descriptor["profile"]
    _reject_unsupported_qiskit_variational(descriptor)
    if not path.is_file():
        raise ValueError(f"model file does not exist: {path}")
    if _is_qiskit_vqc(descriptor):
        return _infer_qiskit_vqc_many(descriptor, path, _vqc_request_rows(requests))
    if _is_cqlib_vqc(descriptor):
        return _infer_cqlib_vqc_many(descriptor, path, _vqc_request_rows(requests))
    rows = _validated_inference_rows(requests)
    if profile == "quantum_kernel" and descriptor["sdk"] in {"qiskit", "cqlib"}:
        return _infer_qiskit_kernel_many(descriptor, path, rows)
    return [load_and_infer(model_path, request) for request in requests]


def infer(request: dict[str, Any]) -> dict[str, Any]:
    descriptor = _descriptor()
    raw_features = request.get("features")
    if not isinstance(raw_features, list) or not raw_features:
        raise ValueError("request.features must be a non-empty list")
    values = [float(value) for value in raw_features]
    quantum_features = [_expectation(descriptor["sdk"], value) for value in values]
    mean = sum(quantum_features) / len(quantum_features)
    operation = descriptor["operation"]
    if operation == "predict":
        return {"operation": operation, "value": mean}
    if operation == "sample":
        return {"operation": operation, "samples": [int(mean >= 0.0)]}
    if operation == "transform":
        return {"operation": operation, "embedding": quantum_features}
    return {"operation": operation, "action": int(mean < 0.0)}


def smoke(model_path: str | Path | None = None) -> dict[str, Any]:
    descriptor = _descriptor()
    rows, targets = _route_smoke_training_fixture(descriptor)
    path = (
        Path(model_path)
        if model_path is not None
        else _models_root()
        / (
            ".qml-smoke-model.json"
            if descriptor.get("persistence_format") == "json"
            else ".qml-smoke-model.bin"
        )
    )
    try:
        training = train_and_save(path, rows=rows, targets=targets)
        result = load_and_infer(path, {"features": rows[0]})
    finally:
        if model_path is None:
            path.unlink(missing_ok=True)
            path.with_suffix(".training.json").unlink(missing_ok=True)
            path.with_suffix(".training-receipt.json").unlink(missing_ok=True)
    return {
        "status": "passed",
        "adapter": _descriptor()["adapter_id"],
        "training": training,
        "result": result,
    }


if __name__ == "__main__":
    print(json.dumps(smoke(), separators=(",", ":")))
