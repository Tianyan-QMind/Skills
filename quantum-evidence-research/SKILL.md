---
name: quantum-evidence-research
description: "Researches actionable evidence for quantum application decisions: classical baselines, datasets, known methods, maintained Cqlib/Qiskit/PennyLane components, evaluation protocols, and local backend constraints. Use when planning lacks sourced evidence. Do NOT use to implement code, make the final route or SDK decision, or claim application readiness."
---

# Quantum Evidence Research

Collect decision-grade evidence that resolves the research-owned uncertainties
in one quantum application intake contract.

## Ownership

`research-agent` owns this skill. Other agents consume its evidence but should not turn unsourced recollection into a route decision.

## Research Scope

- problem assumptions and established classical baselines
- datasets, instances, preprocessing, splits, and licensing constraints
- QAOA, VQE, QML, or hybrid suitability and known failure modes
- maintained components of the user-selected SDK, or bounded route-relevant capability evidence across Cqlib, Qiskit, and PennyLane when selection is pending
- evaluation protocols, reference values, metrics, and uncertainty treatment
- local simulator, dependency, adapter, and documented API constraints

## Workflow

1. Consume the runtime-provided Intake contract and research questions. It names
   one application root. Do not rescan the application directory or inspect
   unrelated generated applications.
2. Start with quantum fit: identify what part of the user's objective a quantum
   PoC can test, the strongest credible classical baseline, and whether evidence
   supports a quantum route at all. A justified no-go is valid research output.
3. Turn those questions into a short search plan: quantum fit, at least one
   viable alternative, the classical baseline/evaluation contract, data
   feasibility, and SDK/runtime feasibility.
4. Inspect source-discovery availability after defining the decision questions.
   For `user_selected`, inspect only that SDK. For `planner_pending`, collect
   comparable route-relevant evidence for Cqlib, Qiskit, and PennyLane without
   choosing a winner. Use Tavily for authoritative web discovery and
   `search_scholarly_sources` for DOI metadata leads.
5. Prefer primary documentation, maintained repositories, peer-reviewed papers,
   dataset repositories, and authoritative platform documentation.
   Use separate focused queries for dataset, SDK, and method evidence when a
   combined query returns irrelevant results. Discover URLs through search results
   or actual links from official indexes; never guess version directories or API
   page names. Qiskit Machine Learning's official documentation uses `/apidocs/`
   for module indexes and `/stubs/` for class pages; follow its current navigation
   rather than assuming a `/stable/` prefix. These are discovery hints, not evidence.
6. Fetch every retained source and record its access time and content hash.
   Crossref metadata and search snippets are leads, not evidence.
   On 404/410, use an official index or a site-specific search to find a corrected
   URL. Empty/irrelevant search results and missing authoritative evidence also
   permit follow-ups. The fetch tool automatically makes up to three attempts for
   transient transport/408/429/5xx failures; after exhaustion choose an authoritative
   alternative or record the gap, without repeating the unchanged failed batch.
   For canonical dataset bytes, use `fetch_evidence_source(mode=dataset_probe)`.
   Its bounded byte sample proves only non-empty download accessibility; record
   it as `download_probe`. Fetch official provenance/schema separately. The probe
   does not verify schema, archive contents, row counts, or full-file integrity;
   implementation must download and validate the complete file. Never use
   `sample_sha256` as an expected full-file checksum. A size-limited document fetch
   can be retried in probe mode at the same URL without consuming a new distinct URL.
7. After each search, identify which decision was answered, contradictory
   evidence, and the smallest missing query.
8. Extract actionable constraints: APIs, versions, licenses, data splits,
   metric definitions, resource limits, diagnostics, and failure modes.
9. In standard mode, preserve completed evidence cards before further research.
   In `time_priority_locked`, gather the bounded findings before writing; allow up
   to two focused corrections for new evidence, missing contract fields, or factual
   errors. Do not restart discovery or rewrite cosmetically after completion.
10. Standard mode permits at most six search calls, twelve distinct fetched URLs,
    and three route smokes. `time_priority_locked` permits at most four search calls,
    eight distinct fetched URLs, and two route smokes. Failed URLs count; redirect
    hops and automatic tool retries do not add distinct URLs. Stop when the decision
    questions are answered. Stop an unproductive query branch after two focused
    follow-ups add no relevant source, while continuing independent unanswered
    questions within the shared budget. At exhaustion, report missing evidence
    explicitly; a passed local smoke does not replace method/documentation sources.
    Do not repeat a passed smoke unless the environment changed. Fast mode allows
    one focused `think_tool` call for conflicting evidence or source recovery and
    does not use `write_todos`.
11. Write a readable `generated_apps/<slug>/evidence_report.md` with these headings:
   `问题与约束`, `量子适用性`, `数据可行性`, `候选路线`, `经典基线`, `反证与限制`, `来源`, `证据卡`, and
   `研究证据简报`/`Research Evidence Brief`. The final brief has exactly three subsections:
   `已验证事实`/`Verified Facts`, `预检假设`/`Preflight Hypotheses`, and
   `待由 Planner 决定`/`Planner Decisions`. The first contains only retrieved-source facts,
   observed local capability results, and Intake constraints. The second contains estimates,
   transfer assumptions, and facts requiring a local probe. The third names decisions owned by
   planning; it must not choose them for the planner. Do not label a route recommended or set an
   empirical success threshold: those require a preflight observation.

## Evidence Record

For molecular VQE without a compatible chemistry driver, first inspect the
selected SDK's algorithm reference. For Qiskit, read
`/skills/quantum-algorithm-vqe/references/qiskit.md` and its fixed-instance
reference when applicable. A bundled precomputed instance is usable only after
checking its pinned upstream molecular source, full source checksum, geometry,
basis, active space, particle sector, and energy offsets. Fetch the retained
upstream evidence and pass those exact constraints to planning. A fixed LiH
instance cannot justify arbitrary bond-length inputs. Missing driver support
never authorizes invented molecular integrals or unsourced Pauli coefficients.

The report contains:

- research questions and decision resolutions
- fetched sources with source type, publisher, dates, version scope, retrieval
  status, URL, and access time
- findings with `supports`, `contradicts`, or `limits`, confidence, scope,
  decision impact, and required verification
- datasets with license, access status, schema, size, and split risks
- classical baselines and quantum route candidates
- search provider, actual queries, provider availability, and stop reason

Each evidence card has a stable local identifier and records: decision question,
source URL, retrieved finding, applicability, limitation, and affected candidate
routes. Planner must be able to cite these cards when it selects or rejects a
route.

For QML, each route candidate records profile, variant, data domain, SDK,
official components, local capability status, applicability, failure modes,
required diagnostics, and evidence IDs. `sdk_primitive_available` means only a
minimal SDK circuit ran; only a passed `smoke_qml_route` may be reported as
`route_smoke_passed`. A metadata lead is not evidence for route selection.
Call `inspect_qml_capabilities` at most once for one environment snapshot; its
matrix covers Cqlib, Qiskit, and PennyLane. Re-run only after dependencies or
the runtime environment change.
Evidence-selected QML compares at least
two viable QML candidates when two exist. When only one route is viable or the
objective has no defensible quantum fit, explain why rather than inventing an
alternative. Dataset and classical baseline records do not pretend to be
alternate quantum routes.

Separate report statements into verified facts, source-bounded expectations, and
empirical hypotheses. A literature score, an estimated runtime, or a dataset-column
name does not establish an application acceptance threshold. Do not infer the ordering
or predictive importance of anonymized PCA components without dataset documentation or
a training-fold feature-selection experiment. For quantum-kernel candidates, identify
an exact representation-matched classical kernel baseline in addition to business
baselines. Record an exact dataset schema and data access status before suggesting a
service request schema.

Never fabricate citations, benchmark values, SDK APIs, backend capability, or availability. Simulator evidence cannot establish real-device behavior or quantum advantage.
When source discovery is unavailable and the Intake contains no explicit public
source URLs, report the evidence blocker; model recollection is not a source.

## Handoff

Target a 12,000-character report with a 16,000-character hard limit in both modes.
Keep the three-subsection Research Evidence Brief at most 6,000 characters,
preserving the complete route integration contract. Return key findings,
source URLs, implementation constraints, unresolved evidence, and candidate implications to
`planner-agent`. Do not rank candidates or emit an application recommendation;
`quantum-solution-ranking` owns the route decision. Research evidence cannot approve
implementation or delivery.
