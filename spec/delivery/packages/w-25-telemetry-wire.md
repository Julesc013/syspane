---
type: "SysPane Work Package Boundary"
title: "W-25 bounded telemetry delivery document"
description: "Close versioned subscription and snapshot delivery shapes without treating decoded documents as admitted native subscriptions."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:20:37+11:00"}
sp_id: "SP-W25-TELEMETRY-WIRE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-DATA-VIEW", "SP-W24-PACKAGE", "SP-PROTOCOL", "SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 bounded telemetry delivery document

This boundary owns `source/protocol/telemetry.*`, the telemetry 0.1 schema and
portable native-compiled conformance cases. It defines a delivery document around
the existing snapshot/observation 0.1 documents; their identities and fixtures stay
unchanged. The model remains independent of JSON. Ordinary three-profile commands
compile and test the codec. A codec pass does not enable a transport feature.

## Exact messages

All four messages use existing wire 0.1 post-handshake envelopes. Require the
negotiated feature `telemetry.snapshot` and exact document versions `telemetry`,
`snapshot`, `observation`, all `0.1.0`. Existing preview and health sessions do not
advertise these. The local authenticated session owns the binding: connection ID,
producer epoch/ID, subscription ID, policy revision, channel and classification.
No body field establishes authentication, policy provenance or a role grant.

| Type | Direction | Exact body members |
|---|---|---|
| subscribe | Consumer to producer | `schema_version`, `subscription_id`, `producer_id`, `policy_revision`, `channel`, `classification` |
| unsubscribe | Consumer to producer | `schema_version`, `subscription_id` |
| snapshot | Producer to consumer | `schema_version`, `subscription_id`, `producer_id`, `policy_revision`, `record_id`, `snapshot` |
| delta | Producer to consumer | Snapshot body members plus `base_generation` |

Version is exactly `0.1.0`. IDs use existing bounded ASCII grammar; all revisions
and generations are canonical uint64 decimal strings. Channels are desktop,
inspector, saver or preview; classes public, operational or sensitive. Every
applicable binding member must match exactly, including snapshot epoch. A delta
contains a complete proposed replacement snapshot and a strictly smaller expected
base generation, matching the initial typed model boundary. It is not a field-patch
language. The consumer still checks its actual accepted base and replay history.

## Bounded decoding and preservation

Decode one complete payload under its negotiated frame limit (at most 1 MiB),
existing UTF-8/duplicate-key/depth-32/node-16,384 rules and exact core member sets.
Return stable fixed error codes; do not expose input values or parser diagnostics.
Convert allocation failure to `telemetry.capacity`. The caller owns framing,
five-second deadlines, closure and queue lifetimes. Count/byte/parser bounds are
admission bounds, not exact RSS guarantees.

Validate snapshot/observation 0.1 shapes, uint64 ranges, date/time syntax and calendar
dates, graph references and duplicate identities/observations. Observation uniqueness
is `(entity_id, field)` as in the existing snapshot semantic checker. Entity and
observation generations may be older than the snapshot but cannot be newer;
observation epochs must equal the snapshot epoch. Unknown core members fail.
Retain entity identity maps (at most 64 entries), extensions and every original
timestamp/value/status/completeness field. Text uses UTF-8 byte ceilings matching
the native profile; identity keys are additionally at most 256 bytes. Extensions
have at most 64 keys matching the existing extension-name grammar; their bounded
contents remain inert. No extension can add a required operation or grant access.

Timestamps remain original offset-bearing strings, including valid subnanosecond
fractional text; this codec neither truncates precision nor compares remote clocks.
Accept years 0001..9999, valid Gregorian dates, hours 00..23, minutes/seconds 00..59,
`T/t`, `Z/z` or offsets through 23:59, and at most 64 bytes. Leap seconds follow the
existing profile's explicit rejection. Model/clock conversion is a separate gate.

Preserve `complete`, `partial` and `gap` distinctly. These shape-valid documents are
not all synchronization successes: only a coherent complete full snapshot may clear
a consumer gap. A partial/gap document cannot silently remove omitted model data.
Likewise, a full state document may report a failed/denied acquisition with a retained
non-null value. It must not be passed as a fresh acquisition attempt to `Store::publish`,
which intentionally derives retained data from local history. Its native consumer
mapping must preserve remote reported state and validate retention provenance.

The codec returns the validated envelope, including the original body bytes and
complete JSON tree. Re-encoding uses those original body bytes, preserving replay
identity rather than silently normalizing whitespace or numeric spelling. No model
projection, live lease, native disclosure or synchronization is created here.

## Native admission and lifecycle still required

Before advertising the feature, connect current mandatory policy and native peer
roles, bounded per-role demand leases, subscription/replay ownership, resync requests,
complete-state import, producer-monotonic provenance and invalidation of queued data.
An unavailable mandatory policy must deny subscription even for public data. Every
decoded candidate must be admitted against the current binding/policy again before
publication; decoding success alone grants nothing. Clock/role authorization cannot
come from an extension. Reconnect must preserve the data owner's existing same-epoch
history; policy replacement must invalidate its attachment and all queued callbacks.

Do not truncate an oversized coherent snapshot or call it complete. Paging/chunking
needs a versioned atomic assembly contract before it is enabled. These remaining
native lifecycle gates, real collector/renderer recovery and independent visibility
remain W-25 work, with no desktop or historical-runtime claim from this codec.

## Fixed acceptance

| Family | Required evidence |
|---|---|
| TELEMETRY-SNAPSHOT | Existing snapshot fixture survives decoding with identity and all observation fields unchanged; large uint64, retained-denied and unsupported observations remain exact. |
| TELEMETRY-MESSAGES | Subscribe/unsubscribe/full/delta shapes and bindings; direction, feature/version, connection/epoch, policy/channel/class and base errors rejected. |
| TELEMETRY-GRAPH | Duplicate entities/sources/observation fields, dangling relationships, unknown references, mismatched/future generations and epochs rejected. |
| TELEMETRY-TIME | Leap/calendar/offset/date bounds and fractional text retained; no timezone-less or leap-second timestamps accepted. |
| TELEMETRY-BOUNDS | Framing/parser budgets, duplicate escaped keys, count/text/identity/extension/value bounds, unknown core fields and overflow rejected without an admitted document. |
| TELEMETRY-PRESERVE | Complete/partial/gap and nested inert extensions remain distinguishable; exact body replay bytes survive re-encoding; original fixture expectations remain independent of the codec. |

Preserve attempts and bind source/profile/artifact identities. Run existing native
regressions because this library shares the protocol dependency; do not report their
passes as native telemetry execution. Continue the next consumer/lifecycle gate
after this codec checkpoint instead of declaring W-25 complete.

The historical test executable reads canonical fixtures through the static C++
file-stream implementation, which adds mandatory Kernel32 `SetEndOfFile` to its
import closure even though the fixture stream is opened for reading. The original
audit failure and complete import table are preserved. Microsoft's
[API requirements](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setendoffile)
identify Windows XP as its minimum client. Declare only that observed additional
import; retain the existing PE/CRT/import rejection rules and separate unexecuted
guest-runtime gate. The API's presence in documentation is not a guest execution.
