"""Framework-owned FastAPI shell for a materialized QML application.

Application-specific model loading, preprocessing, copy, and inference live in
``backend/application.py``. This module owns the stable HTTP and display
contracts so each coding run does not have to recreate them.
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any

from backend import application
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

BACKEND_DIR = Path(__file__).resolve().parent
APPLICATION_ROOT = BACKEND_DIR.parent
FRONTEND_ENTRY = APPLICATION_ROOT / "frontend" / "standalone" / "index.html"
MANIFEST_PATH = APPLICATION_ROOT / "application_manifest.json"
LOGGER = logging.getLogger(__name__)


class SurfaceContractError(ValueError):
    """An application module returned data the fixed product surface cannot render."""


def _application_identity() -> tuple[str, bool, str, str]:
    service = getattr(application, "SERVICE_ID", None)
    model_loaded = getattr(application, "MODEL_LOADED", None)
    score_semantics = getattr(application, "SCORE_SEMANTICS", None)
    score_semantics_en = getattr(application, "SCORE_SEMANTICS_EN", None)
    if not isinstance(service, str) or not service.strip():
        raise RuntimeError("backend.application.SERVICE_ID must be a non-empty string")
    if model_loaded is not True:
        raise RuntimeError(
            "backend.application.MODEL_LOADED must be true after artifact load"
        )
    if not isinstance(score_semantics, str) or not score_semantics.strip():
        raise RuntimeError(
            "backend.application.SCORE_SEMANTICS must be a non-empty string"
        )
    # English semantics is required so the EN switch never falls back to Chinese.
    if not (isinstance(score_semantics_en, str) and score_semantics_en.strip()):
        raise RuntimeError(
            "backend.application.SCORE_SEMANTICS_EN must be a non-empty English string"
        )
    if not callable(getattr(application, "get_info", None)):
        raise RuntimeError("backend.application.get_info must be callable")
    if not callable(getattr(application, "infer", None)):
        raise RuntimeError("backend.application.infer must be callable")
    return service, model_loaded, score_semantics, score_semantics_en


SERVICE_ID, MODEL_LOADED, SCORE_SEMANTICS, SCORE_SEMANTICS_EN = _application_identity()
app = FastAPI(title=SERVICE_ID, version="1.0.0")


def _read_manifest() -> dict[str, Any]:
    try:
        value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("application_manifest.json is missing or invalid") from exc
    if not isinstance(value, dict):
        raise RuntimeError("application_manifest.json must contain one object")
    return value


def resolve_network() -> tuple[str, int]:
    """Resolve the bind address with process-scoped environment precedence."""
    network = _read_manifest().get("network")
    if not isinstance(network, dict):
        network = {}
    host = os.environ.get("APP_HOST", str(network.get("host", "127.0.0.1")))
    raw_port = os.environ.get("APP_PORT", str(network.get("port", 8080)))
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise RuntimeError(
            "APP_PORT/application manifest port must be an integer"
        ) from exc
    if not host.strip() or not 1 <= port <= 65535:
        raise RuntimeError("application host/port is outside the supported range")
    return host, port


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SurfaceContractError(f"{label} must be an object")
    return value


def _display_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise SurfaceContractError(f"{label} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise SurfaceContractError(f"{label} items must be non-empty strings")
    return value


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SurfaceContractError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise SurfaceContractError(f"{label} must be finite")
    return number


_CJK_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def _has_cjk(value: Any) -> bool:
    return isinstance(value, str) and bool(_CJK_PATTERN.search(value))


def _bilingual_text(container: Mapping[str, Any], key: str, label: str) -> None:
    """Reject Chinese display text without an English twin.

    The standalone page switches to ``<key>_en`` and silently falls back to the
    Chinese base value when the twin is missing, so a missing twin is exactly
    the "English page still shows Chinese" defect.
    """
    if not _has_cjk(container.get(key)):
        return
    twin = container.get(f"{key}_en")
    if not isinstance(twin, str) or not twin.strip():
        raise SurfaceContractError(
            f"{label}.{key}_en must be a non-empty English string when "
            f"{key} contains Chinese"
        )


def _bilingual_strings(container: Mapping[str, Any], key: str, label: str) -> None:
    items = container.get(key)
    if not isinstance(items, list) or not any(_has_cjk(item) for item in items):
        return
    twin = container.get(f"{key}_en")
    if not isinstance(twin, list) or not twin:
        raise SurfaceContractError(
            f"{label}.{key}_en must be a non-empty English list when {key} "
            "contains Chinese"
        )
    if len(twin) != len(items):
        raise SurfaceContractError(
            f"{label}.{key}_en must contain {len(items)} items to mirror {key}"
        )
    for index, item in enumerate(twin):
        if not isinstance(item, str) or not item.strip():
            raise SurfaceContractError(
                f"{label}.{key}_en[{index}] must be a non-empty string"
            )


def _validate_info(value: Any) -> dict[str, Any]:
    info = dict(_mapping(value, "/api/info response"))
    required = {
        "title",
        "description",
        "scenario_summary",
        "fields",
        "presets",
        "method_steps",
        "metrics",
        "scientific_boundary",
    }
    missing = required - set(info)
    if missing:
        raise SurfaceContractError(f"/api/info missing keys: {sorted(missing)}")
    if "execution_kind" in info and info["execution_kind"] not in {
        "inference",
        "solver",
    }:
        raise SurfaceContractError(
            "/api/info execution_kind must be inference or solver"
        )
    for key in ("title", "description", "scenario_summary"):
        if not isinstance(info[key], str) or not info[key].strip():
            raise SurfaceContractError(f"/api/info {key} must be a non-empty string")
        _bilingual_text(info, key, "/api/info")

    fields = info["fields"]
    if not isinstance(fields, list) or not fields:
        raise SurfaceContractError("/api/info fields must be a non-empty list")
    field_ids: list[str] = []
    for index, raw_field in enumerate(fields):
        field = _mapping(raw_field, f"fields[{index}]")
        field_missing = {"id", "label", "min", "max", "step", "default"} - set(field)
        if field_missing:
            raise SurfaceContractError(
                f"fields[{index}] missing keys: {sorted(field_missing)}"
            )
        field_id = field["id"]
        label = field["label"]
        if not isinstance(field_id, str) or not field_id.strip():
            raise SurfaceContractError(f"fields[{index}].id must be non-empty")
        if not isinstance(label, str) or not label.strip():
            raise SurfaceContractError(f"fields[{index}].label must be non-empty")
        _bilingual_text(field, "label", f"fields[{index}]")
        minimum = _finite_number(field["min"], f"fields[{index}].min")
        maximum = _finite_number(field["max"], f"fields[{index}].max")
        default = _finite_number(field["default"], f"fields[{index}].default")
        step = _finite_number(field["step"], f"fields[{index}].step")
        if minimum > default or default > maximum:
            raise SurfaceContractError(
                f"fields[{index}].default must stay inside min/max"
            )
        if step <= 0:
            raise SurfaceContractError(f"fields[{index}].step must be positive")
        field_ids.append(field_id)
    if len(field_ids) != len(set(field_ids)):
        raise SurfaceContractError("/api/info field ids must be unique")

    presets = info["presets"]
    if not isinstance(presets, list) or not presets:
        raise SurfaceContractError("/api/info presets must be a non-empty list")
    for index, raw_preset in enumerate(presets):
        preset = _mapping(raw_preset, f"presets[{index}]")
        if not isinstance(preset.get("name"), str) or not preset["name"].strip():
            raise SurfaceContractError(f"presets[{index}].name must be non-empty")
        _bilingual_text(preset, "name", f"presets[{index}]")
        values = preset.get("values")
        if not isinstance(values, Mapping) or set(values) != set(field_ids):
            raise SurfaceContractError(
                f"presets[{index}].values must provide exactly every declared field"
            )

    steps = info["method_steps"]
    if not isinstance(steps, list) or not steps:
        raise SurfaceContractError("/api/info method_steps must be a non-empty list")
    for index, raw_step in enumerate(steps):
        step = _mapping(raw_step, f"method_steps[{index}]")
        if not all(
            isinstance(step.get(key), str) and step[key].strip()
            for key in ("title", "detail")
        ):
            raise SurfaceContractError(
                f"method_steps[{index}] requires non-empty title/detail"
            )
        _bilingual_text(step, "title", f"method_steps[{index}]")
        _bilingual_text(step, "detail", f"method_steps[{index}]")

    metrics = info["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise SurfaceContractError("/api/info metrics must be a non-empty list")
    for index, raw_metric in enumerate(metrics):
        metric = _mapping(raw_metric, f"metrics[{index}]")
        if not isinstance(metric.get("label"), str) or not metric["label"].strip():
            raise SurfaceContractError(f"metrics[{index}].label must be non-empty")
        _bilingual_text(metric, "label", f"metrics[{index}]")
        if "value" not in metric:
            raise SurfaceContractError(f"metrics[{index}].value is required")
    _display_strings(info["scientific_boundary"], "scientific_boundary")
    _bilingual_strings(info, "scientific_boundary", "/api/info")
    return info


def _validate_prediction(value: Any) -> None:
    prediction = _mapping(value, "prediction")
    kind = prediction.get("kind")
    if kind in {"classification", "solution"}:
        if (
            not isinstance(prediction.get("label"), str)
            or not prediction["label"].strip()
        ):
            raise SurfaceContractError(f"{kind} prediction.label is required")
        _bilingual_text(prediction, "label", f"{kind} prediction")
        primary = "decision_value" if kind == "classification" else "value"
        _finite_number(prediction.get(primary), f"prediction.{primary}")
        if (
            not isinstance(prediction.get("score_semantics"), str)
            or not prediction["score_semantics"].strip()
        ):
            raise SurfaceContractError(f"{kind} prediction.score_semantics is required")
        _bilingual_text(prediction, "score_semantics", f"{kind} prediction")
        scores = prediction.get("scores")
        if not isinstance(scores, list) or not scores:
            raise SurfaceContractError(f"{kind} prediction.scores is required")
        for index, raw_score in enumerate(scores):
            score = _mapping(raw_score, f"prediction.scores[{index}]")
            if not isinstance(score.get("label"), str) or not score["label"].strip():
                raise SurfaceContractError(
                    f"prediction.scores[{index}].label is required"
                )
            _bilingual_text(score, "label", f"prediction.scores[{index}]")
            normalized = _finite_number(
                score.get("value"), f"prediction.scores[{index}].value"
            )
            if kind == "classification" and not 0 <= normalized <= 1:
                raise SurfaceContractError(
                    f"prediction.scores[{index}].value must be normalized to 0..1"
                )
    elif kind == "energy":
        _finite_number(prediction.get("value"), "prediction.value")
        for key in ("unit", "score_semantics"):
            if not isinstance(prediction.get(key), str) or not prediction[key].strip():
                raise SurfaceContractError(f"energy prediction.{key} is required")
            _bilingual_text(prediction, key, "energy prediction")
        _bilingual_text(prediction, "label", "energy prediction")
    elif kind == "regression":
        _finite_number(prediction.get("value"), "prediction.value")
        _finite_number(
            prediction.get("normalized_value"), "prediction.normalized_value"
        )
        if not isinstance(prediction.get("unit"), str):
            raise SurfaceContractError("regression prediction.unit must be a string")
        _bilingual_text(prediction, "unit", "regression prediction")
        _bilingual_text(prediction, "label", "regression prediction")
        _bilingual_text(prediction, "score_semantics", "regression prediction")
    else:
        raise SurfaceContractError(
            "prediction.kind must be classification, regression, solution, or energy"
        )


def _validate_convergence(value: Any, prediction: Mapping[str, Any]) -> None:
    """Validate actual solver evaluations without inventing a monotonic curve."""
    convergence = _mapping(value, "convergence")
    if prediction.get("kind") != "energy":
        raise SurfaceContractError("convergence requires an energy prediction")
    if convergence.get("unit") != prediction.get("unit"):
        raise SurfaceContractError("convergence.unit must match prediction.unit")
    _bilingual_text(convergence, "unit", "convergence")
    if (
        not isinstance(convergence.get("semantics"), str)
        or not convergence["semantics"].strip()
    ):
        raise SurfaceContractError("convergence.semantics is required")
    points = convergence.get("points")
    if not isinstance(points, list) or not 1 <= len(points) <= 2000:
        raise SurfaceContractError(
            "convergence.points must contain 1..2000 evaluations"
        )
    previous = 0
    for item in points:
        point = _mapping(item, "convergence.points item")
        evaluation = point.get("evaluation")
        if type(evaluation) is not int or not previous < evaluation <= 1_000_000:
            raise SurfaceContractError(
                "convergence evaluation indices must increase from 1"
            )
        previous = evaluation
        _finite_number(point.get("energy"), "convergence.points.energy")
    if "reference_energy" in convergence:
        _finite_number(convergence["reference_energy"], "convergence.reference_energy")
    # The callback's last line-search evaluation is not necessarily the final
    # optimized point. Keep the final value separate rather than rewriting trace.
    final = _finite_number(convergence.get("final_energy"), "convergence.final_energy")
    if not math.isclose(final, prediction["value"], rel_tol=1e-10, abs_tol=1e-10):
        raise SurfaceContractError(
            "convergence.final_energy must match prediction.value"
        )


def _validate_graph(value: Any, prediction: Mapping[str, Any]) -> None:
    """Check the optional small Max-Cut drawing against its actual partition."""
    graph = _mapping(value, "graph")
    count = graph.get("num_nodes")
    if type(count) is not int or not 2 <= count <= 32:
        raise SurfaceContractError("graph.num_nodes must be an integer in 2..32")
    partition = graph.get("partition")
    if (
        not isinstance(partition, list)
        or len(partition) != count
        or any(type(bit) is not int or bit not in (0, 1) for bit in partition)
    ):
        raise SurfaceContractError(
            "graph.partition must contain one binary integer per node"
        )
    if graph.get("partition_source") not in {
        "best_sample",
        "most_probable_sample",
        "exact",
        "greedy",
    }:
        raise SurfaceContractError(
            "graph.partition_source must name the displayed solution"
        )
    edges = graph.get("edges")
    if not isinstance(edges, list) or len(edges) > count * (count - 1) // 2:
        raise SurfaceContractError("graph.edges must be a bounded undirected edge list")
    seen = set()
    crossing_weights = []
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 3:
            raise SurfaceContractError(
                "graph.edges items must be [source, target, weight]"
            )
        source, target, weight = edge
        if (
            type(source) is not int
            or type(target) is not int
            or not 0 <= source < count
            or not 0 <= target < count
            or source == target
        ):
            raise SurfaceContractError(
                "graph.edges contains an invalid node or self-loop"
            )
        key = tuple(sorted((source, target)))
        if key in seen:
            raise SurfaceContractError("graph.edges must not repeat an undirected edge")
        seen.add(key)
        number = _finite_number(weight, "graph.edges weight")
        if not 0 <= number <= 1e6:
            raise SurfaceContractError("graph.edges weight must be in 0..1000000")
        if partition[source] != partition[target]:
            crossing_weights.append(number)
    cut_value = _finite_number(graph.get("cut_value"), "graph.cut_value")
    if not math.isclose(
        cut_value, math.fsum(crossing_weights), rel_tol=1e-9, abs_tol=1e-9
    ):
        raise SurfaceContractError(
            "graph.cut_value disagrees with its edges and partition"
        )
    if prediction.get("kind") != "solution" or not math.isclose(
        cut_value, prediction["value"], rel_tol=1e-9, abs_tol=1e-9
    ):
        raise SurfaceContractError(
            "graph.cut_value must match solution prediction.value"
        )


def _validate_quantum(value: Any) -> None:
    quantum = _mapping(value, "quantum")
    raw_qubits = quantum.get("qubits")
    qubits = int(_finite_number(raw_qubits, "quantum.qubits"))
    if isinstance(raw_qubits, bool) or qubits <= 0 or qubits != raw_qubits:
        raise SurfaceContractError("quantum.qubits must be a positive integer")
    raw_depth = _finite_number(quantum.get("depth"), "quantum.depth")
    depth = int(raw_depth)
    if depth <= 0 or depth != raw_depth:
        raise SurfaceContractError("quantum.depth must be a positive integer")
    if not isinstance(quantum.get("backend"), str) or not quantum["backend"].strip():
        raise SurfaceContractError("quantum.backend must be a non-empty string")
    gates = quantum.get("gates")
    if not isinstance(gates, list) or not gates:
        raise SurfaceContractError("quantum.gates must be a non-empty list")
    for index, raw_gate in enumerate(gates):
        gate = _mapping(raw_gate, f"quantum.gates[{index}]")
        if not isinstance(gate.get("gate"), str) or not gate["gate"].strip():
            raise SurfaceContractError(f"quantum.gates[{index}].gate is required")
        if not isinstance(gate.get("stage"), str) or not gate["stage"].strip():
            raise SurfaceContractError(f"quantum.gates[{index}].stage is required")
        wires = gate.get("qubits")
        if not isinstance(wires, list) or not wires:
            raise SurfaceContractError(f"quantum.gates[{index}].qubits is required")
        if any(type(wire) is not int or not 0 <= wire < qubits for wire in wires):
            raise SurfaceContractError(
                f"quantum.gates[{index}].qubits contains an invalid wire"
            )
        if len(set(wires)) != len(wires):
            raise SurfaceContractError(f"quantum.gates[{index}].qubits repeats a wire")
        if "params" in gate:
            if not isinstance(gate["params"], list):
                raise SurfaceContractError(
                    f"quantum.gates[{index}].params must be a list"
                )
            for parameter in gate["params"]:
                if isinstance(parameter, bool) or not isinstance(
                    parameter, (int, float)
                ):
                    raise SurfaceContractError(
                        f"quantum.gates[{index}].params must be numeric"
                    )
                _finite_number(parameter, f"quantum.gates[{index}].params")
    top_states = quantum.get("top_states", [])
    if not isinstance(top_states, list):
        raise SurfaceContractError("quantum.top_states must be a list when provided")
    for index, raw_state in enumerate(top_states):
        state = _mapping(raw_state, f"quantum.top_states[{index}]")
        if not isinstance(state.get("label"), str) or not state["label"].strip():
            raise SurfaceContractError(f"quantum.top_states[{index}].label is required")
        normalized = _finite_number(
            state.get("value"), f"quantum.top_states[{index}].value"
        )
        if not 0 <= normalized <= 1:
            raise SurfaceContractError(
                f"quantum.top_states[{index}].value must be normalized to 0..1"
            )


def _validate_result(value: Any) -> dict[str, Any]:
    result = dict(_mapping(value, "/api/infer response"))
    required = {"prediction", "quantum", "explanations", "boundary", "latency_ms"}
    missing = required - set(result)
    if missing:
        raise SurfaceContractError(f"/api/infer missing keys: {sorted(missing)}")
    _validate_prediction(result["prediction"])
    _validate_quantum(result["quantum"])
    if "convergence" in result:
        _validate_convergence(result["convergence"], result["prediction"])
    if "graph" in result:
        _validate_graph(result["graph"], result["prediction"])
    _display_strings(result["explanations"], "explanations")
    _display_strings(result["boundary"], "boundary")
    _bilingual_strings(result, "explanations", "/api/infer")
    _bilingual_strings(result, "boundary", "/api/infer")
    if _finite_number(result["latency_ms"], "latency_ms") < 0:
        raise SurfaceContractError("latency_ms must be non-negative")
    return result


def _current_info() -> dict[str, Any]:
    try:
        return _validate_info(application.get_info())
    except SurfaceContractError:
        raise
    except Exception as exc:  # pragma: no cover - application-owned failure
        LOGGER.exception("backend.application.get_info failed")
        raise RuntimeError("backend.application.get_info failed") from exc


@app.get("/", response_class=FileResponse, include_in_schema=False)
def index() -> FileResponse:
    if not FRONTEND_ENTRY.is_file():
        raise HTTPException(status_code=404, detail="frontend entry missing")
    return FileResponse(FRONTEND_ENTRY, media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": SERVICE_ID,
        "model_loaded": MODEL_LOADED,
        "score_semantics": SCORE_SEMANTICS,
        "score_semantics_en": SCORE_SEMANTICS_EN,
    }


@app.get("/api/info")
def info() -> dict[str, Any]:
    try:
        return _current_info()
    except SurfaceContractError as exc:
        raise HTTPException(status_code=500, detail=f"应用信息合同错误: {exc}") from exc


def _training_json(relative: str, limit: int) -> tuple[dict[str, Any], bytes]:
    """Read only bounded JSON under this application's models directory."""
    if not isinstance(relative, str) or not relative:
        raise ValueError("training artifact path must be a relative string")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.drive:
        raise ValueError("training artifact path must be relative")
    models = APPLICATION_ROOT / "models"
    path = APPLICATION_ROOT / candidate
    if models.is_symlink() or models.resolve() not in path.resolve().parents:
        raise ValueError("training artifacts must stay under models/")
    current = APPLICATION_ROOT
    for part in candidate.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("training artifact symlinks are not supported")
    with path.open("rb") as stream:
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise ValueError("training artifact exceeds size limit")
    value = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError("training artifact must be an object")
    return value, content


def _validated_training_evidence(relative: str) -> dict[str, Any]:
    evidence, _ = _training_json(relative, 64 * 1024)
    model_schemas = {
        "qiskit_vqc_training_v1": "qiskit_vqc_json_v1",
        "cqlib_vqc_training_v1": "cqlib_vqc_json_v1",
    }
    if evidence.get("schema") not in model_schemas:
        raise ValueError("unsupported training evidence schema")
    model, content = _training_json(evidence.get("model_file"), 8 * 1024 * 1024)
    if model.get("schema") != model_schemas[evidence["schema"]] or sha256(
        content
    ).hexdigest() != evidence.get("model_sha256"):
        raise ValueError("training evidence does not match the model")
    arrays = {}
    for key, maximum in (
        ("loss", 60),
        ("initial_weights", 16),
        ("trained_weights", 16),
    ):
        values = evidence.get(key)
        if not isinstance(values, list) or not 1 <= len(values) <= maximum:
            raise ValueError("training array size is invalid")
        arrays[key] = [_finite_number(value, key) for value in values]
        if any(abs(value) > 1e6 for value in arrays[key]):
            raise ValueError("training values exceed the chart display limit")
    names = evidence.get("parameter_names")
    size = len(arrays["trained_weights"])
    if (
        size not in range(4, 17, 2)
        or len(arrays["initial_weights"]) != size
        or names != [f"θ[{index}]" for index in range(size)]
        or names != model.get("weight_parameters")
        or arrays["trained_weights"] != model.get("weights")
        or any(value < 0 for value in arrays["loss"])
        or evidence.get("optimizer") != "COBYLA"
        or type(evidence.get("maxiter")) is not int
        or evidence["maxiter"] != 60
        or type(evidence.get("seed")) is not int
        or evidence["seed"] != 12345
        or type(evidence.get("training_samples")) is not int
        or not 1 <= evidence["training_samples"] <= 256
    ):
        raise ValueError("training evidence does not match the VQC contract")
    # Return an allowlist only; model paths and arbitrary extra JSON stay private.
    return {
        "status": "available",
        "schema": evidence["schema"],
        "model_sha256": evidence["model_sha256"],
        "parameter_names": names,
        **arrays,
        **{
            key: evidence[key]
            for key in ("optimizer", "maxiter", "seed", "training_samples")
        },
    }


@app.get("/api/training")
def training() -> dict[str, Any]:
    """Optional offline evidence; missing charts never disable model inference."""
    relative = getattr(application, "TRAINING_EVIDENCE_PATH", None)
    if relative is None:
        return {"status": "unavailable", "reason": "not_recorded"}
    try:
        return _validated_training_evidence(relative)
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        return {"status": "unavailable", "reason": "invalid_or_stale"}


@app.post("/api/infer")
def infer(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        fields = _current_info()["fields"]
    except SurfaceContractError as exc:
        raise HTTPException(status_code=500, detail=f"应用信息合同错误: {exc}") from exc
    expected = {str(field["id"]) for field in fields}
    if set(payload) != expected:
        missing = sorted(expected - set(payload))
        unexpected = sorted(set(payload) - expected)
        raise HTTPException(
            status_code=422,
            detail={"missing_fields": missing, "unexpected_fields": unexpected},
        )
    normalized: dict[str, float] = {}
    for field in fields:
        field_id = str(field["id"])
        if isinstance(payload[field_id], bool):
            raise HTTPException(
                status_code=422, detail=f"{field_id} must not be boolean"
            )
        try:
            number = float(payload[field_id])
        except (TypeError, ValueError, OverflowError) as exc:
            raise HTTPException(
                status_code=422, detail=f"{field_id} must be numeric"
            ) from exc
        if not math.isfinite(number):
            raise HTTPException(status_code=422, detail=f"{field_id} must be finite")
        if number < float(field["min"]) or number > float(field["max"]):
            raise HTTPException(
                status_code=422, detail=f"{field_id} is outside the declared range"
            )
        normalized[field_id] = number
    try:
        return _validate_result(application.infer(normalized))
    except SurfaceContractError as exc:
        raise HTTPException(status_code=500, detail=f"应用推理合同错误: {exc}") from exc
    except HTTPException as exc:
        if exc.status_code in {400, 422}:
            detail = exc.detail
            if not isinstance(detail, str) or not detail.strip() or len(detail) > 1000:
                detail = "输入不满足应用约束"
            # Only bounded input-validation text crosses the business boundary.
            # Do not forward application-owned headers or unrelated HTTP errors.
            raise HTTPException(status_code=exc.status_code, detail=detail) from exc
        LOGGER.exception("backend.application.infer raised an unexpected HTTP error")
        raise HTTPException(status_code=502, detail="模型推理失败") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="输入无法完成预处理") from exc
    except Exception as exc:  # pragma: no cover - application-owned failure
        LOGGER.exception("backend.application.infer failed")
        raise HTTPException(status_code=502, detail="模型推理失败") from exc
