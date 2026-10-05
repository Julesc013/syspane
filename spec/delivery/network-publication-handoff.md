---
type: "SysPane Work Record"
title: "Supervised real network publication checkpoint"
description: "Publish real Linux counters and rates through measured telemetry with independent child recovery."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:30:07Z"}
sp_id: "SP-NETWORK-PUBLICATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-NETWORK-PUBLICATION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised real network publication checkpoint

From base `1aea85f218adb90e7500f02c2873306af85f506a`, the
[publication package](packages/w-25-network-publication.md) connects real Linux
network acquisition, source lifetimes, measured documents and the synchronized
consumer under independent child supervision. Existing Sessions, DataView,
HealthLink, Child and RestartGate remain the owners of their respective contracts.

The shared adapter publishes receive/transmit cumulative counters and interval
rates with operational classification, original acquisition-start ticks and UTC
observation times. Counters remain exact uint64 strings; rates use actual elapsed
time. Missing/reset/first intervals stay pending. Failed acquisitions report retained
values as failed/stale without refreshing their original times. Whole-document byte
bounds reject capacity overflow before any partial table is offered.

The Linux `SysPane.CollectorProbe` places native collection in a separate owned
child and authenticates it on private health and data streams. The parent performs
no acquisition. Demand creates the held watch and source owner; unsubscribe or typed
revocation destroys them. Increasing health heartbeats renew the independent producer
lease. A hung child expires while the consumer retains its prior measured state;
only observed child exit and the existing backoff admit a new epoch/full snapshot.
An abrupt child exit after confirmed receipt follows the same retained-state and
replacement rules without forcing termination of an already exited process.

This is a finite native experiment. Its data stream reuses the existing console
Sessions server and desktop-role test consumer under typed development policy.
It is not an installed collector/controller service, general demand planner, full
network inventory, protected-policy distribution or a visible desktop edition.

## Evidence and failures

Full suites pass **96 Windows, 101 Linux and 88 historical-toolset host checks**.
Three portable families verify exact values, failure metadata, real codec/data-view
import, replay, replacement, policy erasure and complete-document capacity.
Linux's eight native cases cover actual collection, injected source failure, replay,
hang/restart, abrupt exit/restart, unsubscribe, typed revocation and parent loss. Independent sysfs reads
bracket every received interface counter; rates are checked against rational delta/
interval calculations. Held pidfds prove the child exits before replacement. Procfs
independently observes the watch and confirms its release when demand ends.

The first Linux build failed on misleading-indentation warnings treated as errors.
The first focused run then exposed two caller mistakes: portable snapshot envelopes
included forbidden channel/classification fields, and native unsubscribe omitted
the 0.2 clock ID. The existing codec correctly rejected both. The callers were
corrected to the established schemas; no protocol or acceptance oracle was weakened.
The original failed build, focused output, source archives and public failure record
are preserved. Operational exchanges remain only in owned ignored private evidence.

After the first passing full suites, public evidence was expanded to preserve held
child IDs and the lifecycle sequence, and private failure capture gained both OS
brackets. Full suites were repeated to bind the final harness bytes. Public records
contain outcomes, counts, process identities and timing, without raw network values.
Final contract review also identified the missing abrupt-exit path. Its acceptance
trace was added before implementation: an existing heartbeat proves receipt of the
first full, the child exits 73, and independent exit/backoff observations precede
the replacement. The focused suite passed before the final regression runs.

Profiles are Windows x64 revision 18, Linux x64 revision 19 and historical x86
revision 10. The historical audit covers twelve executables on Windows 10/WOW64;
it does not qualify XP/7 execution. Only Linux builds the native collector probe.
All three relocated model smoke packages pass; their payload is still the development
model. `build-support/evidence/w-25-network-publication-*.json`, preserved attempts,
verification and the machine handoff identify exact source/package/artifact inputs.

## Next admitted work

Continue independent native-host tracks and visible recovery. Connect the qualified
source/data boundary to product controller demand/policy and a real renderer rather
than extending the finite probe into a second runtime. W-07 demand aggregation,
remaining W-25 renderer/visible/editor recovery and the per-platform verticals remain
open. Windows full-table notification coverage remains separate; Linux's counters
do not supply addresses, routes, DNS, device joins or connectivity assessments.

Actual native topology/namespace/suspend fault induction, large-inventory transport
qualification, installed policy, retention and cross-component erasure need their
own evidence. Historical guest scope and Mac laboratory availability remain open.
The full campaign and W-25 are incomplete. No public release, privileged action,
interface mutation, guest change or desktop-support claim follows from these tests.
