---
type: "SysPane Work Package"
title: "Reversible native grouping with explicit geometry"
description: "Close group and ungroup transformations, selection history, drawing order and native persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T05:26:20Z"}
sp_id: "SP-W10-GROUP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-ARRANGE", "SP-W10-EDITOR-DRAFT", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Reversible native grouping with explicit geometry

Continue W-10 through the same serialized EditorDraft, native EditorForm and
resource-aware scene.replace transaction. Add GroupWidgets and UngroupWidget;
no new scene version, wire operation, renderer, storage owner or privilege.
The existing group kind is a structural container and paints no decoration.

## Group transformation

GroupWidgets supplies 2..256 disjoint existing sibling IDs, a fresh group ID and
a bounded plain title. The targets must have structurally equal authored display
assignments. Reject duplicate/missing/overlapping targets, mixed parents/displays,
ID collisions, invalid titles and schema/resource/policy violations atomically.
Caller order does not affect drawing order. Every selected root must have fixed
base and fixed breakpoint layouts. Descendant layouts remain untouched, including
flowing or responsive descendants within a selected fixed group.

Quantize each selected root's base and every breakpoint with the established
1/64-DIP layout rules: nearest origins, ties away from zero; ceiling extents.
Check finite values and existing origin/extent bounds before integer conversion.
The new group's box is the union of ALL those variant boxes. Thus a different
display width does not make an existing fixed variant escape the new container.
Reject bounds exceeding the existing scene limits, without clamping or resizing.
The group has one fixed base, no breakpoints, copied display assignment, empty
bindings, normal priority and supplied title. Scene 0.3 adds empty content;
scene 0.2 omits content. It has no invented extension values or bindings.

For each selected root, replace x/y in every layout variant with its quantized
origin minus the new group origin, divided by 64. Preserve original width/height,
breakpoint thresholds/order and every other property exactly. Descendants retain
all authored values and identities. Origins finer than 1/64 DIP are deliberately
canonicalized by this transformation; rendered coordinates are preserved. Undo
restores the exact original authored values, including finer fractions.

Insert the group at the first selected position in the common ownership array;
remove the selected IDs from that array and make them children in their original
ownership order. Nonselected siblings retain relative order. Nonadjacent selection
therefore becomes one contiguous drawing unit at that first position: intervening
nonselected siblings draw after the entire group. This possible overlap-order change
is explicit behavior, not an assertion that every nonadjacent grouping has identical
pixels. Append the group record to widgets; preserve all existing widget-record order.
Select only the new group as part of the same atomic history entry.

## Ungroup transformation

UngroupWidget supplies one existing group ID. Its layout must be fixed base with
no nonempty breakpoints. Each direct child must have fixed base and fixed breakpoint
layouts, and the same authored display assignment as the group. Every quantized
child variant box must lie within the group's ceiling-quantized width and height.
Reject overflow/clipping-dependent groups: removing their container could reveal
content. Empty groups may be removed and yield an empty selection.

Translate x/y of each direct child's variants by the quantized group origin.
Preserve all other child/descendant fields. Replace the group in its ownership
array with its direct children in stored child order; remove only the group record.
Removing a group deliberately removes that container's title, priority and opaque
extensions. Child identities, extensions, pins and ownership below that level remain.
Select the direct children in ordinary widgets-array selection order in the same
history entry. Responsive container origins and flowing direct children need an
explicit layout transformation; this operation must not silently flatten them.

## Atomicity, state and limits

Use existing 128-operation batches, 256-widget/256-KiB scene limits, depth validation,
64-entry/8-MiB history and current-policy/resource validation. Grouping consumes one
widget slot. Bound work by the scene and breakpoint limits. No filesystem, callbacks,
import, telemetry or native code participates in the shared transformation.

Apply scene and resulting selection together only after complete validation. A later
invalid edit in the same batch preserves the original scene, selection, history and
request. Undo/redo restore both sides exactly under current policy. Selection effects
follow operation order; surviving IDs are canonicalized at the end. A value-identical
batch remains a no-op and preserves selection/history, as before. Pending/unknown
results freeze operations; disclosure loss erases hierarchy/history together.

## Native controls and geometry

Expose labeled Group and Ungroup buttons with accessible descriptions editor.group
and editor.ungroup. Enable Group for at least two selected items, Ungroup for one
selected group, subject to ordinary editable/clean-field gates. The handler still
validates all prerequisites. New IDs come from the existing host allocator; the
initial native group title is Group and remains editable through the title field.

Cancel any gesture before a hierarchy action. Resolve fresh shared-renderer nodes.
Selected roots (or the group and its direct children for Ungroup) must be on the
active display with fixed active variants and rendered extents equal to their
ceiling-quantized authored extents. Their destination parent is either scene roots
or an active fixed/canvas group. This avoids changing flowing parent measurements
or disguising native metric expansion. Shared checks cover all authored variants,
ownership, containment and display intent. Explain ineligible cases without edits.
Static-parent geometry is this checkpoint's admitted native scope; full responsive
container/flow authoring remains required.

Group members remain selectable through the native list and canvas; clicking the
container's empty area selects the group. Existing group move/resize, numeric fields,
history, Apply/Cancel, policy erasure and independent recovery remain available.
Grouping writes nothing until Apply. Keep permanent desktop surfaces passive and
retain the independent escape owner before installed editor admission.

## Verification and completion

Freeze tests/editor/group-cases.json and this package before production edits.
Use complete expected scenes for grouping, nested/nonadjacent groups, moving,
ungrouping, fixed responsive variants and sub-unit origins. Verify exact selection,
history, invalid/overflow/depth/capacity rollback, old scene compatibility, current
policy and scene.replace equivalence. Derive expected values independently.

Use ordinary workspace preflight/configure/build commands on all three development
profiles. Run ctest --preset <profile> -R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure. Linux adds native.EDITOR-GROUP and the existing
native.EDITOR-ARRANGE, native.EDITOR-FORM and native.LARGE-COMMANDS matrices in the
declared non-root private ext4/Xvfb/DBus laboratory.

Native input and externally read pixels must prove group/member geometry, explicit
overlap order, nested selection and history, stored documents/resources, save/reopen,
cancellation, current-policy denial, 200-ms disclosure erasure and lost-result restart.
Detect deliberate stale pixels and altered persisted hierarchy. Preserve failed
attempts, original oracles, source/binary identities and the next work boundary.

This package's checked implementation does not close all W-10 acceptance or qualify
an installed edition. Snapping/grid/guides, responsive/flow container transforms,
remaining properties, clipboard authority, recovery drafts, installed routing,
other native adapters, historical labs and every full-release gate remain required.
