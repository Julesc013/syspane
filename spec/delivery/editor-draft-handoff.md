---
type: "SysPane Work Record"
title: "Shared editor draft checkpoint"
description: "Typed scene edits, bounded history and the common resource-aware transaction owner."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T03:05:50Z"}
sp_id: "SP-EDITOR-DRAFT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-EDITOR-DRAFT", "SP-SETTINGS-RESOURCES-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared editor draft checkpoint

Subsequent checkpoint: [complete-scene commands](large-commands-handoff.md) closes
the larger-scene transport limitation recorded below. This page preserves the
original checkpoint and its remaining independent gates.


Source baseline: `10765b6a65b9fe3e13e7e255fba2b91758107d0b`. The
[package](packages/w-10-editor-draft.md) admits the portable W-10 draft against the
implemented authored/resource/scene boundaries. W-10 remains in progress; this
checkpoint does not qualify a native editor or any complete edition.

EditorDraft composes the existing SettingsDraft transaction owner. Its private scene
staging path validates authored state, policy and resources; publication still uses
the common command API. Settings-only behavior and existing public contracts remain.
The editor retains exact scene identity, schema, untouched extensions and package/
preset selection. Stable selection follows scene IDs, without telemetry reordering.

Typed operations cover title/display/layout/priority, coupled bindings/content,
theme override, insert/remove, reparent, duplicate, fixed-base move and resize.
Batches are atomic undo steps. Group/ungroup compose those operations without a
second mutation path. Duplicate requires a complete explicit fresh-ID map, preserves
authored properties and remaps only identities/children. Parent-local coordinates
and responsive variants remain explicit; no hidden visual transform or clamping.

History retains at most 64 entries and 8 MiB of canonical scene/selection JSON.
Eviction never removes the accepted baseline. Invalid/no-op edits preserve history;
new edits clear redo. Undo/redo recheck current policy/resources. Discard restores
the exact accepted scene and writes nothing. Disclosure loss clears scene, history,
selection and resource references; regrant requires a fresh snapshot. Late accepted
results cannot recreate revoked content.

Apply emits one existing scene.replace under command 0.4 for scene 0.3, or the
applicable 0.2/0.3 legacy command. Preview and accepted/unknown/conflict results reuse
the settings owner's ticket, epoch, cancellation and reconciliation rules. Accepted
commit advances revision once and clears history; visibility is not inferred.

## Evidence

Twelve complete expected scenes and literal operations were prepared independently
and archived with the package and unchanged resource fixture before implementation.
The test does not derive its expected scene by replaying the editor. Eleven editor
families cover exact operations/undo, rejected batches, identity selection, history
limits, transaction equivalence, policy/disclosure, cross-epoch reconciliation,
conflict, cancellation/result scope, local/wire size limits and legacy compatibility.

The first compile failed on misleading indentation in a test loop; splitting the
assertion onto its own line fixed it without changing the expectation or warning
policy. All original inputs and attempt records are preserved. Review additionally
covered malformed intermediate operations, group/ungroup restoration and pending
revocation followed by a late accepted result. No fixed expected scene was changed.

`build-support/evidence/w-10-editor-draft-attempts.json` binds source archives,
commands, native artifacts and CTest logs. The affected portable run contains 69
entries per development profile: eleven editor, seventeen settings and the existing
authored/configuration/policy/component checks. The eighteen-mode independent Linux
native settings regression exercises the changed shared owner; it is not a native
editor test. Historical-toolset checks run on contemporary Windows, not historical OSes.

The workspace build reservation stopped before launch when growth exhausted the
remaining headroom. The 6 GiB allocation stayed unchanged. Only byte-identical
committed source/capture duplicates and verified archived smoke payload copies were
reclaimed from resolved owned roots; original reports and archives remain. Exact
reclamation records, specification/tool results and staging hashes accompany the
machine handoff. Specification checks alone do not qualify product behavior.

## Next required boundary

Connect this draft to an ordinary native interactive surface aligned with the scene,
using the existing independent exit owner before admission. Prove actual pixels,
selection, pointer/keyboard equivalence, Apply/Cancel, topology changes and native
exit independently. Preserve resource/scene/policy identity across preview and
installed desktop restoration. Keep the permanent wall passive.

Local drafts support the existing 256 KiB scene bound, while current commands remain
limited to 16 KiB. An oversized Apply is explicitly rejected with the valid draft
and history intact. This existing envelope gap must be closed through a versioned
contract before full editor completion; it is not a reduced scene-size promise.
Persistent locking, conditional visibility, widget typography, clipboard ownership,
snap/align/distribute controls, crash recovery drafts, full accessibility and native
adapters on the other platforms remain required. Complete 0.1.0 editions and all
release authority/lifecycle/qualification gates remain open.
