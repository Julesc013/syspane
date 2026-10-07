---
type: "SysPane Work Record"
title: "Native widget-creation checkpoint"
description: "All seven primitives through existing draft, resource, policy and transaction owners."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T08:29:17.403156+00:00"}
sp_id: "SP-WIDGET-CREATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-WIDGET-CREATION", "SP-BINDING-AUTHORING-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native widget-creation checkpoint

Source baseline: `8ecf403ebef7622c967f10b90d337d6c3d7037de`. The [package](packages/w-10-widget-creation.md)
adds native creation of text, value, status, table, chart, image and group widgets.
It preserves the existing renderer, validator, immutable catalog and transaction.
W-10 remains in progress; this is a component checkpoint, not a complete edition.

Explicit root/group ownership and parent-local geometry determine placement. A
child copies its parent's exact authored display assignment. Image choice is
mandatory; counter defaults remain editable and do not grant source access.
Each kind has a private buffer; Cancel and owner/policy changes erase it. Insertion
and selection form one atomic undo step. Apply separately persists the draft.
Existing InsertWidget callers retain their prior selection behavior by default.

## Verification

The package, complete default objects/root/nested scenes and unchanged resource
fixture were frozen before implementation. Six portable families cover all kinds,
parent intent, geometry/resource/identity/depth/capacity bounds, atomic rejection,
selection history, exact submitted documents and policy loss.

All 124 affected checks pass on Linux GCC 13, Windows GCC 15 and v141_xp on
contemporary Windows. This is not historical Windows runtime qualification.
Seventeen owned Linux creation cases exercise native controls, rendered content,
selection, Undo/Redo, coherent persistence, reopen, cancellation, lost acknowledgement
and held-reference erasure. Deliberate wrong-object, frozen-preview and retained-text
faults require positive distinguishing observations. Existing binding (15), content
(15), snap (13), group (11), arrangement (14), editor (20) and large-command (24)
matrices pass: 129 native cases across eight matrices.

Preserved failures include an initializer brace, strict compiler diagnostics in
new test code, and native observer assumptions. Pixel comparisons now isolate the
insertion area because existing scene replacement resets chart retention. Native
buttons use actual pointer input; combo menus use native keyboard navigation after
observed opening, without relying on popup item coordinates. An isolated keyboard-focus
observation failure remains preserved without a qualification claim. Fault
classification awaits positive live accessibility, selection, storage and pixel
witnesses within the existing bounded observation window. Expected scenes and
contract bytes remain frozen and unchanged.

One final arrangement attempt failed when AT-SPI returned no component interface
for the object tree before submission. The unchanged matrix was rerun; retain the
failure as an unresolved observation, not evidence of its cause. The large-command
GUI drag case also had a keyboard-focus deadline on Undo before submission; its
unchanged matrix was rerun. These intermittent native observation failures remain
a limitation and do not establish complete native qualification. Three bounded
direct diagnostic wrapper runs passed the original large-command checks and did
not reproduce a failure for the added X11/AT-SPI snapshot. That investigation is
inconclusive; it does not explain the ordinary CTest failures. The final ordinary
matrix uses the unchanged runner and acceptance cases.

Detailed attempts preserve source snapshots, binary identities, original failures,
native records and frozen inputs. See the [attempt index](../../build-support/evidence/w-10-widget-creation-attempts.json),
[native archive index](../../build-support/evidence/w-10-widget-creation-native-index.json),
[verification](../../build-support/evidence/w-10-widget-creation-verification.json),
[staged identities](../../build-support/evidence/w-10-widget-creation-staging.json)
and [machine handoff](../../build-support/evidence/widget-creation-handoff.json).

The existing 7 GiB output limit was retained. Fifteen duplicate native output
directories (55,185,203 bytes) were removed only after exact files and links were
verified against their already committed binding-checkpoint archives. The current
checkpoint originals and all failed attempts remain preserved.

## Remaining work

Investigate the preserved native focus/interface failures. Close responsive/flow
transforms, lock/visibility/typography, clipboard authority
and recovery drafts. Connect installed controller/catalog/policy ownership and
scene-aligned entry/restoration with independent escape. Complete accessibility,
performance, other adapters, historical laboratories and every release gate.
Owned ext4/Xvfb/DBus checks do not qualify an installed desktop or physical power
loss. Continue Windows 9x, Windows NT, X11, Wayland and Mac OS X independently.
