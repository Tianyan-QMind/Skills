---
name: quantum-algorithm-qml
description: "Routes evidence-selected quantum machine-learning work across quantum kernels, variational supervised models, hybrid neural models, quantum reservoirs, generative models, representation learning, and reinforcement learning. Use only for the qml_model workstream after plan.md selects one QMLRoute. Do not use for baseline, research, API/UI, documentation, verification, QAOA, or VQE."
---

# Quantum Machine Learning

QML is the capability domain. Hybrid quantum-classical neural networks are the
`hybrid_neural` profile, not a separate algorithm family.

## Core Contract

- Read the current `selected_route`; never select a profile or SDK from keywords.
- Use the planner-recorded capability evidence and call `materialize_qml_adapter` before custom code.
- Prefer maintained SDK algorithms and connectors. Use framework-owned official-primitives
  adapters only where the SDK lacks the required high-level model.
- Keep data preparation, encoding, trainable circuit, measurement, loss, optimizer, and
  analysis separately testable.
- Train offline with fixed seeds. Persist parameters, preprocessing, output mapping, package
  versions, expected shapes, and a known inference fixture.
- Services load persisted artifacts and infer only. Never expose training through startup,
  API requests, or browser actions.
- Treat every user-provided model path or artifact as untrusted. Only load service-owned models
  created by the offline training workflow under the generated application's `models/` directory;
  never pass a path from chat, an API request, an upload, or a browser action to a model loader.
- Never deserialize Pickle, Dill, Cloudpickle, or Joblib artifacts, and never write an ad hoc
  loader to bypass a disabled runtime route. Qiskit native routes that require Dill persistence
  are unavailable until a non-executable model format is implemented.
- Never silently switch SDK, profile, dataset, metric, backend, or data split.
- Preserve wire order, parameter order, measurement mapping, dtype, shots, and uncertainty.

## Planning Handoff

Planner chooses the QML profile and variant from evidence; this Skill never reselects
them. Before implementation, provide planner-agent the data provenance, task type,
baseline representation, split/resampling boundary, score-to-probability mapping when
applicable, and expected inference operation. The plan must separate a
representation-matched classical comparison from any full-feature classical reference,
and must define threshold selection without consuming the final test set.

## Implementation Workflow

1. Confirm that `selected_route` fixes `profile`, `variant`, `sdk`, `adapter_id`, and
   `adapter_version`.
2. Call `materialize_qml_adapter` before writing application algorithm, training, loading, or
   inference source; its route validation is the implementation-stage capability gate. A
   dependency declaration may be written first. Missing allowlisted dependencies may be installed
   once through `install_app_dependencies`, followed by a fresh capability/materialization check.
   Never invoke a package installer from application scripts or raw pip/uv commands. Preserve any
   concrete installation failure; missing route implementation is not an installable dependency.
   Do not call exploratory SDK probes to choose or change the route. Continue only for
   `materialized` or `unchanged`; on `unavailable` or a capability error, stop for planner replan.
3. Treat `algorithm/qml_runtime/**` as framework-owned and
   opaque; never inspect it to derive a replacement, edit it, or reproduce its circuit, optimizer,
   trainer, persistence, or loader in application code. Use the opaque integration contract returned by
   `materialize_qml_adapter`.
4. In an application-owned offline training script, import `train_and_save` from
   `algorithm.qml_runtime.runtime`, pass real acquired `rows` and `targets` explicitly, and write
   the model under application-root `models/` (never `artifacts/models/`). The runtime rejects paths
   whose resolved location escapes that directory. Use the exact call
   `train_and_save(model_path, rows=rows, targets=targets)`. Fit application preprocessing outside
   the runtime and persist that metadata separately under `models/`.
   Name the offline command in the plan (`scripts/train.py` recommended; a combined
   `scripts/prepare_data.py` is valid), then execute it through `run_app_work_package`.
   Successful `train_and_save` automatically writes a framework-owned
   `.training-receipt.json` bound to the model hash; the command tool records that receipt.
   Never handwrite receipts/history or create a load-only wrapper to mimic training.
   Reuse valid existing model-bound evidence for naming/format repairs without retraining.
5. In a fresh process, call
   `load_and_infer(model_path, {"features": features})` with the persisted model and the known fixture.
   Production service and UI paths use this load-and-infer path only. Validation, test, and other
   dataset scoring must use bounded chunks through
   `load_and_infer_many(model_path, [{"features": row} for row in feature_rows])`; do not loop over
   the single-row entrypoint.
6. If the selected variant cannot complete its own train, serialize, reload, and infer smoke,
   report the capability as unavailable. Do not substitute another variant, SDK, or handwritten
   approximation.
7. For a requested training-size sweep, build one deterministic pool at least as large as the
   maximum requested size. For every candidate, require the returned `training_samples` to equal
   the requested size; otherwise the sweep is invalid and must stop.
8. Once a candidate is selected, store an explicit `selected_n_train` (or equally unambiguous
   selected-size field) in structured results. Refresh application-owned frontend copy and backend
   metadata from that frozen value before handoff; do not leave an earlier candidate size presented
   as the final trained model.
9. Make dataset scoring fail closed. Each bounded chunk writes a unique
   `scores-<subset>-<start>-<end>.jsonl.tmp` and atomically renames it only after its exact index
   range, row count, finite values, and `(subset,index,row_id)` uniqueness pass. Never append or
   overwrite duplicate ranges. The final merger must reject overlaps and assert
   `raw_count == unique_count == expected_count` plus complete index coverage before metrics.

The materialized runtime is an executable asset, not implementation documentation. Do not read
the complete `assets/runtime.py` during normal work; load only the selected SDK reference
sections needed to integrate it.

## Progressive Disclosure

Load exactly one profile reference and, only when implementation detail is needed, exactly
one SDK reference.

| QML profile | Reference |
|---|---|
| `quantum_kernel` | `references/profile-quantum-kernel.md` |
| `variational_supervised` | `references/profile-variational-supervised.md` |
| `hybrid_neural` | `references/profile-hybrid-neural.md` |
| `quantum_reservoir` | `references/profile-quantum-reservoir.md` |
| `quantum_generative` | `references/profile-quantum-generative.md` |
| `quantum_representation` | `references/profile-quantum-representation.md` |
| `quantum_reinforcement` | `references/profile-quantum-reinforcement.md` |

SDK detail paths are `references/sdk-cqlib.md`, `references/sdk-qiskit.md`, and
`references/sdk-pennylane.md`.

Profile references expose the exact headings `Variant Scope`, `Data and Encoding`,
`Model and Training`, `Measurement and Output`, `Diagnostics`, `Failure Modes`, and
`Acceptance`. SDK references expose `Selection Boundary`, `Library-First Components`,
`Runtime Adapter`, `Parameter and Measurement Semantics`, `Persistence`,
`Unsupported Behavior`, and `Evidence`. Read only the reference section needed for the active task.

## Required Evidence

- Store structured result metadata with the selected route, reused components, execution semantics,
  profile diagnostics, metrics, persisted model information, operation, input/output expectations,
  preprocessing, known fixture, and limitations under `artifacts/results/`. Commands are recorded
  automatically in `artifacts/run_history.jsonl`.
- Store reproducible metrics, predictions, and training traces under
  `artifacts/results/`.
- For learned QML, write the selected held-out metric to `artifacts/results/metrics.json`
  as `primary_metric: {"name": "macro_f1", "value": 0.0}` with the actual name and
  measured numeric value replacing this example. Keep raw predictions/evaluation evidence.
  The handoff also accepts numeric metric fields at the top level, in `metrics`, or in
  `evaluation`; filenames in diagnostics are observations, not a request to create
  literal angle-bracket placeholders. A format repair must preserve measured values
  and must not repeat successful training. Command/smoke success alone does not prove
  that the runtime's delivery postcondition passed.
- Preserve per-chunk score files until the fail-closed merge succeeds; record raw, unique,
  expected, duplicate, and missing counts in the structured metric result.

## Handoff

Return the structured result paths to data-analysis-agent. This Skill
does not compare against the baseline, approve scientific acceptance, package a service, or
approve delivery.
