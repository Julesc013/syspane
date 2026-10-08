---
type: "SysPane Work Record"
title: "Real native network acquisition checkpoint"
description: "Read bounded interface counters on Windows and Linux without claiming reconciled model identity or complete collection."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:26:25+11:00"}
sp_id: "SP-NETWORK-ACQUISITION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-NETWORK-ACQUISITION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Real native network acquisition checkpoint

From base `89f0c42fca4cb4babb8a72a28bd1cc17bfdeafc8`, the
[native acquisition package](packages/w-25-network-acquisition.md) adds actual
Windows interface-table and Linux route-netlink readers to `source/platform/`.
The shared result contains native keys, indices/types and optional paired 64-bit
receive/transmit counters. It excludes labels, device addresses and packet data.

The reader returns a complete bounded candidate or an explicit empty failure.
Linux bounds datagrams, aggregate bytes, row count and wait intervals, and rejects
malformed/interrupted/incomplete dumps. Windows frees its native table on every
return. Pre-call cancellation and deadline checks prevent querying; subsequent
checks discard cancelled/late results. A Windows call already in progress remains
potentially blocking and requires the existing child isolation before production
integration. Cooperative cancellation does not attest native termination.

The raw key is deliberately not a model identity. Reconciled publication still
requires subscribe-before-enumerate, dirty generations, deletion/index-reuse
handling and the acquisition-time bracket. The reader has no hidden polling loop,
automatic retry, demand grant or public telemetry/export endpoint.

## Evidence

`native.NATIVE-NETWORK` compares every returned row to independent before/after OS
reads, with fixed inclusive 64-bit counter brackets and unchanged key/type/index.
Windows uses a separate ctypes table decoder; Linux uses sysfs. Four native cases
cover actual reads, already-cancelled requests, expired deadlines and zero-capacity
rejection without a partial prefix. The Windows oracle shares the kernel API, so
it verifies adapter decoding rather than independent kernel correctness.

Two Linux native-layout cases cover exact uint64 extremes, missing stats and
malformed/interrupted/incomplete/duplicate/error/capacity rejection. They do not
claim that a live kernel fault or device replacement was induced. Full CTest
suites pass 89 Windows, 92 Linux and 81 historical-toolset host checks.
Fresh relocated model smoke packages pass on all three profiles. These remain
development model packages, not distribution packages for the network probe.

The first Windows compile failed because the pinned MinGW headers require
`ws2tcpip.h` before `iphlpapi.h` to expose the modern table declarations. Adding
that header resolves the failure. The source archive and complete failed build
output remain in the attempts evidence; no acceptance condition was changed.
Windows development profile revision 16 pins `libiphlpapi.a` through lock revision
3; Linux is revision 17. Native network targets remain absent from historical x86
revision 8. Existing historical host/import checks remain distinct from XP/7 tests.

Per-profile `out/evidence/w-25-network-acquisition-*.json`, attempts and
verification records identify the actual runs, artifacts and source hashes. Public
native-network evidence includes case outcomes and comparison counts, with no
native keys or counter values. Failed raw exchanges, if any, are retained only in
owned ignored output under the explicit local probe disclosure contract.

## Next boundary

Connect these readers to notification-backed identity reconciliation and an
independently supervised collector, then publish measured state through the existing
session/data-view boundary. Tests must preserve old values on failure, invalidate
rate baselines on reset/replacement, discard cancelled/obsolete work, and prove
child exit before restart. The acquisition start/end bracket must prevent receipt
time from refreshing old samples. Product demand/policy, rendering, retention,
cross-component erasure and visible/editor recovery remain open.

The full campaign remains active. There is no complete collector, desktop
qualification, privileged operation, guest mutation, release or AIDE activation.
