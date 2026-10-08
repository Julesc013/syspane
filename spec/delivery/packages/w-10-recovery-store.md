---
type: "SysPane Work Package"
title: "Private native recovery record storage"
description: "Bounded exact-byte retention with conditional replacement, retirement and process-cut evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T14:05:29+00:00"}
sp_id: "SP-W10-RECOVERY-STORE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-RECOVERY-DRAFT", "SP-W10-RECOVERY-APPLY", "SP-PERSISTENCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Private native recovery record storage

Implement LinuxRecoveryStore as the filesystem owner for one recovery record per
private profile. This is required by the full editor; its native queue and
Restore/Discard recovery/Keep controls remain the next integration gate. Do not
perform filesystem work in a GTK callback. The admitted experiment is the existing
non-root Linux development profile on ext4, separate from committed generations.

## Storage and authority

The host supplies an existing absolute private directory, bounded to 4096 bytes,
without empty, dot or parent components or symbolic-link traversal. This primitive
does not choose/create a profile root or repair permissions. The directory must be
owned by the effective user, mode 0700 without special bits, on the admitted
ext-family primitive profile. Actual qualification here covers ext4 only.

Only .writer, draft.json and .pending may exist. Regular nodes must have the same
owner, mode 0600, one hard link and no special bits. The lock is empty. Both data
files are bounded to 786432 bytes. Refuse symlinks, directories in file positions,
FIFOs, sockets, hard links, non-private modes, oversized nodes and foreign entries
without following or recursively cleaning them. Nonblocking opens prevent a FIFO
from hanging validation. Verify descriptor metadata and pathname identity around
reads and before mutation. Recheck the selected root and lock identity at operation
boundaries. Preserve foreign content on refusal.

Hold an exclusive nonblocking flock on .writer for the owner's lifetime. Use one
serialized thread; reject concurrent/reentrant calls. The lock coordinates cooperating
owners; it is not a sandbox against an actively hostile process with the same user
authority. Check observed substitutions and exact identities without claiming to
eliminate every same-user race after the final check.

A required guard callback checks current native retention/disclosure or explicit
deletion authority and session/generation lifetime. Missing, false or throwing guards
deny the operation. Snapshot checks before reading and again before returning bytes.
Mutation checks before cleanup and immediately before its publishing/removal action.
Callbacks must not reenter or destroy the store. Policy denial alone does not grant
retirement. A successful guard is the authorization point for the following serialized
filesystem action; the future owner must serialize invalidation with that point.

The store treats record bytes as opaque, bounded data. It does not parse commands,
grant a role, import packages, commit configuration or activate a scene. Before
offering/restoring data, the native owner must use the existing EditorDraft inspection
and restore contract against its separately verified committed identity and current
policy. Invalid records remain discardable with explicit deletion authority.

## Snapshot and conditional operations

Snapshot returns optional published bytes, their SHA-256 (absent for no record),
whether a bounded staging file exists, and a RecoveryVersion. That version contains
a random 128-bit instance identity and uint64 sequence, initially zero. The digest
belongs to the exact published bytes, not an alleged field inside the record.

Replace and retire require the exact instance, sequence and expected optional digest.
Reject a stale version, changed on-disk record, or exhausted sequence without modifying
the record. After successful initial admission, increment the sequence before any
staging work, including on a later failed attempt. This invalidates earlier queued
operations. Retirement of an already absent matching record also increments it;
an old queued create cannot resurrect a retired record. A new store instance never
accepts a previous instance's version. The future coalescing owner obtains a fresh
snapshot/version when dispatching its next admitted operation.

Replace accepts nonempty bytes up to the limit and publishes their exact bytes.
There is no normalization, appended newline, truncation or cumulative history.
Snapshot may return a bounded malformed or empty published file for explicit
diagnosis/discard; it never makes those bytes an executable recovery draft.

## Replacement, retirement and errors

After admission, remove only a validated leftover .pending and synchronize the
directory. Create .pending exclusively with mode 0600. Write a bounded first part
and remainder, handling short writes and at most sixteen EINTR retries per primitive.
Synchronize the staging file. Recheck current/root/lock/staging identities, exact
staged bytes and current authorization, then rename .pending over draft.json in the
same directory. Synchronize the directory before returning durable. At most the old
published record and one staging record coexist. Never offer .pending, even when
no published record exists. Reopening does not promote or automatically delete it.
The next explicitly authorized replacement/retirement may remove it.

Retirement first removes validated leftover staging, then rechecks the exact expected
published digest and current deletion authority. Unlink only that matched record
and synchronize the directory. No recursively computed cleanup, purge of another
record, backup history or in-place truncation. Byte-identical replacement still uses
the replacement protocol and a new operation version.

Operations report unchanged, durable or unknown plus a bounded error code. A failure
before published rename/unlink preserves the previous complete published bytes;
partial staging may remain. After publishing/removing but before successful completion,
report unknown and poison the owner: no subsequent snapshot or mutation succeeds.
Reopen under a new owner and verify actual state. No false unchanged or durable result.
Errors do not authorize an automatic retry, forced overwrite or restoration.

Use fixed observable transitions: admitted, pending_removed, pending_created,
pending_partial, pending_written, pending_flushed, publish_ready, published, durable
for replacement; admitted, pending_removed, retire_ready, retired, durable for
retirement. Probe hooks are development fault instrumentation, not a product callback
or a new transaction ledger. The named stages surround the actual native primitives.

## Fixed acceptance and next integration

Freeze this package and literal old/new records plus expected phase outcomes before
production edits. An independent Python process observes each stage, kills only its
held probe, reopens through a fresh process and checks exact published bytes, staging
state, directory entries and modes. Cut every listed replacement and retirement stage,
including creation without an earlier record. Before publication reopen yields the
old record/absence; after publication it yields the exact new record/absence.

Check exact byte ceilings, malformed opaque bytes without activation, old/new record
replacement, cleanup of interrupted staging, at most three directory entries, stale
digest/sequence/instance rejection, absent retirement and late-create refusal, current
guard revocation at publication/removal, guard exceptions/reentrancy, writer exclusion,
all refused filesystem entries, observed root/lock/staging/current substitution,
prepublication failures and poisoned-owner recovery. A wrong-byte witness must fail
the independent comparison. Preserve failures and source/artifact/environment identities.
Run existing shared recovery checks and native Apply regression, plus component graph
checks on all three development profiles. Keep all earlier fixed fixtures unchanged.

Then connect this owner to one coalesced native queue and explicit recovery offers.
Queue at most one active and one latest pending operation; bind every completion to
its editor session, current generation and operation version. Invalidation erases
queued bytes, and retirement cannot be followed by an obsolete write. Qualify process
exit during native editing and actual Restore/Discard/Keep controls before enabling
product recovery. No hardware power-loss, secure-erasure, Windows/macOS storage or
complete-edition claim follows from the ext4 process-cut experiment alone.

The primitive sequence follows Linux [rename](https://man7.org/linux/man-pages/man2/rename.2.html),
[fsync](https://man7.org/linux/man-pages/man2/fsync.2.html),
[open](https://man7.org/linux/man-pages/man2/open.2.html) and
[flock](https://man7.org/linux/man-pages/man2/flock.2.html) contracts. In particular,
file synchronization and directory synchronization are separate obligations; native
process-cut observations remain necessary evidence for this named profile.
