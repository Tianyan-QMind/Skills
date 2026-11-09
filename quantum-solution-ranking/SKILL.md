---
name: quantum-solution-ranking
description: "Turns research evidence into a bounded, executable quantum-application plan and reflects on observed experiments."
---

# Quantum Application Planning

Use `application_manifest.json.intake` and `evidence_report.md` to choose one practical route
for QAOA, VQE, QML, hybrid QML, or explicitly authorized TianYan work. Write
one readable `plan.md` in Simplified Chinese (preserving technical identifiers); it is the implementation contract for the application,
not a collection of workflow certificates.

## Route Selection

Start with hard constraints: user-locked SDK, local execution mode,
input/output semantics, delivery profile, available data or instances, and
locally verified dependencies. Reject a route that violates one of them rather
than compensating with a made-up score.

When Intake records `planner_pending`, select exactly one of Cqlib, Qiskit, or
PennyLane from retrieved SDK evidence, observed local availability, maintained
route components, semantic fit, and implementation cost. There is no default or
preferred framework. When Intake records `user_selected`, preserve that SDK and
return a blocker if it cannot satisfy a hard requirement. Record the decision and
its evidence in `plan.md`; code-agent must not repeat probes to make the choice.

For the selected route, explain problem fit, retrieved evidence, SDK capability,
classical reference, resource limits, falsifier, and delivery impact. A numeric
ranking is allowed only when the user supplied criteria and weights. Keep a
classical-only conclusion visible when a quantum route is not defensible.

Prefer maintained SDK algorithms and framework adapters over handwritten quantum
cores. A primitive capability check proves only a dependency; a route smoke
proves only an implementation path; neither proves scientific performance.

For a learned `runnable_app`, a QML route is eligible only when its local capability evidence
records `persistence_status=safe`, the exact variant is present in
`route_smoke_supported_variants`, and that exact route has a passed route smoke. Treat
`not_run`, `not_implemented`, `failed`, and any route requiring executable Pickle, Dill,
Cloudpickle, or Joblib persistence as blockers. Do not downgrade these conditions to a pending
implementation task or ask code-agent to invent a replacement adapter.

## Code-Ready `plan.md`

The initial plan must let code-agent implement the requested application without
making another algorithm, SDK, data, baseline, evaluation, or delivery decision.
Use these sections:

1. **Scope and delivery**: user goal, intended audience, delivery profile, and
   claimed limitation.
2. **Selected route and SDK primitives**: one route, fully qualified library
   APIs or adapter, safe persistence format, route-smoke evidence, and backend assumptions. A failed
   hard constraint is a `replan` or `stop`, not permission to invent an in-plan fallback.
3. **Data and evaluation contract**: source/access method, expected schema and
   failure behavior; train, validation, and final-test roles; preprocessing fit
   boundaries; seeds; primary metric.
4. **Baseline and comparison**: primary representation-matched baseline plus
   contextual baselines. For a QML quantum kernel this is RBF-SVC on identical
   rows, transformations, validation folds, and score metric.
5. **Implementation work packages**: source modules, train/infer commands,
   model persistence, API/UI tasks when requested, and focused tests.
6. **Allowed adjustments**: the parameter family, candidate range, validation
   metric, conditions that remain fixed, and a stop condition. Do not put more
   than one parameter family in one adjustment.
7. **Stop and replan triggers**: unavailable data/SDK, a semantic contradiction,
   or an explicit user scope change. Weak metrics alone do not authorize an
   unbounded route change.

Do not turn literature values, expected runtime, PCA variance, or unmeasured
scores into gates. Record them as observations to collect. Feature selection,
hyperparameter selection, and calibration use training/validation data only;
the final test set is used once after the configuration is frozen.

For `runnable_app`, the data contract must name either an existing user file or a retrieved,
credential-free direct download URL for the actual dataset bytes plus its primary/official
provenance and schema source. Catalog pages, login-gated downloads, and unverified mirrors are
blockers. Name one `canonical_download_url`, verified to return non-empty bytes, and require every
downstream stage to copy it byte-for-byte without reconstruction or substitution. Never plan
synthetic, generated, simulated, fixture, or random training data, including
as a fallback. For materialized QML, use only the returned opaque integration contract and
application-root `models/`; do not plan `artifacts/models/` or a duplicate adapter, circuit,
optimizer, trainer, persistence layer, or loader.

When multiple training sizes are compared, retain a deterministic pool at least as large as the
maximum requested size and record an equality check between each requested size and the adapter's reported
`training_samples`. Reusing a smaller pool is a protocol violation, not a completed sweep.

## Reflection

Run `MODE: REFLECTION` only after a completed baseline, quantum experiment, or
data-analysis result. Do not reflect after documentation, ordinary debug work,
or API/UI repairs.

Append one entry to `plan.md`:

```markdown
## Iteration N

Observed: <command, result, changed paths>
Decision: keep | adjust | replan | stop
Adjustment: <one allowed parameter family, or none>
Validation: <training/validation command and metric>
Stop condition: <when this iteration ends>
```

`adjust` may tune only an already declared parameter family. Changing route,
SDK, data semantics, split boundary, primary metric, baseline family, or delivery
profile is `replan`. Reflection entries never rewrite the initial plan.

## Handoff

Return `plan.md`, selected route, next work package, and any unresolved hard
constraint. The framework limits planner reflections per LangGraph thread; when
the allowance is exhausted, continue verification and delivery or report the
best reproducible result and limitations. Planning does not approve scientific
claims, deployment, or delivery; application tests and independent verification
establish those separately.
