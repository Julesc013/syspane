---
type: "SysPane Work Record"
title: "Native inventory subscription checkpoint"
description: "Bind demand expiry, policy-bound queues and complete-state receipt to authenticated native process experiments."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:14:08+11:00"}
sp_id: "SP-SUBSCRIPTIONS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-SUBSCRIPTIONS", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native inventory subscription checkpoint

From base `dc44b697b72a5a40a88db4d1dee8c760fcf55f22`, W-25 connects the existing
session owner, outbox, native local IPC and complete-state consumer under the
[subscription package](packages/w-25-subscriptions.md). W-25 remains in progress.

## Implemented and executed

An optional locally configured inventory source enables exact document/feature
negotiation. Preview-only composition retains its feature set. Subscription admission
checks native role grants, fixed producer/channel/classification and current mandatory
policy. Each connection owns one identity, a monotonically allocated callback ticket,
and a three-second demand lease renewed only by increasing heartbeat sequences.
Unsubscribe, expiry, disconnect, shutdown and policy replacement remove demand.

An identical repeated subscribe requests full resynchronization and replaces the
ticket without extending demand. Obsolete callbacks are rejected before parsing or
time mutation. Full/delta ordering, separate bounded queues, overflow gaps and control
priority retain the existing transport rules. Policy replacement discards queued
frames/demand before checking revision/time; invalid revision or regressed clock
closes the affected owner instead of retaining old payload. Already written bytes
still require the consumer's current-policy enforcement.

`SysPane.TelemetryProbe` exercises separate unelevated, authenticated Windows/Linux
processes. The consumer imports actual framed data, retains its model across native
reconnect, and exposes independently asserted generations and values. Five scenarios
pass: journey (full/delta/resync/unsubscribe/reconnect), data overflow/full recovery,
revocation before dequeue, demand expiry and wrong producer rejection. The journey
imports generations 1, 2, 3, confirms 3 after reconnect, then accepts 4. Overflow
delivers a gap followed by complete generation 18. Revocation delivers no queued
generation 2 and removes the consumer payload. Expiry retains its last model without
live presentation; the server has no remaining demand.

These are synthetic inventory observations with no measured tick or TTL/rate claim.
Typed development policy is explicit; no protected policy is installed and no host
telemetry is read. One fixed source/identity per connection is an initial tightening,
not the full W-07 field/entity/age/priority/recording planner. The experiment does not
qualify a real collector, renderer, product subscription feature or desktop host.

All configure/build attempts pass. Full CTest suites pass 81 Windows, 82 Linux and
76 historical-toolset host entries, including three new portable subscription
families. Historical PE/import checks cover nine executables, with no new permitted
imports or XP/7 guest execution. Profile revisions are Windows x64 13, Linux x64 14
and historical x86 7. Fresh relocated model smoke packages pass for all profiles;
these remain model-only local archives.

## Evidence and workspace allocation

Records are `build-support/evidence/w-25-subscriptions-<profile>.json`, adjacent
native reports/CTest logs/smoke results, `w-25-subscriptions-attempts.json`,
`w-25-subscriptions-verification.json` and the machine `subscriptions-handoff.json`.
Original build/test source archives and binary artifacts remain in ignored owned
roots. Later recorder/documentation/workspace metadata changes do not change the
compiled code or test oracles; original attempts retain their original identities.

The initial 1 GiB workspace allocation was exceeded after the debug builds:
1,108,437,093 bytes, 34,695,269 above that ceiling. Further launches stopped;
`subscription-workspace-overrun.json` preserves the measurement. The current
[admission](campaign-admission.md) allocates 2 GiB combined and requires reserved
headroom before build/test/package launches. This is a development allocation,
not a relaxed product limit, a retroactive pass or an enforced OS quota.

Before those builds, 38 exact generated checkerboard wallpaper fixtures were
archived losslessly: 54,720,570 original bytes remain recoverable from a verified
5,776-byte local archive. `subscription-lab-archive.json` identifies every original
path/digest and the archive/member. Journals, captured observations, configurations,
native reports and active binaries remain. Byte restoration does not recreate
historical filesystem permissions or attest a new native run.

## Next admitted work

Define producer-monotonic provenance and conservative consumer clock mapping for
measured fields, then connect real collection to independent supervision and the
native receive path. Complete product demand aggregation, policy distribution,
failure retention, cross-component erasure, renderers and external visible/editor
recovery. Preserve existing Linux composition failures and independently resume
other host tracks within their laboratory scope. Historical guest scope and a Mac
endpoint remain unresolved. No privileged operation, release, AIDE activation or
human review is attested.
