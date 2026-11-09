# Qiskit QAOA Adapter

## Support Status

- Local statevector QAOA and seeded decoding: `verified`
- Qiskit Optimization/Qiskit Algorithms integration: `verified` for the version-matched path
- IBM Runtime or hardware execution: outside this skill's verified path

Target the dependency range declared by the active project and inspect active signatures before using optional APIs. Qiskit Optimization 0.7.x provides `qiskit_optimization.minimum_eigensolvers.QAOA`; older supported stacks may provide `qiskit_algorithms.QAOA`. Never combine imports copied from different release lines.

## Library-First Path

For the homepage Max-Cut application with 2–10 vertices, read and reuse the bundled
`../assets/qiskit_maxcut.py` reference as the application-owned solver module.
Its `solve_maxcut(num_nodes, edges, reps=1, shots=2048, maxiter=60, seed=42)` uses
`Maxcut`, `MinimumEigenOptimizer`, and the Qiskit Optimization 0.7 QAOA/COBYLA
implementations; it does not implement another quantum optimizer. Edges are
`[source, target, nonnegative_weight]`; at least one positive edge is required.
The reference bounds vertices to 10, depth to 3, shots to 4096, and evaluations
to 120. Preserve those bounds or replan explicitly; defaults are a small local
starting point, not literature guarantees or a performance threshold.

The returned JSON includes actual bound SDK gates, sample probabilities, distinct
best/most-probable/expected cuts, exact and greedy references, the independent
all-bitstring Ising check, and a graph partition matching the best sample. Use
`save_result` / `load_result` for inert result evidence under `artifacts/results/`.
Loading those results is a labeled replay, not a learned-model load or a solve
for changed input. The web `infer` adapter must call `solve_maxcut_isolated` on its
validated current fields and map its `best_sample.cut_value` to
`prediction={kind: "solution", label: <partition description>, value: <cut>,
score_semantics: <best-sample objective semantics>, scores: <finite metrics>}`,
plus returned `graph` and `quantum`.
This entry uses the same library solver in a fresh local Python process, with at
most two concurrent workers per application process, a five-second queue wait,
and a 120-second solve timeout. It contains a native Qiskit failure observed in
a long-lived Windows HTTP process; it does not claim to fix upstream native
memory behavior. A crash, timeout, or full queue is a failed request, never a
cached success. Keep the reusable asset intact so its internal worker entry
remains available. Offline `scripts/solve.py` may use `solve_maxcut` directly.
Exercise repeated and two concurrent real HTTP requests, then check health and
a new successful solve; a one-shot numerical test does not establish service
stability. Account for interpreter startup in request latency.
If adding sampled-state bars, map actual samples to the surface's field names:
`quantum["top_states"] = [{"label": s["bitstring"], "value": s["probability"]}
for s in result["samples"][:5]]`. The framework expects `label` and numeric
`value`, not raw `bitstring`/`probability` keys. Raw QAOA `trace` may be exposed as
API evidence; the current template's convergence plot supports energy results
only, so do not promise a QAOA curve unless an actual supported renderer exists.

The main `prediction.value` and its `score_semantics` must both describe the
best sampled cut in edge-weight units. Put the dimensionless approximation ratio
in a separately labeled score; never label a cut such as 17 as a ratio or a
probability. Reports must distinguish the best sampled cut from the distribution
mean and the exact reference, even when the best sample reaches that reference.
Derive displayed vertex sets by enumerating `partition[q]` in vertex order:
`A = [q for q, bit in enumerate(partition) if bit == 0]`, with B using bit 1.
Reuse those sets in the UI and final report; do not decode the printed bitstring
mentally. For example, `[0,1,1,0,1,0]` means A={0,3,5}, B={1,2,4}, while its
Qiskit display string is `010110` (q5...q0). Recompute the crossing-edge sum
from those same sets before quoting the objective.

On the standard numeric-field surface, plan a fixed small vertex count and expose
each undirected edge weight as one field (zero means absent). State that graph
size and input limits in the UI. Do not promise the unsupported freeform JSON
graph editor or fabricate a `models/*.json` file. Per-instance solve results and
fixed problem configuration belong under `artifacts/results/` and application
source respectively; the official surface smoke handles explicit solution results.
Create `scripts/solve.py` as the bounded offline validation entry point and persist
its checked result JSON under `artifacts/results/` so the workflow can hand the
solver artifacts to the surface stage. Set `get_info()["execution_kind"] = "solver"`
to select solver-specific smoke checks and hide unrelated model-training history.
Document only declared fields: for vertices 0 through 5 the last undirected
edge field is (4,5), not (5,6). Reject an all-zero graph with a clear bounded
input error; zero-weight edges and disconnected graphs with positive edges
remain valid under the reference solver contract.

Prefer these maintained components when present and compatible:

1. `qiskit_optimization.problems.QuadraticProgram` and its converters for supported application models.
2. The installed release's `QAOA` minimum eigensolver with a supported Sampler primitive and optimizer.
3. `qiskit_optimization.algorithms.MinimumEigenOptimizer` for compatibility checks, QUBO conversion, solve orchestration, and result decoding.
4. Official optimizer callbacks/result objects for the convergence trace.

Check `MinimumEigenOptimizer.get_compatibility_msg()` before execution. Keep the neutral QUBO evaluator and feasibility decoder independent, but do not duplicate the production QAOA ansatz or solver loop.

## Independent Validation

- Compare the library-produced Ising operator with direct QUBO energies for every bitstring of a tiny instance.
- Evaluate one fixed parameter point through the selected library ansatz and independently score its returned distribution.
- Test decoding with prepared basis states; this may use basic state preparation but must not recreate QAOA.
- Recompute feasibility and the original objective outside Qiskit's optimization result.

Qiskit bitstrings display the highest classical/qubit index on the left for the standard register layout. Keep the application mapping explicit and test `q0` against the rightmost bit rather than relying on memory.

## Optimization

- Use the optimizer bundled with or supported by the active QAOA implementation after checking its installed API.
- Seed algorithm globals and any sampler used by the active implementation.
- A direct statevector energy calculation is allowed only as a fixed-point validation check, not as a replacement production optimizer.
- Record whether the objective uses exact probabilities or finite shots.

## Adapter Checklist

- No deprecated blueprint circuit is required by the implementation.
- Parameter order is passed explicitly to assignment.
- The statevector energy matches direct Ising evaluation on known states.
- The report records `sdk: qiskit`, package versions, backend, seed, and limitations.
- No IBM credentials, Runtime service, or hardware job is used by local tests.
- The report distinguishes the library production path from any validation-only native oracle.
