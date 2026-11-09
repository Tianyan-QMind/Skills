---
name: quantum-application-intake
description: "Clarifies a quantum application request and records the current machine contract. Use before research. Do not choose the algorithm, implement code, or approve delivery."
---

# Quantum Application Intake

Turn the user's objective into enough context for research and planning without
prematurely designing the solution.

## Responsibilities

- identify the application goal, intended user, inputs, outputs, and constraints
- distinguish user requirements from assumptions and optional preferences
- ask only questions whose answers materially change scope, data access, delivery
  profile, or expected result
- choose a lowercase kebab-case application slug
- publish the complete operational `application_manifest.json`

Write this single contract directly under `generated_apps/<slug>/`.

## Guidance

Do not select a QML family, variant, or SDK merely from keywords. Cqlib, Qiskit,
and PennyLane are equal built-in local SDK options. During interactive application
Intake, ask which SDK to use when it is unspecified and record the answer as a
required constraint. If the user explicitly delegates SDK selection to the
system, or interactive questioning is unavailable, record `selected_sdk=null`
with `sdk_selection_source=planner_pending`; planner-agent then owns the later SDK
decision. The current workflow supports local simulation by default; real-machine
execution on the TianYan quantum cloud platform is an explicit user choice (see
"Real machine selection" below).

## Real machine selection (天衍真机)

Local simulation is the default. Only when the user explicitly asks to run on a
real quantum machine (真机/天衍云平台) does Intake offer the real-machine path:

1. Call `inspect_tianyan_machine_availability` to query the platform's live
   machine list (Running / Calibration / Maintenance / Offline, free / paid).
   The tool reads the user's saved cloud-platform key through QMind's effective
   configuration (with legacy `TIANYAN_API_KEY` support). Try the tool first;
   do not ask the user to configure an already saved key. If credentials are
   missing, direct the user to Settings → Cloud platform connection key; never
   ask them to paste a key into the conversation or a generated script. Report
   other blockers such as a missing SDK accurately; do not invent machine status.
2. Present ONLY the available machines from `presentable_machines` (do not
   show unavailable machines), in `recommended_order`, and ask which machine
   to target. For each machine list its `computer_code`, `status`, `toll`,
   and `gate_support` (supported/unsupported gates; physics machines also
   carry a `profile` with qubit count and error rates). Recommend the
   machine whose gate set best covers the task's needs — e.g. QML needs
   parameter gates (RY/RZ) plus an entangling gate (CZ/CNOT); QAOA needs
   RZ/RX/RZZ; VQE needs RY plus an entangling gate. A Running machine may
   still reject submission later (insufficient machine time, institution-
   exclusive resource). In that case implementation must record the platform
   rejection honestly in `artifacts/tianyan/cloud_job_record.json` as
   `submission_error`. Choosing a real machine makes the submission attempt
   itself a mandatory delivery step, never optional: the plan must include a
   bounded verification submission (frozen model/solver parameters, at most 4
   logical qubits, at most 1024 shots) executed with `submit_tianyan_task`,
   and the final report must show the machine code, task ID, submitted
   content, duration, and real platform counts.
3. Record `execution_mode: "tianyan_authorized"` and a top-level
   `tianyan_device` object with at least `computer_code` (the exact machine
   code from the availability query), plus the observed `status`, `toll`, and
   `checked_at` snapshot. Never record the API key or any credential. Add to
   `intake.success_criteria` that the delivery includes the real-machine
   verification submission evidence (`artifacts/tianyan/cloud_job_record.json`
   with task ID, submitted content, duration, and real counts, or an honest
   `submission_error`).
4. Do not submit circuits during Intake. Real-machine submission happens during
   implementation via the `submit_tianyan_task` tool (code-agent / debug-agent),
   which uses the pre-configured platform credentials and reports real platform
   results or real platform errors.

Classify whether the application contains learned model parameters. Learned-model
training must be a separate local offline command, persisted model and preprocessing
artifacts must be reusable, and preview/service/browser paths are inference-only.
Declared per-instance QAOA/VQE optimization is not model training.
For those solvers, record a bounded problem input and execution budget; do not add an
inference-only or no-optimization constraint unless the user actually requests result replay.
If only a fixed molecular geometry/Hamiltonian can be supported, state that limitation
explicitly. Do not turn a general solver request into cached-result display silently.

Match success criteria and question options to the task. Classification metrics such
as F1, ROC-AUC, and Accuracy do not apply to pure QAOA/VQE solvers. For Max-Cut,
distinguish best cut value, expected cut, and approximation ratio against a feasible
exact reference. For VQE, use energy in Hartree, absolute error against an agreed
reference, and convergence/evaluation budget. Preserve the user's time budget;
research/planning establish the reference and its feasible scope. Do not invent a
classification-style accuracy percentage or ask already answered metric questions.

Unknown details remain in `intake.open_questions`. Intake is complete when the
next research agent can understand what is being built and what remains uncertain;
it does not require a field-complete scientific contract.

## Output

`application_manifest.json` is an unversioned contract using `language: "zh-CN"` and contains:

- top-level slug, delivery profile, execution mode, selected SDK policy, and Chinese user summary
- when `execution_mode` is `tianyan_authorized`, a top-level `tianyan_device` object
  recording the confirmed machine (`computer_code`, `status`, `toll`, `checked_at`)
- `intake.goal`, `target_user`, `inputs`, `outputs`, `constraints`, `success_criteria`,
  `delivery_profile`, and `open_questions`
- canonical `artifacts` paths for evidence, plan, run history, results, README, and final report

Do not write `schema_version` or legacy top-level business fields such as `summary`,
`goal`, `intended_user`, `input`, or `output`. If the write tool rejects the
contract, correct every reported field before delegating research.

Create a new manifest with `write_file`. If the path already exists, first read
the current manifest and then use one `edit_file` call whose `old_string` and
`new_string` each contain the complete JSON document. Partial manifest edits are
forbidden.

The manifest is a machine handoff contract, not validation evidence.
Intake does not approve the selected method or final delivery.

## Handoff

Return the application slug, generated paths, assumptions, and open questions to the
research stage.
