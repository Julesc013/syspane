---
type: "SysPane Work Package Boundary"
title: "W-25 bounded subscription lifetime and native inventory experiment"
description: "Admit one fixed inventory stream per authenticated connection, with demand expiry, policy-bound queues and complete-state receipt."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:57:54+11:00"}
sp_id: "SP-W25-SUBSCRIPTIONS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-STATE-IMPORT", "SP-W24-PACKAGE", "SP-SCHEDULER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 bounded subscription lifetime and native inventory experiment

Extend the existing configuration session owner and outbox; do not add a second
session runtime. A locally supplied optional source fixes producer, channel and
classification. Absent source configuration keeps the preview feature set unchanged.
One connection may own one subscription identity for its entire lifetime; at most
16 connections share this source. This is the initial inventory-stream tightening,
not the W-07 field/entity/age/priority/recording planner.

## Admission and ownership

Only advertise `telemetry.snapshot` when this source is configured and all three
exact telemetry/snapshot/observation 0.1 document versions are common. Missing a
required document fails negotiation; a missing optional document removes the feature.
The authenticated role maps exactly to its channel: desktop/desktop, console/inspector,
saver/saver, preview/preview. Mandatory policy must be available, permit telemetry
subscription and permit both that channel and accessibility at the fixed source
classification. A requested producer/channel/classification/revision cannot alter
this server configuration. Codec validation is followed by current policy checks.

Each admitted subscription has a server-local monotonically allocated nonzero ticket.
Tickets never repeat within this owner, including after disconnect and connection-ID
reuse; exhaustion closes the requesting connection. Local source configuration may
tighten the default uint64 ticket ceiling for a bounded experiment; it cannot raise
or reset it. A producer callback supplies
connection and ticket. Reject an obsolete callback before parsing/serializing its
payload or observing its clock. Tickets convey lifetime, not peer or policy authority.

The first complete snapshot is the observable subscription admission; no command
result or invented acknowledgement schema is introduced. An identical repeated
subscribe body while active requests a fresh full snapshot: discard pending data,
allocate a successor ticket and preserve the consumer's existing replay history.
Changed body bytes or another subscription ID conflict. Unsubscribe clears demand
and pending data, permanently retires this connection's subscription, and is
idempotent for the same ID. Subscribe after retirement closes; use a fresh connection.
Malformed, denied or incorrectly bound subscription input closes without data.

## Demand, queues and policy

Admission starts a 3,000 ms demand lease. Only a strictly increasing peer heartbeat
sequence renews it; duplicate heartbeats may be echoed but do not extend demand.
An accepted sequence followed by a lower sequence closes with `heartbeat.regressed`
and discards that connection's queues and demand; it does not close other peers.
Data, repeated subscribe, and dequeue do not renew it. At exact expiry close the
connection and discard its queues/demand. Native EOF/shutdown/write failure likewise
destroys demand. The native loop ticks on bounded reads even without incoming bytes.
Demand count is the number of active connections after the latest tick, never a
collection-frequency instruction or proof that a native source stopped.

The existing 16-frame/2 MiB data and 16-frame/64 KiB control reservations apply.
Validate and authorize each complete full/delta before queueing. A delta needs the
exact preceding queued generation and a larger generation. Full snapshots may
confirm or advance; consumer replay/model checks remain authoritative. Partial/gap
state or data overflow clears pending data, emits the existing gap control and
requires a full snapshot. A control overflow closes and drops demand. Recheck current
policy before dequeue. Queue acceptance proves neither delivery nor activation.

Policy replacement clears all pending frames and demand before checking revision
or time; valid replacement emits only a fresh policy-changed gap. Invalid revisions
or clock regression close connections; regressed time permanently faults this owner.
No stale payload survives a clock error or a failed policy update. Native callers
close a session reported closed. Data already handed to a bounded native write
cannot be recalled: receiver-side current policy and revocation remain mandatory.

## Native experiment and time scope

Use the existing local IPC adapters and independent harness, with an explicit
`SysPane.TelemetryProbe` composition on modern Windows/Linux. Authenticate native
peer identity before session admission; the probe alone supplies typed development
policy and the fixed synthetic source. Consumer receipt uses the existing data owner,
including full recovery and same-epoch history across native reconnect. No protected
policy is changed and no actual host telemetry is read.

Only synthetic inventory with no TTL/rate claim is produced. Record local monotonic
receipt/lease events; observation 0.1 still carries no measured tick. This admits
native lifecycle experiments, not measured-field freshness or a general product
subscription feature. Before any real measured source advertises support, add its
producer-monotonic provenance and conservative clock mapping. Existing codec/import
clock gates remain for that capability. Complete product demand planning, collector
supervision, renderers and cross-process current-policy distribution remain open.

## Fixed acceptance and execution

| Family | Required result |
|---|---|
| SUB-ADMIT | Optional source/versions/role/current policy gate advertisement and admission; conflicting IDs/body and retired reuse close. |
| SUB-QUEUE | Full before delta, exact base, partial/overflow gap, full recovery and control priority; no queued data after unsubscribe. |
| SUB-LIFETIME | Strict heartbeat renewal/exact expiry, disconnect, stale-ticket/connection reuse, monotonic ticket exhaustion and policy replacement even under bad time. |
| NATIVE-SUB | Separate authenticated processes prove full/delta/resync/unsubscribe/reconnect, queue overflow, policy revocation before dequeue, expiry and wrong producer rejection. Consumer reports imported generation/value and retained/removed state; no visibility claim. |

Run all three existing profiles' complete CTest suites; the historical profile runs
portable cases only. Preserve source, artifact, command, native-process identity,
failure and blocked qualification records. No public release or desktop support
follows from a native inventory exchange.
