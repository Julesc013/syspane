---
type: "SysPane Work Record"
title: "Bounded native recovery queue checkpoint"
description: "Coalesced recovery I/O with exact helper identity, retirement fences and observed process exit."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T15:33:49+00:00"}
sp_id: "SP-RECOVERY-QUEUE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-RECOVERY-QUEUE", "SP-RECOVERY-STORE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded native recovery queue checkpoint

Baseline 830d05d928c04a787af38fc2d0d1f65dac5f5062. The
[queue package](packages/w-10-recovery-queue.md) adds LinuxRecoveryQueue and
SysPane.RecoveryWorker, reusing the existing Child, frame codec and
[private recovery store](recovery-store-handoff.md). Recovery-file I/O executes in
a separate held native process. The serialized parent loop transfers bounded bytes,
observes the child without waiting and retains at most one active and one latest
pending operation. These development components are not installed product recovery.

The caller supplies trusted session/profile/generation identity, policy revision
and separate read, retain and erase grants. Initial load must complete and be
consumed before mutation. Every helper guard requests a matching parent grant.
Successful results require exact context/ticket, complete bytes, channel EOF and
verified zero child exit. The five-second operation deadline includes startup,
transfer, grants and exit observation; progress cannot reset it.

Captures coalesce while an active write finishes. The resulting verified digest
becomes the next helper's expected record; an external change refuses replacement.
Retirement removes pending capture, seals this owner against further writes, waits
for its active operation and then retires only the matching result. Absent retirement
is still a fence. An unknown result discards pending work and requires verified reopen.

Close/invalidation drops private parent buffers, rejects new work and requests stop
of the exact held child. The host keeps polling and retains the closing owner until
actual exit is confirmed. It does not use the Child emergency destructor as normal
GTK shutdown. A granted action can race invalidation; the owner never claims that
an unacknowledged mutation was absent or that retained bytes were deleted. No further
write is possible from that child after confirmed exit or successful retirement.

## Verification

RECOVERY-QUEUE passes 31 native scenarios in the admitted non-root ext4 laboratory.
The independent Python observer drives the real queue process and ordinary worker,
compares exact files and returned record identities, and observes held native process
lifetimes. A separate fault-worker executable supplies named faults; ordinary helper
entry cannot select them from filenames or untrusted record bytes.

Cases cover exact initial/maximal/empty/opaque byte records, old/intermediate/latest
coalescing, a held writer, external replacement, retirement during writing, retirement
of absence and rejection of later captures. Prepublication and postpublication closure
remove pending bytes and completions, kill only the held helper and preserve the
specified coherent file. Parent death independently terminates a stopped helper.

Other cases check separate grants, wrong-thread calls, size bounds, retained-load
buffer release, stale guard requests, forged binding/ticket, duplicate/trailing/
oversized replies, nonzero exit after a plausible reply and the five-second hang
deadline. A direct socket peer supplies stale, mismatched and denied grants to the
ordinary worker; no mutation is admitted. Storage refusal before any grant preserves
its unchanged outcome. Parent calls remain under the existing experiment's 100 ms
observation bound. A wrong final-byte expectation is detected independently.

The earlier 28-case run passed before the opaque-byte and early-refusal additions.
Both records remain preserved. Review tightened the observer to await the expected
replacement ticket after SIGCONT, avoiding confusion with a not-yet-resumed old
process. No observed failure or fixed expectation was removed by that change.

Existing RECOVERY-STORE passes 74 scenarios, and RECOVERY-APPLY and
RECOVERY-STORED-APPLY each pass eleven. All three development profiles configure
and build; their component graph and forbidden-dependency checks pass. These checks
do not qualify historical Windows execution, native controls or a full desktop edition.
No shared runtime behavior changed; previous full portable results remain separate.

The [compact checkpoint](checkpoints/recovery-queue.json) binds fixed inputs,
source archives, native reports, exact executables, action results and specification
checks. Raw recordings and binary copies remain ignored local out/evidence content.
The original schema/fixture bytes and prior recovery contract/example hashes remain.

Specification validation passes 46 schemas and 158 fixture expectations. Tooling
runs 62 tests: 60 pass and two existing Windows symlink-privilege cases skip.
Generated projections and the unchanged settings resource fixture also pass.

## Workspace evidence and open work

The build preflight stopped after the first new queue/runtime/helper artifacts.
Thirteen completed native directories were archived and byte/node verified before
11858810 duplicate bytes were reclaimed. The next preflight still could not reserve
the required build growth. The measured development allocation now permits 8 GiB,
with the same build/test/package reservations. Available checkout/native storage,
the original stop and exact decision are preserved; product limits and fixed
acceptance remain unchanged. The [campaign admission](campaign-admission.md) records
this routine reversible allocation. Prior native observation failures and GTK
shutdown diagnostics remain unresolved.

Keep W-10 in progress. Connect the native editor's verified committed generation
and current recovery authority to this owner. Define capture scheduling and the
interaction of Keep for later with subsequent editing before enabling automatic
retention. Add real Restore, Discard recovery draft and Keep for later controls;
Apply/discard must fence and retire the matching record without a late-write race.
Close and reap on policy, session or generation invalidation and expose unavailable
or unknown recovery state honestly. Never offer uninspected bytes or perform
recovery-directory I/O in GTK callbacks.

Exercise actual editing-process death, startup offers, private-buffer erasure and
independent native observations through that integration. Installed controller/
catalog/policy ownership, scene-aligned entry/restoration, full accessibility and
performance, all platform adapters and all five complete editions remain required.
No hardware power-loss, secure-erasure, privileged operation, public release or
Git history rewrite is claimed.
