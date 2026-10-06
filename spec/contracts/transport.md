---
type: "SysPane Specification"
title: "Local transport and request lifecycle"
description: "Define experimental framing, negotiation and bounded result retrieval."
tags: ["contracts"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-TRANSPORT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROTOCOL", "SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-06T02:15:05+11:00", "scope": "Native W-25 owned-child supervision checkpoint; diagnostic and visible recovery remain pending"}
---

# Local transport and request lifecycle


## Wire 0.1 framing

An authenticated native byte stream carries a four-byte unsigned big-endian payload
length followed by exactly that many UTF-8 JSON bytes, without BOM or trailing LF.
Length excludes the prefix. Zero and lengths above 1,048,576 bytes are rejected
before allocation. Partial reads accumulate only within the negotiated bound;
coalesced frames are parsed independently. EOF mid-frame is truncated, never a
partial accepted message. Export NDJSON is a separate framing format.

The initial [handshake](handshake.schema.json) advertises wire major/minor, role,
producer epoch, supported document versions and required/optional features. Major
must match, minor is the lower supported value, and unknown required features fail.
Effective frame limit is the minimum of both peers and the hard ceiling; parse depth
is at most 32. Authentication uses native peer user/session identity and endpoint
access controls before any subscription. Claimed role/epoch never authenticates a
peer or grants privileges. No network listener is enabled by this contract.

Handshake and incomplete-frame deadlines are five seconds in the experimental
profile. A connection has bounded queues and at most 128 in-flight requests;
reserve control capacity for policy, health, cancellation and shutdown. A stalled
reader is disconnected with an explicit subscription gap. Native profiles can
tighten limits and must record any future versioned alternative.

## Messages and resynchronization

Every payload has `type` and `body`; after handshake it also carries negotiated
connection ID and producer epoch. Types are hello, welcome, command, result,
subscribe, unsubscribe, snapshot, delta, gap, heartbeat, cancel, result.get and
shutdown. Unknown types fail; optional annotations stay inert. Message-specific
document versions are negotiated independently. Command bodies use the selected
command schema; results use [command-result](command-result.schema.json).

The [W-25 health profile](../delivery/packages/w-25-recovery.md#initial-native-supervision-closure)
adds optional `render.challenge` and `render.progress` envelopes only under its
negotiated `recovery.progress` feature. Preview command sessions do not enable them.
That health profile carries no telemetry snapshot/delta or configuration mutation.

Snapshot/delta sequence and producer epoch must agree. A gap, validation failure or
new epoch invalidates incremental state and requires a coherent full snapshot.
Independent surface leases expire after three missed negotiated heartbeat periods;
the experimental heartbeat period is one second. Metric freshness remains separate.
Subscriptions have per-role demand leases and cancellation revokes only that demand.
Role-specific native tests must prove access control and progress under saturation.

## Requests, cancellation and results

Request IDs are scoped to authenticated principal, installation/session and producer
epoch. Identical replay returns the recorded result; changed bytes under the same
ID are a conflict. Committed request identities persist with their generation.

The experimental 128-request admission bound has two explicit counters:

| Resource | Scope and lifetime |
|---|---|
| In-flight requests | At most 128 on one connection, from admission until terminal outcome; finishing releases this active slot |
| Mutation deduplication reservations | At most 128 across connections for an authenticated principal, installation/session and producer epoch; admitted unfinished mutations plus unexpired retained terminal results share this capacity |

A new mutation reserves both resources before execution. Completion converts its
deduplication reservation to a retained terminal record; it does not free that
reservation. Retain each record for 600 seconds from its terminal outcome using
the controller's monotonic clock, then reclaim it when needed. A profile may retain
longer but must declare that alternative and its admission consequences. Neither
replay nor result retrieval consumes a new mutation reservation or extends expiry.

If either required resource is full, return busy before executing the new mutation.
Do not evict an unexpired record. Disconnect/reconnect does not clear principal
reservations. Replay and authorized result retrieval remain possible while new
mutations are busy. Thus 128 rapid completed changes can exhaust this conservative
experimental window even when no request is in flight; a different capacity is an
explicit profile/contract change, not an implementation optimisation.

Result retrieval, cancellation, policy/health and shutdown need separately reserved
bounded control capacity. W-24 must record controller-wide connection/memory limits,
control queue sizes and saturation outcomes before implementation; multiplying
per-connection limits is not a global resource bound. The durable committed-request
journal is separate from the ordinary result cache and follows the storage
retention/reconciliation contract. The [request budget cases](../assurance/acceptance-traces.md#request-budget-cases)
test these distinctions without claiming complete transport conformance.

The [W-24 package](../delivery/packages/w-24-transport.md) now records the initial
preview profile's concrete global/queue budgets and message/state coverage. Its
portable helpers and initial Windows/Linux peer/stream integration now have
executed development cases in the [native handoff](../delivery/native-transport-handoff.md).
This preview slice conservatively retains preview IDs within the same
reservation budget, with current-policy checks on retrieval and replay.

The [asynchronous command profile](../delivery/packages/w-08-command-sessions.md)
negotiates `configuration.transactions` with command 0.2/result 0.1. Its one ledger,
worker-stop ownership, connection lifetimes, reply reservations and commit permit
make cancellation and policy ordering explicit. This is a finite development
composition; installed ownership and original-epoch wire reconciliation remain open.

Cancel before commit may abort preparation. After commit it cannot undo the accepted
generation; return the committed result with activation status. A lost connection
does not prove cancellation. `result.get` reads a retained result without execution;
expired/unknown outcomes require reconciliation of revision and request journal,
never blind mutation retry across epochs.

Stored, durable, activated and visible are independent response facts. Errors carry
stable code, bounded safe text and retryability. Native implementations still need
fragmented/coalesced frame, timeout, saturation, reconnect and cancellation tests;
JSON shape fixtures alone do not execute this transport.

The [W-25 telemetry document boundary](../delivery/packages/w-25-telemetry-wire.md)
now defines versioned subscribe/unsubscribe and full replacement snapshot/delta
shapes, bounded native decoding and exact body replay preservation. The
[telemetry schema](telemetry.schema.json) reuses snapshot/observation 0.1.
The bounded subscription/complete-state adapter is now exercised by native
inventory probes; preview-only and health compositions keep their feature set.
The [measured-time extension](../delivery/packages/w-25-measured-time.md) explicitly
selects the 0.2 triple and qualified clock domain without changing wire framing,
queue limits or exact body replay identity. Product demand/collector/policy
integration and native qualification remain separate gates.
