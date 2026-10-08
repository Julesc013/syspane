---
type: "SysPane Work Record"
title: "Portable recovery implementation checkpoint"
description: "Record lease, render-progress and restart decisions while preserving native recovery gates."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:38:11+11:00"}
sp_id: "SP-RECOVERY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W25-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Portable recovery implementation checkpoint

W-25 is in progress. Its [package](packages/w-25-recovery.md) closes the portable
recovery-state boundary before implementation. The base is
`3ac41bfe5d8923741623387be01d56d57650fa31`; the containing commit and recorded input
digests bind this checkpoint. The full foundation/native-experiment campaign is
still active. W-25's native and visible recovery gates are not satisfied here.

## Implemented and tested

`source/diagnostics/recovery.hpp` exposes single-owner, noncopyable guards without
model, JSON, native-handle, renderer or provider dependencies. `ProducerLease`
separates producer liveness, synchronization and retained-update identity. Exact
duplicates do not renew a lease; late heartbeats cannot resurrect an expired
attachment. Reconnect requires a snapshot, stale attachment callbacks are inert,
and a new producer/epoch never relabels retained data. Policy-driven forget can
remove metadata even after a clock fault, but grants no right to retain payloads.

`RenderWatch` tracks one increasing challenge and a deadline that unrelated traffic
cannot postpone. Its completion is a render-path signal, not independent evidence
of visible pixels. `RestartGate` reserves one child slot, quarantines unconfirmed
termination and limits replacement starts to three in a rolling minute. Backoff,
jitter, explicit circuit reset, graceful stop and exact deadline behavior are
specified before their test expectations. Circuit reset preserves the last error.

Both Windows/Linux development profiles, revision 4, pass 48 CTest entries: the
previous 37 model/protocol/native-IPC checks and eleven portable recovery cases.
`LEASE-04` uses a real model snapshot to show that continued heartbeat activity
leaves the observation unchanged while its freshness expires. Other cases cover
disconnect/reattach, gaps, sequence/epoch mismatch, busy rendering, restart budgets,
quarantine, stale callbacks, clock regression and uint64 boundary arithmetic.
Expected times/results are literal test oracles, not values imported from runtime
constants. Both compilers retain warnings as errors.

Records are `out/evidence/w-25-portable-<profile>.json`, matching CTest
logs and the exact native IPC report copies. The recorder requires all named cases
and binds contract, source, dependency, profile, artifact and oracle digests. The
native reports remain IPC regression evidence; their cross-user/logon and desktop
qualification limits are unchanged. No failed build/test was observed for this
checkpoint; historical failures remain in their original records.

## What this does not prove

Recovery tests inject local monotonic times and typed events. They do not freeze a
real producer, stall a real renderer, kill/restart a child or inspect visible stale
state. The guards own decisions and metadata; they cannot verify native child-stop
proof, policy-driven payload erasure, event-loop scheduling or kernel progress.
Actual profile limits must be measured when connected to native processes.

There is still no independent `SysPane.Diag.exe` / `syspane-diag` entry, conservative
native diagnostic inspector or independent native editor-exit path. The package's
mandatory native completion gates remain open. W-24 snapshot/delta subscriptions
and persistent commands remain disabled; no new recovery role/feature is advertised.
W-02's external desktop oracle and all native host tracks remain required.

## Next admitted work

Connect these guards to native process supervision using the W-24 adapter. Close
trusted launch/handle ownership, producer/surface role negotiation, full snapshot
and render-challenge message bodies before enabling those features. Preserve a
separate health path so an IPC-responsive render stall is observable. Prove actual
child termination before replacement; a timeout alone must leave the slot quarantined.

Implement independent diagnostic startup with bounded safe metadata, current
mandatory policy and a native inspector. Execute optional-content/history failure
cases without loading those failed dependencies. W-02 supplies external pixel and
native-exit evidence in a permitted desktop lab. Missing XP/7, Mac or desktop labs
block their qualification independently; they do not block contemporary Windows
or deterministic work. Keep W-25 incomplete until its required outputs and cases
exist. No public release or privileged action has been performed.
