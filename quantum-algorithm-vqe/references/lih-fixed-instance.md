# LiH fixed-instance VQE on native Windows

Use this route only when a small, fixed-geometry LiH demonstration meets the
application contract. It is not a substitute for generating integrals at a new
bond length, changing a basis, or computing a full molecular potential curve.

The validated native Windows / Python 3.12 environment had no compatible PySCF
wheel. A missing compatible chemistry-driver wheel is a
chemistry-driver/platform blocker, not a failure of Qiskit's VQE solver. Do not
keep retrying the same unsupported install. Qiskit Nature can instead load
trusted precomputed molecular integrals without importing PySCF.

## Reproducible instance

The bundled `../assets/lih_sto3g_2e2o.json` is derived from the Qiskit Nature
project's LiH FCIDUMP regression fixture at the pinned revision and SHA256
recorded inside it. Its upstream test describes neutral, singlet LiH at nominal
1.6 angstrom in STO-3G. The source's nuclear constant is preserved exactly; do
not replace it by a separately rounded geometry-derived constant.

The generation script `../assets/rebuild_lih_fixture.py` loads the original
FCIDUMP with Qiskit Nature, selects two active electrons in spatial orbitals
`[1, 2]`, freezes occupied orbital 0, excludes virtual orbitals 3--5, and applies
Jordan-Wigner mapping. This gives four qubits and 27 Pauli terms. The two
independent constants are nuclear repulsion and inactive electronic energy.
Neither constant is included in the stored active-space Pauli operator.

This reduced Hamiltonian is an explicit approximation. Agreement with its
exact eigenvalue proves numerical correctness for this instance. It does not
establish chemical accuracy against the full six-orbital molecule, experiment,
or hardware performance.

## Maintained solver path

Install `qiskit-nature` and `qiskit-algorithms` through the authorized dependency
tool if needed; PySCF is not required to consume this instance. Use
`qiskit_nature.second_q.circuit.library.HartreeFock` and `UCCSD` with
`JordanWignerMapper`, `qiskit.primitives.StatevectorEstimator`, and
`qiskit_algorithms.VQE` with a maintained optimizer. Keep a zero initial point
for the Hartree-Fock state and capture actual callback evaluations.

For a generated runnable application, write a `requirements.txt` containing its
actual direct runtime dependencies and the validated versions: Qiskit, Qiskit
Algorithms, Qiskit Nature, NumPy/SciPy, and its web-service packages. A successful
install in the current environment is not a portable dependency declaration.
Do not include PySCF for this fixed precomputed route. The final documentation
must distinguish installation instructions from commands actually executed in
the current run, and identify the verified interpreter and application directory.

The bundled runtime `../assets/lih_qiskit_runtime.py` is a small reference adapter
for this route. Copy it and its JSON input into the application together rather
than reconstructing the Pauli coefficients or writing a second optimization
loop. It supports bounded local solves and pure JSON result persistence. It
does not train a model or require a QML adapter.

Its actual optimizer is `qiskit_algorithms.optimizers.SLSQP` with a zero
Hartree-Fock initial point and exact statevector expectations. Its primitive has
an internal fixed seed of 42, but `solve_lih` accepts no `seed` parameter and
does not randomize the initial point. Preserve this contract in plan,
wrapper, API, presets, page labels, and final summaries. Do not advertise COBYLA
or add a seed control that is merely echoed without affecting execution.
Use the returned `optimizer.class`, `optimizer.iterations`, and
`optimizer.energy_evaluations` as execution evidence. A requested optimizer
change requires a real implementation change and focused validation.

Qiskit Algorithms 0.4.0 truncates the VQE callback parameter vector to one scalar
per energy evaluation. The reference adapter observes copied parameter rows at
the public EstimatorPub boundary, delegates the unchanged request to Qiskit's
StatevectorEstimator, and associates each callback energy with its actual row.
It preserves the SDK VQE and optimizer and does not patch installed packages.
Validate trace replay from the full saved parameters, not only the final point.
The [official 0.4.0 VQE source](https://qiskit-community.github.io/qiskit-algorithms/_modules/qiskit_algorithms/minimum_eigensolvers/vqe.html)
and the installed source both show this callback shape behavior.

For each solve, validate the particle sector, independently recompute the final
state expectation, add the two offsets once, and compare against exact
diagonalization of the same sector. Never compare a molecular fixed-electron
result to the unconstrained Fock-space minimum without checking its sector.

## Application contract

- Clearly label the page as fixed LiH / nominal 1.6 angstrom / STO-3G / CAS(2e,2o).
- Expose only controls the solver actually uses, such as optimizer iteration
  limit. Reject arbitrary bond lengths or basis choices in this fixed route.
- A bounded per-instance VQE solve is algorithm execution, not model training.
- Store Hamiltonian metadata, ordered parameters, actual convergence trace,
  final state, optimizer termination, exact reference, offsets, and versions.
- Distinguish optimizer iterations from energy function evaluations; callback
  energies can increase during line search and need not be monotonically decreasing.
- The final callback can be a line-search or finite-difference evaluation, not
  the returned optimum. Keep its actual energy and parameters. Independently
  recompute `final_energy` from the returned parameters; require agreement with
  `prediction.value`, not equality with the last callback. Never append a fake
  callback point or change the recorded trace to force equality.
- An iteration limit is not evidence of convergence. Report
  `optimizer.iteration_limit_reached`, observed error, and any separately
  evaluated reference tolerance. When the SDK does not report optimizer
  success, preserve `success_reported: null`; do not infer success merely from
  a returned result or from meeting a loose energy-error threshold. Describe
  bound circuits as using returned parameters, not unconditionally converged
  parameters. Passing an active-space error threshold does not establish
  chemical accuracy for the full molecule.
- Official numeric fields reach `application.infer` as finite floats, including
  integer-valued inputs and accepted numeric strings. For `max_iterations`,
  validate finiteness, `value.is_integer()`, and the range, then convert to
  `int` before calling this runtime. Do not reject `100.0` with an `int`-only
  type check. The framework rejects booleans before business execution.
- JSON reload is evaluation-only: recompute the bound circuit state and energy
  from the persisted parameters without launching another optimization.
- The reference adapter validates a canonical JSON content hash before trusting
  the fixed LiH identity. Never edit its coefficients/offsets while retaining
  the official-instance label; use another explicitly sourced instance instead.
- Use the returned `quantum` metadata directly: it is extracted from the final
  bound UCCSD circuit, including preparation, gate parameters and global phase.
  For the official app surface return `prediction.kind=energy` and map the
  actual `convergence_trace` to `convergence.points`, preserving total energies,
  evaluation indices, the independent final energy and same-sector reference.

Sources: [PySCF platform support](https://pyscf.org/user/install.html),
[Qiskit Nature FCIDUMP loading](https://qiskit-community.github.io/qiskit-nature/migration/0.5_c_electronic_structure.html),
and the pinned upstream source URLs inside the asset.

Declare `execution_kind: "solver"` in `get_info()` so the UI hides the unrelated QML training panel.
