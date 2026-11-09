# PennyLane VQE Adapter

## Support Status

- `default.qubit` Hamiltonian expectation: `verified`
- Local autograd/PyTorch optimization: `verified`
- Chemistry plugins and external devices: `experimental` until separately installed and tested
- Cloud or hardware execution: outside this skill's verified path

Inspect the installed PennyLane version and optional chemistry dependencies before choosing components.

## Library-First Path

- For molecular inputs, prefer `qml.qchem.Molecule`, `qml.qchem.molecular_hamiltonian`, active-space helpers, excitation helpers, and maintained mappings rather than hand-building chemistry Hamiltonians.
- Prefer maintained initial-state and ansatz templates such as `qml.BasisState`, `qml.UCCSD`, `qml.AllSinglesDoubles`, or a standard hardware-efficient template when they satisfy the contract.
- Use QNode differentiation plus an interface-compatible PennyLane or host-framework optimizer rather than implementing gradients manually.
- Use `qml.expval(hamiltonian)` for the production expectation path and keep analytic/statevector checks independent.

PennyLane does not require a monolithic VQE class for this path, but the Hamiltonian, ansatz, differentiation, and optimizer building blocks must still be reused. A thin objective/update loop that calls those components is acceptable; custom gates or custom optimizer mechanics require an unsupported scientific requirement to be recorded.

## Independent Validation

- Check the converted Hamiltonian on analytic basis states and against exact diagonalization for a tiny case.
- Re-evaluate optimized parameters through the selected maintained ansatz template and `qml.expval`.
- Compare the optimization trace with the independent final evaluation and the variational bound.
- Keep validation evaluation-only; do not create a second optimizer or duplicate the VQE workflow.

Construct the neutral Pauli terms explicitly as PennyLane observables. Confirm wire labels, coefficient dtype, and constant terms before optimization.

## Differentiation and Measurement

- Record the QNode interface, device, shots, and resolved differentiation method.
- Use `shots=None` for deterministic reference and variational-bound checks.
- Prove a finite gradient or use a derivative-free optimizer for a flat/symmetric initial point.
- Do not assume a chemistry helper uses the same total-energy convention as the application contract.

## Adapter Checklist

- Hamiltonian conversion has an analytic known-state test.
- Ansatz parameter shape and wire order are explicit.
- Final energy is re-evaluated at the reported parameters.
- The report records `sdk: pennylane`, version, device, differentiation method, and limitations.
- The report lists reused chemistry/ansatz/optimizer components and any justified custom portion.
