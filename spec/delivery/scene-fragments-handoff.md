---
type: "SysPane Work Record"
title: "Shared scene fragments checkpoint"
description: "Bounded authored copy/paste with explicit disclosure and atomic resource/history ownership."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T11:30:46.531139+00:00"}
sp_id: "SP-SCENE-FRAGMENTS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-SCENE-FRAGMENTS", "SP-THEME-CONTROLS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared scene fragments checkpoint

Baseline 8e1beba8b20f8fb5d05f95e55887ea955e7beeb4. The [package](packages/w-10-scene-fragments.md)
adds explicit sensitive-copy admission, a revocable serialized snapshot and atomic
PasteWidgets to the existing EditorDraft. Copy preserves selected authored subtrees,
including opaque extensions, direct bindings, selectors, exact image pins, own locks
and conditions. It excludes scene metadata, settings, packages and live values.
Selected descendants already contained by selected ancestors are copied once.

Paste requires a complete fresh-ID map and explicit root/group insertion point.
Only IDs and children references are rewritten. Parent-local coordinates and display
intent remain exact. Destination theme and resource closure remain in force; missing
pins reject the whole edit. Scene 0.3..0.5 promotion requires existing capabilities.
Undo/redo and Apply reuse existing scene/resource/transaction owners and limits.

The trusted context must admit editor.clipboard and current authenticated desktop
or console policy must grant sensitive clipboard disclosure. Each outgoing borrow
rechecks permission. Policy updates, disconnect, successful reload/discard/request
admission, close and ownership loss erase the snapshot. Regrant does not restore it.
The owner promises logical erasure, not allocator scrubbing or recall of bytes
already delivered to another application.

## Verification and retained evidence

Eight portable families cover complete forests/all seven kinds, exact expected
scenes, mapping/ownership/version rules, malformed/oversized/deep inputs, missing
resources, atomic failure, history, policy, lifetime and cross-epoch reconciliation.
A single paste inserts 129 objects; invalid total count, combined scene byte size
and depth after destination insertion reject without changing any draft state.
Wrong-ID and metadata-leak witnesses differ from the frozen complete expectations.
Those expectations and this package were frozen before production changes; none
was revised to fit implementation output.

All 195 affected checks pass on each development profile. Full portable suites pass
372 Linux GCC13, 369 Windows GCC15 and 366 v141_xp checks (1107 total). Four existing
Linux native families pass: EDITOR-FORM, EDITOR-VISIBILITY, EDITOR-FONTS and
THEME-HISTORY. These regress existing controls/persistence; they do not test or
qualify native clipboard transfers. Historical compiler use on contemporary Windows
does not qualify a historical OS.

The attempt index (local archive: `out/evidence/w-10-scene-fragments-attempts.json`)
preserves 16 source-bound executions, logs, exact source archives
and final executable identities. The initial build refused misleading indentation
and unnecessary copying in new test code; that failure remains archived. Production
acceptance examples and existing schemas were unchanged. Workspace preflight
refusals also remain in execution records. Cleanup first refused a mismatched smoke
archive and deleted nothing; the completed cleanup retained all mismatches, original
ZIPs and test records, removing only byte-verified extracted copies. Prior committed
attempt duplicates were separately verified before removal. The 7-GiB bound remains.

Specification/tool/integrity and staged identity results are linked by
the [machine handoff](checkpoints/scene-fragments.json).
Existing Windows symlink privilege skips remain explicit. Original oracle, native
and qualification failures from earlier checkpoints are not rewritten.

Shared build utilities moved from the retired root into `source/build/` at the
user's request. Raw evidence moved byte-for-byte into ignored `out/evidence/` and
was removed from tracking. Historical records retain their original source paths
and hashes; their pre-move paths are archive identities, not current build commands.
The four target/capability fixture path examples changed only to the new tooling
location. Fresh configure/build and portable regression checks cover that migration;
the checkpoint record distinguishes the original and relocated executions.

## Next boundary

Native clipboard actions remain disabled. Close bounded asynchronous custom-target
transfers before allocation, per-chunk authorization, timeout/cancel/late-response
ownership and stale-draft reconciliation. Implement explicit native Copy/Paste and
prove exact bytes, foreign-owner preservation, revoked serving, invalid transfers,
undo and durable save/reopen using independent requester/owner processes.

Recovery drafts, installed controller/catalog/policy ownership, scene-aligned desktop
entry/restoration, complete accessibility/performance and all five complete editions
remain required. W-10 stays in progress; no release or platform qualification is
claimed by this checkpoint.
