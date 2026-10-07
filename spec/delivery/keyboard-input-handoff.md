---
type: "SysPane Work Record"
title: "Native keyboard-input checkpoint"
description: "Queued navigation completion explains the recorded layout-button focus failure."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T11:01:07.990994+00:00"}
sp_id: "SP-KEYBOARD-INPUT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-KEYBOARD-INPUT", "SP-LAYOUT-AUTHORING-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native keyboard-input checkpoint

Source baseline: `1327296abae9e592ad6f20dd0334004c244c67c1`. The [package](packages/w-10-keyboard-input.md)
closes the specific layout-button focus failure recorded by the preceding checkpoint.
Production source/binaries and all frozen product expectations remain unchanged.
W-10 and every complete desktop edition remain in progress.

## Causal evidence

The preserved keyboard oracle is replayed with the same native binary in the owned
unprivileged ext4/Xvfb/D-Bus laboratory. Three detailed-snapshot runs pass but are
inconclusive. Removing successful-path snapshots and replaying the original fixed/
flow prelude reproduces the canvas focus failure in all three repetitions. Explicit
queries show the editor remains the active X11 window, while its object list/Image
row retains focus. One diagnostic Space does not open Layout.

A paired experiment uses the same keys and dialog-boundary observations, retaining
the original three-second bound for each wait. The final corrected oracle instead
bounds the entire navigation sequence to three seconds.
All three batched runs fail and all three ordered runs focus and activate Layout.
The input trace shows End/Home/Down/Down/Down queued together, followed by an early
`Layout group` title read. End selected that same group before the following keys
completed. The later navigation reclaimed focus after the accessibility focus
request. Per-key row/title acknowledgement removes that ambiguity without changing
the producer or weakening the required focused state.

GTK's [3.24.41 focus-request implementation](https://raw.githubusercontent.com/GNOME/gtk/3.24.41/gtk/a11y/gtkwidgetaccessible.c)
requests widget/window focus before returning success. That return alone is not the
oracle's completion condition: the explicit focused-state check remains required.
Upstream source hashes explain the API boundary; the paired native observations
establish this failure's cause. They do not establish causes for earlier unrelated
interface lookup or focus failures.

## Correction and verification

The layout oracle reads explicit selected rows and the expected title after each
navigation key, within one three-second deadline for the entire operation. It logs
bounded expected/observed transitions. It performs no mutation retries, focus forcing
inside held checks or arbitrary settling sleep. Layout buttons again use explicit
focus plus Space. Existing showing/modal-state checks, exact scenes/pixels/storage,
negative fault controls and the 200-ms erasure bound remain fixed.

The first restored-keyboard regression run also exposed an alignment completion
race: the oracle changed selection immediately after queuing Space, before the
expected alignment appeared. Its screenshot preserves the unaligned second pane.
The correction observes the same frozen aligned caption pixels before moving focus,
then checks the original exact geometry and stored scene. This adds an observable
completion condition; it does not change the expected scene or retry the action.

All 157 native cases pass across ten matrices: layout 21, observer calibration 7,
creation 17, binding 15, content 15, snap 13, group 11, arrangement 14, editor 20 and
large-command 24. The three diagnostic matrices contain 24 separate investigative
cases, including intended failures and inconclusive passes; they are not added to
the product-pass count. Production bytes match the baseline, whose 132 affected
checks per development toolchain remain the portable evidence. No new Windows
runtime or historical qualification is claimed.

Records: `build-support/evidence/w-10-modal-focus-attempts.json`,
`w-10-modal-focus-native-index.json`, `w-10-modal-focus-verification.json`,
`w-10-modal-focus-staging.json` and `build-support/evidence/keyboard-input-handoff.json`.
They preserve every attempt, frozen package/inputs, exact diagnostic scripts,
native traces, source snapshots, executable identities and specification checks.
Twenty-one duplicate native folders were reclaimed only after verifying their
already committed layout archives. The existing output budget remains unchanged.

## Next boundary

Continue flow/container group transformations and remaining property contracts,
then installed controller/catalog/policy ownership and scene-aligned entry/restoration
with independent escape. Earlier unrelated focus/interface failures, complete
accessibility/performance, historical laboratories, other adapters and all five
complete-edition release gates remain open.
