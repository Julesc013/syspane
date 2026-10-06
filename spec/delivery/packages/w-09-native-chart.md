---
type: "SysPane Work Package"
title: "Policy-owned native charts"
description: "Exact numeric geometry and every-publication history feed with native pixels and accessibility erasure."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T23:15:00Z"}
sp_id: "SP-W09-NATIVE-CHART"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-CHART-HISTORY", "SP-W09-SCENE-SURFACE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned native charts

Extend SceneSurface with scene 0.3 chart widgets. Preserve old schemas and the
existing singleton binding, measured-history, layout and policy contracts. Scene
0.2 charts remain unsupported because they have no authored content. Images and
full native accessibility navigation remain separate required capabilities.

## Exact geometry

The portable plot function consumes a bounded history borrow, its measured horizon,
window_ms, axis and interpolation, plus device dimensions 2..2048 per axis. Reject
nonfinite values, inconsistent numeric types, nonincreasing timestamps, timestamps
outside the inclusive window, a missing horizon with nonempty points, more than
4096 points or an invalid first-point continuity flag. It never changes history.

Auto range uses the exact minimum/maximum retained values, optionally extended to
include zero. With no points the auto range is unavailable. A constant auto range
places each value at floor((height-1)/2), with equal exact range labels. Fixed bounds
use the authored finite binary64 interpretation already used by scene validation;
they must be strictly increasing. No implicit margin, unit conversion or rounding
of uint64 into binary64 occurs. Values outside fixed bounds saturate at the nearest
edge and increment an explicit clipped-sample count.

For nonconstant ranges, y is height-1 minus round-half-up of
(value-minimum)*(height-1)/(maximum-minimum). Evaluate that ratio exactly for the
finite binary64/uint64 operands, including subnormals, opposite finite extremes,
and adjacent integers above 2^53. For x, use round-half-up of
(measured-start)*(width-1)/(horizon-start), where start=max(0,horizon-window_ns).
A zero-duration initial horizon places its sole point at width-1. Never extrapolate
beyond the last point or retain a hidden point outside the history window.

Paint every point. When joins_previous is true, linear joins the two quantized
points; step paints a horizontal leg at the previous y followed by a vertical leg
at the current x. Each leg has N=max(abs(dx),abs(dy)); for integer i from 0 through
N, paint round-half-up((a*(N-i)+b*i)/N) independently for x and y. A zero-length
leg paints its endpoint once. Use one device-pixel stroke. Breaks never acquire a
connecting leg. Shared columns preserve all extrema; no sample decimation occurs.
The bounded pixel mask is the union of this coverage, so overlaps apply color once.
This is the defined device-resolution reduction, not an untested heuristic.

Count one work step per visited raster point, including repeated coverage. Reject
before allocating the mask when required work exceeds 1048576 for one chart or
the caller's remaining scene budget. A scene allows 4194304 plot steps. Output
mask pixels count toward the existing temporary construction-pixel budget.

## Native size, appearance and accessible content

The initial graph extent is ceil(320*display_scale) by ceil(120*display_scale)
device pixels. These are minimum/preferred graph dimensions, separate from the
authored layout box. Use existing unwrapped readable text and whole-scene overflow
behavior. The text block is the scalar title/value/status block followed by:

1. `Samples N | Segments S`, optionally ` | Capacity truncated`, ` | Gap pending`.
2. `Range minimum .. maximum`, or `Range unavailable`; append the reported unit
   unless empty or 1, and ` | Clipped N` when the fixed range clips any points.
3. `Window N ms | linear` or `Window N ms | step`.

Below the native text block, leave ceil(4*scale) pixels, then the graph at x=0.
Widget width is max(text width, graph width); height ends at the graph bottom.
Fill the authored/contrast background once. Text and the curve use effective
foreground; the one-pixel graph border uses muted (effective foreground in high
contrast). Draw the mask over the border with the existing premultiplied integer
OVER rule. Keep native text glyph/size and scene construction limits.

Accessible text contains the scalar's full status axes, the same three summary
lines, then `Point nanoseconds: exact-value; generation N; start` or `; join` for
each retained point in order. All strings and identities count toward the existing
262144-byte frame budget; exceeding it selects the whole-scene alternative. Keep
typed sample/segment counts and graph rectangle in the synchronous SurfaceFrame.
No borrowed history pointer may escape. This gives exact point content through the
existing native name boundary; full chart navigation/actions remain a later gate.

## One history and presentation owner

SceneSurface owns one ChartHistory per unchanged chart binding. Admit at most 32
charts and a sum of max_points no greater than 16384. Reserve the history package's
logical payload accounting before creating them; it is below 1 MiB at these bounds.
Repainting clears only the prepared frame. Policy changes, scene/resource/binding
replacement, close, native-clear failure and owner clock faults clear histories.
Both current desktop/accessibility permission and explicit operational history
disclosure are required. Resource capability denial also erases retained samples.
After a policy change, fresh attachment and complete state are required, including
when only history permission changed. A chart/history denial restricts the whole
scene, with no labels, points, counts, accessible names or pixels disclosed.

receive accepts an optional map of current qualified ticks for other providers;
the mandatory receiving-provider tick overrides its map entry. After successful
admission and before returning, resolve every chart whose binding routes through
that producer against the complete relevant current context and feed its history.
Direct bindings route by exact producer; selectors/pins route by declared scope and
entity type. An unrelated producer publication cannot clear another chart merely
because its current tick was not supplied. Paint resolves again for expiry/status and duplicate
suppression. Never reuse an old tick as another producer's current clock. Missing
selector context yields the existing incomplete binding and erased history. A
transport gap, disconnect, failed current delivery or lease lapse marks affected
history discontinuous before any later successful sample; stale attachment callbacks
cannot alter a successor history. Attachment invalidates affected history, even in
the same epoch. An expired attachment stays closed; heartbeat cannot revive it.
Reattachment and full state reset the affected history before further samples.

Bound history allocation and resource authorization before any retention. If that
preparation fails, erase histories and select the same restricted/alternative
outcome at paint; valid non-chart telemetry admission remains usable. Chart faults
must remain visible as `Chart conflict`, `Chart clock fault`, `Chart invalid`,
`Chart unsupported` or `Chart clock unknown` in the text/accessible summary rather
than silently looking like a healthy empty graph. Current scalar status still applies.

## Acceptance and continuation

Archive contract and independent expected geometry before implementation. Compare
portable numeric projection with exact Python Fraction expectations, including
uint64 boundaries and finite binary64 extremes/subnormals. Fixed masks distinguish
linear/step, duplicate columns, point-only segments, clipping and resource rejection.
Preserve old scene/content tests. Native component cases cover multiple deliveries
before paint, identity/gap/expiry/reconnect, resource/history denial, regrant, budget
and native-clear failure, with actual DataView admission.

Extend the owned Xvfb/GTK/AT-SPI observer with a public synthetic chart trace and
independently composed expected pixels and complete accessible text. Keep the
200 ms post-command bound and deliberate old-pixel/old-name controls. The synthetic
producer clock is controlled by the fixture; observation deadlines use real monotonic
time. This experiment does not qualify an installed desktop or actual live collector.
Use ordinary commands on the three development profiles, source-bound evidence,
preserved failures and updated handoff. W-09 and all full release editions stay open.
