---
type: "SysPane Work Package"
title: "Deterministic portable scene layout"
description: "Resolve admitted scene geometry from explicit topology and native readable metrics without mutating authored state."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T19:10:00Z"}
sp_id: "SP-W09-LAYOUT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RENDERING", "SP-SCENE", "SP-BINDINGS", "SP-W08-AUTHORED"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Deterministic portable scene layout

Continue W-09 under the complete release instruction. Implement one shared engine
in source/scene, used by future native renderers and direct editors. Preserve scene
0.2 and layout 0.1 identities and every admitted layout kind. This package closes
geometry and fallback meaning; it does not establish text shaping, raster output,
telemetry binding evaluation, direct manipulation or visible activation.

## Inputs and units

Resolve a validated scene, explicit host topology and premeasured readable leaf
metrics. No filesystem, telemetry acquisition, font lookup or native calls occur
inside resolution. The caller supplies a complete immutable input snapshot; no
cache survives a call. Native metric identity/versioning belongs to its later
adapter. Every leaf has exactly one minimum/preferred size pair; groups have none.
Minimum size includes the native adapter's mandatory status/label affordances.

All typed geometry uses signed 64-bit units of 1/64 DIP. Authored positions round
to nearest unit, ties away from zero; fixed/canvas sizes and gaps round upward.
Flow minima round upward, maxima downward, preferred sizes to nearest. Native
metric minima/preferred sizes are positive, ordered and at most 32768 DIP.
Use integer arithmetic after authored decoding, with no platform float layout.
Keep authored documents byte/value unchanged and retain their scene ID/revision.

Topology contains one to sixteen uniquely identified displays, each with bounds,
contained work area, nonnegative safe insets, at most sixteen exclusion rectangles,
an explicit pixel origin and rational scale. Bounds/work dimensions are positive
and at most 32768 DIP; origins are within +/-100000 DIP. Exclusions are positive
and contained in display bounds, then intersected with the safe work area. Insets
may exhaust that area and produce a no-region diagnostic. Pixel origins are within
+/-16777216 pixels. Scale numerator/denominator are integers 1..16 and their ratio
is between 1/4 and 8. No monitor is selected by enumeration index.

Up to 256 unique role names map to at most sixteen distinct local IDs each. Consider
only currently present IDs: one is resolved, zero is missing, multiple ambiguous.
A missing/ambiguous role or absent local ID uses the explicitly named present
fallback display with a per-widget diagnostic. Every child must resolve to its
root's display; a conflicting assignment rejects the projection atomically with
layout.display_conflict. Authored ownership/assignments never change.

## Safe region and responsive selection

Inset the native work area. From all axis-aligned rectangles inside it that avoid
the clipped exclusions, choose maximum area, then smallest y, smallest x, widest,
then tallest. Find this exactly using pairs of exclusion/work-area y edges and
merged blocking x intervals; touching edges do not overlap. Input exclusion order
cannot change the answer. Empty safe space has zero visible extent, a no-region
diagnostic and requires an alternative presentation; it never grants unsafe space.

All breakpoints in a root subtree use the width of that display's chosen safe
region in DIP, including equality at a threshold. Select the highest applicable
alternative, otherwise base. This is a display-viewport query, independent of
subsequent child allocation: no iterative resize/variant feedback is allowed.

## Measurement and placement

Emit nodes in root/child preorder, independent of the widgets array's order.
Group decorations consume no implicit padding in this geometry contract. Native
adapters needing padding/header space require an explicit future contract.

Flow leaf minimum is max(authored minimum, native minimum). Its effective maximum
is at least that readable minimum; exceeding an authored maximum emits
layout.constraint. Preferred is max(authored preferred, native preferred), clamped
to the effective min/max. Fixed leaf sizes expand only enough to satisfy native
minimum, with layout.fixed_size when expanded. Fixed group sizes are preserved.
Canvas sizes are fixed. Empty auto containers have zero intrinsic minimum/preferred.

Fixed children are positioned relative to the parent origin, remain outside flow
allocation and never consume stack/grid slots. Fixed roots are relative to the
safe display origin. Auto stack/grid roots fill that safe region. Canvas roots use
their authored size at its origin. Flow roots size to available space and apply
their anchor on both axes. If content exceeds available size, leading alignment
wins so a negative centering offset cannot hide its start.

Stack intrinsic main size sums in-flow child sizes plus gaps; intrinsic cross size
is their maximum. Also include positive fixed-child extents on either axis. A fixed
group is a bounded canvas. Canvas/fixed groups place nonfixed children in an implicit
vertical zero-gap stack. Nested auto groups use their intrinsic main size and fill
the cross axis, at least their intrinsic minimum. Canvas children retain fixed size.

Stack starts at preferred main sizes. When space is short, shrink secondary first,
then normal, then essential, never below minima. Within one priority, distribute
the remaining deficit equally among shrinkable children, assigning leftover units
in authored order; repeat only when a child reaches its minimum. Extra main space
stays trailing. On the cross axis, flow uses preferred clamped to space; stretch
uses available space clamped to min/max. Start/center/end position within remaining
space. Auto groups fill cross space; fixed/canvas sizes remain fixed.

Grid assigns only nonfixed children in row-major order using authored columns.
Begin with equal-width tracks after gaps, giving leftover units to earlier columns.
Each track grows to its own largest child minimum if needed. Row preferred/minimum
heights are maxima of their children. Shrink rows by the stack rule using each
row's highest child priority. Do not hide columns or change the authored count.
Flow children fit/anchor on both axes in their cell; auto groups fill their cell,
at least intrinsic minima; canvas children retain size. Grid intrinsic width is
the sum of per-column maxima plus gaps, and height the sum of row maxima plus gaps.

No item disappears to satisfy a constraint. Unfittable content retains readable
geometry. Each node records its box, ancestor/display-clipped visible rectangle,
subtree content bounds and whether any of its box is outside that visible rectangle.
Group overflow reports scroll when requested, diagnose otherwise (fixed groups
implicitly diagnose); leaf overflow diagnoses. Every clipped leaf requires an
alternative presentation. Consumers must expose scrolling/inspector/reflow or
retain the working presentation with an explanation; clipped geometry is not
successful visible activation. Priorities influence shrink order, never deletion.
Overlapping visible siblings receive layout.overlap diagnostics identifying the
other sibling. Deliberate absolute overlap remains authored and is not silently moved.

Convert only clipped visible bounds to pixels: subtract display DIP origin, multiply
by its rational scale, floor left/top and ceil right/bottom, then add pixel origin.
Adjacent fractional bounds can cover the same edge pixel; adapters own clipping/
paint order. Use signed floor/ceil correctly at negative origins. Zero intersection
has zero width/height at the nearest point within its clipping region.

## Results, bounds and failures

The result is ready without diagnostics, degraded with diagnostics, or alternative
when any leaf is clipped or a used display has no safe region. Preserve every node,
chosen variant index (base is -1), display identity, authored revision and geometry.
Diagnostics are unique and sorted by widget ID, code and related ID, with an
absolute 65536-entry construction ceiling (the scene's pair bound is smaller). Emit
display.missing/display.ambiguous, layout.no_region, layout.constraint,
layout.fixed_size, layout.overflow and layout.overlap as applicable.

Invalid scene/topology/metrics and cross-display hierarchy throw stable errors and
return no partial plan. Existing scene bounds (256 nodes, depth 16, eight variants)
remain. Enforce topology/metric limits before allocation and bound diagnostic pairs
by the 256-node scene. All intermediate coordinates and areas fit signed 64-bit
arithmetic under these limits; reject invalid values before computing them.

## Execution and completion

Add the shared scene target and a dedicated test executable to the component graph
for all three current development profiles. Record fixed input/expected-geometry
cases before implementation; compare exact units and pixel bounds across toolchains.
Cover all layout kinds, both stack axes, anchors, priority shrink and minimum
overflow, breakpoints, nested/fixed groups, monitor loss/ambiguity/conflict, safe
insets/exclusions, fractional/negative pixels, invalid/bounded inputs and immutability.
Permuting widget/display/exclusion input order must preserve the result.

Use ordinary workspace preflight/configure/build/test commands from the developer
guide. Run the full suites and the expanded historical executable/linker audit.
Preserve original failures and source/archive/artifact hashes. A passing shared
geometry engine does not complete W-09 or qualify native layout, fonts or rendering.
