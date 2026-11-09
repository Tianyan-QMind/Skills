---
name: quantum-application-verification
description: "Run focused delivery checks in an isolated snapshot and document observed results without certifying application correctness."
---

# Quantum Application Verification

Run only the declared focused checks through `run_app_check`, which copies the
application into a disposable snapshot and automatically appends sanitized execution facts to
`artifacts/run_history.jsonl`. Return a concise Simplified-Chinese summary directly.

List:

- artifacts that are present
- commands actually executed and their observed output
- results and limitations from the isolated checks
- checks that remain unverified or cannot be run
- missing files or unresolved blockers

Do not modify production source, run commands outside `run_app_check`, fabricate
evidence, write a role-specific report, or convert an observed local pass into a broader claim.
The summary does not certify runtime correctness beyond the executed check, deployment readiness,
TianYan execution, scientific validity, or quantum advantage.
It does not approve the application or release.

No generated artifact escapes or duplicates the application root.

## Handoff

A local runnable-app handoff must retain the framework-issued application entry even when
the model's final response omits a URL or later generation fails. Verify real application
inference separately from the framework's fallback circuit demonstration. The fallback is
interactive and explicitly declares that the task model is incomplete/unavailable; it must
never be counted as passed task inference, successful training, or a quantum advantage result.
Documentation completion is not a prerequisite for opening an available application surface.

Return executed commands, statuses, evidence paths, missing artifacts, blockers, and unverified checks.
