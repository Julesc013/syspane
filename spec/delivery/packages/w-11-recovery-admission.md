---
type: "SysPane Work Package"
title: "Native recovery helper admission"
description: "Verify transferred recovery observations against local session and held native directory identities."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T01:05:00+00:00"}
sp_id: "SP-W11-RECOVERY-ADMISSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-RECOVERY-TRANSFER", "SP-W11-EDITOR-HELPER-WORKER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native recovery helper admission

Connect the existing verified helper worker to native recovery admission. Keep one
recovery handle, queue, writer and command owner. Existing explicit path experiments
retain their behavior. Installed recovery requires the admitted path described here;
this package does not yet enable it or remove the consumer-validation latency gate.

The trusted host supplies a local ProfileLocation, a validated ProfileRecoveryView
and a current-session callback. That callback returns no authority after disconnect,
supervisor replacement, session withdrawal or policy loss. Its connection, epoch,
profile, editor session, document revision and policy revision must exactly match
the immutable view. Retention must remain allowed; erase additionally requires both
the original view's permission and current erase permission. Generations are exact
lowercase SHA-256 identities. Changing the saved revision invalidates this admission;
post-commit draft retirement needs separately composed original-request reconciliation.
Do not reinterpret a new revision as authority to retire an old draft.

Before accepting a recovery task, derive its expected path from the local location
and compare it to the view. Independently open and hold its state and recovery
directories without symlinks or creation. Reuse existing profile path, ancestor,
same-user/private-permission and ext4 rules. Match every transferred uid/device/inode
to the held nodes and require their common device. Reopen from the absolute root and
check both held and current nodes at every verification. Any mismatch, withdrawal,
callback exception or wrong thread fails closed; a withdrawn admission never revives.
The observer does not acquire the controller's exclusive profile leases.

The native helper owner accepts a trusted admission factory. Invoke it and all
directory/current-session callbacks outside shared mutexes on its serialized worker.
Compare a requested task's path and complete immutable context with the admission;
the GUI cannot broaden permissions. Recheck before dispatch, during native polling,
for every storage guard and before result publication. Suppress queued/completed
private results after withdrawal, close the exact child and wait for observed exit.
GUI cancellation still erases its shared buffers synchronously. No new thread or
GUI filesystem work is introduced.

Pass the expected directory identities through an explicit private worker request
extension. The child must verify them before creating its writer file, then retain
the checks through the existing store's publication sequence. A valid pathname that
has been substituted must not create files in the replacement directory. Original
unextended requests retain their exact shape. The extension contains exactly uid,
state_device, state_inode, recovery_device and recovery_inode as canonical uint64
strings; uid fits uint32, inodes are positive and devices equal. Its root/profile
come from the existing request. It does not increase existing frame/record limits.

Loss after a dispatched final storage grant can race publication, as already defined.
Withdrawal is not rollback. Preserve actual files and uncertain outcomes; never
claim a cancelled operation could not have published. Once closed and reaped, no
later mutation or result is allowed. Regrant requires a fresh admission and handle.

Freeze the accompanying case list before implementation. Independently observe a
relocated verified helper bundle and exact files. Cover admitted load/capture/retire,
each session mismatch, denied retention/erase, forged task context/path, replacement
of held directories, permission/symlink changes, child substitution before its first
instruction, withdrawal with a held native child, completed-result erasure and
non-revival. A wrong expected record must fail. Keep original helper/queue/store and
profile-owner/recovery-context/transfer tests. New cases have 30-second ceilings and
a 300-second family ceiling; fixed GUI task, native helper and workspace limits stay.
Record source-bound results and failures, update the handoff and sync main. Next
compose the actual frontend session callback, exact applied-draft retirement and
asynchronous consumer validation before enabling installed recovery. All five full
release editions remain required.
