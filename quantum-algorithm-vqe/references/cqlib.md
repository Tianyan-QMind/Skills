# Cqlib VQE Adapter

## Support Status

- Local statevector expectations: `verified`
- Seeded derivative-free optimization: `verified`
- Native end-to-end autodiff: `unsupported` unless proven by the active Cqlib version
- TianYan execution: `experimental` and authorization-required

Inspect the installed Cqlib API before using an entry point not already present in the target project.

## Reuse-First Capability Check

Search the installed Cqlib package, bundled examples, and active project for a maintained VQE solver, Hamiltonian/Pauli abstraction, ansatz template, expectation evaluator, optimizer adapter, and result object. Reuse compatible components and record their import paths and version. Do not duplicate an existing project VQE workflow.

If no maintained algorithm layer exists, record the inspected modules and missing capabilities before using the fallback patterns below. Keep any tiny statevector oracle separate from the production optimization path.

## Fallback Ansatz Pattern

```python
from cqlib import Circuit, Parameter


def build_ansatz(n_qubits, layers):
    names = [
        f"theta_{layer}_{q}"
        for layer in range(layers)
        for q in range(n_qubits)
    ]
    circuit = Circuit(n_qubits, parameters=names)
    index = 0
    for layer in range(layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(names[index]))
            index += 1
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)
    return circuit, names
```

Build the initial state separately and prepend or compose it using behavior confirmed by the active version. Keep the parameter order returned by the builder.

## Pauli Expectation

Use the statevector for deterministic local verification. Apply basis rotations on a copy when measuring terms with X or Y factors, or compute expectations from the statevector when the active API exposes a verified statevector representation.

```python
from cqlib.simulator import StatevectorSimulator

bound = circuit.assign_parameters(dict(zip(names, values, strict=True)))
state = StatevectorSimulator(circuit=bound).statevector()
```

Validate each Pauli term against a one- or two-qubit analytic state before summing the Hamiltonian. Do not mix Cqlib bitstring ordering with the neutral Pauli wire convention.

## Optimizer Boundary

- Convert outputs to classical floats only after quantum expectation evaluation.
- Use an explicit derivative-free or finite-difference optimizer unless the active simulator proves a connected gradient path.
- Record every objective evaluation, seed, initial point, and stopping reason.

## Adapter Checklist

- Hamiltonian wires and Cqlib qubits map explicitly.
- Parameter binding has a known-state test.
- Basis rotations or statevector expectations are tested term by term.
- The report records `sdk: cqlib`, active version, backend, energy convention, and limitations.
- The report lists reused Cqlib/project components or the evidence supporting each fallback component.
