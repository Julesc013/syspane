---
type: "SysPane Work Record"
title: "Native layout-authoring checkpoint"
description: "Existing layout grammar and active fixed variants through the shared draft."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T10:19:48.459090+00:00"}
sp_id: "SP-LAYOUT-AUTHORING-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-LAYOUT-AUTHORING", "SP-NATIVE-OBSERVATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native layout-authoring checkpoint

Source baseline: `321a11e67d28582b5c03c4f0b4c89ecc4c6b550c`. The [package](packages/w-10-layout-authoring.md)
adds fixed/flow leaf and fixed/canvas/stack/grid group authoring, ordered responsive
breakpoints, priority, sibling order and whole-root display assignment. It preserves
scene/layout/wire versions and the existing renderer, resource and transaction owners.
W-10 remains in progress; complete editions remain required.

Each variant/kind retains private input. Set layout is one atomic undo step; Apply
persists separately. Direct move/resize/arrange operations capture active fixed
variants without changing inactive layouts. Topology cancels gestures and layout
input; buffered geometry rejects a changed variant. Root display assignment handles
256 nodes in one typed operation without expanding the batch-operation limit.

## Verification

Complete authored/expected scenes, exact resolved geometry, package and unchanged
resource/schema inputs were frozen before implementation. Eight portable families
cover kinds, thresholds, variant indices, order/display, bounds, atomic rejection,
history, current policy and exact submitted scenes. All 132 affected checks pass on
Linux GCC 13, Windows GCC 15 and v141_xp on contemporary Windows.

Twenty-one owned Linux layout cases cover actual controls, rendered geometry,
save/reopen, history, topology, cancellation, policy erasure and lost acknowledgement.
Wrong persisted layout, retained private input and frozen preview require positive
fault observations. Existing observation (7), creation (17), binding (15), content
(15), snap (13), group (11), arrangement (14), editor (20) and large-command (24)
matrices pass: 157 native cases across ten matrices.

Every failed and successful attempt retains source snapshots and binary identities.
The evidence is under `out/evidence/w-10-layout-authoring-attempts.json`,
`w-10-layout-authoring-native-index.json`, `w-10-layout-authoring-verification.json`
and `w-10-layout-authoring-staging.json`; the machine handoff is
`out/evidence/layout-authoring-handoff.json`.

The first strict build rejected misleading indentation; the initial portable test
incorrectly reloaded a pending request. Both failures are preserved. Native setup
also exposed an initially unselected GTK cursor for which Home did nothing and a
dialog-close/open timing race. The harness now makes an explicit keyboard selection,
awaits editor re-enablement and requires visible modal controls. An alignment sample
incorrectly included transparent pixels over another expected widget; it now checks
the unobscured caption without changing frozen scenes or geometry. List selection
no longer rebuilds its own model during the selection callback.

The topology case initially clipped a fixed child on a 399-DIP display, which
requires the existing surface alternative. Native controls now temporarily fit
the root and child for the visible variant-change exercise and restore all frozen
geometry before saving. Combo activation uses its native accessibility action so
dialog resizing cannot invalidate a pointer rectangle before allocation completes.

A separate button-focus failure after modal closure retains X11 ownership and
accessibility-state evidence. Layout buttons use native pointer activation; direct
keyboard editing and list selection remain exercised. This does not qualify all
keyboard/accessibility paths or explain the earlier intermittent focus failures.

## Remaining work

Close flow/container group transformations, lock/visibility/typography, clipboard
authority and recovery drafts. Connect installed controller/catalog/policy ownership
and scene-aligned entry/restoration with independent escape. Full accessibility,
performance, other adapters, historical laboratories and all five complete editions
remain open. Owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior,
historical Windows runtimes or physical power loss.
