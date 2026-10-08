---
type: "SysPane Handoff"
title: "Native profile storage and asynchronous command ownership"
description: "One native profile thread across joined transaction workers."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T12:00:00+11:00"}
sp_id: "SP-PROFILE-WORKER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-WORKER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native profile storage and asynchronous command ownership

LinuxProfileWorker connects the thread-bound LinuxProfileStore to existing
AsyncCommands. It creates, uses and destroys the native store on one dedicated
storage thread and retains all profile locks between commands. Each transaction
worker still has to exit and be joined before AsyncCommands accepts completion.
No command, receipt, protocol, policy or persistence format changes.

The synchronous facade admits one outer invocation. Concurrent calls and close
refuse immediately; publication guards can read back through the facade on the
same native thread. Recursive writes/lifecycle calls and policy-source reentry
refuse. Explicit close destroys the native owner and joins its thread; later calls
refuse. Native startup errors join before escaping. All native I/O remains on the
store's creating thread, including protected-policy reads and first-profile setup.

## Verification

The fixed package and literal case manifest precede implementation. Sixteen native
cases pass on the admitted non-root Linux/ext4 environment, observing actual kernel
task identities and files independently. Two sequential command workers retain
one storage owner; profile locks exclude a competing process between transactions.
Exact initial and committed documents, resource closure, revisions, receipts and
same-request replay are checked against the earlier literal startup fixtures.

Held policy reads reject concurrent facade calls. Cancellation before publication
preserves revision zero. A completed transaction held before thread exit still
reports pending; only a real join releases its result. Guard readback, recursive
refusal, policy invalidation, failed startup and joined close/reopen pass. Two
actual process kills cover pre-selection and post-durability interruption. Fresh
epoch reconciliation recovers the latter as revision one with no automatic replay.
A deliberate wrong-output expectation is rejected by the independent file oracle.

Existing profile/startup/storage and command/reconciliation checks remain required;
their exact execution results and artifact identities are recorded in the
[checkpoint](checkpoints/profile-worker.json). The current native protected-policy
source remains unavailable and fails closed; positive cases use the separate
in-process test fixture, without changing machine policy. Raw source captures,
native files and observations are ignored local out/evidence/profile-worker*
content. A fresh checkout regenerates its own evidence using the developer guide.

## Next admitted work

Connect this composition to the installed controller/IPC and existing independent
health/transaction supervisor. The facade blocks while native I/O is pending: it
is appropriate for controller bootstrap and transaction workers, never GTK or a
running session loop. It cannot bound a hung filesystem operation. Installed use
still requires an independently held process, startup/operation deadlines, actual
stop/reap, new epochs and reconciliation without replay. Controller shutdown joins
transaction callers before closing storage; an uncooperative child must be stopped
as a process rather than destroying live C++ thread state.

Then connect native settings/editor startup and the configured import catalog,
and qualify protected-policy deployment in an admitted environment. Full layers,
non-Linux storage/ownership, accessibility/performance, native lifecycle and all
five complete desktop editions remain required. W-08 stays in progress; this
checkpoint does not qualify an installed application or authorize publication.
