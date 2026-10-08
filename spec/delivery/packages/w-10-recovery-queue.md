---
type: "SysPane Work Package"
title: "Bounded native recovery operation owner"
description: "Coalesced private-file operations with held child lifetime, explicit grants and retirement fences."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T02:05:00+11:00"}
sp_id: "SP-W10-RECOVERY-QUEUE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-RECOVERY-STORE", "SP-W10-RECOVERY-DRAFT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded native recovery operation owner

Add LinuxRecoveryQueue and one recovery I/O helper using the existing held Child
owner, existing frame codec and LinuxRecoveryStore. Recovery directory I/O, reads,
writes and synchronization execute in the helper. Parent operations perform bounded
memory/IPC work and native child launch/observation; they never wait synchronously
for a recovery-file operation. The helper is a private component, not a public
service, second transaction ledger or command-execution interface.

## Identity and admission

The trusted caller supplies an immutable context: session and profile identifiers,
verified 64-character lowercase generation digest, uint64 policy revision, and
separate read, retain and explicit erase grants. This does not derive grants or
identity from record bytes. The caller must invalidate the owner on any relevant
policy, session or committed-generation change. New context requires a fresh owner;
regrant never resumes a closed owner or implicitly restores content.

Construction queues an initial load, ticket 1. Initial load requires read authority.
No replacement or retirement is admitted until that load succeeds and its completion
is consumed. Successful load reports exact optional bytes, their digest and orphan
staging presence. A malformed bounded record remains opaque; EditorDraft inspection
under current authority remains mandatory before presenting a restoration offer.

All parent methods belong to one thread and reject wrong-thread/reentrant calls.
Tickets are uint64, strictly increasing, never reused; exhaustion refuses admission.
Each admitted capture is nonempty and at most 786432 bytes. Replacement additionally
requires retain authority; retirement requires explicit erase authority. Denial
does not silently delete retained files. Queue methods never infer current policy.

## Coalescing and retirement

At most one helper operation and one pending operation exist. Replacing a pending
capture discards its bytes; the latest ticket wins. An active capture may complete
before a newer pending capture. Its exact successful digest advances the storage
expectation, but its superseded completion is not delivered as the latest capture.
The next helper receives that expectation and must compare its fresh snapshot before
mutating. No forced overwrite of a changed record and no automatic retry on error.

Retirement seals this owner against further captures immediately, removes a pending
capture and superseded completion, and waits for its active operation to finish.
It then conditionally retires the resulting matching record. It is pending until
its own durable result and verified child exit; queuing retirement is not deletion.
Retirement of absence is still a completed fence. A late capture cannot follow it.
If the active operation fails or becomes unknown, do not guess the record identity:
discard pending work, report unavailable and require a new verified owner.

Retain at most one deliverable completion, bound to the full immutable context,
ticket and operation. Successful load and the latest capture/retirement can be
consumed once. Failed or stale completion cannot release another active slot.
Expose state, active/pending tickets, held process identity, retained buffer bytes,
bounded error code and whether the child has actually been reaped. Do not report
idle, ready or successful retirement while a helper is still live.

## Invalidation and process lifetime

Invalidate/close immediately rejects new work, drops pending and deliverable bytes,
clears partial input/output frames, closes channels and requests stop of only the
held helper. It does not wait or assert termination. Poll continues until Child::wait
confirms actual exit, then reports closed and reaped. No next helper starts before
the preceding helper is reaped. The host retains a closing owner until that proof,
then destroys it. The existing Child emergency destructor is not the normal GTK
shutdown path. Parent death arms the existing native helper lifetime before I/O.

The helper requests a fresh parent grant at every LinuxRecoveryStore guard call.
The parent grants only the exact current context, active ticket/operation and next
guard sequence. Closing or changed authority prevents further grants and consumes
no returned record. A grant is the linearization point for its following serialized
filesystem action, as in the storage contract. Invalidation after a granted action
can race with actual publication; the outcome remains unknown until a fresh owner
verifies storage. It does not authorize deletion or claim that old bytes vanished.
After closed/reaped or durable retirement, the former helper cannot publish later.

Any timeout, abnormal exit, malformed/oversized/out-of-order reply, unexpected EOF,
unknown storage publication or mismatch makes the owner unavailable, drops pending
work and stops its held child. Preserve whether a returned storage failure was
unchanged or unknown; an unacknowledged mutation is conservatively unknown. Successful
results require a matching complete reply, channel EOF and verified zero exit.
No success from output alone, signal requests, process IDs or an observation timeout.

Use one five-second monotonic deadline per dispatched helper operation, including
startup, frame transfer, grant exchanges and exit observation. Check elapsed time
before accepting buffered progress. A hung helper cannot extend its deadline by
sending progress. Poll transfers at most 262144 bytes each direction and performs at
most 32 receive attempts per call; EINTR/EAGAIN returns to the caller within those
bounds. Stopping polls remain nonblocking. Error output is at most 1024 bytes and
never becomes a product message containing arbitrary native text.

## Private helper frames

Use the existing four-byte big-endian frame codec with limit 819201. A payload is
one UTF-8 JSON header, one NUL separator and raw optional record bytes. The header
is at most 32768 bytes and the raw suffix at most 786432. Parse headers with the
existing duplicate-key/depth/node checks. No implicit newline, base64 expansion or
record normalization. A load result may contain empty-but-present opaque bytes.

Every header carries kind, binding, ticket and operation. Binding has exactly
session, profile, generation and policy_revision; revision and ticket use canonical
uint64 decimal strings, and operation is load, replace or retire.

| Kind | Additional header members | Raw suffix |
| --- | --- | --- |
| request | root (bounded absolute caller-selected directory), expected (null or digest) | Nonempty record for replace; empty otherwise |
| guard | guard (canonical sequence 1 through 8) | Empty |
| grant | guard (matching sequence), allow (boolean) | Empty |
| result | outcome, error, digest, present, pending | Exact record for successful load; empty otherwise |

Requests have no extra members. Load requires expected null. The worker compares
the supplied expected digest against its fresh store snapshot for mutations and
passes that snapshot's exact RecoveryVersion to the store. Request/grant identity
must match exactly. Extra messages, repeated guard sequence, raw control-frame
bytes, multiple results or trailing input are errors, not ignored extensions.

Successful load uses outcome loaded and matching present/digest/raw bytes; replacement
and retirement use durable. Replacement reports the exact submitted digest and
present true; retirement reports null digest/present false. Successful mutations
report pending false. Failure uses unchanged or unknown and a bounded lowercase
code of at most 64 characters; digest is null, present/pending false and suffix
empty. Those failure fields make no assertion that an existing file is absent.
No record bytes are disclosed on a denied or failed operation.

The helper receives only the existing clean native launch environment and stdio,
closes the held executable descriptor and arms its expected parent lifetime. It
does not open a listener, import packages, execute record contents or activate UI.
Fault hooks belong to a separately built development probe; ordinary helper entry
does not select faults from filenames, record bytes or caller-controlled metadata.

## Fixed acceptance and next boundary

Freeze this package and literal operation traces before production edits. Test real
separate helpers on the admitted non-root ext4 profile: initial read, exact maximum,
coalesced old/intermediate/latest captures, a held active writer, replacement conflict,
retirement while active, absent retirement and rejection of post-fence captures.
Independently inspect exact files, child exit and operation/context identities.

Hold a helper at prepublication and postpublication stages, invalidate/close, and
verify no later completion or write after confirmed exit. Preserve either coherent
record if invalidation races an already granted publication. Check stale grants,
forged binding/ticket, duplicate/trailing/oversized replies, nonzero exit after a
plausible result, hang deadlines, parent death and private-buffer release. A deliberately
wrong final-record comparison must fail. Re-run the existing storage and composed
Apply tests, plus component graph checks on all three development profiles.

This queue supplies the native I/O owner. Actual editor capture scheduling, independent
current-policy checks, crash startup offers and Restore/Discard recovery/Keep controls
remain the next integration gate. Do not enable product recovery or claim other OS,
hardware power-loss, secure-erasure or complete desktop qualification from this work.
