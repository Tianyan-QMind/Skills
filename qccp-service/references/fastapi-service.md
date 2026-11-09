# Python FastAPI Quantum App Service

Use this path for local quantum application services and the `runnable_app` delivery profile when the app is not being implemented inside the Java `qccp-service` repository.

## Service shape

- Keep the quantum algorithm code separate from the FastAPI route layer.
- Use `<application_root>/backend/main.py` or an equivalent entry point under `backend/`.
- Expose `GET /api/health`, which does not run expensive quantum computation.
- Expose app metadata through `GET /api/info` when the frontend or INTEGRATE notes need capability discovery.
- Expose QML through `POST /api/infer`, with schemas recorded in manifest/model metadata and documented for users in `README.md`. Predictive profiles may add `POST /api/predict` as a compatibility alias. Non-QML tasks may use `/api/solve` or a declared domain route.
- Validate request payloads and return explicit 4xx errors for invalid inputs.
- Keep long-running, stochastic, or hardware-backed execution clearly labeled in responses and docs.

## Trained model boundary

For learned QML, hybrid, or classical models, training and preview are separate programs:

- Provide a local offline training command or script that owns data splitting, preprocessing fitting, model fitting, optimizer steps, checkpoint selection, and artifact writing.
- Persist model parameters plus every fitted transform needed for inference, class/output mappings, artifact format, framework/SDK versions, and expected input/output shapes.
- The FastAPI process may load those artifacts once at startup and reuse them for inference. Startup, lifespan handlers, dependencies, background tasks, and API routes must not call `fit`, retrain, backpropagate, or step an optimizer.
- Expose inference endpoints only. Preserve `predict`, `sample`, `transform`, or `act` semantics from the bundle. Do not expose `/train`, `/fit`, fine-tuning, checkpoint-selection, or browser-triggered training controls.
- If an artifact is absent, corrupt, version-incompatible, or shape-incompatible, fail startup or return an explicit service error. Never retrain automatically or silently substitute untrained/random parameters.
- Add a known-input inference smoke fixture and verify that model parameters or artifact checksums remain unchanged across service startup and repeated requests.

This boundary applies to learned models. Declared per-instance QAOA/VQE parameter optimization is algorithm execution and may remain in a solve endpoint when its runtime and semantics are explicit.

## API contract

Document each endpoint and, when `application_manifest.json` is in scope, record the route summary under `local_demo.endpoints` and the detailed schema in `README.md`:

- method and path
- request schema, including required and optional fields
- response schema, including `status`, result fields, metadata, and error fields when used
- backend assumptions such as simulator, shots, seed, model path, and data source
- for learned models, the local training command, persisted model/preprocessing artifact paths, artifact versions/shapes, inference entry point, and missing-artifact error
- known limitations and expected runtime

Do not invent platform-only fields such as `apiCode`, device IDs, tenant IDs, or internal gateway headers unless they already exist in the target integration docs or the user provides them.

## Static frontend and runnable app

- Runnable app layout is `frontend/standalone/index.html` plus `frontend/standalone/static/` for CSS, JS, and local vendor libraries.
- Mount `/static` to the actual `frontend/standalone/static` directory and serve `/` from `frontend/standalone/index.html`.
- For generated runnable apps, use a single-origin service: the same FastAPI process serves `/`, `/static/*`, and `/api/*` on `application_manifest.json.network.host` and `.port`.
- Frontend JavaScript must call relative API paths such as `/api/infer`; do not hardcode `localhost`, `127.0.0.1`, `10.9.1.8`, or any full backend domain in frontend source.
- The runnable app UI must use the `tianyan-ui-suite` standalone visual profile: Chinese-first copy, qccp token colors/typography/spacing/radius, vertical cloud-showcase layout, no emoji, and no generic English labels such as "Run Baseline". Keep it standalone; do not depend on qccp-web runtime imports.
- Read `standalone-demo-ui.md` before writing `frontend/standalone/index.html`. It is the HTML-specific application of tianyan-ui-suite interaction design.
- In page-local CSS, use the canonical `shadow-sm` expansion `0 1px 3px rgba(0,0,0,0.06)` and the loading-spin `/40` exception `rgba(255,255,255,0.4)`. Other shadow geometries, hex-colored shadows, and other rgb/rgba values fail the standalone preflight.
- Use `Path(__file__).resolve()` based paths, not shell working-directory assumptions.
- Missing `frontend/standalone/index.html` or `frontend/standalone/static` is a startup/configuration error; do not silently create empty frontend directories or skip static mounting.
- Record each static asset mapping in `application_manifest.json` under `local_demo.static_assets` as URL plus actual file path so validation can request or inspect the referenced CSS/JS.
- Use `static_assets: []` only for a self-contained single-file HTML demo with no `/static/...` references. Otherwise each item must be an object such as `{"url": "/static/style.css", "path": "frontend/standalone/static/style.css"}`; never use bare strings.
- Record `local_demo.serve_command` as the cross-platform `python scripts/serve.py`. Keep `APP_HOST` and `APP_PORT` configuration separate instead of embedding POSIX or PowerShell environment syntax in that field.
- Core runtime libraries for the runnable app should be vendored under `frontend/standalone/static/vendor/`; do not rely on CDN-hosted Chart.js, ECharts, Vue, or similar runtime dependencies for a deliverable app.
- Record only `host` and `port` under `application_manifest.json.network`. FastAPI and the browser preview share that same address; do not create separate bind/public/frontend host or port settings. Read `APP_HOST` and `APP_PORT`, which come from onboard generated-app configuration.
- Record `local_demo.ui_profile = "tianyan-ui-suite"` and `local_demo.language = "zh-CN"`.

## Configuration and secrets

- Use environment variables or ignored local config for tokens, cloud credentials, model paths, data paths, and platform endpoints.
- Do not paste API keys, tokens, private endpoints, cloud account identifiers, or Nacos credentials into code, docs, tests, or logs.
- Do not silently fall back from real hardware or cloud execution to local simulation.

## Verification commands

Use the smallest command that proves the changed surface:

```bash
python -m pytest
python backend/main.py
APP_HOST=<network.host> APP_PORT=<network.port> python backend/main.py
uvicorn backend.main:app --host <network.host> --port <network.port>
curl -s http://<network.host>:<network.port>/api/health
```

If the app has targeted tests or smoke scripts, run those first. Report the command, result, and any missing dependency or port conflict.

For a trained-model preview, also run a clean-process load and repeated-inference test. Compare parameter files or checksums before and after; preview verification fails if startup or any request mutates them or reaches training code.

## Handoff evidence

For application packaging evidence, provide:

- backend entry point and run command
- health-check result or reproduction command
- endpoint contract and sample request/response
- Consume the application `application_manifest.json` network and runnable-app contract. Update
  implementation-time endpoint, fixture, asset, entrypoint, or browser-selector changes together
  with the manifest; preserve the configured network values.
- `local_demo.ui_profile` and `local_demo.language` evidence
- single-origin frontend/backend URL derived from `network.host` and `network.port`
- environment variables and ignored config keys
- local offline training command plus persisted model/preprocessing artifacts when the application uses learned parameters
- README, INTEGRATE, and verification report paths when in scope

Do not decide final delivery readiness from this path. Provide backend/API evidence for the verification stage.
