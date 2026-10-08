---
type: "SysPane Work Record"
title: "Network lifetimes and Linux watched acquisition checkpoint"
description: "Preserve observation identity and measurement age before supervised native publication."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T22:49:24Z"}
sp_id: "SP-NETWORK-RECONCILIATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-NETWORK-RECONCILIATION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Network lifetimes and Linux watched acquisition checkpoint

From base `3a7776175ab89e7e1627a5ec31054662bf2a491e`, the
[reconciliation package](packages/w-25-network-reconciliation.md) adds a shared
serialized source owner and a Linux watch. Existing native readers and the
measured telemetry contract keep their identities. The source owner remains below
model/wire publication; it does not grant demand or policy authority.

Surviving interfaces retain observation lifetimes. Removal, disappearance, changed
native index/type and reappearance retire the old mapping. Lifetimes are bounded
and never recycled within the producer epoch. Obsolete demand results cannot
change state or poison the active clock. Dirty, failed and over-capacity candidates
retain the previous immutable sample and its measurement time as non-current.
Unknown notification continuity and local clock faults latch until the owner is
replaced under the existing cleanup/epoch rules.

Accepted paired counters produce exact integer deltas and actual start-to-start
intervals. Reset, missing counters, replacement and non-increasing sample times
produce no rate interval; equal counters over positive time produce valid zero.
Acquisition start and completion remain separate. This does not attest the physical
instant at which the kernel measured a counter.

Linux now binds a private route-netlink link subscription before its first dump,
holds the calling thread's network namespace handle, demultiplexes notifications
from sequenced replies, and drains before and after enumeration. A changed revision
discards the table. Malformed/lost input or an interrupted in-flight operation closes
the watch to prevent leftover replies from entering a successor. Pre-call stops
preserve a healthy registration. Reads have explicit datagram/byte/event/time bounds.

## Evidence

All 93 Windows, 97 Linux and 85 historical-toolset host CTest entries pass.
Four portable reconciliation families cover fixed identity, counter/clock,
cancellation/failure and capacity cases. Linux adds an interleaved native-layout
decoder case and a fifth case within `native.NATIVE-NETWORK`.

The live Linux observer matches the owned process's socket inode to its route-netlink
link multicast group before the first dump, compares two real acquisitions to
independent sysfs brackets, and observes successful process exit. Already-cancelled
and expired requests leave registration healthy. No interface change is induced;
fixture deletion/overflow semantics do not establish live kernel fault delivery.

Windows x64 profile revision 17, Linux revision 18 and historical x86 revision 9
include the shared source owner. The historical import audit covers eleven
executables on Windows 10/WOW64; no XP/7 runtime claim follows. Windows lock revision
3 is unchanged. Windows notification coverage remains open because the IP-interface
callback alone does not establish coverage of every raw interface-table entry.

The three fresh relocated model smoke packages pass. Their payload is still the
development model, not a collector or complete product. All fifteen configure/build/test
attempts passed; their source archives and outputs are preserved. Per-profile
`out/evidence/w-25-network-reconciliation-*.json`, attempts, verification
and the machine handoff bind results to actual source/package/artifact identities.
Public native evidence contains outcomes and counts without raw keys or counters.

Final review removed an allocating copy from the watch's failure return so its
already-owned notification buffer can move out during memory pressure. Builds and
suites were repeated against the final source; no acceptance condition changed.

An initial direct Linux package invocation omitted `SYSPANE_LINUX_BUILD_ROOT` and
stopped before relocated execution. Its archive and transcribed tool error are
retained separately. The documented wrapper supplied the environment and the
subsequent package passed; no source or acceptance change was needed.

## Next boundary

Connect real acquisition, this identity owner and the measured session/data view
through independent producer supervision. Close the mapping from source lifetimes
to model entities and metric descriptors, and preserve acquisition time, stale
values, policy erasure, bounded demand and exact replay. Prove OS-confirmed child
exit before restart; a cooperative stop does not attest native-call termination.
Linux can proceed independently while Windows notification coverage is resolved.

Actual topology/namespace/suspend faults, renderer supervision, product policy,
retention, cross-component erasure and visible/editor recovery remain open. W-25
and the campaign remain incomplete. No privileged action, guest change, public
release, complete collector or desktop qualification is attested.
