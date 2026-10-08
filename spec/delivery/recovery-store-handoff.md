---
type: "SysPane Work Record"
title: "Private native recovery storage checkpoint"
description: "Exact bounded recovery files, conditional retirement and independent ext4 process-cut evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T01:45:00+11:00"}
sp_id: "SP-RECOVERY-STORE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-RECOVERY-STORE", "SP-RECOVERY-DRAFT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Private native recovery storage checkpoint

Baseline 203c6a231b76915541cff721922c78020c101c22. The
[storage package](packages/w-10-recovery-store.md) adds LinuxRecoveryStore as the
filesystem owner for one opaque recovery record in a private caller-selected root.
The [earlier shared and Apply checkpoint](recovery-draft-handoff.md) retains semantic
validation, generation identity, explicit restoration and the transaction owner.

The store requires an existing private ext-family directory, holds a cooperative
writer lock and checks root, lock and record identities. It rejects unsafe nodes,
foreign entries and non-private permissions. Exact bytes are bounded to 786432;
replacement uses one staging file, file synchronization, same-directory rename and
directory synchronization. Retirement removes only a matching published record.
Orphan staging is never offered or promoted. A current guard must authorize reading,
cleanup and publication/removal; denial alone never authorizes deletion.

Every conditional operation binds a random owner instance, sequence and exact-byte
digest. Admitted attempts invalidate old operation versions, including retirement
of an absent record. A queued old create therefore cannot resurrect that record.
Failures after publication return unknown and poison the owner until verified reopen.
Malformed bounded bytes remain diagnosable and explicitly discardable; the store
does not validate or execute a recovery command, commit configuration or activate UI.

## Verification

The native RECOVERY-STORE family passes 74 cases on the admitted non-root ext4
development filesystem. A separate process kills its held writer at all nine
replacement stages, both with and without an old record, and all five retirement
stages. Reopen independently checks exact bytes, digest, staging presence, modes and
entry bounds. Interrupted staging is cleaned only by a subsequent authorized mutation.

Further checks cover actual short writes using a process-local file-size limit,
injected failures before and after publication, poisoned owners, size limits,
malformed bytes, stale versions, absent retirement, guard revocation/exceptions,
writer exclusion, reentrancy and wrong-thread calls. All three file positions reject
symlinks, hard links, directories, FIFOs, sockets, non-private modes and oversized
nodes. Root, lock, current and staging substitutions preserve foreign content.
A deliberately wrong byte expectation fails the independent comparison.

RECOVERY-APPLY retains all eleven existing cases. RECOVERY-STORED-APPLY runs the
same seven scene/font Apply, lost-result, refusal and wrong-report cases through
actual storage publication, process exit and fresh-owner reading, plus the four
unchanged generation-token refusal cases. It compares returned bytes against the
fixed record before giving them to EditorDraft. Accepted Apply retains the old
recovery bytes until explicit retirement; retirement leaves the new committed
selection unchanged. This composes native components without claiming a native UI.

All ten shared recovery families pass on Linux GCC13, Windows GCC15 and v141_xp.
The component graph and forbidden-dependency checks pass on all three profiles.
These are 30 shared checks and six graph checks; full portable suites retain their
earlier checkpoint evidence and were not rerun for this Linux-only storage addition.
The v141_xp checks executed on contemporary Windows, not a historical guest.

The [compact checkpoint](checkpoints/recovery-store.json) binds frozen inputs,
every build/test attempt, exact source archives, executable identities, native
records and specification checks. Raw output remains ignored local out/evidence
content. Existing schemas and fixtures retain their exact bytes.

Specification validation passes 46 schemas and 158 fixture expectations. The tooling
suite runs 62 tests: 60 pass and the two existing Windows symlink-privilege cases
skip. Generated projections and the unchanged settings resource fixture also pass.

## Preserved failures and workspace evidence

The first Linux build failed four misleading-indentation warnings. Splitting the
adjacent statements fixed the build without changing the frozen contract or literal
outputs. The failed source snapshot and compiler diagnostics remain preserved.

Both Windows build preflights stopped at the existing 7 GiB active-output allowance.
Sixteen completed native recording directories, totaling 16727029 bytes, were
archived and verified before removing their working duplicates. Archives retain
regular bytes, symlink targets, empty directories, FIFO/socket modes and node metadata.
Prior failures remain preserved. The allocation and retained-evidence accounting
did not change; the subsequent build preflights passed.

Earlier CONTENT-COMMANDS and accessibility timeouts and the known GTK shutdown
diagnostics remain unresolved. Passing storage/Apply checks do not explain them.

## Next boundary

Keep W-10 in progress. Implement one native recovery owner outside the GTK thread,
with at most one active and one latest pending operation. Bind captured bytes and
completions to the exact editor session, verified generation and operation version.
Serialize policy/lifetime invalidation with the guard authorization point; erase
queued bytes and prevent stale completions or late writes after retirement.

Then connect actual Restore, Discard recovery draft and Keep for later controls.
Qualify process death during editing, recovery-unavailable reporting, current-policy
changes, save/discard retirement and independent native UI observations. Never run
this filesystem work from a GTK callback or enable recovery from this component
checkpoint alone. Installed controller/catalog/policy ownership, scene-aligned
entry/restoration, complete accessibility/performance and every required platform
edition remain open. No hardware power-loss, secure-erasure, Windows/macOS storage,
complete release, privileged operation or Git history rewrite is claimed.
