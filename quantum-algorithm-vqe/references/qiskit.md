# Qiskit VQE Adapter

## Support Status

- Local statevector Pauli expectations: `verified`
- Qiskit Algorithms VQE 0.4.x path: `verified`
- IBM Runtime or hardware execution: outside this skill's verified path

Use the Qiskit and `qiskit-algorithms` versions declared by the active project. Avoid deprecated blueprint-only assumptions and verify optional API signatures at runtime.

## Library-First Path

- Use the installed version's maintained `VQE` implementation with a supported Estimator primitive, optimizer, callback, and initial point.
- Reuse Qiskit circuit-library ansatzes and initial-state components when they satisfy the scientific contract.
- For molecular problems, use Qiskit Nature problem, mapping, and ansatz components only when that optional package is installed and its energy convention is verified.
- Treat Qiskit Nature and a chemistry driver as separate dependencies. If a compatible
  chemistry-driver wheel is unavailable in the current environment (as observed in
  the validated Windows / Python 3.12 setup), for an explicitly fixed LiH demonstration load the
  trusted precomputed integral route in `lih-fixed-instance.md` without PySCF. A new
  geometry or basis still requires a compatible driver or verified matching integrals.
- Use the solver result and callback interfaces for convergence evidence, then independently recompute the final energy.

Do not duplicate the production VQE optimization loop or Pauli expectation engine. If the VQE package is missing, report the dependency blocker instead of silently creating a native solver.

## Independent Validation

- Check the library Hamiltonian on analytic basis states and against exact diagonalization for a tiny case.
- Restrict molecular references to the same particle sector as the ansatz. Verify both
  the Hamiltonian's sector conservation and the optimized state's sector probability.
- Include inactive and nuclear offsets exactly once, consistently in trace, final value,
  and reference. The final state/energy must agree after JSON parameter reload.
- Bind the optimized parameters to the selected maintained ansatz and independently recompute the final expectation.
- Compare callback trace values with the final solver result and the independent recomputation.
- Keep this validation evaluation-only; it must not contain a second optimizer or a duplicate VQE loop.

Qiskit Pauli strings and circuit qubits use a documented ordering convention. Verify the neutral Pauli-term mapping with analytic basis states before loading an application Hamiltonian.

## Solver Rules

- Use `qiskit_algorithms.VQE` or the maintained version-matched replacement only with a primitive and optimizer supported by the installed versions.
- Seed `qiskit_algorithms.utils.algorithm_globals` and any primitive options.
- Capture callback evaluations rather than relying only on the final result object.
- Preserve an evaluation-only local objective as an independent debugging path.

## Adapter Checklist

- Qubit/Pauli ordering has an analytic test.
- Circuit parameters are assigned from an explicit list.
- Final energy is recomputed independently at optimized parameters.
- The report records Qiskit, Qiskit Algorithms, backend, optimizer, and limitation metadata.
- The report distinguishes the library solver from independent evaluation-only checks.
