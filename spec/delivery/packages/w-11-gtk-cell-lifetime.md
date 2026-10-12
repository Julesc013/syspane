---
type: "SysPane Work Package Boundary"
title: "GTK text-cell cache lifetime ownership"
description: "Clear cached disclosure before collapse/removal retires a cell; preserve standard lifecycle events."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T22:50:00+00:00"}
sp_id: "SP-W11-GTK-CELL-LIFETIME"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-GTK-HISTORY-LIMITS", "SP-ACCESSIBILITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# GTK text-cell cache lifetime ownership

Continue W-11 from 1e7f324f. The preceding standalone experiment leaves collapsed
and retired local text/name/layout readable under stock cells. Its expanded scrub
also fails timing; all strict external empty-response cases remain failed.
Preserve those checkpoints, collectors, errors and original performance oracles.

## Fixed boundary

Introduce an internal Linux text renderer and accessible subtype using public GTK
class-init and widget-unset hooks. GTK owns each cell's lifetime and calls its
unset hook when collapse, removal, model replacement or destruction retires it.
There is no application registry, copied row cache, global scene pointer or worker
access. Existing GTK/SceneInspector thread ownership and all resource limits apply.

Before forwarding the inherited widget-unset operation, acquire the cell's shared
renderer, save its text, temporarily set empty text, and invoke the inherited
public text-cache update slot with emit_signal false. Restore the shared renderer's
exact prior text, including null, and release temporary references/strings. This
erases the retired cell's text/count/name-derived value and cached word/layout
content while preserving other active cells. Forward the normal inherited unset
hook exactly once; retain native defunct/model/visible-data events. Do not block
signals, touch private toolkit fields, alter the accessibility tree, recreate the
root or detach as a performance substitute. Cells use derived names; product code
does not install explicit per-cell names. Verify that invariant and held names.

The helper owns no additional per-row storage. Place its internal declaration and
implementation in source/interfaces/scene_inspector_text_linux.hpp/.cpp, with one
declared scene-inspector component source and ordinary GTK dependency. First use
it only in a native lifetime probe; integrate both real inspector columns after
the semantic gate succeeds. The integration changes no row values, keys, policy,
source, history, selection, interface version or renderer cadence.

## Evidence and acceptance

Reuse the preceding exact 3172-row, 6344-cell canaries and fresh rows in a new
lifetime mode. Hold every original cell; compare the 66 retired-root cells after
retirement, all 6276 chart children after collapse, every cell after erase and
again after fresh regrant. All retired native text/name/count/word values must be
empty. The expanded live chart remains exact; the collapsed chart root remains
exact. This proves shared-renderer restoration instead of merely erasing all data.

Keep the original strict empty-response experiment unchanged and unqualified.
The separate lifecycle test recognizes two distinct wire outcomes: a successful
empty reply, or verified withdrawal of the exact previously supported object.
Withdrawal requires the precise UnknownObject error for the retained bus/path,
the same live application/root, exact fresh rows and normal exit. Timeout, service
loss, generic errors, missing initial support or rebound old paths fail. Never
map errors to empty text or use an SDK default as a successful reply. The literal
oracle is settled from lifecycle meaning, not regenerated from candidate output.

Run native.GTK-CELL-LIFETIME as two fresh expanded/collapsed children, each bounded
by the existing 120 seconds, family 250 seconds. Keep the same input/output/observer
caps and lossless wire journals. Record all callback/mutation times and failures.
This semantic gate does not qualify GUI performance; no 100-ms GUI/200-ms erasure
limit, timing sample or original case is changed or excluded. A collapsed/removed
cell is allowed to be withdrawn, not required to remain a live object forever.

Before product integration, pass the lifetime oracle and component graph checks.
After integration, run the same lifetime probe plus real SceneInspector/model,
renderer/background, receiver/frame-boundary and held-erasure regressions. Record
source-bound artifacts and declared installed smoke/harness identities if changed.
Preserve every preceding failure and blocked qualification. General GTK history
update/erase performance, maximum-policy cases, installed/human/desktop integration
and all five complete release editions remain required.

Add native.INSPECTOR-CELL-LIFETIME in the existing inspector test executable,
with a private Xvfb and 25-second bound. Feed three actual complete chart packets
at generations 1..3 and measurement 0/1/2 ms, values 10/11/12, through the public
receiver/delivery boundary. Inspect both real column renderers and all eight text
objects. Collapse the root: six held child objects become empty/defunct while
the root remains current. Deny inspector at revision 8: all eight old objects
become empty. Regrant 9 with scope (11,5), value 99/generation 4/3 ms: one fresh
start point, no old cache value. Close and destroy the real widget while holding
old/fresh text objects, then check every full/name/count/word getter. Each native
cell receives exactly one ordinary defunct transition; no signal is suppressed.
This small real-component test complements the complete standalone lifetime
cohorts; it does not replace maximum/history/policy/installed performance tests.

Preserve the first real-inspector fixture failure: it incorrectly required an
allocated empty value from the optional modern native word slot. The pinned GTK
text cell does not implement that slot; ATK documents null and offsets -1/-1 when
no implementation exists. Verify that absence before retirement, record it as
unsupported and require the same explicit result afterward. Do not count it as a
successful empty-data read. Full text/count/name and all three implemented legacy
word/layout slots remain mandatory empty after retirement. Wire GetStringAtOffset
is checked separately with its real reply/error; native absence is not a wire pass.
Primary definitions: GTK 3.24.41 gtktextcellaccessible.c and AT-SPI 2.52.0
atk/atktext.c, with the original failed fixture/source retained for review.

## Avoid redundant cache recreation

The integrated baseline passes both lifetime cohorts and real-widget erasure,
but the unchanged live-table POLICY case records 106937 us of GUI work against
100000 us; retain its source and complete report. Its erasure observation is
169.490 ms against 200 ms. This is a failure, not evidence of its cause.

Before acquiring/mutating the renderer, test whether the existing native cache is
already empty using public ATK reads: non-null empty derived name, zero character
count, allocated empty full text and allocated empty values from all three
implemented legacy word/layout getters at offset zero. Require every condition.
If the name is null, do not query potentially uninitialized layout getters;
perform the original refresh. A missing getter, null read or nonempty value also
requires refresh. Free every temporary string. No cache pointer, copied row state
or application registry is introduced. Always forward the inherited widget-unset
hook once, including when refresh is unnecessary.

The pinned public cache-update slot recreates a Pango layout even when cached
text is already empty. This guard avoids that redundant work after normal live
model blanking while still refreshing collapsed/retired values. Verify both
paths with the existing complete lifetime cohorts and actual widget test; rerun
the original table, erasure, history/renderer and installed suites. Preserve the
baseline failure even if the new candidate passes. Do not infer a general timing
qualification or proven causal attribution from a later passing run.
Primary source: https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtktextcellaccessible.c

## Bounded retirement-cost experiment

Continue from 07b7b26e. Product privacy passes, but ordinary maximum chart/mixed
work reaches 718584/534685 us; complete standalone expanded erase is 896274 us
and collapsed retirement 309696 us. Preserve every source-bound failure.

Use the same exact 3172 rows, 6344 held native/wire cells, cohorts, fresh rows,
seven wire methods and lifecycle oracle. Add three test-only candidates:
lifetime-profile keeps the original blank/clear sequence; lifetime-remove clears
the store directly; lifetime-detach detaches the model, clears the store and
reattaches the same empty store. All use the current product text renderer. Keep
retirement/collapse identical so surviving active chart values remain an oracle.
No product clear/reconcile behavior changes until a candidate passes privacy.

In this owned prototype process only, install a public GtkCellAccessibleClass
cache-update wrapper on the text-cell class before any fixture cell exists.
Forward the original slot exactly once with the original cell/signal argument.
During each synchronous command record call counts, inclusive microseconds,
maximum call time, signal/quiet counts and maximum nesting depth. Keep the complete
original callback and mutation clocks, including instrumentation. Do not sum nested
durations as disjoint work. At most 1000000 calls/depth 32/120000000 inclusive us
per command; record a failed experiment on overflow. Restore the original slot
after owned widget/cell destruction. There is no production instrumentation,
private toolkit access, per-row copied cache or external process modification.

Hold bounded per-cell transition counters in the fixture. Retired cells have one
normal defunct transition; live chart cells remain live until their own retirement.
After erase/regrant every original cell remains empty and has exactly one defunct
transition. Preserve normal model/visible-data events; block no signal. The two
existing cohort shapes and independent raw wire journals still enforce exact live
and fresh rows, old-path non-reuse, verified withdrawal and actual normal exit.

Run native.GTK-RETIREMENT-PROFILE as six fresh children, 120 seconds each and a
750-second family, with unchanged input/reply/stdout/stderr/observer caps. A
semantic pass does not qualify the 100-ms GUI/200-ms erasure limits. Select a
product change only from measured results and passing complete privacy; then
rerun the actual inspector/renderer/erasure/installed and ordinary maximum suites.

The first six cases pass lifetime with depth one. Expanded blank/remove/detach
callbacks take 828374/526127/308786 us. Quiet public cache work is only 38852/34495
us for remove/detach; collapsed retirement is about 307–315 ms with 33 ms of quiet
cache work. Do not attribute the unmeasured remainder to Pango or notifications
without another controlled observation.

Add native.GTK-RETIREMENT-BATCH with two fresh lifetime-bulk cohorts, 120-second
children/250-second family and unchanged caps. Before each retire/erase command,
freeze property notifications on the two owned shared renderers; thaw both before
reply and include the whole scope in the original callback clock. Erase directly
clears the store. Count actual renderer notify::text emissions in every profiled
variant. Public property writes/cache reads remain immediate. This is bounded
notification coalescing on owned renderers, not signal blocking on native cells,
the tree, model or root. Preserve every normal defunct/model/visible-data event,
exact active/fresh values and held-cache/wire checks. This narrow experiment is
an explicit exception to the earlier no-signal-blocking shorthand for renderer
property batching; it permits no suppression of accessibility lifecycle events.
Select product batching only after the full cohort gate, with exception-safe
thaw and exact renderer ownership closed before implementation.

## Complete projection retirement

The batch experiment passes lifetime but still takes 486891 us for expanded
removal and 322404 us for collapsed retirement. Do not claim notifications caused
or solved the delay. Select the earlier lifetime-detach candidate as a measured
increment: it passes every retained native/wire/lifecycle check and reduces
expanded erasure to 308786 us without batching. This is not timing qualification.

For complete native projection retirement only, clear the requested summary,
selection/row/expansion bookkeeping, detach the existing tree model, clear the
owned store while disconnected and reattach that same empty store. Keep the same
tree/root, columns, renderers and model owner; never create a replacement widget
or copy. Empty already-retired stores need no model reset. The existing text-cell
unset hook must finish physical text/name/count/layout erasure before each normal
defunct event; this proven erasure is required and detachment alone is forbidden.
This explicitly permits complete projection detachment after the lifetime gate,
superseding the earlier shorthand ban on detachment as a substitute for erasure.

Separate native projection cleanup from admission/adopted-result cleanup. Explicit
clear/shutdown still resets admission and adopted input. Presenting an empty
qualified projection retires native rows/summary/selection/expansion but preserves
the current result, status, ticket and renderer acknowledgement. Nonempty and
partial reconciliation remains unchanged. Preserve GTK model/visible-data events,
one normal defunct transition per cell, current/fresh values, selection semantics
and producer/renderer closure. No renderer-property batching enters the product.
Run the actual lifetime, model/frame/renderer/background, erasure, installed and
table cases plus ordinary maximum history; keep all original failures and limits.

## Inherited native retirement measurement

Continue from 98ac09e5. Actual maximum chart/mixed work is 296850/315191 us after
complete projection cleanup. Each case completes content/recovery/owner exit and
has one over-limit tick. Preserve both failures and the original 100/200-ms gates.

Add native.GTK-RETIREMENT-UNSET as two fresh lifetime-unset cohorts with the same
detachment sequence and complete retained-cell/live/fresh/wire/lifecycle oracles.
In the owned prototype only, wrap the public inherited GtkAccessibleClass
widget-unset slot on the text-cell class before fixture cells exist. Forward it
exactly once with the original object and preserve all defunct/model/visible-data
events. Restore it after owned teardown. Record inclusive calls/time/max time/depth
independently from the cache-update slot and full callback clock. These are nested
component clocks, not disjoint durations to sum. The same one-million calls,
depth 32, 120-million inclusive microseconds, GTK-owner and output caps apply.
Use 120-second children/250-second family; never relax or exclude original times.
No product source, private fields, signal suppression or foreign process changes
are admitted by this instrumentation. The result must distinguish measured native
unset work from the still-unmeasured remainder before selecting the next repair.

The first expanded collection fails its initial SDK Text-interface lookup before
any retirement command; the collapsed case passes and measures 128923 us in the
inherited unset slot, 31864 us in cache slots and 313454 us in complete retirement.
Preserve both exact sources/reports. Add bounded initial lookup context: attempted
row/column, retained reference, completed initial-cell count, live-process state
and actual raw text/name/count replies or explicit errors for that suspect object.
The same initial interface/data assertions still decide the case. This is
diagnostic collection, not timeout extension, retry-to-pass or changed acceptance.

The diagnostic collector's next cases pass the unchanged oracle. Expanded erase
records 312091 us total, 128673 us inherited unset and 31917 us public cache time;
collapsed retirement is 313587/128799/31964 us respectively. Preserve the first
initial lookup failure; the later pass does not prove its cause.

Extend this test-owned instrumentation with the public GObjectClass property-
notification dispatch slot on the same text-cell class. Forward every original
property specification once. For dispatches including widget, record calls,
inclusive time, maximum call time and nesting, with the existing count/time/depth/
GTK-owner limits. Keep full callback clocks and all normal notifications. Restore
the original slot after owned teardown. No property is blocked, deferred or
changed. These clocks locate widget-notification dispatch outside inherited unset;
they do not authorize a product notification change or prove the unmeasured cost.

The dispatch cases pass complete lifecycle/wire checks. Expanded erase is 307603
us, with 126475 us in inherited unset, 123578 us in widget-property dispatch and
31211 us in cache updates. Keep the complete clocks and treat the remaining time
as unmeasured. No native event may be suppressed to fit the budget.

Add native.GTK-UNSET-NO-BRIDGE as a diagnostic native-only control. Use the same
prototype, 3172 rows/6344 native holds/cohorts/commands, exact one-defunct checks
and cache getters, with NO_AT_BRIDGE=1 and no external wire qualification. Prime
full text/name/count/legacy and modern word getters before readiness so native
word-layout work is not silently omitted relative to the external initial reads.
Mark priming explicitly in readiness. Keep input/output limits and full callback
clocks. Use fresh private Xvfb, two bounded 15-second children and 40-second family.
Record actual source/artifact/runtime identity, native values and normal exit;
do not call this accessibility, GUI or edition qualification. This control tests
the relationship with bridge presence; it cannot authorize disabling the bridge
in the product or rewriting either 100/200-ms gate.

The primed native-only control passes: expanded erase is 35442 us with 2253 us
inherited unset and 2551 us widget dispatch; collapsed retirement is 32070 us.
This local comparison does not qualify the enabled bridge or prove every timing
cause. Keep the bridge enabled in every product/qualification path.

Add a synchronous deferred-notification prototype, native.GTK-RETIREMENT-DEFERRED,
with the same two complete lifetime cohorts/120-second children/250-second family.
During retirement only, copy the original inherited-unset/property-dispatch calls
into an owned FIFO; retain the exact cell and parent/root plus every parameter
specification. Physically clear cache data and perform the public model operation
before invoking queued notifications. Check all original native caches before
queue drainage as well as after it. Forward every original call exactly once in
order, with no coalescing/suppression; release every temporary reference afterward.
The window/root stays owned throughout this synchronous control. Queue at most
16384 operations and property arrays at most 8 entries; overflow fails rather
than truncating or dropping an event. Keep the original complete command clock,
record preparation/queue size/drain time and bounded 64-operation drain slices.
Do not label slices as GUI callbacks: this control remains synchronous and is
not a performance pass. Test late original callbacks against real native events,
held data, exact active/fresh rows and actual wire withdrawal before proposing
any asynchronous production ownership, shutdown or observer-lifetime contract.
