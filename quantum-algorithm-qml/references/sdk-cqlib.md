# Cqlib SDK Contract

## Selection Boundary

Use Cqlib only when the selected `QMLRoute` names `sdk=cqlib`, the installed version passes
capability inspection, and the selected variant passes its own materialized smoke. Cqlib
currently provides circuit and simulator primitives rather than maintained high-level QML
estimators; do not describe a primitives-based adapter as a native Cqlib QML algorithm.

## Library-First Components

The managed `quantum_kernel/qsvc` and `qsvr` routes use real Cqlib
`StatevectorSimulator` fidelity kernels and scikit-learn's precomputed-kernel
solver. They persist numeric support vectors and coefficients as JSON. The fixed
encoding is RY(x), then RZ(x²), in radians without an extra pi factor, followed
by an input-independent linear CX chain. Show those exact angles in any bound
feature-map illustration; this fixed encoding does not imply quantum advantage.
One QSVC model accepts exactly two classes. For multiclass data, application-owned
one-vs-rest aggregation may call one managed binary model per class; preserve the
uncalibrated decision values rather than presenting softmax values as probabilities.

The managed `variational_supervised/vqc` route uses Cqlib circuit/statevector
primitives with scipy COBYLA optimization, not a native Cqlib classifier or
automatic differentiation. Inputs are RY(x), RZ(x²); the trainable ansatz is an
RY layer, a linear CX chain, then another RY layer. Input angles are radians with
no additional pi factor; a displayed bound circuit must use those exact angles
and the saved weight ordering. Cqlib bit-string keys have
q0 as the rightmost (least significant) bit; class probabilities aggregate
basis_index modulo class_count. Exact circuit probabilities are not calibrated
fraud risks. The route supports 2–8 features, up to 256 training rows, up to
min(10, 2**feature_width) numeric classes, and 256 requests per inference batch.
Training uses fixed seed 12345 and at most 60 COBYLA objective evaluations.
An evaluation limit is reported separately from optimizer convergence.
The inference `probabilities` are already class-aggregated in `classes` order;
do not reaggregate them or fabricate one-hot values if they are absent. The last
loss evaluation is not necessarily the objective at the saved final weights.

`train_and_save` writes inert weights JSON and a `.training.json` sidecar.
Set `backend.application.TRAINING_EVIDENCE_PATH` to its returned relative
`training_evidence_file` for authentic loss and parameter charts. Inference
reconstructs only this fixed circuit after validating its schema, versions,
weights, class labels and parameter ordering; it never retrains. Persist
preprocessing independently and evaluate all requested batches, without
overriding the framework runtime or silently changing to a kernel route.

Use balanced training subsets when appropriate, fit preprocessing on training
data only, and disclose any enriched test prevalence. For held-out evaluation
larger than 256 rows, chunk `load_and_infer_many` into batches of at most 256.

- Use `cqlib.Circuit` and `cqlib.Parameter` for circuit and parameter semantics.
- For a separately supported differentiable route, use `cqlib.simulator.SimpleSimulator`
  for the local PyTorch-backed path. This does not describe the managed VQC route above.
- Keep tensors connected through `SimpleSimulator.probs()` or statevector computation; do
  not convert to `float`, NumPy, or detached values before the loss.
- Prove a finite nonzero gradient and one effective parameter update before claiming native
  autodiff.

## Runtime Adapter

Call `materialize_qml_adapter`, then use:

```python
from algorithm.qml_runtime.runtime import load_and_infer, train_and_save

trained = train_and_save("models/qml-model.json", rows=train_rows, targets=train_targets)
result = load_and_infer("models/qml-model.json", fixture_request)
# For VQC, use trained["training_evidence_file"] for TRAINING_EVIDENCE_PATH.
```

Keep application-specific data preparation and configuration outside
`algorithm/qml_runtime/**`. Do not create another task-local classifier, reservoir, QNN
wrapper, simulator bridge, or replacement implementation. Convert NumPy training
arrays with `.tolist()` before calling the list-based runtime training interface.
Persist the preprocessing parameters actually fitted on the training split. For
JSON reload, apply stored scaling, centering and projection matrices directly;
whitening also needs the real fitted variances. Do not guess a partial sklearn
PCA object's internal attributes to reconstruct preprocessing.

## Parameter and Measurement Semantics

Record qubit and classical-output ordering, parameter insertion and binding order, tensor
dtype/device, statevector or probability shape, observable construction, and conversion into
the profile output. Do not detach, cast to `float`, or convert to NumPy before a differentiable
loss. The C backend is not equivalent to the local PyTorch-backed simulator.

## Persistence

The offline training script writes model state under `models/`; the inference bundle records
its hash, preprocessing, route, package versions, request/response schemas, and known fixture.
Reload in a fresh Python process and verify the fixture before publishing the bundle.

## Unsupported Behavior

If the materialized adapter lacks the selected variant's actual model and acceptance smoke,
return an unavailable capability. Do not replace it with a one-qubit feature, linear
placeholder, another SDK, or TianYan execution. This Skill is local-only and must not submit
cloud jobs.

## Evidence

Record the Cqlib and PyTorch versions, simulator class, tensor dtype, device, parameter/wire
mapping, reused adapter ID/version, gradient or non-gradient method, model hash, reload fixture,
and profile-specific diagnostics.
