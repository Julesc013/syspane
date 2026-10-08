---
type: "SysPane Work Package"
title: "Recovery draft native Apply boundary"
description: "Verified generation identity and explicit recovered Apply through the private Linux store."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:00:00+11:00"}
sp_id: "SP-W10-RECOVERY-APPLY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-RECOVERY-DRAFT", "SP-PERSISTENCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Recovery draft native Apply boundary

LinuxGenerationStore::generation_token returns the lowercase SHA-256 of the exact
selecting-record bytes verified by that loaded store. It performs no additional
filesystem access. The store must have a current verified generation and must not
be poisoned, damaged or using read-only previous-generation recovery. Otherwise it
throws storage.unavailable. A newly initialized empty store has no token. The token
belongs to the same loaded snapshot as load(), under the existing writer lock;
it is not a claim about later external filesystem changes. Reopening verifies the
files again. Publication retains the existing external-change and durability guards.

Normal publication updates the token only with the durable current generation.
An indeterminate publication prevents token access until a new store owner recovers
and verifies the selecting record. Even a valid same-revision storage republication
has a new generation identity. This is a storage-bound identity, not a revision
counter or permission. No legacy document/selector format changes.

Freeze this package and native cases before changing the store. In the admitted
non-root ext4 laboratory, independently compute SHA-256(current.json), compare it
to the accessor across separate processes, and verify refusal for empty, corrupt
current/fallback, corrupt previous/damaged and post-selection indeterminate stores.
For indeterminate publication, reopen and verify the new token and unchanged exact
documents; do not infer that the old owner remained usable.

Use the already frozen recovery-draft literals. A capture process loads the real
generation, edits and emits its record, then exits. A new process explicitly
inspects/restores the supplied record, proves one-step undo/redo, and requests Apply
through the existing transaction interface. Inspect exact documents, request bytes,
resource manifests and assets independently in the stored generation. Exercise
ordinary scene edits and canonical theme edits. Neither capture nor restore may
change current.json. Current policy denial and a mismatched token refuse restore
without a request or revision change.

For each edit kind, interrupt the separate commit process immediately after its
durable transition, before it can return its result. Reconcile the original request
through a newly opened store/controller epoch; the editor must settle at revision
41 with no unresolved request or history. Reopen in another owner and reject the
old generation-40 recovery bytes. There must be exactly one new generation and no
revision 42. A deliberately wrong scene report must fail the independent scene
comparison. Preserve the cut exit, original request and observations.

The test harness transports a recovery record between processes; it is not a
product recovery-file writer. This experiment does not qualify recovery retention,
startup offers, native controls, hardware power loss or other filesystems. The
native storage/UI gate in the parent package remains mandatory for the full editor.
