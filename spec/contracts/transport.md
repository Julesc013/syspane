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
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
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
profile. A connection has bounded queues and at most 128 outstanding requests;
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

Snapshot/delta sequence and producer epoch must agree. A gap, validation failure or
new epoch invalidates incremental state and requires a coherent full snapshot.
Independent surface leases expire after three missed negotiated heartbeat periods;
the experimental heartbeat period is one second. Metric freshness remains separate.
Subscriptions have per-role demand leases and cancellation revokes only that demand.
Role-specific native tests must prove access control and progress under saturation.

## Requests, cancellation and results

Request IDs are scoped to authenticated principal, installation/session and producer
epoch. Identical replay returns the recorded result; changed bytes under the same
ID are a conflict. Deduplication retains terminal results for at least ten minutes
within the 128-request admission limit. When retention cannot be guaranteed, reject
new mutations with a busy outcome before executing them, rather than evict a live
deduplication entry. Committed request identities persist with their generation.

Cancel before commit may abort preparation. After commit it cannot undo the accepted
generation; return the committed result with activation status. A lost connection
does not prove cancellation. `result.get` reads a retained result without execution;
expired/unknown outcomes require reconciliation of revision and request journal,
never blind mutation retry across epochs.

Stored, durable, activated and visible are independent response facts. Errors carry
stable code, bounded safe text and retryability. Native implementations still need
fragmented/coalesced frame, timeout, saturation, reconnect and cancellation tests;
JSON shape fixtures alone do not execute this transport.
