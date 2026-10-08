---
type: "SysPane Work Record"
title: "Complete-scene command checkpoint"
description: "Negotiated full-scene edits, bounded admission and coherent native request recovery."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T04:33:13Z"}
sp_id: "SP-LARGE-COMMANDS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-LARGE-COMMANDS", "SP-NATIVE-EDITOR-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Complete-scene command checkpoint

Source baseline: `c7c2f32489caec1c1cba143ec3c48cef707a86e5`. The
[package](packages/w-08-large-commands.md) closes the mismatch between 256 KiB
authored scenes and legacy 16 KiB commands. W-08/W-10 remain in progress; this is
shared implementation and owned Linux laboratory evidence, not a complete edition.

Command 0.5 permits 320 KiB of original UTF-8 body and canonical JSON. Its negotiated
parser provides wrapper headroom while independently rechecking each scene's
existing byte/node/depth limits. Exact document versions, transaction/large-command
features and a 328,704-byte frame floor are required. Content and scene-content
permissions remain independent. Legacy commands and non-command messages retain
their original limits; health and preview-only owners gain no mutation authority.

The existing ledger still reserves original body bytes plus 4 KiB per result within
16 MiB, alongside its principal/connection/record bounds. Fifty maximal bodies fit;
the next returns busy. Retained results survive until their existing expiry, and
replay compares original bytes. No second ledger or chunk assembly owner is added.

SettingsDraft, EditorDraft and EditorForm accept explicit host opt-in. Enabled drafts
emit 0.5 and keep exact requests through cancellation and unresolved outcomes.
Legacy construction remains compatible and retains an oversized rejected draft.
Preset preview accepts the corresponding capability while preserving resource pins.

Linux generation manifest 0.3 binds the original request through a SHA-256 identity
and separate private `request.json`. It is flushed before manifest/selection and
validated with document revisions, command identity and the complete resource
closure. Old manifest 0.1/0.2 inline identities remain readable. Missing, oversized,
linked, substituted or corrupt requests cannot enter a recovered mixed generation.
Current/previous receipt ownership and read-only coherent fallback remain unchanged.

## Verification and preserved failures

Before production changes, archive literal initial/expected scenes, exact byte and
ledger limits, the new schema and a negative missing-resource example. The fixed
scene contains multibyte characters, quotes and backslashes; a move reaches exactly
262,144 canonical bytes. Those inputs remain unchanged.

The five new portable families cover raw/canonical size, one-byte overflow,
node/depth wrapper boundaries, unchanged legacy rejection, negotiated feature/frame
requirements, policy, exact replay, ledger exhaustion/expiry, Apply, cancellation,
confirmed worker stop and cross-epoch receipts. All 88 affected checks pass on each
development toolchain. The historical toolset runs on contemporary Windows and
does not qualify a historical operating system.

Twenty-four independent native cases compare resource-free and resource-backed
store bytes and exact request hashes, kill
processes at request/manifest/selection/durable transitions, corrupt request files,
and exercise authenticated IPC through the existing independent supervisor. Actual
process exit precedes replacement; restart reconciliation does not add revision 42.
GTK tests drive full-size drag/undo/redo/save/reopen, cancellation, policy erasure
and lost acknowledgement/restart. Deliberately incorrect stored geometry must fail
the independent expected-scene comparison. Legacy native storage/content/IPC and
editor/settings cases remain part of regression evidence.

The first build found two strict indentation warnings in test code. The first
native cancellation observer raced large-command validation: cancellation could
finish before the deliberately stalled preparation began. Preserve that failure;
the corrected observer first records the native worker's timed-sleep wait channel
and then tests cancellation without confusing it with proof of process exit.
No expected scene, budget, recovery deadline or outcome was weakened.

`out/evidence/w-08-large-commands-attempts.json` binds every preserved
attempt, exact source archive, binary identity, CTest log and native record.
`out/evidence/large-commands-handoff.json` separately records schema/tool
checks, staged identity verification and remaining qualifications. Documentation
and independent observer changes after compilation are identified explicitly.

## Next required boundary

Close remaining authoring/property contracts and connect installed controller,
catalog and policy ownership to scene-aligned editor entry and restoration. Keep
the permanent wall passive and require independent escape before mapping the editor.
Snap/grid/guides, align/distribute, complete binding/content/theme/group panels,
lock/visibility/typography, clipboard authority and recovery drafts remain required.

Maximum-size performance qualification, representative accessibility/localization,
Windows/AppKit adapters, non-Linux durable storage, historical floors/labs, complete
editions and release lifecycle/authority remain open. Process interruption evidence
does not establish power-loss guarantees or installed desktop qualification.
