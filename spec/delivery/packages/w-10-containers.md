---
type: "SysPane Work Package"
title: "Explicit reflowing container transformations"
description: "Wrap and unwrap authored layout rules without silently freezing responsive or flow geometry."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T11:18:58.977458+00:00"}
sp_id: "SP-W10-CONTAINERS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-GROUP", "SP-W10-LAYOUT-AUTHORING", "SP-W10-KEYBOARD-INPUT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Explicit reflowing container transformations

Continue W-10 through the existing draft, layout projector, native modal owner and
scene.replace transaction. Keep existing GroupWidgets/UngroupWidget geometry and
rejection semantics unchanged. Add explicit WrapWidgets/UnwrapWidget operations
for authored-rule transformations, including flowing children, auto containers,
responsive origins and nested parents. Do not infer a destructive conversion to
current pixels. No new document, wire, renderer or storage owner is introduced.

## Exact transformation

WrapWidgets supplies 1..256 disjoint existing sibling IDs, a fresh group ID, title,
complete group layout and priority. Require one common ownership array and
structurally equal authored display assignments. Reject missing/duplicate/overlapping
targets, mixed parents/displays, identity collisions and invalid group fields.
Caller selection order never changes ownership order.

Create a group with the supplied layout/title/priority, copied display assignment,
empty bindings and no invented extensions; scene 0.3 adds empty content, scene 0.2
omits it. Its children are the selected IDs in original ownership order. Replace
those IDs with the new group at the first selected position and append the group
record to widgets. Nonselected siblings retain relative order. Nonadjacent wrapping
makes the selection one contiguous drawing unit, as the existing Group operation does.

Preserve every existing widget value exactly: fixed coordinates, flow constraints,
anchors, all breakpoint thresholds/layouts, priorities, bindings, content and opaque
extensions. Those rules now resolve relative to the new parent. Fixed children keep
their numeric parent-local coordinates; they are not translated to preserve world
position. Flow/auto/canvas children participate in the existing new-parent allocation.
Changes to measurement, placement, clipping and overlap are intentional preview
results, not claims of pixel preservation. Select only the new container atomically.

UnwrapWidget supplies one group ID. Require each direct child to have that group's
authored display assignment. Replace the group in its ownership array with its
children, in stored order, and remove only the group record. All surviving authored
values remain exact, including every child's layout rules. They resolve in their
new parent or as roots. Removing the container removes its title, layout, priority,
extensions and clipping boundary; formerly clipped content can become visible.
Select the direct children in normal widgets-array selection order. An empty group
is removed with empty selection. Non-group, missing and display-conflicting targets
reject atomically. There is no fixed-layout or containment prerequisite for this
explicit reflow operation.

Wrap then Unwrap restores the exact initial document when selected siblings were
contiguous and no intervening edit occurred. Nonadjacent children remain contiguous
after Unwrap; Undo, rather than Unwrap, restores their original interleaving.
Existing 128-operation, 256-widget/256-KiB scene, depth 16, eight-breakpoint and
64-entry/8-MiB history limits apply. Validate the entire resulting scene and current
resource/policy context before adopting scene and selection together. Pending or
unknown requests freeze mutation. Invalid later edits preserve the original scene,
selection and history. Undo/redo and value-identical batch behavior remain unchanged.

## Native authoring

Expose distinct Wrap and Unwrap controls with accessible IDs editor.wrap and
editor.unwrap. Wrap needs a nonempty selection; Unwrap needs one group. Ordinary
clean-field, current-policy and modal gates apply; handlers validate exact scope.
Cancel a gesture before opening either modal. Existing Group/Ungroup controls retain
their existing behavior and availability.

Wrap uses the existing layout input grammar and private variant buffers. Offer all
group kinds and up to eight ordered breakpoints, a bounded title and priority.
Default to title Container, vertical stack, gap 8, diagnose overflow and normal
priority. Other kind defaults remain those of the Layout panel. Child display and
insertion position are fixed by selection, so no assignment/reorder input is offered.
Reserve a fresh host ID for the proposed container; cancellation may leave an unused
ID but creates no authored state. Set is one WrapWidgets history entry.

Explain before Set that child layout rules are kept and their positions/sizes may
change. Unwrap presents an explicit confirmation that layout rules remain, children
reflow in the enclosing parent and removing clipping may reveal content. It has no
layout input; its action is labeled Unwrap and reflow. Both operations change only
the draft until Apply. Cancel/Escape makes no change and exposes no transaction.

Reuse the existing modal lifetime: disable other mutation/selection/Apply paths,
preserve invalid private input for correction, and erase it on cancel, close,
policy/owner loss, reload or topology replacement. Regrant alone cannot restore
private state. Held accessibility references retain the 200-ms erasure bound.
No interactive container control is installed into the passive desktop surface.

## Fixed verification and continuation

Freeze this package and complete input/expected scenes and geometry before code.
Cover all group layout kinds, responsive wrapper and child rules, nested/mixed and
nonadjacent ownership, empty unwrap, exact undo/redo, scene 0.2, policy, pending
requests, invalid kinds/displays/identities, overflow/depth/capacity rollback and
exact scene.replace requests. Geometry expectations come from authored examples,
not the implementation's output. Keep original failures if an oracle needs correction.

Use ordinary workspace preflight/configure/build and affected editor/settings/
configuration/composition/protocol suites on all three development profiles. The
owned non-root Linux ext4/Xvfb/D-Bus matrix must use native controls and independently
compare reflowed pixels, exact submitted/stored scenes, save/reopen, history, invalid/
cancel, topology erasure, policy erasure and lost-result recovery. Detect deliberate
wrong hierarchy, retained private input and frozen preview. Rerun all existing editor
native matrices because their shared native owner and modal implementation change.
Preserve source/script/artifact/environment identities and bounded-workspace evidence.

This closes explicit rule-preserving container authoring. It does not claim an
automatic, appearance-preserving conversion between arbitrary responsive layouts.
Remaining lock/visibility/typography, clipboard/recovery drafts, installed ownership,
full accessibility/performance, historical laboratories and every complete-edition
release gate remain required. Routine private implementation choices are delegated;
existing acceptance, privilege and publication boundaries are fixed.
