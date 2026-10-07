---
type: "SysPane Work Record"
title: "Native alignment and spacing checkpoint"
description: "Deterministic shared arrangement with native controls and independently observed persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T04:57:30.608519+00:00"}
sp_id: "SP-ARRANGE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-ARRANGE", "SP-LARGE-COMMANDS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native alignment and spacing checkpoint

Source baseline: `62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1`. The
[package](packages/w-10-arrange.md) closes fixed-base alignment and equal spacing
through the existing EditorDraft, GTK form, renderer and transaction owner.
W-10 remains in progress and every complete-edition release gate remains open.

Typed AlignWidgets and DistributeWidgets operate atomically on disjoint siblings
with matching authored display intent. Six alignments use a common original bounding
interval. Two spacing actions preserve endpoints and distribute integer remainders
deterministically. Positions use nearest 1/64-DIP rounding with ties away from zero;
extents use ceiling. Negative spacing, invalid intermediate values and incompatible
selections reject without partial edits or history changes. Untouched properties,
breakpoints, pins and selection remain exact.

The native form resolves current geometry before arrangement and rejects inactive
responsive bases or native metric expansion. It supplies eight labeled native
buttons, count/field/pending gates and useful rejection messages. Arrange changes
the draft and preview; Apply uses the original resource-aware scene.replace owner.
Undo/redo, cancellation, policy erasure and reconciliation retain their existing
semantics. No new schema, wire operation, import authority or persistent cache exists.

## Verification

The package and complete expected scenes were archived before production edits.
Independent literal cases cover all eight actions, negative and positive half-unit
rounding, ceiling extents, fractional endpoints and zero gaps. Six new portable
families also exercise invalid/atomic edits, hierarchy and ownership order, flow,
breakpoint preservation, history, current policy and exact command submission.

The affected selection passes 94 CTest entries on each of Linux GCC 13, Windows
GCC 15 and v141_xp on contemporary Windows. Fourteen private Linux native cases
exercise all buttons via native selection and keys, actual preview pixels,
undo/redo, stored documents/resources, save/reopen, cancellation, policy denial,
200 ms disclosure erasure and lost-result restart. Deliberate frozen preview and
altered committed geometry controls are positively detected. The existing 20-case
native editor matrix and 24-case complete-scene/storage/IPC matrix also pass.

The first strict build found misleading indentation in a test. The first native
oracle incorrectly expected clicking an already-selected widget to collapse a
multiselection; it now explicitly clears selection before inspecting one widget.
Original failed runs and their source archives are retained. Neither correction
changes the frozen geometry or expected product behavior.

The existing frozen-preview regression also exceeded its 40-second observer limit.
An isolated diagnostic preserved stack traces in repeated accessibility-tree scans
during failure inspection. The observer now caches stable native control references
per process, while reading live text/state/geometry and clearing references on
reopen. The unchanged fault predicate and deadlines then pass; full native matrices
are rerun. This changes no product geometry, timing bound or expected result.

Removing those incidental delays exposed an initial-frame race in the new pixel
oracle: native selection state was ready before its selection outlines were painted.
The observer now awaits all three independently captured outlines before taking
its reference pixels. The original failed screenshot, all geometry expectations
and the unchanged observation deadline are preserved.

Native key checks then exposed a product issue: the general button-state update
briefly disabled every control before applying exceptions. Repaints interrupted
held Space-key activation of Revert fields and Cancel request, even when focus
remained on the button. A deterministic 160 ms held-key case failed before the fix.
The form now applies each final state once. Native checks preserve focus and
activation across repaints without relaxing policy or pending-state gates.

Evidence: [attempts and artifact identities](../../build-support/evidence/w-10-arrange-attempts.json),
[native archive index](../../build-support/evidence/w-10-arrange-native-index.json),
[specification/tool checks](../../build-support/evidence/w-10-arrange-verification.json),
[staged identity checks](../../build-support/evidence/w-10-arrange-staging.json) and
[machine handoff](../../build-support/evidence/arrange-handoff.json).

## Next admitted boundary

Close snapping/grid/guides and grouping semantics, remaining binding/content/theme
and lock/visibility/typography properties, responsive arrangement, clipboard authority
and recovery drafts. Then connect installed controller/catalog/policy ownership to
scene-aligned desktop entry and restoration with independent escape before mapping.
Continue other adapters and historical native qualification independently.

These owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, representative accessibility/performance
or a complete edition. Specification tools still have two existing Windows symlink
skips. Full Windows 9x, Windows NT, X11, Wayland and Mac OS X scope is unchanged.
