---
type: "SysPane Work Package"
title: "Native scene editing and independent exit"
description: "Connect the shared draft to real native pixels, input, transactions and recovery."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T03:29:40Z"}
sp_id: "SP-W10-NATIVE-EDITOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-EDITOR-DRAFT", "SP-W25-EDITOR-EXIT", "SP-W09-SCENE-IMAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native scene editing and independent exit

Continue W-10 with an embeddable Linux GTK EditorForm using EditorDraft and the
existing SceneSurface. Preserve the passive desktop wall. The host supplies native
authority, current policy, coherent authored/resource context, topology, selected
display and providers. No new storage, telemetry or resource resolver. The form
owns its native controls, gesture state, preview and erasure caches on one GTK thread.
Installed entry still requires a separate recovery owner before mapping the editor.

The [arrangement extension](w-10-arrange.md) now closes fixed-base align/distribute
operations and native controls through this same owner. Its deterministic arithmetic
and geometry eligibility apply alongside the remaining authoring requirements.

The [grouping extension](w-10-group.md) adds reversible fixed-container hierarchy
operations and selection history through this same owner. Its variant bounds,
containment and native geometry requirements apply alongside remaining authoring.

## Native behavior

Updating native control availability must apply each control's final state once.
An otherwise available control must retain keyboard focus and a held key activation
across ordinary preview repaints. Do not transiently disable and re-enable it while
computing its state. Actual permission/pending changes still disable it immediately.

Draw the actual shared renderer output for the selected display. Hit-test its
resolved visible node rectangles in reverse drawing order using device pixels;
convert GTK logical coordinates through the widget scale factor. Translate pointer
deltas back to DIP through the selected display's scale. Preserve authored parent-local
coordinates. Only fixed base variants admit direct gestures; responsive/flow nodes
remain selectable and inspectable. Do not silently modify an inactive base variant.

Plain click selects a stable ID; Shift-click toggles membership. A native widget
list supplies keyboard selection. Pointer drag moves the captured disjoint selection;
the bottom-right 8-device-pixel handle resizes a single fixed widget. Capture IDs and
geometry at press, show geometry-only feedback during drag, then apply one typed
operation on release. No authored change before release. Escape cancels that gesture.
Focus loss, topology or policy change cancels it. Live telemetry must not retarget
the gesture or enter the undo history. Out-of-range release rejects without clamping.

On the canvas, arrows move by 1 DIP, Shift by 10 DIP. Alt-arrows resize one widget;
Ctrl-Z and Ctrl-Shift-Z undo/redo. The same typed operations serve pointer and keyboard.
Expose native Add text, Duplicate, Delete, Undo, Redo, Apply, Cancel session, Cancel
request and Reload actions. New IDs come from the host and shared validation rejects
collisions. Duplication remaps complete selected subtrees and selects the new roots
in the native form; deleting immediately afterwards removes the copies. All widget kinds render
through SceneSurface; initial precise properties cover title, text body and fixed
base x/y/width/height. Other binding/content/theme/group controls remain required.

Properties are buffered until Set properties, producing one atomic history step.
Use canonical signed decimal syntax with optional fractional digits, no whitespace,
exponent, NaN/infinity or locale-dependent parsing; shared schema bounds still apply.
Invalid text remains visible with an error and cannot be committed. Revert fields
restores current draft values. While fields differ, block selection/gesture/undo/
duplicate/delete/Apply until Set properties or Revert fields; Cancel session may
discard them. Geometry fields are disabled for non-fixed or non-base nodes.

Reuse a shared bounded GTK plain-text control with the existing settings clipboard
restrictions, including AT-SPI copy/cut and PRIMARY selection. Title allows 512
characters, body 1024, numbers 64. The common control retains settings' 256-character
single-line behavior. Full clipboard authority and rich text are not admitted.

## State, policy and lifetime

Apply queues the exact existing EditRequest and returns to GTK. Callbacks cannot
re-enter the form. Pending/unknown disables editing and session Cancel; Cancel request
targets the same identity and does not claim rollback. Callback failure is unknown.
Conflicts require explicit Reload. Accepted saves show durable/pending/unconfirmed
visibility facts. Cancel session discards local draft then requests native close;
closing or emergency release cannot reverse an already submitted command.

Disclosure loss erases fields, list cells, accessible content, gesture state and
preview resources in the same owner call. Hold native accessible references in the
test and require erasure within the existing 200 ms bound. Regrant does not recreate
the draft; reload is required. Re-evaluate policy in both draft and SceneSurface.
Close clears local state and reaps any rendering workers through their existing owner.
Topology replacement cancels gestures and uses the declared fallback viewport while
retaining authored monitor associations. Reload takes coherent current resources.

Use the existing independent X11 key/recovery probe to launch the actual editor
fixture as a held child, with parent lifetime armed across exec. Keep the existing
250 ms escalation and 1,500 ms external recovery bound. Exercise unsaved edits and
frozen/held-pointer editor, native escape button, owner death and shortcut conflict.
Verify original underlying pixels/input, actual child exit and no stored draft commit.
The observer supplies a private Xvfb/DBus laboratory; no user desktop is modified.

## Evidence and remaining gates

Preserve literal scene/resource inputs and expected geometry, content, revision,
policy and recovery outcomes before implementation. Independent native XTest input,
AT-SPI reads, pixel movement and generation-store bytes must agree. Cover drag versus
keyboard equivalence, resize, multi-selection, property validation, undo/redo,
Apply/reopen, cancellation, conflict, restart/reconciliation, revocation and topology.
Calibrate deliberate frozen-preview, wrong-commit and retained-disclosure controls;
recognize only each intended failure with its positive distinguishing observations.

Run affected portable suites, native settings regression after extracting its text
control, existing editor-exit regression and the new native editor scenarios. Preserve
all failures and exact source/binary/oracle/runtime identities. Ordinary bounded
workspace/build commands remain the execution path. Consult the GTK primary docs for
[drawing/input](https://docs.gtk.org/gtk3/class.DrawingArea.html) and
[device scaling](https://docs.gtk.org/gtk3/method.Widget.get_scale_factor.html).

This component does not qualify behind-icons integration, a full native editor or a
release. Larger-scene transport, remaining authoring contracts/panels, snap/align/
distribute, clipboard, recovery drafts, full localization/accessibility, maximum-size
responsiveness, installed ownership and other native adapters remain required.
