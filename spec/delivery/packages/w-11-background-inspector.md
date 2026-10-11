---
type: "SysPane Work Package Boundary"
title: "Background inspector rendering and current-result adoption"
description: "Move admission and native composition off GTK while keeping current authority, temporal validity and truthful shutdown."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T16:38:41.448537+00:00"}
sp_id: "SP-W11-BACKGROUND-INSPECTOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSPECTOR-ADMISSION-OWNER", "SP-W11-INSPECTOR-TELEMETRY", "SP-W11-FRONTEND-PHASES", "SP-W11-TABLE-RASTER-REUSE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Background inspector rendering and current-result adoption

Implement the ordinary Linux inspector's admission/painting repair through the
existing SceneSurface, InspectorAdmission and inspector_rows. Keep the synchronous
SceneInspector interface for its existing component fixtures. The ordinary frontend
selects an explicit background factory; do not silently change direct synchronous
attachment, receive or phase-observer outcomes. This is W-11 work, not another
runtime or scheduler. The fixed maximum-input and privacy oracles remain.

## Execution and input ownership

A background task has one dedicated rendering thread. Construct, use and destroy
its SceneSurface, InspectorAdmission, native text sessions, installation witness
and image jobs there. GTK widgets, selection/expansion and requested summary stay
on their GUI owner. Service supervision, controller/client/network acquisition
and their leases continue on the existing independent owners. Do not render on
those workers or migrate GTK-bound image proxies to the rendering thread.

The immutable setup contains current authority/policy, authored/resources/topology,
provider declarations and exact frontend profile identity. The native frontend's
trusted compiled helper expectation creates a fresh worker-owned installation
witness and verified ImageJob factory. No adjacent manifest, environment or
authored path supplies that expectation. Fixture-only initializers may provide
controlled native jobs on the same owner; they grant no installed qualification.

Keep one claimed input, one latest pending complete input and one completed
result per task. A replacement pending input releases the superseded handle;
no delta merge is allowed. Each telemetry frame retains its original immutable
bytes/receipt/tick/ordinal and remains at most the existing 1-MiB wire limit.
Explicit clock maps remain bounded by sixteen provider declarations. The owner
uses actual monotonic time at job start, never the submission time as a new
native receipt. Latest replacement still produces the existing ordinal gap when
the claimed input reaches InspectorAdmission. Duplicate full states remain
duplicates. A completed result contains only owned InspectorRow strings/tree,
status and bounded provenance/time metadata, with the existing 65536-row/2-MiB
projection limits. Surface pixels and model pointers never escape the worker.
The GUI may retain one adopted frame/provenance guard while its semantic cells
remain displayed: at most four distinct bounded frame handles including that
guard, and no second retained semantic-tree copy. New publications may leave an
already displayed, still-authorized/fresh result in place until replacement;
initial adoption still requires the exact current complete frame.

The existing model, authored/resource, frame, pixel, text, chart and image budgets
remain unchanged. In-flight/pending/completed inputs may reference three distinct
bounded full frames; each result slot owns at most one bounded semantic tree.
The worker retains one normal surface/model and its existing image job. A retiring
surface and one latest replacement setup may coexist, but a second task/thread
must not start until retirement acknowledges destruction/drainage. No unbounded
publication, configuration, result or native-thread queue is introduced.

## GUI adoption and temporal meaning

The GUI supplies its current loaded profile/context on every delivery or refresh.
When inspection starts, the event-loop snapshot may precede publication of the
backend's native scope. While that scope is absent, keep the inspector pending
and do not submit or adopt native delivery. The next backend snapshot supplies
the real scope; never fabricate a native generation or relax wrong-profile closure.
Keep ordinary inspection navigation readiness pending until the first rendering
outcome is known. An initially empty pending tree is not a successful empty view
or a reported refusal. The existing quit/shutdown path remains available; known
ready/degraded/refused outcomes restore ordinary navigation.
It consumes results on ordinary event-loop ticks, independently of the 100-ms
render-request cadence. A ticket is monotonic and cannot wrap; never present an
older ticket after an adopted newer result. A newer queued request alone does
not invalidate an otherwise current result and cause endless starvation.

Adopt only the exact task/setup and current profile/policy/resource/topology
context. An active telemetry result additionally requires the same current native
scope, binding and complete frame, a still-live original native deadline, and
the original qualified clock sample no older than 250 ms at adoption. Check the
current independently sampled native clock too. Never extrapolate native
nanoseconds from GUI milliseconds. Displayed age is calculated at the qualified
clock used for that composition, within the existing 250-ms sampling contract;
adoption does not rewrite the source measurement or manufacture a newer sample.
After adoption, keep the displayed projection while its independently current
native scope/binding/lease/clock and temporal guard remain valid. The old job's
receipt deadline and sample-age limits gate initial adoption; they do not erase
an already displayed, still-current projection merely because that job ages.
The current native sample still has the unchanged 250-ms limit at every update.
Requested summaries remain frozen until another explicit request or actual
authority/lifetime/identity invalidation, as in the synchronous presenter.
For an already adopted scalar/table projection, keep its GTK cells and original
qualified age between unchanged native full frames while the temporal guard and
current native context remain valid. Do not replace native accessible objects
solely for duplicate-frame clock/age updates. A new full frame, status change or
temporal transition adopts its current projection normally. Chart projections
retain their time-dependent update path, including moving windows; any loading
image also keeps that path even if another image masks its aggregate status.
Image progress and refusal still reach presentation. Worker
admission, qualified clocks and lease maintenance continue at the bounded cadence.
Reconcile exact native keys, order and text before changing GTK expansion or
selection. If no model row changed, keep the user's current hierarchy and cursor
without redundant expand/collapse/restoration calls. Content or hierarchy changes
still use the existing keyed preservation rules; no second semantic-tree copy or
hash approximation replaces exact native row comparison.

Use native grow-only, user-resizable columns within one current presentation.
Do not force whole-column autosizing on every telemetry row update. Reset native
column measurement contexts whenever cells are erased, including policy, topology,
resource and profile retirement; derived text widths must not survive that erasure.
Keep complete accessible text, horizontal scrolling and the existing hierarchy,
selection and privacy oracles. This is an ordinary native sizing choice, not a
smaller row limit, truncated payload or relaxed accessibility timeout. GTK documents
the sizing behaviours in its [column sizing reference](https://docs.gtk.org/gtk3/enum.TreeViewColumnSizing.html)
and provides [queue_resize](https://docs.gtk.org/gtk3/method.TreeViewColumn.queue_resize.html)
to reset native measurement state. Qualify this choice against the original
installed and maximum-input cases rather than claiming the preceding AT-SPI
timeout's cause from tick timing alone.

Add a typed temporal guard from the worker-owned surface: for every used native
clock, retain its domain/sample and the earliest next freshness/window transition.
Conservatively include all current observations in its DataView and any displayed
chart point that can expire. Use the existing model freshness and chart-window
boundaries; saturate arithmetic rather than wrapping. At adoption, require a
current matching native clock at or after that sample and before any transition.
Otherwise discard and request current composition. A stale prepared "Current"
label, visibility decision or unevicted chart point cannot cross that boundary.
This metadata grants no policy or disclosure authority and exports no observation
payload or borrowed model pointer.

When current native delivery becomes unavailable, immediately clear any previously
active native presentation while requesting the existing retained-data rendering.
That retained result uses no qualified measurement tick and reports retained lease
and unknown age. It may retain only the surface's previously admitted values;
an unseen queued publication cannot become retained data. Accept it only while
the exact current profile/context and unavailable-delivery state still agree.
If current delivery becomes live again, reject an obsolete retained result and
admit the fresh complete state normally. Maintain current profile checks even
when no new frame arrives.

Policy change or topology/resource replacement immediately erases native cells,
summary and selection/expansion ownership and cancels the old task. Rebuild under
the complete new setup only after old-task drainage; coalesce at most one latest
replacement setup. A regrant requires its current policy/setup and fresh native
attachment, never adoption from a retired job. Current profile replacement keeps
the frontend's existing new-inspector rule. Refusal cannot silently fall back to
the old synchronous renderer or reuse an old result.

## Cancellation, shutdown and observation

Close drops unclaimed input and completed result immediately and marks the claimed
job obsolete. No later result can publish after cancellation. The native owner
finishes its current bounded operation, closes its surface, cancels/drains image
children, destroys input/result/surface/setup owners and then acknowledges stop.
GUI methods do no native I/O or live-worker join. Continue the event loop and
independent service shutdown until acknowledgements arrive; destruction joins
only after that normal acknowledgement. Emergency destruction still closes/joins
rather than detaching. A stuck native thread remains stopping, never "reaped" or
a fabricated bounded-shutdown pass. Native fixtures must preserve that failure
and the final process/child lifetime evidence.

Existing phase observers are synchronous borrows. Never retain or invoke one on
the worker. Append a GUI adoption phase (17) to the fixture journal vocabulary,
preserving 1--16 and the old synchronous paint/presentation meanings. Background
GUI observations measure queue/adoption/presentation work; worker admission and
painting durations belong to owned completion metadata, not overlapping GUI
spans. Keep strict journal limits/refusal behavior and preserve earlier journals.
Updating the diagnostic decoder's known vocabulary changes no timing acceptance
limit, table case, expected value, erasure requirement or observer authority.

## Executable completion and continuation

Before enabling the frontend path, run controlled real-worker tests for exact
scalar/table/chart output, latest-slot coalescing and gaps, ticket/context refusal,
lease/clock/freshness/window expiry, policy/topology retirement, cancellation during
claimed work, no stale publication, input destruction acknowledgement and native
image-child drain. Expected results come from literal prior cases and independent
temporal examples, never regenerated candidate output. Hold a worker through an
explicit fixture barrier to prove GUI/service progress and honest stopping.

Run the unchanged native inspector, installed telemetry/image/topology and
authored-limit families, fixed raster/role/frame/erasure checks and selected shared
checks. Then run the original ordinary maximum-table family and its complete
phase diagnostic with the fixed 100-ms GUI/200-ms erasure bounds. Preserve all
failures and exact sources/binaries/environments. A passing diagnostic does not
erase an ordinary failure. Continue maximum GTK chart/mixed and actual installed
history accumulation, human usability, desktop/lifecycle and all five full editions.
