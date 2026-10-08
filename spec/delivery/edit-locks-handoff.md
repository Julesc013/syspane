---
type: "SysPane Work Record"
title: "Persistent editor lock checkpoint"
description: "Versioned own/inherited locks through shared guards, native editing and durable transactions."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T12:34:52.737595+00:00"}
sp_id: "SP-EDIT-LOCKS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-EDIT-LOCKS", "SP-CONTAINERS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Persistent editor lock checkpoint

Source baseline: `83da967d8a7311b8124c3beae304af103730eccd`. The
[package](packages/w-10-edit-locks.md), schemas and complete input/expected scenes
were frozen before production edits. Scene 0.4 adds optional edit_locked without
changing scene 0.3. Command 0.6 retains complete-command bounds and requires explicit
edit-lock/resource/scene-content/large-command negotiation. Prior schemas and
fixtures remain byte-identical; the fixture registry gains the new cases.

SetWidgetLocks changes own flags atomically; group locks are inherited. Explicit
unlock never clears an ancestor. Ordinary edits to protected objects/branches reject;
selection, independent sibling insertion, scene theme and history retain their
specified roles. Native controls expose Lock/Unlock and accessible lock status,
disable protected fields/actions and prevent pointer gestures. Apply remains a
separate durable transaction. Locks affect editing, not policy or live rendering.

## Executed evidence

Eight shared families cover schemas/types/versions, exact promotion/history,
operation guards, inheritance, rollback, policy/capability/pending states,
negotiation and durable replay. All 146 affected checks pass on Linux GCC13,
contemporary Windows GCC15 and v141_xp on contemporary Windows. These are
development runs, not historical Windows execution qualification.

The complete non-native suites also pass: 311 Linux, 308 contemporary Windows and
305 v141_xp checks. Their existing platform-specific coverage remains explicit;
the counts include the affected families above rather than adding distinct cases.

Eleven native matrices pass 156 cases, including all seven lock cases and the
editor/container/layout/creation/binding/content/arrangement regressions. The
additional 24-case large-command matrix failed in both attempts, so the complete
180-case native regression set has not passed. Native lock cases compare full scenes, pixels, guarded pointer/keyboard
input, own/inherited/multiple selection, undo/redo, storage before Apply, durable
save/reopen, lost-result reconciliation and policy erasure. A deliberately removed
stored lock must be positively detected.

Initial schema/header admission and compile failures are preserved. The first native
unlock/move test wrongly expected the numeric label string 60, while the captured
native field showed 60.0 at the correct origin. Its correction uses the existing
independent numeric read with unchanged values, frozen scenes, pixels, deadlines
and production behavior. The original failure and correction record are retained.

The first large-command regression run failed before submission: Apply was enabled,
the editor process and X focus were live, but Apply never reported keyboard focus.
The same failure recurred in one of three bounded unchanged-case reproductions.
Six further runs with extra focus-owner observations only on failure did not
reproduce it. These observations do not identify a cause or repair the failure;
native interaction reliability remains open. The full-suite rerun also failed,
this time while focusing Undo after the drag. The original failures, diagnostic
runs and failed full-suite rerun remain separate records. No production or
acceptance change was made to hide the failure; this checkpoint is not qualified.

Records: `out/evidence/w-10-edit-locks-attempts.json`,
`w-10-edit-locks-native-index.json`, `w-10-edit-locks-verification.json`,
`w-10-edit-locks-staging.json`, `w-10-edit-locks-focus.json` and
`out/evidence/edit-locks-handoff.json`.
Exact source archives, input identities, executable identities and failed/successful
native observations are preserved. Cleanup removed only duplicates verified against
committed archives, within the unchanged workspace bound.

## Remaining boundary

W-10 and the full 0.1.0 release remain in progress. Continue conditional visibility,
typography, clipboard authority, recovery drafts, installed controller/catalog/policy
ownership and scene-aligned entry/restoration with independent escape. Complete
accessibility/performance, earlier unrelated focus/interface causes, other platform
adapters, historical laboratories and all five edition/release gates remain open.
Investigate the reproduced Apply-focus failure before claiming reliable native
interaction; it is not attributed to the lock change or to the environment without
additional evidence.
