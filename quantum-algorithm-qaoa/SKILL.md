---
name: quantum-algorithm-qaoa
description: "Guides SDK-neutral QAOA application engineering for QUBO/Ising optimization, MaxCut, portfolio selection, scheduling, unit commitment, knapsack/TSP-like problems, penalty design, feasible decoding, baseline comparison, and structured result evidence. Use after the user selects Cqlib, Qiskit, or PennyLane and the project records quantum_runtime. Load only the selected SDK reference. Do NOT use for VQE, QML, hybrid neural models, application packaging, or final delivery readiness."
---

# Quantum Algorithm: QAOA

Build a reviewable QAOA application without coupling the problem model or evidence contract to a quantum SDK.

## When to Use

- The task is binary combinatorial optimization and can be expressed as QUBO or Ising.
- The application needs constraint penalties, top-k feasible decoding, and comparison with a classical solver.
- The selected SDK is recorded in `quantum_runtime.sdk` before implementation.

## When NOT to Use

- Ground-state or molecular energy work -> `quantum-algorithm-vqe`.
- Classification, regression, or feature maps -> `quantum-algorithm-qml`.
- A larger classical model containing a quantum layer -> `quantum-algorithm-hybrid`.
- API, UI, packaging, or delivery decisions. Use `qccp-service` or `tianyan-ui-suite` when those concerns are explicitly in scope.

## Load the Selected SDK Reference

Read exactly one implementation reference after the user or planner has selected an SDK:

| `quantum_runtime.sdk` | Reference | Local simulator |
|---|---|---|
| `cqlib` | `references/cqlib.md` | verified |
| `qiskit` | `references/qiskit.md` | verified |
| `pennylane` | `references/pennylane.md` | verified |

Do not load or mix code from another SDK. This workflow is local-simulator only.
For a supported Qiskit Max-Cut case, the selected reference includes the reusable
`assets/qiskit_maxcut.py` solver and its result contract; prefer it over generating
another implementation of the same SDK integration.

## Implementation Reuse Gate

Before writing quantum algorithm code:

1. Inspect the active environment, dependency lockfiles, installed package versions, and existing project utilities.
2. Inventory the selected SDK's QAOA algorithm, optimization-model converters, ansatz/layer helpers, optimizers, primitives, and result decoders.
3. Use the highest-level supported library implementation that preserves the required QUBO, mixer, parameter, sampling, and decoding contracts.
4. Record the fully qualified components and versions selected for production execution.

Do not reimplement a standard QAOA ansatz, optimization loop, QUBO converter, optimizer, sampler wrapper, or result container when a compatible maintained implementation is available. Custom quantum code is allowed only for a required unsupported mixer/ansatz, a missing capability in the selected SDK, or a tiny independent semantic oracle. Record the exact reason and keep validation-only code out of the production path. A missing optional package is a dependency blocker; do not silently replace it with a handwritten production implementation without user approval.

## Required Contracts

Before coding, define:

- binary variables and stable variable-to-qubit mapping
- original objective, optimization direction, and known bounds when available
- each constraint, violation function, and penalty coefficient
- QUBO convention, constant offset, and QUBO-to-Ising conversion
- QAOA depth, parameter order, mixer, initial state, and optimizer budget
- bitstring convention, decoding, feasibility check, and tie-breaking
- exact or heuristic classical baseline on the same instance
- seeds, execution mode, shots, backend, tolerances, and allowed claims

Keep the original objective separate from penalty energy. Rank candidate solutions by feasibility and original objective, not only by penalized energy.

## Planning Handoff

Before implementation, provide planner-agent the instance family, variable count,
constraint types, exact-solver limit, and local simulator constraints. The plan must
freeze a tiny semantic oracle, feasible-solution rule, original-objective metric, and
resource escalation trigger. It must not select depth or penalty values only because a
generic template suggests them.

## Required Outputs

- `artifacts/results/qaoa_model.json`: variables, objective, constraints, penalties, QUBO coefficients, Ising coefficients, constant offset, and bit order.
- `artifacts/results/qaoa_trace.json`: evaluation index, parameters, expectation, best feasible objective, feasible rate, and optimizer status.
- `artifacts/results/qaoa_samples.json`: top-k bitstrings, decoded variables, probability or count, feasibility, violations, and original objective.
- Result metadata under `artifacts/results/`: runtime, fully qualified library components and versions,
  qubits, depth, optimizer settings, best feasible solution, artifact paths, and limitations. Commands
  are recorded automatically in `artifacts/run_history.jsonl`.

## Workflow

1. Normalize the application instance into binary variables.
2. Implement the original objective and constraints as classical functions first.
3. Build and exhaustively verify the QUBO/Ising model on a tiny instance.
4. Declare the bit order and parameter order before selecting the implementation.
5. Load the selected SDK reference, pass the reuse gate, and configure the selected library QAOA path.
6. Run exact probabilities or seeded shots on an authorized local backend.
7. Decode top-k states, score feasibility, and compare with the classical baseline.
8. Write the required artifacts and run the project's scientific and application checks when available.

## Modeling Rules

- State whether the QUBO is upper-triangular, symmetric, or full-matrix form.
- Record the constant offset even when it does not affect the optimizer.
- Choose penalties from objective-scale bounds or a documented empirical sweep.
- Treat zero feasible samples as a modeling or search failure, not a successful run.
- Test one-hot, cardinality, capacity, and balance constraints independently.
- Preserve qubit indexing, parameter ordering, gate ordering, and measurement mapping across implementation and report artifacts.

## Optimization and Validation

- Start with shallow depth and deterministic seeds; increase depth only with evidence.
- Record initial points, bounds or periodic normalization, restarts, evaluation count, and stopping reason.
- Validate the energy function against direct QUBO evaluation for known bitstrings.
- Validate decoding with one- and two-qubit states whose expected bit order is obvious.
- Compare baseline and QAOA using the same instance, objective direction, feasibility rules, and metric.
- Never claim quantum advantage from simulator-only or single-instance evidence.
- Never silently change SDK or backend after a failure. Return to the lifecycle selection step.

## Max-Cut Application Checks

Max-Cut is a per-instance optimization task, not supervised model training. A
declared graph, user-entered edges, or a clearly labeled deterministic demo graph
is a problem instance; it does not require a downloaded training dataset or a QML
adapter. Preserve the selected SDK and use its maintained QAOA solver path.

- Freeze the supported vertex count, edge/weight format, duplicate-edge policy,
  self-loop policy, and bounds before implementation. If a numeric-field surface
  exposes a fixed graph size through edge weights, state that limit in the plan,
  API, and page; do not advertise arbitrary graph JSON input that it cannot accept.
- Verify every bitstring of a tiny graph against both the direct cut objective and
  the library QUBO/Ising operator, including its sign, constant offset, and bit order.
- Report the best sampled cut, most probable sample's cut, and distribution-weighted
  mean cut separately. Label which statistic a displayed approximation ratio uses;
  finding one optimal sample does not mean the expected cut equals the optimum.
- Define the zero-optimum case before dividing. Reject unsupported empty graphs or
  explain the trivial result explicitly; never fabricate a finite approximation
  ratio or a quantum execution for a problem that was short-circuited classically.
- Exercise the real solve API on two different supported graph instances, validate
  the returned partition and cut independently, and ensure the displayed circuit
  comes from the same bound SDK execution. Replaying a saved result must be labeled
  as replay, never presented as solving a newly changed input.
- For the Qiskit Max-Cut HTTP path, use the reference's bounded
  `solve_maxcut_isolated` entry so a native SDK process failure cannot terminate
  the application server. Validate repeated/concurrent requests and subsequent
  health; offline single-run validation retains the direct library entry.
- Save JSON-safe instance, optimizer configuration, parameters, sample distribution,
  and trace evidence. Recompute the saved cut and partition in a fresh process;
  do not invent a learned model or claim training/persistence checks that do not apply.

## Application Handoff

Treat `application_manifest.json` as application source. Record algorithm result paths
plus `quantum_runtime` in code-owned evidence, and update the manifest with matching implementation
changes when endpoints, fixtures, assets, entrypoints, or selectors change. This skill contributes
algorithm evidence only and cannot declare the application ready.
