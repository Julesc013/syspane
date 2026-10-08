---
type: "SysPane Work Package"
title: "Thread-bound profile storage for asynchronous commands"
description: "Retain native profile ownership across joined command workers."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T12:00:00+11:00"}
sp_id: "SP-W08-PROFILE-WORKER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-STARTUP", "SP-W08-COMMAND-SESSIONS", "SP-W08-SUPERVISION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Thread-bound profile storage for asynchronous commands

LinuxProfileStore and its profile leases belong to one creating thread. The
existing AsyncCommands composition creates and joins a transaction worker per job.
Connect these owners without transferring a native store between threads or
weakening actual transaction-stop proof. Add LinuxProfileWorker in the existing
platform component tree, implementing the existing blocking GenerationStore API.

## Ownership and calls

Construct, use and destroy exactly one LinuxProfileStore on a dedicated storage
thread. Retain that thread and all three profile locks across transaction jobs.
Copy construction inputs before dispatch; use the existing fixed native policy
source by default. Trusted test policy/transition functions remain in-process
injection only, with no product argument or environment override.

The facade is synchronous. Construct it before starting the controller session
loop, and call it from the serialized transaction worker after startup. It is
never a GTK callback API. AsyncCommands may obtain its initial state during
controller startup; its established session-loop queries and receipt snapshots
remain free of store calls. Command worker join, completion delivery, ledger bounds,
policy/cancellation permits and transaction-watch messages retain their contracts.

Admit one outer facade invocation at a time, including its reply transfer. A
concurrent invocation or close fails immediately with profile_worker.busy; it does
not wait in a second queue. One bounded invocation slot owns no extra command ledger
or scheduler. Existing document/resource bounds apply; argument references remain
alive until the synchronous call returns. Native exceptions propagate to that
caller after the invocation has returned and its callable has been destroyed.

During the native publication guard, allow synchronous read-only facade calls on
the storage thread (load, receipts, reconcile, verified_paths, generation_token and
recovered_previous). They execute directly on the same native owner. Reject nested
publication, lifecycle changes and other storage-thread reentry with
profile_worker.reentrant. This includes policy/transition callback reentry outside
the publication guard. Existing LinuxProfileStore policy reentry rules still apply
inside it. A recursive call must never deadlock or release the outer invocation.

close is a blocking, serialized lifecycle operation. It stops admission, destroys
the native store on its owning thread and joins that thread before returning.
Repeated close after successful close is harmless; later operations fail with
profile_worker.closed. Destruction performs the same close and requires no live
caller, as for ordinary C++ object lifetime. Startup exceptions join the failed
storage thread before escaping. No worker is detached and no thread is killed.

## Process supervision remains necessary

This adapter preserves affinity; it cannot bound a blocked filesystem operation.
Its controller must use the existing independent startup, transaction and health
deadlines before installed use. Shutdown must invalidate commands and join their
workers before closing this facade. An uncooperative call requires exact process
termination and native reap, followed by a fresh profile owner and producer epoch.
Never destruct a live facade on the UI loop, claim cancellation proves stop, or
replay an uncertain commit. A closed facade is not evidence of visible activation.

## Fixed acceptance

Freeze this package and profile-worker-cases.json before production edits. Reuse
the literal initial documents and command from the earlier startup package; do not
derive expected stored output from this adapter's replies. A native non-root ext4
runner verifies initial bytes, two sequential real command workers, held profile
locks between jobs, exact revisions and receipts, and no extra generation on replay.

Hold a policy read and a commit before publication. Independently inspect native
task IDs: all storage callbacks use the same thread, distinct from the caller and
transaction worker. Verify concurrent load/close refuse, result.get stays pending,
cancel before the permit preserves revision zero, and a completion returned before
worker exit cannot release the AsyncCommands slot. Actually join before finish.

Cover permitted guard readback, forbidden recursive publication/lifecycle/source
reentry, policy invalidation and failed startup, normal close/reopen and closed
calls. Kill an owned process while held before selection and after durability;
prove exit, reopen under a new epoch, independently inspect coherent bytes and
reconcile the original request. The after-durable case must yield revision one
exactly once. Keep failed runs and a deliberate wrong-output oracle control.

Run native.PROFILE-WORKER, existing PROFILE-STARTUP, PROFILE-OWNER and command/
reconciliation tests, plus component graphs. Source-bound records name exact
artifacts and environment. This package supplies the storage/command connection;
installed controller/IPC lifecycle, protected-policy positive qualification,
catalog import, complete native UI and all five release editions remain required.
