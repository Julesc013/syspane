---
type: "SysPane Implementation Handoff"
title: "Native GJS measured network consumer checkpoint"
description: "Shared measured model, policy and lease semantics inside the native GJS runtime before operational shell delivery."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:22:07Z"}
sp_id: "SP-GJS-NETWORK-VIEW-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GJS-NETWORK-VIEW", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native GJS measured network consumer checkpoint

From `66c3d0d9df599aac1b36c0589e86cdcfe8b2bb30`, the existing native module adds
`SysPaneClock.NetworkView`. It owns the shared C++ Framer, DataView and network
projection, so JavaScript does not redefine model import, policy or freshness.
This closes the standalone consumer prerequisite; it does not connect operational
collector messages to the shell or qualify their displayed age.

The [package](packages/w-25-gjs-network-view.md) fixes ownership, message admission,
resource limits, policy replacement and teardown. Admission duplicates an
authenticated same-session Unix stream and retains its native peer identity.
Local measurement-clock checks supply provenance; no wire string grants clock
authority. GJS feeds bounded original protocol frames and receives bounded
process-local projections with exact counter/time strings and full status metadata.
The trusted caller supplies typed development policy. Installed policy remains open.

The five-second welcome and partial-frame deadlines are enforced during feed and
projection, including a completely silent peer. Heartbeats renew only producer
leases. Replays preserve the original sample; a conflicting replay closes the
owner. A new policy revision erases native model data; regrant requires a new owner
and source session. It cannot revive the old connection. Explicit close/finalization
release native resources; faulted objects cannot reopen.

## Executed results

Twelve native case groups pass in standalone GJS with one retained synthetic peer:

- Native admission and fixed invalid-input errors.
- Exact maximum uint64/zero counters, null first rates and original status/UTC data.
- Derived rate formatting, advancing age, stale transition and immutable replay.
- Independent lease expiry, duplicate heartbeats and policy deny/regrant erasure.
- Gap retention and failed-acquisition value/time/error preservation.
- Conflicting replay, directional negotiation and negotiated frame-limit rejection.
- Wrong epoch, future sample, malformed length and input/batch limits.
- Silent-welcome and partial-frame deadlines, 64 explicit close cycles and held-peer exit.

The observer brackets each returned age against native BOOTTIME, verifies all three
processes share the time namespace, compares descriptors before/after cleanup, and
requires both owned children to exit normally without warnings or leftover output.
The fixture injects synthetic bytes through the serialized caller; the peer supplies
socket/clock identity. This is not a claim of actual socket delivery or shell pixels.

Complete CTest suites pass: **109 Linux, 102 Windows and 94 historical-toolset host
checks**. Linux includes the existing native clock regression. All three local model
smoke archives pass relocated execution. Historical checks ran on Windows 10/WOW64;
XP/7 guest qualification remains unresolved. MSB8051 remains the recorded vendor
warning for the historical toolset, not a compiler warning accepted by the project.

Evidence uses `build-support/evidence/w-25-gjs-network-view-`; the machine handoff
is `build-support/evidence/gjs-network-view-handoff.json`. Thirteen configure/build/
test attempts and all three native consumer reports retain their source archives.
All executed attempts passed. Earlier passing consumer runs had narrower checks;
the final full-suite record binds the complete twelve-case source and artifacts.
Initial preflights completed in tool output before the file coordinator was added;
the attempt index distinguishes that provenance instead of inventing original logs.
The first staged smoke-report digest check rejected Git's CRLF normalization of
two original Windows reports. A scoped byte-preserving attribute and explicit
restaging retain their original bytes. The failed digest observation is preserved;
no native result or package artifact changed.

The Linux shared module now links the model/protocol/recovery/projection closure
as position-independent code. This rebuilt Linux artifacts, including the collector.
The earlier desktop experiments retain their original identities; their pinned
collector/library evidence must be explicitly refreshed before another native run.
No earlier native qualification is silently transferred to this build.

## Next boundary

Close the live collector forwarding and teardown contract, then connect its
original measured messages through this native owner and the qualified asynchronous
shell path. The existing relay waits for collector exit and remains a retained-data
experiment. A live experiment must preserve producer/namespace/epoch provenance,
keep the supervised source alive while samples age and bound forwarding queues.
Independently verify actual values, advancing displayed age/expiry, policy erasure,
heartbeat loss and native exit, with frozen-age and ignored-expiry controls.

Continue the [campaign coverage audit](campaign-coverage.md). The Windows synthetic
lab designation, historical guest scope and macOS endpoint remain unresolved; no
guest or active user desktop was changed. Product controller demand/policy, general
queues, render supervision, visible/editor recovery, suspend and namespace changes
remain open. W-25 and the full campaign are incomplete. No release or AIDE activation
is claimed.
