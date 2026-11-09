---
name: quantum-algorithm-vqe
description: "Guides SDK-neutral VQE application engineering for ground-state energy, molecular energy, Pauli Hamiltonians, ansatz design, expectation measurement, optimizer loops, reference-energy validation, and structured result evidence. Use after the user selects Cqlib, Qiskit, or PennyLane and the project records quantum_runtime. Load only the selected SDK reference. Do NOT use for QUBO/QAOA, QML, hybrid neural models, application packaging, or final delivery readiness."
---

# Quantum Algorithm: VQE

Build VQE applications from a framework-neutral Hamiltonian and scientific contract, then implement execution with one selected SDK.

## When to Use

- The target is a minimum eigenvalue, molecular energy, or Pauli-Hamiltonian expectation.
- The work needs explicit ansatz, measurement, optimizer, energy convention, and reference checks.
- The selected SDK is recorded before implementation.

## When NOT to Use

- QUBO or combinatorial optimization -> `quantum-algorithm-qaoa`.
- Classification, regression, or quantum feature maps -> `quantum-algorithm-qml`.
- Classical networks containing quantum layers -> `quantum-algorithm-hybrid`.
- API, UI, packaging, or delivery readiness work.

## Load the Selected SDK Reference

| `quantum_runtime.sdk` | Reference | Local simulator |
|---|---|---|
| `cqlib` | `references/cqlib.md` | verified |
| `qiskit` | `references/qiskit.md` | verified |
| `pennylane` | `references/pennylane.md` | verified |

Load one reference only. Do not translate an already-built SDK circuit object into another framework.

## Implementation Reuse Gate

Before writing quantum algorithm code:

1. Inspect the active environment, dependency lockfiles, installed package versions, and existing project utilities.
2. Inventory the selected SDK's VQE solver, Hamiltonian and chemistry builders, ansatz templates, primitives, optimizers, gradient methods, and result objects.
3. Use the highest-level supported library implementation that preserves the Hamiltonian, ansatz, measurement, optimizer, callback, and reproducibility contracts.
4. Record the fully qualified components and versions selected for production execution.

Do not reimplement a standard VQE solver loop, chemistry-to-qubit conversion, ansatz template, expectation engine, optimizer, or result container when a compatible maintained implementation is available. Custom quantum code is allowed only for an unsupported ansatz/observable/measurement requirement, a missing capability in the selected SDK, or a tiny independent semantic oracle. Record the exact reason and keep validation-only code out of the production path. A missing optional package is a dependency blocker; do not silently replace it with a handwritten production implementation without user approval.

## Required Contracts

Define before implementation:

- Hamiltonian source, coefficients, Pauli wire order, units, and constant terms
- active-space, symmetry reduction, and qubit mapping assumptions when applicable
- total-energy convention, including nuclear repulsion when applicable
- molecular particle/spin sector for both the ansatz and the exact reference
- initial state, ansatz gates, parameter order, depth, and symmetry expectations
- measurement grouping or exact expectation strategy
- optimizer, initialization seeds, bounds, stopping criteria, and evaluation budget
- exact diagonalization or accepted reference value for a tiny known case
- variational bound, tolerances, reproducibility, and claim boundaries

## Planning Handoff

Before implementation, provide planner-agent the Hamiltonian provenance, units, qubit
mapping, reference-energy availability, ansatz constraints, and local/device budget.
The plan must define a tiny analytic oracle and a reference-energy comparison before
scaling. It must not use a generic chemistry accuracy target when the Hamiltonian,
mapping, or reference convention differs.

## Workflow

1. Parse the Hamiltonian into an SDK-neutral Pauli-term representation.
2. Verify Hermiticity, coefficient types, wire range, units, and constant offsets.
3. Compute an independent reference on the same Hamiltonian when tractable.
4. Define the initial-state and ansatz requirements, then map them to maintained library components.
5. Load the selected SDK reference, pass the reuse gate, and configure the selected library VQE path.
6. Optimize through the selected solver with deterministic seeds and preserve the complete convergence trace.
7. Re-evaluate the final parameters and compare with reference and baseline values.
8. Produce reports and run the project's scientific and application checks when available.

## Required Outputs

- Hamiltonian artifact under `artifacts/results/` with coefficients, Pauli strings, wire convention, units, and source.
- Convergence trace under `artifacts/results/` with evaluation index, parameters, energy, optimizer status, and runtime.
- Result metadata under `artifacts/results/` with runtime, fully qualified library components and versions,
  energy convention, final/reference energy, error, ansatz, measurement strategy,
  optimizer, qubits, artifact paths, and limitations. Commands are recorded automatically in
  `artifacts/run_history.jsonl`.

## Scientific Rules

- Compare electronic energy with electronic references and total energy with total references.
- Separate active-space electronic, inactive electronic, and nuclear energies; add every
  constant exactly once. A reduced active-space reference is not a full-molecule reference.
- Validate particle-sector membership before using a fixed-electron exact reference.
- Preserve the same Pauli wire order in the Hamiltonian, circuit, measurement, and tests.
- Require final energy to respect the variational lower-bound convention within tolerance.
- Test at least one basis state or analytic one-qubit Hamiltonian before a larger molecule.
- Separate optimizer failure from incorrect Hamiltonian, ansatz, or measurement semantics.
- Do not infer hardware performance from exact statevector results.
- Do not silently switch SDK or backend after execution failure.
- For a fixed-geometry LiH demo with Qiskit and no compatible chemistry driver,
  use the provenance and bounded maintained-solver path in
  `references/lih-fixed-instance.md`; never invent coefficients or relabel H2 as LiH.
- Bounded per-instance VQE optimization is algorithm execution, not supervised model
  training. A fixed result replay must be clearly labelled and must not pretend to solve
  user-supplied geometries. Persisted parameter reload only evaluates the saved circuit.

## Application Handoff

When `application_manifest.json` exists, record the selected runtime and application-root-relative
evidence paths. Hand off the Hamiltonian and convergence trace under `artifacts/results/`; this
skill does not decide final delivery readiness.
