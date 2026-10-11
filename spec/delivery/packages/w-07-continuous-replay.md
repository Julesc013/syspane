---
type: "SysPane Work Package"
title: "Continuous measured telemetry with reserved sequence identities"
description: "Close the foundation's long-running replay boundary without unbounded payload storage or epoch cycling."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T00:00:00+00:00"}
sp_id: "SP-W07-CONTINUOUS-REPLAY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-W25-STATE-IMPORT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Continuous measured telemetry with reserved sequence identities

The chart experiment admits 128 distinct snapshots, then rejects publication 129
with capacity. The foundation assigns this unresolved boundary to W-07. Close it
before claiming continuous native collection or maximum-history qualification.

## Negotiation and identity

Add the feature telemetry.monotonic-replay to the existing measured-time 0.2.0
contract. Select it only from an authenticated negotiated binding and a trusted
source that explicitly offers it. Require measured-time and all three 0.2.0
documents. Unselected bindings retain the original epoch-reserved replay policy,
128-record exhaustion and arbitrary bounded record IDs. No received payload may
select a replay policy. A same-policy/producer/epoch reconnect cannot switch the
policy or reset any reservation, retired identity or measured-time high-water mark.

Selected streams carry complete snapshot messages only. Their record_id is
sample:N, where N is a canonical positive uint64 decimal, without leading zeros,
signs, whitespace, overflow or wrapping. N is an independent publication sequence;
it need not equal the snapshot generation. The producer owns it for its epoch,
across connections/subscriptions. Increasing sequence may confirm the identical
current generation under a fresh body identity; normalized snapshot and preserved
document equality remain mandatory. Deltas need a separately admitted extension.

## Bounded replay and permanent reservations

The shared model adds an explicit monotonic-window policy for complete reported
state. Its default remains epoch-reserved. Keep the existing 8-MiB candidate,
64-MiB retained-data and 128-record ceilings. Store two fixed uint64 watermarks:
the highest admitted sequence and the highest retired sequence (initially zero).
Retain up to 128 newest original candidate/body records within the retained-byte
budget, retiring oldest sequences only as part of an accepted new publication.
Retired sequence identities remain permanently unavailable through the watermark;
the model never forgets the reservation or silently accepts a reused identity.

For a retained record, exact original replay is duplicate; altered reuse is
conflict. A sequence at or below the retired watermark is replay_expired, an
explicit failure, even when the caller supplies apparently identical data. An
unretained sequence at or below the admitted high-water mark is record_order.
Every new sequence must be greater than that high-water mark. Preserve the same
checks on snapshot generation, typed values, full confirmation, measured time,
retired entities, complete coverage and current policy. Neither error admits or
replays data, advances watermarks, evicts a record, or renews a lease.

Before commit, validate the entire candidate and prepare replay reclamation,
snapshot, permanent tombstones and measured-time reservations in temporary owned
state. Retire enough oldest replay payloads to fit count and byte ceilings; never
retire permanent entity/time bookkeeping. If the candidate plus persistent
bookkeeping cannot fit, return capacity with the old snapshot and reservations
intact. Allocation failure has the same atomicity. Publish all owners and both
watermarks together. This remains logical payload accounting, not an RSS quota.
External immutable snapshots preserve the existing reader ownership contract.

## Native composition and failure

The Linux network source explicitly offers the feature; its ordinary native
consumer requires it. Select sample:N records for selected subscriptions and
retain the old record grammar for unselected clients. All source-demand, one-second
cadence, authenticated transport, policy, cancellation and supervision boundaries
remain current. The two-second source deadline and independent shutdown owner
continue to apply. A rejected old/altered record is a protocol/model fault with
the existing explicit gap/disconnect behavior, never an automatic policy or epoch
reset. Producer sequence exhaustion is an explicit terminal fault.

DataView constructs the correct model policy only after binding validation.
Compatible reconnect preserves it; incompatible policy selection rejects before
changing the old attachment. Policy withdrawal still clears all state. The native
inspector adopts the same negotiated binding and reserves the same identities.

## Acceptance and evidence

Freeze tests before implementation. Require at least 4097 accepted complete
publications under one producer/epoch/policy, exact current state, replay of a
retained record, changed retained body conflict, expired identity refusal, late
unseen sequence refusal and canonical uint64 limits. Check invalid candidates do
not advance or retire anything; same-generation confirmation remains exact.
Force count and retained-byte reclamation separately. After reclamation, verify
retired entities and per-field time reservations still reject reuse/regression.
Keep original model/import/measured-time/session tests and legacy capacity cases.

Wire tests cover feature absence, incompatible documents, deltas, malformed IDs,
compatible reconnect and an attempted policy switch. Verify authenticated source
negotiation and the ordinary installed consumer/service. Run shared checks and
historical import audits on all three development profiles. Re-run the unchanged
chart/mixed oracle: 3138/2087 last-fitting points, explicit frame alternatives,
window recovery and policy erasure; preserve all earlier failures and corrections.
Keep native GTK/installed maximum-history and human accessibility qualification
separate from this receiver/frame boundary. All five release editions remain open.

The ordinary native consumer fixture adds an explicit --continuous test mode with
a 160-second child lifetime, 150-second observation limit and 180-second CTest
deadline. Observe at least 130 successive actual one-second source publications
through the supervised installed helper and authenticated consumer. Require one
unchanged producer epoch, exact sample sequence/generation order, real counter and
clock comparisons, preserved original wire bytes, and exact child reaping. Bound
retained fixture events to 512/32 MiB and stderr to 1 MiB. Short original consumer
cases keep their prior lifetime limits. This proves crossing the replay boundary
at native cadence; it does not qualify a 4096-point installed GUI workload.
