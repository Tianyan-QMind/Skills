"""Reusable API + desktop/mobile browser smoke for materialized QML apps."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

APPLICATION_ROOT = Path(__file__).resolve().parents[1]
if str(APPLICATION_ROOT) not in sys.path:
    sys.path.insert(0, str(APPLICATION_ROOT))

MANIFEST = json.loads(
    (APPLICATION_ROOT / "application_manifest.json").read_text(encoding="utf-8")
)
BROWSER_CONTRACT = MANIFEST["local_demo"]["browser_test"]
SELECTORS = {
    "status": BROWSER_CONTRACT["status_selector"],
    "action": BROWSER_CONTRACT["action_selector"],
    "result": BROWSER_CONTRACT["result_selector"],
    "showcase": BROWSER_CONTRACT["showcase_selector"],
    "circuit": BROWSER_CONTRACT["circuit_selector"],
    "wire": BROWSER_CONTRACT["wire_selector"],
}
READY_TEXT = BROWSER_CONTRACT["status_ready_text"]
SERVE_SCRIPT = APPLICATION_ROOT / "scripts" / "serve.py"


def _json_request(
    url: str, payload: dict[str, Any] | None = None, timeout: float = 120.0
) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="GET" if body is None else "POST",
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        data = error.read().decode("utf-8")
        try:
            detail = json.loads(data)
        except json.JSONDecodeError:
            detail = {"detail": data}
        return error.code, detail


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _wait_ready(
    base_url: str, process: subprocess.Popen[str], timeout: float = 120.0
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        return_code = process.poll()
        if return_code is not None:
            output, _ = process.communicate(timeout=1)
            diagnostic = (output or "")[-4000:]
            raise AssertionError(
                f"server exited before readiness (exit={return_code}): {diagnostic}"
            )
        try:
            status, health = _json_request(f"{base_url}/api/health", timeout=5)
            if status == 200 and health.get("status") == "ok":
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.25)
    raise AssertionError(f"server did not become ready: {base_url}")


def _terminate_tree(process: subprocess.Popen) -> None:
    import psutil

    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
    except (psutil.NoSuchProcess, OSError):
        children = []
    for child in children:
        try:
            child.terminate()
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            pass
    try:
        psutil.wait_procs(children, timeout=10)
    except (psutil.Error, OSError):
        pass
    try:
        process.terminate()
        process.wait(timeout=10)
    except (psutil.NoSuchProcess, OSError):
        pass
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _assert_port_closed(port: int) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.25)
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return
        time.sleep(0.25)
    raise AssertionError(f"owned server port still listens after cleanup: {port}")


def _model_hashes() -> dict[str, str]:
    """Protect learned models and declared-location solver inputs, not run outputs."""
    hashes: dict[str, str] = {}
    patterns = (
        "models/**/*.json",
        "algorithm/**/*.json",
        "data/**/*.json",
        "data/**/*.fcidump",
        "artifacts/results/*hamiltonian*.json",
        "artifacts/results/*problem*.json",
    )
    paths = {path for pattern in patterns for path in APPLICATION_ROOT.glob(pattern)}
    for path in sorted(paths):
        if path.is_symlink() or not path.is_file():
            raise AssertionError(f"unsafe model artifact: {path.name}")
        hashes[path.relative_to(APPLICATION_ROOT).as_posix()] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    return hashes


def _validate_info(info: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
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
    assert required <= set(info), (
        f"/api/info missing keys: {sorted(required - set(info))}"
    )
    fields = info["fields"]
    presets = info["presets"]
    method_steps = info["method_steps"]
    metrics = info["metrics"]
    scientific_boundary = info["scientific_boundary"]
    assert isinstance(fields, list), "/api/info fields must be a list"
    assert fields, "/api/info fields must be non-empty"
    assert isinstance(presets, list), "/api/info presets must be a list"
    assert presets, "/api/info presets must be non-empty"
    field_ids = [str(field["id"]) for field in fields]
    assert len(field_ids) == len(set(field_ids)), "field ids must be unique"
    for field in fields:
        missing = {"id", "label", "min", "max", "step", "default"} - set(field)
        assert not missing, f"field {field.get('id')} missing keys: {sorted(missing)}"
        assert float(field["min"]) <= float(field["default"]) <= float(field["max"]), (
            f"field {field['id']} default must stay inside min/max"
        )
        assert float(field["step"]) > 0, f"field {field['id']} step must be positive"
    for index, preset in enumerate(presets):
        assert isinstance(preset, dict), f"preset {index} must be an object"
        name = preset.get("name")
        assert isinstance(name, str), f"preset {index} requires a string name"
        assert name.strip(), f"preset {index} requires a non-empty name"
        values = preset.get("values")
        assert isinstance(values, dict), f"preset {index} values must be an object"
        assert set(values) == set(field_ids), (
            f"preset {index} must provide exactly one value for every field"
        )
    values = presets[0]["values"]
    assert isinstance(method_steps, list), "/api/info method_steps must be a list"
    assert method_steps, "/api/info method_steps must be non-empty"
    assert all(
        isinstance(step, dict) and step.get("title") and step.get("detail")
        for step in method_steps
    ), "/api/info method_steps items require title/detail"
    assert isinstance(metrics, list), "/api/info metrics must be a list"
    assert metrics, "/api/info metrics must be non-empty"
    assert all(
        isinstance(metric, dict) and metric.get("label") and "value" in metric
        for metric in metrics
    ), "/api/info metrics items require label/value"
    assert isinstance(scientific_boundary, list), (
        "/api/info scientific_boundary must be a list"
    )
    assert scientific_boundary, "/api/info scientific_boundary must be non-empty"
    assert all(
        isinstance(item, str) and item.strip() for item in scientific_boundary
    ), "/api/info scientific_boundary items must be non-empty strings"
    return field_ids, values


def _validate_result(result: dict[str, Any]) -> int:
    required = {"prediction", "quantum", "explanations", "boundary", "latency_ms"}
    assert required <= set(result), (
        f"/api/infer missing keys: {sorted(required - set(result))}"
    )
    prediction = result["prediction"]
    assert prediction.get("kind") in {
        "classification",
        "regression",
        "solution",
        "energy",
    }, prediction
    if prediction["kind"] == "classification":
        assert isinstance(prediction.get("label"), str), prediction
        assert prediction["label"], prediction
        assert "decision_value" in prediction, prediction
        assert "score_semantics" in prediction, prediction
        assert isinstance(prediction.get("scores"), list), prediction
        assert prediction["scores"], prediction
        assert all(
            isinstance(score, dict)
            and score.get("label")
            and isinstance(score.get("value"), (int, float))
            and 0 <= float(score["value"]) <= 1
            for score in prediction["scores"]
        ), "classification scores require label and normalized numeric value"
    elif prediction["kind"] == "energy":
        assert type(prediction.get("value")) in (int, float)
        assert math.isfinite(prediction["value"])
        assert isinstance(prediction.get("unit"), str)
        assert prediction["unit"]
        assert isinstance(prediction.get("score_semantics"), str)
        assert prediction["score_semantics"]
        convergence = result.get("convergence")
        if convergence is not None:
            assert convergence["unit"] == prediction["unit"]
            assert convergence["semantics"]
            assert math.isclose(
                convergence["final_energy"], prediction["value"], abs_tol=1e-10
            )
            points = convergence["points"]
            assert 1 <= len(points) <= 2000
            indices = [point["evaluation"] for point in points]
            assert indices == sorted(set(indices))
            assert indices[0] >= 1
            assert all(type(i) is int and i <= 1_000_000 for i in indices)
            assert all(
                type(p["energy"]) in (int, float) and math.isfinite(p["energy"])
                for p in points
            )
            if "reference_energy" in convergence:
                assert math.isfinite(convergence["reference_energy"])
    elif prediction["kind"] == "solution":
        assert isinstance(prediction.get("label"), str), prediction
        assert prediction["label"], prediction
        assert isinstance(prediction.get("score_semantics"), str), prediction
        assert prediction["score_semantics"], prediction
        assert type(prediction.get("value")) in (int, float), prediction
        assert math.isfinite(prediction["value"]), prediction
        assert isinstance(prediction.get("scores"), list), prediction
        assert prediction["scores"], prediction
        assert all(
            isinstance(score, dict)
            and score.get("label")
            and type(score.get("value")) in (int, float)
            and math.isfinite(score["value"])
            for score in prediction["scores"]
        ), (
            "solution scores require finite objective values, not classification probabilities"
        )
    if "graph" in result:
        graph = result["graph"]
        partition = graph["partition"]
        assert len(partition) == graph["num_nodes"]
        assert all(type(bit) is int and bit in (0, 1) for bit in partition)
        independently_scored = math.fsum(
            weight
            for source, target, weight in graph["edges"]
            if partition[source] != partition[target]
        )
        assert math.isclose(
            independently_scored, graph["cut_value"], rel_tol=1e-9, abs_tol=1e-9
        )
        assert math.isclose(
            graph["cut_value"], prediction["value"], rel_tol=1e-9, abs_tol=1e-9
        )
    quantum = result["quantum"]
    qubits = int(quantum["qubits"])
    assert qubits > 0, quantum
    depth = float(quantum["depth"])
    assert depth.is_integer(), quantum
    assert depth > 0, quantum
    assert isinstance(quantum.get("backend"), str), quantum
    assert quantum["backend"], quantum
    assert isinstance(quantum.get("gates"), list), quantum
    assert quantum["gates"], quantum
    for gate in quantum["gates"]:
        assert isinstance(gate.get("gate"), str), gate
        assert gate["gate"], gate
        assert isinstance(gate.get("stage"), str), gate
        assert gate["stage"], gate
        assert gate.get("qubits"), gate
        assert all(0 <= int(index) < qubits for index in gate["qubits"]), gate
    assert isinstance(result["explanations"], list), result
    assert result["explanations"], result
    assert all(
        isinstance(item, str) and item.strip() for item in result["explanations"]
    ), "explanations must be non-empty display strings"
    assert isinstance(result["boundary"], list), result
    assert result["boundary"], result
    assert all(isinstance(item, str) and item.strip() for item in result["boundary"]), (
        "boundary items must be non-empty strings"
    )
    return qubits


def _browser_once(base_url: str, field_count: int, qubits: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for viewport in (
                {"width": 1280, "height": 800},
                {"width": 390, "height": 844},
            ):
                page = browser.new_page(viewport=viewport)
                diagnostics: list[str] = []
                page.on(
                    "console",
                    lambda message, bucket=diagnostics: (
                        bucket.append(f"console:{message.type}:{message.text}")
                        if message.type in {"error", "warning"}
                        else None
                    ),
                )
                page.on(
                    "pageerror",
                    lambda error, bucket=diagnostics: bucket.append(f"page:{error}"),
                )
                page.on(
                    "requestfailed",
                    lambda request, bucket=diagnostics: bucket.append(
                        f"request:{request.method}:{request.url}:{request.failure}"
                    ),
                )
                page.goto(base_url, wait_until="domcontentloaded", timeout=120_000)
                page.wait_for_function(
                    "([selector,text]) => (document.querySelector(selector)?.innerText || '').includes(text)",
                    arg=[SELECTORS["status"], READY_TEXT],
                    timeout=30_000,
                )
                page.wait_for_function(
                    "count => document.querySelectorAll('#input-form input').length === count",
                    arg=field_count,
                    timeout=30_000,
                )
                info = page.request.get(f"{base_url}/api/info").json()
                if info.get("execution_kind") == "solver":
                    assert page.locator('[data-testid="training-evidence"]').is_hidden()
                with page.expect_response(
                    lambda response: (
                        response.url.endswith("/api/infer")
                        and response.request.method == "POST"
                    )
                ) as inference_response:
                    page.click(SELECTORS["action"])
                inference = inference_response.value.json()
                prediction = inference["prediction"]
                page.wait_for_function(
                    "selector => document.querySelector(selector)?.dataset.inferenceState === 'success'",
                    arg=SELECTORS["result"],
                    timeout=120_000,
                )
                assert page.locator(SELECTORS["wire"]).count() == qubits
                if prediction.get("kind") == "classification":
                    assert float(page.locator("#quantumProb").inner_text()) == float(
                        prediction["decision_value"]
                    ), "displayed model score differs from the API decision value"
                    assert (
                        page.locator("#scoreMeaning").inner_text()
                        == prediction["score_semantics"]
                    ), "displayed score semantics differ from the API"
                elif prediction.get("kind") == "energy":
                    assert (
                        float(page.locator("#result-value").inner_text())
                        == prediction["value"]
                    )
                    assert (
                        page.locator("#result-unit").inner_text() == prediction["unit"]
                    )
                    assert page.locator("#riskLevel").inner_text() == "能量求解结果"
                    assert (
                        page.locator("#scoreMeaning").inner_text()
                        == prediction["score_semantics"]
                    )
                elif prediction.get("kind") == "solution":
                    assert (
                        page.locator("#result-value").inner_text()
                        == prediction["label"]
                    )
                    assert (
                        float(page.locator("#quantumProb").inner_text())
                        == prediction["value"]
                    )
                    assert (
                        page.locator("#scoreMeaning").inner_text()
                        == prediction["score_semantics"]
                    )
                    assert page.locator("#riskLevel").inner_text() == "组合优化结果"
                convergence = inference.get("convergence")
                convergence_section = page.locator("[data-testid='solver-convergence']")
                if convergence is None:
                    assert not convergence_section.is_visible()
                else:
                    assert convergence_section.is_visible()
                    assert int(
                        convergence_section.get_attribute("data-evaluation-count")
                    ) == len(convergence["points"])
                    assert len(
                        page.locator("[data-testid='convergence-trace']")
                        .get_attribute("points")
                        .split()
                    ) == len(convergence["points"])
                    rows = page.locator("#convergenceRows tr")
                    assert rows.count() == len(convergence["points"])
                    for index, point in enumerate(convergence["points"]):
                        cells = rows.nth(index).locator("td")
                        assert int(cells.nth(0).text_content()) == point["evaluation"]
                        assert float(cells.nth(1).text_content()) == point["energy"]
                    assert (
                        page.locator("#convergenceSemantics").inner_text()
                        == convergence["semantics"]
                    )
                graph = inference.get("graph")
                graph_section = page.locator("[data-testid='graph-partition']")
                if graph is None:
                    assert not graph_section.is_visible(), (
                        "an application without graph evidence must not show a partition"
                    )
                else:
                    assert graph_section.is_visible()
                    assert (
                        page.locator("[data-graph-node]").count() == graph["num_nodes"]
                    )
                    assert page.locator("[data-graph-edge]").count() == len(
                        graph["edges"]
                    )
                    for node, group in enumerate(graph["partition"]):
                        assert page.locator(
                            f'[data-graph-node="{node}"]'
                        ).get_attribute("data-partition") == str(group)
                    for source, target, _weight in graph["edges"]:
                        expected = str(
                            graph["partition"][source] != graph["partition"][target]
                        ).lower()
                        assert (
                            page.locator(
                                f'[data-graph-edge="{source}-{target}"]'
                            ).get_attribute("data-crossing")
                            == expected
                        )
                    assert (
                        str(graph["cut_value"]).removesuffix(".0")
                        in page.locator("#graphStatus").inner_text()
                    )
                assert page.locator(SELECTORS["showcase"]).is_visible()
                assert page.locator(SELECTORS["circuit"]).is_visible()
                assert page.locator("[data-testid='method-flow']").is_visible()
                overflow = page.evaluate("""() => ({
                  width: window.innerWidth,
                  scrollWidth: document.documentElement.scrollWidth,
                  elements: Array.from(document.querySelectorAll('body *'))
                    .filter(el => el.clientWidth > 0 &&
                      getComputedStyle(el).overflowX === 'visible' &&
                      el.scrollWidth > el.clientWidth + 1)
                    .slice(-12).map(el => ({
                      tag: el.tagName, id: el.id, className: String(el.className),
                      clientWidth: el.clientWidth, scrollWidth: el.scrollWidth,
                      text: (el.textContent || '').trim().slice(0, 100)
                    }))
                })""")
                assert overflow["scrollWidth"] <= overflow["width"] + 1, (
                    f"horizontal page overflow at {viewport}: {overflow}"
                )
                body_text = page.locator("body").inner_text()
                assert "undefined" not in body_text, (
                    "page rendered undefined contract data"
                )
                assert "[object Object]" not in body_text, (
                    "page rendered an object instead of display text"
                )
                assert not diagnostics, diagnostics
                page.close()
        finally:
            browser.close()


def _browser_check(base_url: str, field_count: int, qubits: int) -> None:
    from playwright.sync_api import Error as PlaywrightError

    last_error: PlaywrightError | None = None
    for _ in range(2):
        try:
            _browser_once(base_url, field_count, qubits)
            return
        except AssertionError:
            raise
        except PlaywrightError as error:
            last_error = error
    raise AssertionError(f"browser phase failed twice: {last_error}")


def main() -> int:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    environment = os.environ.copy()
    environment["APP_HOST"] = "127.0.0.1"
    environment["APP_PORT"] = str(port)
    before_hashes = _model_hashes()
    child = subprocess.Popen(
        [sys.executable, str(SERVE_SCRIPT)],
        cwd=str(APPLICATION_ROOT.parent.parent),
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        _wait_ready(base_url, child)
        health_status, health = _json_request(f"{base_url}/api/health")
        assert health_status == 200, health
        assert health.get("status") == "ok", health
        assert isinstance(health.get("service"), str), health
        assert health["service"], health
        assert isinstance(health.get("model_loaded"), bool), health
        assert isinstance(health.get("score_semantics"), str), health
        info_status, info = _json_request(f"{base_url}/api/info")
        assert info_status == 200, info
        field_ids, known_input = _validate_info(info)
        infer_status, result = _json_request(f"{base_url}/api/infer", known_input)
        assert infer_status == 200, result
        qubits = _validate_result(result)
        if info.get("execution_kind") == "solver":
            assert result["prediction"]["kind"] in {"solution", "energy"}
        else:
            assert any(path.startswith("models/") for path in before_hashes), (
                "learned applications require inert JSON model artifacts"
            )
        repeat_status, repeated = _json_request(f"{base_url}/api/infer", known_input)
        assert repeat_status == 200, repeated
        assert repeated["prediction"] == result["prediction"], (
            "known-input inference changed"
        )
        invalid_status, _ = _json_request(f"{base_url}/api/infer", {"unexpected": True})
        assert invalid_status in {400, 422}, f"invalid input returned {invalid_status}"
        assert _model_hashes() == before_hashes, (
            "service mutated persisted model or solver input artifacts"
        )
        with urllib.request.urlopen(base_url, timeout=30) as response:
            html = response.read().decode("utf-8")
        for selector in SELECTORS.values():
            match = re.fullmatch(
                r"\[data-testid=(?:'([^']+)'|\"([^\"]+)\")\]", selector
            )
            assert match is not None, f"unsupported browser selector: {selector}"
            token = match.group(1) or match.group(2)
            assert f'data-testid="{token}"' in html, selector
        assert 'data-testid="method-flow"' in html
        assert 'data-circuit-source="api"' in html
        assert 'lang="zh-CN"' in html
        _browser_check(base_url, len(field_ids), qubits)
        assert _model_hashes() == before_hashes, (
            "browser solve mutated persisted model or solver input artifacts"
        )
    finally:
        _terminate_tree(child)
        _assert_port_closed(port)
    print(
        json.dumps(
            {
                "status": "passed",
                "browser_check": "passed",
                "desktop_and_mobile": True,
                "field_count": len(field_ids),
                "quantum_wires": qubits,
                "model_artifacts_unchanged": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
