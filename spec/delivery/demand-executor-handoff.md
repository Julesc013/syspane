---
type: "SysPane Work Record"
title: "Linux demand and native acquisition integration"
description: "Keep IPC responsive while a bounded native task owns acquisition and obsolete results remain unpublishable."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T14:52:43Z"}
sp_id: "SP-DEMAND-EXECUTOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W07-DEMAND-OWNER", "SP-DEMAND-OWNER-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Linux demand and native acquisition integration

Source baseline: `70df8f5419a7f06148460232c5d8cb3d2d432648`. Git history identifies
the resulting commit. Build/test attempts retain their exact source archives.

The existing collector now translates its authenticated fixed network subscription
into a DemandOwner lease. Actual accepted client heartbeat sequences renew it;
subscription loss or current typed policy revocation retires it. The shared owner
selects acquisition work instead of the collector's old fixed polling timer.

One held native worker performs the watched network read outside the IPC/health
loop. Its actual acquisition times feed the unchanged model and wire projection.
Atomic cancellation retains the slot until the task finishes and its thread joins.
Only current exact-job completion may commit or publish. Source retirement discards
consumed indications together with the old source/watch; a late obsolete read cannot
silently reconstruct a successor identity map. The independent parent still owns
whole-process recovery if a task cannot stop. Threads are never detached.

Five new native cases pass: merged desktop/saver/recorder work, cancellation with a
held slot, policy revocation/regrant, timeout with a late real result, and revocation
through the actual collector IPC path while its acquisition thread is alive. The
observer independently brackets native counters and measurement clocks, sees the
OS worker thread and watched socket, and checks join/exit before replacement. The
late-result delay follows a real read and does not replace acquisition timestamps.
Recorder demand here is an acquisition lease; it does not implement history storage.

The initial 14-entry targeted run passed. A subsequent full Linux run passed 124
of 125 entries; its only failure was in the new IPC observer, which expected stdout
from a child whose launcher deliberately directs stdout to `/dev/null`. The original
oracle and failure remain archived. The correction observes the held child's actual
thread at the parent's existing revocation event. The contract requirement remains
revocation before native completion; no 500 ms response-time qualification is claimed.
The corrected five-case family passes on rerun against the same compiled binary.
Thus all 125 entries have passing evidence, with the full-run failure preserved;
there is no claim of a single all-green full run after that observer-only correction.

The existing eight collector and five consumer-continuity scenarios pass without
changing their expectations. They continue to compare original measurements, failed
acquisitions, replay, demand release, native source/consumer exit and replacement.
Windows configure plus 11 existing demand/component checks pass; no Windows native
collector or historical runtime qualification follows from this Linux-only change.

`out/evidence/w-07-demand-executor-attempts.json` indexes commands, source
archives, native reports and the tested artifact. Tooling/integrity results are in
`out/evidence/w-07-demand-executor-verification.json`; the machine handoff
is `out/evidence/demand-executor-handoff.json`. Raw operational probe
output remains in owned ignored storage; committed native records contain outcomes
and counts, not telemetry values. No real-user shell, VM or privileged policy was
changed, and no release was published.

W-07 and W-25 remain in progress. Next finish general per-session demand selection,
bounded invalidation/coalescing and installed controller/policy ownership, then wire
common scene commands and persistence into the native vertical. The fixed wire
subscription, typed development policy and finite probe are not a complete product
controller. All five required [0.1.0 release families](release-0.1.0.md), complete native
settings/editing/persistence, providers and package/qualification gates remain open.
