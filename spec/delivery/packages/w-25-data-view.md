---
type: "SysPane Work Package Boundary"
title: "W-25 synchronized model view and policy lifetime"
description: "Join model validation, producer leases and revocable presentation without enabling an unspecified wire subscription."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:58:29+11:00"}
sp_id: "SP-W25-DATA-VIEW"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-STATE", "SP-POLICY", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 synchronized model view and policy lifetime

The next dependency is a data owner that joins the implemented model validator and
producer lease. `syspane_data_view` owns this boundary in `source/diagnostics/` and
depends on model, recovery and configuration policy; their existing dependency
directions remain unchanged. The three current C++17 profiles may compile it.
It is an in-process consumer component. Native subscriptions, wire snapshot/delta
codecs, real collectors and visible rendering remain separate required integration.
Do not advertise a transport feature based on these typed cases.

## Ownership and admission

One serialized independent event-loop owner supplies local monotonic milliseconds,
authenticated authority, current mandatory policy and typed complete publication
candidates. Attachment tokens are lifetime guards, never authority. One view fixes
one role/channel/classification and metric registry. Allowed channels are desktop,
inspector, saver and preview; classification is public, operational or sensitive.
The producer must classify the entire supplied projection at least as restrictively
as every field, identity and label in it. Mixed classifications require upstream
filtering and classification; this component cannot infer sensitivity from values.

Require available policy, authenticated role grant, no `telemetry.subscribe` denial,
and permission for the fixed channel plus accessibility at that classification.
The owner does not grant itself a role. A denied attachment admits no data or lease.
All data calls carry both local attachment token and admitted policy revision.
Old tokens and revisions are rejected before reading candidate content or advancing
the successor clock. A trusted adapter must obtain the token after authentication
and bind the policy revision to its subscription; untrusted document fields cannot
supply either provenance.

Exactly one model store is owned. Reattach to the same producer/epoch under the
same policy retains validation/replay/tombstone history but requires a full snapshot.
A new producer/epoch keeps the old data available only as explicitly retained until
a complete valid new snapshot is accepted, then replaces it atomically. No old
observation is relabelled to the new producer. Delta candidate shape remains the
model's complete proposed next snapshot plus exact expected base, not a new wire
patch format. Full candidates have no expected base.

Use existing model limits: 8 MiB accounted candidate, 64 MiB replay/retired storage,
128 publication identities, existing graph/observation counts. The metric registry has at most
1,024 entries; limits may be tightened but not increased by this profile. Local
view-lifetime serial exhaustion fails closed without wrapping. A speculative copy
of validation state may exist during admission, sharing immutable records; its
additional accounted state is at most the same store limits plus one candidate.
These are admission bounds, not an allocator/RSS guarantee. No capacity failure
resets history or synthesizes a new producer epoch. Trusted caller construction and
future bounded wire decoding remain outside this typed API's allocation boundary.

## Atomic data and lease transitions

Validate the whole candidate in a speculative model store before changing the
accepted data or lease generation. Wrong identities, duplicate graph members,
invalid observations, missing bases, record conflicts, generation regressions and
capacity failures retain the prior coherent data and require a full snapshot.
The model's exact replay detection still runs before generation/base rejection.
A replay of an older accepted record does not move the current view backwards or
update acceptance time. While resynchronization is required, a delta is rejected
even if it replays a prior record. Only a complete full snapshot may clear the gap.

A full snapshot with the current generation may re-establish synchronization when
its complete normalized snapshot equals current data. Validate its shape using a
speculative store before equality/replay handling; changed bytes under a previously
used record ID remain a conflict. A new full record ID at the same generation may
confirm exactly the current normalized data and consumes its ordinary replay/storage
reservation. Changed same-generation data is a conflict; a lower generation is an
ordering failure. Add an explicit consumer-only `Store::resynchronize` operation;
ordinary producer `Store::publish` keeps its strictly increasing generation rule.
Never create a new store merely to accept a confirming full snapshot. This connects
the standalone lease helper's existing same-generation recovery semantics to data.

Heartbeat, gap, disconnect and expiry retain existing 3,000 ms lease behavior.
Data never renews the lease. Heartbeats never renew metric freshness or clear a gap.
Clock regression latches a fault; a superseded token cannot inject a regressed time.
An invalid current publication creates a gap even when its previous payload remains
available. Every status/projection call advances the observed clock/expiry first.

## Presentation and revocation

Status contains only fixed state/reason codes, permission, synchronization and a
local lifetime serial; it exposes no producer, epoch, generation or payload while
denied. Projection uses a synchronous borrowed callback after a fresh local policy
decision. No shared snapshot handle escapes. The callback may display during that
call but may not retain references, cache/export the payload, or reenter the owner.
Future render queues need their own policy-bound invalidation; this API alone does
not qualify them. C++ callers are trusted components, not a hostile-code sandbox.

Projection describes active versus retained data separately from metric validity.
It does not rewrite observation timestamps, values or acquisition/error states.
Consumers must present retained data as stale even if its last observation was
current. The callback receives the unchanged snapshot and explicit lease status;
an active lease never overrides `model::freshness_at` or TTL calculation.

Replacing current policy requires a strictly higher revision, except that any
unavailable snapshot immediately removes data even with an unchanged/lower revision.
Malformed same/lower-revision available replacements fail closed. Every observed
policy replacement invalidates the attachment, drops all owned payload/store
references and increments the view lifetime before any further projection, even if
the new permission still allows access. A later grant requires a new authenticated
attachment and full snapshot tagged with its new policy revision. It never restores
a cached payload. Clock fault cannot prevent revocation.

This new authorization/subscription lifetime has no inherited consumer identity
bindings. The authoritative producer must still preserve its own epoch-wide identity
and replay history; consumer revocation is not permission to recycle source IDs.
Releasing this owner's references is not physical memory zeroization, deletion of
user files, revocation of previous exports, or erasure of other components' copies.
The broader policy/data-erasure and native renderer gates remain open.

## Fixed acceptance and execution

| Case | Required observations |
|---|---|
| VIEW-ATOMIC | Initial full publication; invalid graph/observation leaves exact prior value/generation; valid full snapshot recovers; mismatched delta base yields retained/resync. |
| VIEW-REPLAY | Exact full/delta replay preserves current data and acceptance time; changed record bytes conflict; new full record can confirm identical current data but cannot change it or evade capacity; full replay after gap restores synchronization. |
| VIEW-RECONNECT | Same-epoch reconnect preserves retired-ID and replay reservations; new epoch waits with explicitly old retained data then atomically replaces it; obsolete token cannot poison successor time. |
| VIEW-LEASE | Native-owner timestamps drive expiry at 3,000 ms; data traffic/duplicate heartbeat do not renew; failed acquisition retains model value but is stale; current heartbeat does not refresh TTL. |
| VIEW-POLICY | Wrong authority/channel/class or unavailable policy blocks attachment and callback; revision replacement drops data; stale revision callback cannot advance time; renewed permission needs new attachment/full snapshot. |
| VIEW-FAULT | Clock regression latches; revocation still removes data; bounded model capacity retains prior state; callback exceptions unwind without corrupting owner and reentrancy fails. |

Run ordinary configure/build/CTest commands on all three profiles. Keep fixed literal
input/expected values independent of implementation, preserve failed attempts, bind
source/profile/artifact identities and state native integration as unexecuted.
