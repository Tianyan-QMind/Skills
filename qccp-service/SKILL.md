---
name: qccp-service
description: "Guides backend, API, and runnable FastAPI application artifacts for CT TianYan Quantum Computing Cloud Platform showcases. Local standalone HTML follows tianyan-ui-suite visual rules. Use for Python FastAPI packaging or explicit Java/Spring Cloud qccp-service integration, endpoint contracts, deployment checks, and backend verification evidence."
---

# qccp-service Backend and Runnable App Dispatcher

Use this skill as the owner of backend/API contracts and the `runnable_app` delivery profile. First choose the backend path, then load only the reference file needed for the current task.

## When to Use

- User needs backend/API/deployment artifacts for a quantum application or cloud showcase.
- User is packaging a local Python FastAPI quantum app service with health checks, API contracts, local HTML/static demo hosting, or INTEGRATE evidence.
- User explicitly targets Java/Spring Cloud qccp-service modules, Controller/Service/Mapper/XML, Feign, config, security/current-user, Maven verification, endpoint contract, or health-check guidance.
- A quantum application needs backend or deployment packaging evidence.

## When NOT to Use

- **Standalone page visual design** -> use `tianyan-ui-suite`; this skill owns its FastAPI hosting and API integration.
- **Quantum algorithm implementation or simulator/cloud circuit execution** -> use the selected `quantum-algorithm-*` skill and its SDK reference.
- **Planning only or final delivery approval** -> keep this skill out of scope.

## Backend path selection

1. **Python FastAPI quantum app service (default)**: use when the task is a local quantum application backend, demo API, static frontend service, `/health` endpoint, `/api/info`, `/api/solve`, `/api/infer`, deployment note, or INTEGRATE handoff.
2. **Java qccp-service integration**: use only when the active repository is `qccp-service`, the files are Java/Spring Cloud/POM/Mapper/XML/Nacos/Feign files, or the user explicitly asks for qccp-service-compatible Java integration.
3. If the task mixes both, keep the FastAPI app service as the demonstrable local backend and document the Java qccp-service integration boundary separately.
4. Never silently rewrite a Python FastAPI sample into Java. Never silently fall back from Java qccp-service integration to a simulator or runnable app when real platform integration is requested.
5. Never commit secrets, Nacos credentials, cloud tokens, certificates, private endpoints, logs, generated temp files, or IDE config.

## Reference routing

- `references/fastapi-service.md`: Python FastAPI app service packaging, endpoint contract, static frontend hosting, config, verification, and INTEGRATE evidence.
- `references/standalone-demo-ui.md`: Required standalone HTML information architecture and tianyan-ui-suite design alignment.
- `references/java-qccp-service.md`: Java qccp-service integration workflow and links to Java-specific module, coding, Feign/config, security, and Maven rules.
- `references/project-map.md`: Java qccp-service repository identity, stack, module responsibilities, module routing, and key files.
- `references/backend-coding-rules.md`: Java layout, Controller, Service, Mapper/XML, response model, file-stream, logging, and style rules.
- `references/feign-and-config.md`: Java Feign contracts, cross-service headers, Nacos/bootstrap config, and qccp-ctyun AI assistant paths.
- `references/security-and-commands.md`: Java current-user/security rules, safe edit workflow, search commands, Maven commands, and verification reporting.

## Backend workflow

1. Select the backend path from the evidence in the request and repository.
2. Read the relevant reference file before editing.
3. Read `quantum-application-intake/references/application-layout.md` and `application_manifest.json`. Keep service code under `<application_root>/backend/`, standalone UI under `<application_root>/frontend/standalone/`, launch commands under `<application_root>/scripts/`, and final integration instructions in `<application_root>/README.md`.
4. For `runnable_app`, use the small `local_demo` contract as the implementation source of truth: endpoint path, method, request schema, response schema, error cases, sample request when needed, static asset mappings, backend entry point, standalone app entrypoint, and verification command. All paths are relative to the application root. Preserve `network` because onboarding owns host and port. For a QML surface, `materialize_qml_app_surface` atomically owns the standard endpoints, assets, entrypoints, and selectors; after a successful materialization, do not read or edit the manifest in that package. Other implementation roles may update their actual contracts together with the source that changes them.
   Also record `api_base: /api`, `ui_profile: tianyan-ui-suite`, `language: zh-CN`, and a `browser_test` object with stable `status_selector`, `status_ready_text`, `action_selector`, `result_selector`, `showcase_selector`, `circuit_selector`, and `wire_selector`. The standalone page must expose those selectors through `data-testid` attributes.
   Record the cross-platform launch value as `serve_command: python scripts/serve.py`; keep host and port in `network`/`APP_HOST`/`APP_PORT`, not shell-specific inline environment assignments. Every endpoint entry must contain `method`, `path`, and `summary`. A self-contained HTML page uses `static_assets: []`; otherwise every static asset is an object with `url` and application-root-relative `path`, never a bare string.
   For page-local CSS, expand `shadow-sm` exactly as `0 1px 3px rgba(0,0,0,0.06)` and spell the loading-spin `/40` color as `rgba(255,255,255,0.4)`. Do not substitute a hex-colored shadow or invent another shadow geometry/alpha; these exact semantic exceptions are what `run_app_check` validates.
5. Keep algorithm execution, backend service wrapping, frontend display schema, deployment notes, and verification evidence separate.
6. A learned-model runnable app must use the Research-confirmed credential-free direct public dataset (or named existing user file) and a separate local offline training command. Catalog/login pages do not qualify. Persist learned QML models and safe preprocessing artifacts under application-root `models/`, not `artifacts/models/`; their service startup and request handlers may infer only. They must not fit, retrain, backpropagate, step a training optimizer, expose a training endpoint, return a fixed fixture, or contain synthetic/generated training-data fallbacks. When the dataset, training, or required SDK is unavailable, report the concrete blocker rather than fabricating a demo response.
   QAOA/VQE per-instance optimization is solver execution, not model training. A bounded request may solve a validated graph/Hamiltonian using the plan's SDK, seed, size and iteration/time limits. Keep import/startup free of optimization, reuse the application solver, and report actual objective/energy, reference and convergence. No training dataset or persisted learned model is required. Fixed-instance replay must be explicitly labelled and must reject unsupported inputs; never pretend replay is a fresh solve.
7. For QML, read the operation and schema from the manifest, plan, and structured model/result metadata. Always expose `POST /api/infer`; predictive profiles may additionally expose `/api/predict` as a compatibility alias. `sample`, `transform`, and `act` retain their own response semantics.
   On a QML surface whose materializer returns `materialized`, `upgraded`, or `unchanged`,
   `backend/main.py` is framework-owned. Implement only the fixed exports in
   `backend/application.py` and the compact data named by the returned machine-readable contract;
   never duplicate FastAPI routes or edit the framework entrypoint.
8. Run the smallest relevant local verification command for the selected path.
9. Application-root discovery must be independent of the current working directory. Resolve it
   from an owned source file, validate the `application_manifest.json` marker, and include one
   fresh-process inference or service check launched from outside the application directory.

## Application delivery handoff

For quantum application delivery, backend work contributes app packaging and verification evidence. Provide:

- endpoint paths, methods, request/response schema, and error cases
- conformance evidence against the main-owned, application-root-relative `application_manifest.json` `local_demo` contract
- service boundaries and persistence or job-execution ownership
- local training command, inference entry point, persisted model/preprocessing paths, and explicit missing/incompatible-artifact errors for trained-model applications
- required environment variables or ignored local config keys
- health-check and build/test commands for the selected backend path
- contract evidence for frontend/backend integration when both are in scope

Do not decide delivery readiness from this skill. Provide reviewable backend/API evidence for the application packaging and verification stages.

## Completion checklist

- [ ] Backend path is explicitly identified as Python FastAPI or Java qccp-service.
- [ ] Generated FastAPI, standalone frontend, scripts, and integration artifacts use the canonical application directories.
- [ ] A runnable FastAPI app serves `/`, `/static/*`, `/api/health`, `/api/info`, and `/api/infer` from one origin; predictive apps may also expose `/api/predict`.
- [ ] The standalone page follows `tianyan-ui-suite` tokens and the local information architecture in `standalone-demo-ui.md`; it is not a raw API form or a qccp-web/Vue imitation.
- [ ] The standalone page can pass `run_app_check` qccp standalone preflight before API/browser smoke tests are counted as delivery evidence.
- [ ] Endpoint contract and error cases are documented.
- [ ] `local_demo` contract is recorded in `application_manifest.json` when the application manifest is in scope.
- [ ] Health check and smallest relevant verification command are reported.
- [ ] Frontend/backend integration evidence is captured when in scope.
- [ ] Trained-model previews load persisted artifacts and expose inference only; startup, API requests, and browser actions cannot trigger training.
- [ ] Learned-model delivery has a real-public-data training command, a bounded fixed-seed training scale and a persisted model/preprocessor. Solver delivery has a validated problem, a bounded actual solve and a same-instance reference. Both have `tests/test_smoke.py` and a browser/API smoke result. Full scientific comparison is documented as later work unless explicitly requested.
- [ ] Java module/call chain is confirmed before Java edits.
- [ ] Mapper/XML and Feign/provider/caller files stay synchronized when Java contracts change.
- [ ] Secrets and environment-specific values remain outside code and docs.
