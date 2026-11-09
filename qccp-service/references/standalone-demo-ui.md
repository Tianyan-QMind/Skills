# Standalone Local Demo UI

This reference applies only to the standalone FastAPI surface of `runnable_app`.
It turns the `tianyan-ui-suite` visual specification into a browser
page served by FastAPI. It does not introduce Vue, Element Plus, qccp-web
routes, stores, or CDN dependencies.

## Relationship to tianyan-ui-suite

- `tianyan-ui-suite` is the visual authority: use its exact color, type, spacing, and
  radius tokens.
- Show explicit loading, empty, error, ready, and submit-pending states; keep a
  vertical, task-first structure; bind the page to a real API contract.
- TianYan UI 2.0 is the product-design authority. Local standalone HTML maps
  the same tokens and feedback rules into page-local CSS variables and reusable
  classes; it does not import Vue, Tailwind, Element Plus, qccp routes, or qccp
  stores.
- This file owns the HTML-specific implementation contract below.

## Product surface

Build the local page as a polished algorithm application showcase. It should
look like a deployable TianYan quantum-app page: light background, white panels,
blue token accents, a domain-specific algorithm/result visual area, compact
controls placed near the data they affect, and an explicit method explanation.
Do not use a dark sci-fi theme, gradient heading, glow shadow, glass card,
marketing hero, raw endpoint list, JSON-only result pane, or form-first
interface.

Use the tianyan-ui-suite product rules rather than copying one fixed template. The page
layout should be chosen from the application domain: image recognition pages
should foreground images and recognition process; forecasting pages should
foreground input/output series; optimization pages should foreground candidate
selection and recommendation; circuit-centric pages should foreground circuit or
operation evidence.

UI 2.0 product requirements:

- Every submit or inference action must show loading and then a success/failure
  state. Use only toast, loading, and status tags as feedback forms.
- Every chart, metric, prediction, or result block must display a timestamp,
  data source, model artifact state, or run status label.
- Keep the core path within three steps: choose or inspect input -> run inference
  -> read result/explanation.
- Use page-local reusable classes for buttons, inputs, tabs, tags, cards, toast,
  and status dots. Do not hand-style each element separately.

## Required information architecture

Use one Chinese-first page with these sections:

1. A compact application header: name, one-sentence purpose, and a small
   service state tag. Do not use a marketing hero, gradient, mascot, decorative
   illustration, or a row of engineering metadata badges. SDK names, local
   simulator mode, qubit count, framework/library names, and execution backend
   details are not first-viewport chips or cards unless the user explicitly asks
   for an engineering console.
2. A short method summary band focused on user-visible evidence: data source,
   selected algorithm route in plain language, model artifact state, and the
   verified training or sample scale. Place simulator/TianYan status, SDK, qubit
   count, and dependency details in the later method/limitation section or
   documentation.
3. A first-viewport algorithm showcase stage with
   `data-testid="algorithm-showcase"`. This is the primary visual focus and
   must be larger than the input controls. It renders the current prediction,
   score distribution, forecast curve, optimization/circuit summary, or other
   domain-specific model output from `/api/infer` or declared static evidence.
4. A service-status strip with `data-testid="service-status"`. It calls
   `GET /api/health` on page load and shows loading, ready, degraded, and
   unavailable states using text and tianyan-ui-suite state colors.
5. An operation dock: model or route selector only when the API exposes one;
   otherwise show the fixed route as read-only metadata. Inputs must be derived
   from the declared request schema, include validation messages, and use
   Chinese labels. Keep this dock compact; it supports the showcase and must not
   become the whole page.
6. A single primary action with `data-testid="infer-action"`. It calls the
   relative `POST /api/infer` endpoint, disables while pending, and never calls
   training code.
7. A results explanation panel with `data-testid="infer-result"`. It renders only API
   response values or declared static artifacts, and distinguishes an empty
   result from an error. Charts require a stable-height container and local
   assets; do not invent result data.
8. A traceable quantum circuit panel with `data-testid="quantum-circuit"`, a
   `data-circuit-source` value of `api`, `model-artifact`, or `declared-static`,
   and at least one `data-testid="quantum-wire"`. Prefer API-returned gates and
   wires. When the API does not expose a per-run trace, render the verified
   feature-map/ansatz topology from the adapter or plan and label it as a model
   structure diagram, never as live execution. The circuit remains available on
   mobile through responsive layout or horizontal scrolling.
9. A method flow with `data-testid="method-flow"`: concise visual explanation
   from public data to preprocessing, quantum encoding/model/search, classical
   decoding, and result interpretation. It can be a diagram, step rail, card
   sequence, or annotated evidence area. Use readable Chinese step labels and
   concrete evidence/state text; do not make unexplained single-letter glyphs
   such as D/S/Q/K/C the main communication.
10. A compact method/limitation section sourced from the application evidence,
   including simulator versus TianYan status, SDK, qubit count, dependency
   status, and scientific limits when relevant. This section supports trust but
   must not compete with the main result.

Product hierarchy rules:

- The first viewport is for the user-facing task: domain input or selection,
  one primary action, main result, and a result explanation. Internal
  implementation metadata belongs below the fold or in documentation.
- For classification apps, the main result should include the selected label,
  confidence or ranking, and a compact probability/comparison visualization.
  Classical baseline comparison is secondary evidence unless the requested
  product is specifically an algorithm-comparison app.
- For forecasting apps, the first viewport should emphasize the input range,
  historical series, predicted series, and uncertainty/status.
- For optimization apps, the first viewport should emphasize candidate
  selection, constraints, recommendation, and objective value.
- Avoid oversized blank result cards. Each first-viewport panel needs a
  meaningful visualization, current result, compact empty state, or clearly
  labeled pending state with stable dimensions.
- Time priority may simplify decorative detail, but it must not remove the
  algorithm showcase, API-derived result visual, method flow, or quantum circuit.

## Standalone implementation rules

- Use `lang="zh-CN"`, a page-local stylesheet, and page-local JavaScript.
- Use only tianyan-ui-suite colors and the 4px/6px/8px radius scale. No gradients,
  emoji, external images, external fonts, external CDNs, or decorative
  animation.
- Use the light qccp palette by default: `#F4F7FC` page background, `#FFFFFF`
  panels, `#DCE0EB` dividers, `#020814` titles, `#41464F` subtitles, and
  `#1664FF` primary actions. Dark themes require an explicit user requirement.
- Success toast uses `#34C759`; card-bottom text actions use `#7A8391` and hover
  to `#1664FF`. Explicit dark mode may use only `#0A0E1A`, `#131A2E`,
  `#2A3457`, `#E8EDFF`, and `#9AA6CF`.
- Use relative `/api/...` and `/static/...` paths only. Direct `file://`
  opening is unsupported by design; FastAPI owns the page and API origin.
- Define a small CSS variable block from tianyan-ui-suite tokens and reuse classes for
  panels, tags, buttons, inputs, status text, and metric rows. Do not scatter
  one-off colors or radii.
- Page-local CSS must expand `shadow-sm` as exactly
  `box-shadow: 0 1px 3px rgba(0,0,0,0.06)`. The only other rgba exception is
  loading-spin `/40`, written as `rgba(255,255,255,0.4)`. Do not replace the
  shadow color with a hex token or use a different geometry/alpha; the verifier
  checks these canonical semantic exceptions.
- Keep a constrained content width, responsive single-column flow, and stable
  dimensions for status, action, and result areas. The mobile layout must not
  hide the operation action or result content.
- Desktop may use a two-column first viewport only when the larger column is
  the algorithm showcase and the smaller column is the operation dock. Mobile
  collapses to showcase first, then operation.
- Record every external static file under `local_demo.static_assets`; a
  self-contained `index.html` uses an empty list.

## Minimum browser test contract

The browser smoke test must load `/`, wait for the status selector, confirm the
algorithm showcase, quantum circuit, quantum wire, and method flow exist,
perform one known valid request through the action selector, and assert an
API-derived result at the result selector. It must fail on console errors,
failed API requests, missing static assets, a missing/unknown circuit source,
or a page that only works through `file://`.

Every browser assertion must identify the failed stage and retain console
errors, page errors, failed request details, and the last reached selector. If
the API and static-DOM stages already passed, a transient browser launch,
navigation, or selector-readiness failure may discard the disposable
page/context and retry only the browser stage once. Deterministic contract
failures are not retried, and a browser-only retry must never rerun data
acquisition, training, or evaluation.

The verifier's `run_app_check` performs a qccp standalone preflight before the
application smoke test. The preflight rejects gradients, decorative shadows,
non-token colors, absolute API URLs, external CDNs, emoji, generic English demo
copy, missing showcase/method-flow/status/action/result test ids, wrong `lang`,
missing circuit evidence, and malformed `local_demo.static_assets`.

The preflight is intentionally a coarse guard. It does not replace visual QA,
but it prevents runnable apps from passing delivery with raw API forms, non-qccp
colors, missing algorithm showcase, or missing method-flow evidence.
