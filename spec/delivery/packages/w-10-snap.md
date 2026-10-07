---
type: "SysPane Work Package"
title: "Deterministic pointer snapping and visible alignment guides"
description: "Close bounded grid and guide projection through existing editor gestures and typed edits."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T05:55:00Z"}
sp_id: "SP-W10-SNAP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-GROUP", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Deterministic pointer snapping and visible alignment guides

Continue W-10 through the same EditorDraft, EditorForm, SceneSurface and transaction
owner. Add a pure bounded geometry projection; it returns deltas and guide facts,
never mutates an authored scene. Release still executes MoveWidgets/ResizeWidget.
No scene/schema/wire/storage change or new authority is required.

## Geometry contract

Use signed 1/64-DIP units. Input contains the original selection union, raw dx/dy,
resize/bypass flags, grid origin and spacing, an alignment area, and at most 256
uniquely identified sibling rectangles. Origins, extents, origins plus extents,
deltas and grid origins must be within +/-134217728 units; extents are positive.
Grid spacing is 1..256 DIP and threshold 0..16 DIP. Reject invalid inputs before
arithmetic, including oversized lists, duplicate/invalid IDs and integer extremes.
The native choices are 4, 8, 16 and 32 DIP, initially 8; threshold is 6 DIP.

Project axes independently. A zero raw delta on an axis stays exactly zero and has
no guide. With bypass, or both snap modes disabled, return raw deltas without
guides. Otherwise consider candidates within the inclusive threshold of the raw
proposed geometry. Movement uses the union's leading, center and trailing anchors;
resize uses only its trailing edge and preserves its leading edge. Centers use
origin plus floor(extent/2). Each guide area/sibling supplies all three anchors.
Grid snapping uses only the leading edge for movement and trailing edge for resize.
Grid lines are origin + k*spacing, with nearest k and exact ties away from zero
relative to that origin. A negative resulting resize extent has no snap candidate;
return its raw delta for the existing authored validation to reject.

Choose lexicographically by absolute correction, source priority (sibling, area,
grid), guide coordinate, target ID (byte order), moving anchor index then target
anchor index (leading=0, center=1, trailing=2). Thus input enumeration order is
irrelevant. Add the selected correction to the original raw delta. Return the
coordinate, source, target ID and anchor indices for each chosen guide. Do not
iterate after snapping, clamp authored bounds or apply hysteresis. Quantize native
pointer deltas with nearest-unit ties away from zero only when snapping is enabled;
ordinary unsnapped gesture precision remains unchanged.

## Native capture and lifetime

When either snap mode is enabled, resolve current nodes at press. Selected roots
must be disjoint fixed-base siblings on the active display with no native metric
expansion. Their parent must be fixed/canvas with no metric expansion, or scene
roots. Capture selection union, same-parent nonselected sibling boxes, viewport
scale, grid origin at display bounds, and alignment area. Root area is the display
work rectangle inset by safe margins; a nested selection uses parent content.
Freeze that snapshot and options until release. Telemetry repaint cannot retarget
the gesture. Responsive/flow direct gestures retain their existing rejection.

Show native check buttons Snap to grid, Snap to guides and Show grid, all initially
off. Grid spacing cycles 8 -> 16 -> 32 -> 4 -> 8 DIP through a labeled native button.
These are session preferences: they do not dirty the scene, enter history or save
with Apply. Reload/regrant retains preferences; closing/reopening resets them.
Changing an option cancels a gesture. Buffered property fields and pending/unknown
requests disable the controls under existing editing gates.

Pointer motion shows snapped selection outlines plus one magenta line per chosen
axis and a native accessible text description of guide coordinates in display-local
DIP. Ctrl temporarily bypasses snapping; the release modifier state governs the
committed result. Arrow keys and numeric fields remain precise unsnapped editing
alternatives. No authored change or undo entry occurs before release. Escape,
focus loss, topology/policy replacement, request/disconnect, reload and close erase
gesture/guide state. Policy erasure includes held accessible guide text and pixels
within the existing 200-ms bound. Regrant cannot reconstruct erased geometry.

Show grid draws gray lines at display-relative grid coordinates over the actual
scene preview, independently of snap mode. Bound drawing to at most 512 lines by
using the smallest whole spacing multiplier satisfying that bound; snapping still
uses the selected spacing. Draw guides over the grid and selection. Never render
grid or guides when the draft is unavailable. Guide feedback is transient, not an
authored guide object; persistent ruler-guide authoring remains a future explicit
contract if added. It is not required to interpret these alignment guides.

## Verification and completion

Freeze this package and literal input/output cases before production changes.
Cover positive/negative/tie/fractional coordinates, resize, union movement, zero
axes, threshold edges, sibling/area/grid priority, order independence, bypass,
bounds, invalid input and same typed-operation history/policy behavior.

Run the affected editor/settings/configuration/composition/protocol selection on
all three development toolchains. Linux adds native.EDITOR-SNAP plus unchanged
EDITOR-GROUP, EDITOR-ARRANGE, EDITOR-FORM and LARGE-COMMANDS matrices. Native input,
held-gesture pixels/accessible guides, stored documents and reopen must agree.
Exercise grid, sibling guides, resizing, multi-selection, bypass, precise keys,
Escape, option changes, policy erasure, cancellation and lost-result restart.
Detect deliberately frozen preview and altered committed geometry. Preserve all
failed attempts and source/artifact/oracle/environment identities.

W-10 stays in progress. Installed entry/restoration, responsive/flow transforms,
remaining binding/content/theme/lock/visibility/typography controls, clipboard
authority, recovery drafts, full accessibility/performance, other adapters and
all complete desktop editions remain required.
