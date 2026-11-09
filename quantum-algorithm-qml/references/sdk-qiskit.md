# Qiskit SDK Contract

## Selection Boundary

Use Qiskit only when the selected `QMLRoute` names `sdk=qiskit`, installed Qiskit and Qiskit
Machine Learning versions pass capability inspection, and the selected variant completes its
own materialized smoke. Do not infer variant support from a successful one-qubit primitive.

## Library-First Components

- Quantum kernels: `FidelityQuantumKernel`, `FidelityStatevectorKernel`, `QSVC`, `QSVR`.
- Supervised variational models: `VQC`, `VQR`, `NeuralNetworkClassifier`,
  `NeuralNetworkRegressor`.
- Custom QNN outputs: `EstimatorQNN` or `SamplerQNN`.
- PyTorch integration: `TorchConnector`.

Use installed Qiskit 2.x and Qiskit Machine Learning 0.9.x signatures. Do not use removed
`QuantumKernel`, `CircuitQNN`, or `TwoLayerQNN`.

## Runtime Adapter

Call `materialize_qml_adapter`, then use:

```python
from algorithm.qml_runtime.runtime import (
    load_and_infer,
    load_and_infer_many,
    train_and_save,
)

train_and_save("models/qml-model.json", rows=train_rows, targets=train_targets)
result = load_and_infer("models/qml-model.json", fixture_request)
scores = load_and_infer_many(
    "models/qml-model.json",
    [{"features": row} for row in validation_rows],
)
```

For `quantum_kernel` variants `qsvc` and `qsvr`, the adapter uses
`FidelityStatevectorKernel` with Qiskit's `zz_feature_map`, fits a precomputed-kernel
scikit-learn SVM offline, and persists only inert JSON support vectors, dual
coefficients, intercept, class mapping, feature-map parameters, and adapter version.
Inference reconstructs the Qiskit kernel and decision function without loading an
executable object. The bounded batch entrypoint validates immutable JSON state once per model
SHA-256 and evaluates all rows in one kernel call; process-local cache entries are read-only and
resource-limited. Compatible hybrid routes persist tensor state and reload it with
the framework's weights-only mode.

For `variational_supervised/vqc`, the managed adapter now trains the official `VQC`
with exact `QMLSampler(shots=None)`, `zz_feature_map(reps=1, entanglement="linear")`,
`real_amplitudes(reps=1, entanglement="linear")`, and seeded COBYLA (60 evaluations).
It saves only validated JSON: trained numeric weights, ordered input/weight names,
numeric classes, fixed circuit/execution settings, schema/adapter version, and SDK versions.
Inference reconstructs a `SamplerQNN` and calls its forward pass with the saved weights;
no training, optimizer restore, or executable object loading occurs. This initial route
supports 2 to 8 input features, up to 256 training or batch-inference rows, and 2 to
`min(10, 2**feature_width)` numeric classes. Measurement interpretation is the integer
basis index modulo class count. `classes` gives the probability order; `label` is the
original numeric label, and `value` is the predicted class's circuit probability.
These probabilities are not calibrated business confidence. Exact Qiskit and Qiskit
Machine Learning versions must match the training environment. The fixed circuit
topology must be disclosed; learned gate angles come from training, not from the LLM.
Preprocessing remains application-owned and must be frozen alongside the model.
`variational_supervised/vqr` remains unavailable until its own safe adapter is implemented;
VQC readiness does not imply VQR readiness. Inspect variant-specific persistence metadata.

VQC `train_and_save` also writes a `.training.json` sidecar and returns its relative
path as `training_evidence_file`. Set `backend.application.TRAINING_EVIDENCE_PATH`
to this returned path for the standard application charts. The framework reads
real optimizer evaluations, initial weights and trained weights through
`GET /api/training`, verifies the model SHA256 and weight alignment, and draws
the charts without training during requests. Missing or stale records produce
an explicit unavailable state; never invent a loss curve for QSVC.
For local statevector kernels, fit application-owned reduction on training data only and target at
most 10 output features. The runtime rejects widths above 12 before constructing a circuit; this
hard ceiling is a resource-safety boundary, not a recommended modeling dimension.
Application code must not duplicate the QNN, kernel, optimizer bridge, or
serialization logic to bypass that boundary.

## Parameter and Measurement Semantics

Keep feature parameters and trainable weight parameters separate and ordered. Record circuit
qubit order, primitive/backend, observables, sampler interpretation, output shape, class
mapping, shots, seed, and transpilation assumptions. Set `input_gradients=True` when a
PyTorch-connected upstream layer requires input gradients and verify the resulting tensor.

## Persistence

Only load service-owned artifacts created by the offline training workflow under the generated
application's `models/` directory. Never accept a model path or artifact from chat, an API,
an upload, or a browser action. Do not deserialize Pickle, Dill, Cloudpickle, or Joblib data,
and do not write a substitute loader when the adapter rejects a route. Persist preprocessing,
route and adapter versions, feature/weight ordering, interpretation, model hash, and known
fixture in the inference bundle, then verify the adapter-selected safe reload path in a fresh
process.

## Unsupported Behavior

For reservoirs, generative, representation, and reinforcement profiles, use the
framework-owned adapter built from current Qiskit circuit/statevector/primitives APIs. Do not
claim Qiskit supplies a high-level algorithm when it supplies only primitives.

If that adapter does not exercise the selected variant's real training and inference
semantics, return unavailable. Do not map clustering to `QSVC`, map qGAN to threshold sampling,
or replace the selected route with another SDK or handwritten approximation.

## Evidence

Record Qiskit and Qiskit Machine Learning versions, selected fully qualified components,
primitive/backend, input and weight parameter partitions, output interpretation, gradients,
shots, seeds, adapter and model hashes, reload fixture, and limitations. Hardware and IBM
Runtime are outside this local Skill.
