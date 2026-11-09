---
name: quantum-cloud-execution
description: "Execute a bounded, user-authorized verification job on the TianYan Quantum Computing Cloud Platform through submit_tianyan_task and record the receipt artifacts/tianyan/cloud_job_record.json. Active for execution_mode=tianyan_authorized deliveries."
---

# Quantum Cloud Execution

Execute an already validated circuit or workload on the TianYan Quantum Computing Cloud Platform without exposing secrets or changing scientific semantics.

## Authorization Gate

The user authorization is the Intake contract: `execution_mode=tianyan_authorized`
with a confirmed top-level `tianyan_device.computer_code` in
`application_manifest.json`. Remote execution targets the TianYan Quantum Computing Cloud Platform only, through the Cqlib only SDK client. Do not route to another cloud platform. Never invent client classes. Platform
credentials are pre-configured by the deployment environment (config.yaml →
`TIANYAN_API_KEY`); never request, print, or commit credentials. Authorization
for one machine does not authorize another.

## Workflow

1. Read the manifest's `tianyan_device` and the plan's TianYan submission item.
2. Pick the delivered model/solver's representative circuit with frozen
   parameters: at most 4 logical qubits and at most 1024 shots. Do not retrain,
   re-optimize, or change the scientific meaning; if the selected machine lacks
   a required gate, compile the logical circuit to its native gate set (for
   example CNOT → Z-CZ-Z) without changing logical qubit/measurement semantics.
3. Pre-check the circuit with the read-only QCIS check endpoint when available;
   fix rejected circuits per the reported error instead of silently dropping gates.
4. Submit exactly once with `submit_tianyan_task` on the confirmed machine and
   wait for the real platform result.
5. Write `artifacts/tianyan/cloud_job_record.json` containing at least:
   `computer_code`, `task_id` (or `submission_error` when the platform rejects),
   `shots`, `circuit_summary`, `submitted_at`, `duration_ms`, and `counts`.
   `submitted_at` is the real ISO-8601 wall-clock time captured at submission;
   `duration_ms` is the measured wall-clock milliseconds between submission and
   receiving the platform result. Never write placeholder values (such as a
   00:00:00 timestamp or a null duration) when a submission actually happened.
   The framework gate blocks the writing stage until this receipt exists.
6. Hand real results to writing-agent through the receipt; never hand local
   simulation output as TianYan evidence.

## No Silent Fallback

Do not replace the selected TianYan execution with a local simulator, change
device, reduce shots, or switch SDK after a failure. A platform rejection
(invalid circuit, insufficient quota, machine unavailable, pre-check failure)
is a real outcome: record it honestly in the receipt as `submission_error` with
the platform's message. Skipping the submission entirely for an
`execution_mode=tianyan_authorized` delivery is forbidden; the receipt must
exist either way.

## Handoff

Return the machine code, task ID or honest rejection, submitted content, shots,
duration, and counts. A completed TianYan job is evidence, not approval of
application readiness or proof of quantum advantage.
