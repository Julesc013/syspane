---
type: "SysPane Work Package"
title: "Shared controller demand and acquisition ownership"
description: "Merge authorized consumer leases, schedule bounded source work and retain ownership until stopped work is confirmed."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T14:10:00Z"}
sp_id: "SP-W07-DEMAND-OWNER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SCHEDULER", "SP-POLICY", "SP-W25-SUBSCRIPTIONS", "SP-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared controller demand and acquisition ownership

This controller prerequisite is admitted under the foundation campaign's transport,
policy and recovery scope. W-07 owns its reusable implementation in `source/runtime/`;
W-25 consumes it when replacing fixed collection demand. It is not a second session
runtime or a new wire protocol. Existing Sessions authenticate connections and own
outboxes; this owner receives locally authenticated authority and validated demand.
Installed controller/session adapters and native source execution remain separate
integration gates. No process or task becomes authorized by possessing a ticket.

## Inputs and policy

One serialized owner has an immutable catalog of at most 16 sources and 256 unique
fields. Source/field/entity IDs use the existing 256-byte identifier grammar. A source
declares its collection capability, minimum interval (100–3,600,000 ms), timeout
(1–60,000 ms), optional existing cadence-setting path and fields with public,
operational or sensitive classifications. Active diagnostics are not admitted.

At most 32 consumer leases hold at most 64 unique field/entity selections each.
An absent entity means all entities for that field; a present entity is an exact
lifetime ID, never a name/position selector. Each request has one channel, maximum
age (100–3,600,000 ms), priority 0–3 and recording flag. Desktop/desktop,
console/inspector, saver/saver and preview/preview are allowed nonrecording pairs;
console/history is the recording pair. Native authentication and role grants must
agree. The owner never reads policy from a consumer payload.

Collection requires available mandatory policy, absence of `telemetry.subscribe`
denial, the catalog source's collection capability, and allowed disclosure for every
selected field on the requested channel. Recording additionally requires absence
of `history.record` denial. This does not authorize another channel, storage writes
or native source permissions. Reject a mixed allowed/denied request atomically.
Projection, accessibility and retained-data erasure remain independently enforced.

The native composition supplies the existing immutable `configuration::Policy`.
Replacement first retires every lease and invalidates all outstanding work. An
available replacement must have a revision strictly above the highest available
revision observed by this owner; an invalid revision leaves policy unavailable.
Unavailable policy never permits collection. Later valid regrant needs fresh demand;
no old lease, queued job or callback is revived. Existing records are not purged.

## Lease and plan semantics

Admission allocates a unique nonzero uint64 lease and starts the existing 3,000 ms
lease. Only a strictly increasing heartbeat sequence renews it. The first sequence
may be zero. Duplicate renewal is a no-op; regression retires that lease. Release
and exact expiry remove only that consumer. A saver exit therefore preserves an
independent recorder. Changes use release followed by fresh admission; no retained
lease can change authority. IDs are never recycled or wrapped within the owner.
Exhaustion faults the owner with capacity status, retires demand and cancels jobs;
only stop confirmation can drain existing slots afterward. A locally supplied test
limit may lower the uint64 identity ceiling without changing those semantics.

Merge selections by source and field, union exact entity IDs and let all-entity
selection subsume individual IDs for that field. The source uses the smallest
requested maximum age, highest requested priority and any recording demand.
Its interval is the maximum of the requested age floor, source minimum and any
forced existing cadence setting. Report `age_feasible=false` when a cap prevents
the requested age; scheduling never proves actual freshness. A change to merged
fields, scope, cadence, priority or recording increments a source plan revision
and cancels outstanding work from the previous plan. Identical merged demand does
not create duplicate queries or invalidate a useful job.

Initial demand is immediately eligible. Later dispatches respect the interval
from the previous dispatch, including failures and released/readded demand; demand
churn cannot reset the rate cap. A completion does not rewrite the sample timestamp.
The model/provider retains actual acquisition, identity and reconciliation duties.

## Scheduling and stop proof

At most one job per source and a configured total of 1–8 jobs may be outstanding.
The effective total is additionally capped by forced `sampling.max_workers`.
Lowering that cap blocks new dispatch until outstanding count falls below it;
it does not manufacture completion of existing work. Selection uses priority aged
by one level per 1,000 ms of continuous eligibility, capped at 3. Ties prefer the
oldest eligibility time, then least recently dispatched source, then source ID.
This provides bounded priority aging and deterministic fairness without timers or
threads per consumer. The host calls `tick`/`take` on its independent bounded loop.

A job carries unique ticket, source, plan revision, policy revision, merged fields,
interval, feasibility and start time. Timeout at equality, demand removal/change,
policy replacement or clock failure marks the job cancelled. Cancelled work still
occupies its source and global slot until the owner receives its exact completion
or explicit stop confirmation. A timeout never authorizes an unbounded replacement
pool. `complete` returns obsolete for cancelled or superseded work; it cannot publish
such a result. An unknown/old ticket cannot free another job. The native executor
must stop/confirm its held worker using the existing recovery contract.

All operations advance expiry before processing their input, including renewal and
completion. Monotonic regression permanently faults the owner, clears demand and
cancels jobs. Native stop confirmation remains allowed to drain those slots. Use
subtraction for elapsed bounds; no deadline arithmetic may wrap at uint64 maximum.
Allocation exceptions escape to the composition's bounded failure handling; no
allocation failure authorizes collection. The catalog/request bounds cap metadata;
the owner stores no telemetry values, native handles, history or unbounded event log.

## Fixed acceptance and delivery

Implement `syspane_demand` with typed interfaces and ordinary CMake/CTest integration
on the existing Windows, Linux and historical-toolset host profiles. Fixed cases
must prove: five widgets merge into one acquisition; exact/all-entity union; native
role/channel and mixed-field denial; recorder survival after saver release; duplicate
and exact-expiry heartbeat behavior; policy invalidation/regrant; stale completion
and confirmed-stop slot retention; timeout equality; policy worker/cadence caps;
continuous-eligibility aging and equal-priority fairness; changed and unchanged
plans; capacity rejection; uint64 exhaustion and permanent clock fault.

Tests use independently written expected job fields and dispatch order. A component
pass is not native source cancellation, installed policy or desktop qualification.
Keep the existing transport, native collector and desktop evidence intact. Handoff
must identify exact source/build artifacts, executed cases, failures, remaining
native integration and the next admitted step. W-07/W-25 stay open until their
actual native and full scheduling/reconciliation requirements are met.

## Admitted Linux executor integration

Connect the existing Linux collector's authenticated fixed network subscription to
one DemandOwner lease selecting its four operational network fields at 1,000 ms.
The session still owns the wire subscription and rejects invalid input. Only its
accepted increasing client heartbeats renew acquisition demand; a busy loop cannot
renew it. Subscription loss retires this source composition rather than guessing
that consumed native topology indications can be replayed into a later lifetime.
Wire document versions, measurement clocks and existing publication oracles stay fixed.

Acquisition runs outside the IPC/health owner on at most one native worker thread.
The existing watched netlink source is exclusively used by that thread until join.
Capture qualified measurement start/end and UTC acquisition time in the worker,
not when its completion is delivered. The collector's stream clock is accessed only
by that worker while it runs; the IPC owner retains byte I/O and stream lifetime.
The source minimum cadence is 1,000 ms, acquisition deadline 2,000 ms and demand-job
timeout 2,500 ms. No second task or source replacement may begin until the held
thread has completed and joined. Cancellation is an atomic request, never stop proof.
The independent parent retains the existing whole-process termination fallback if
the native source or join cannot finish; no detached replacement thread is allowed.

Before considering a result, process current session/policy/lease state, cancel any
invalidated task, and join a completed task. Only DemandOwner's exact current-job
completion permits NetworkState commit and publication. Discard obsolete values;
retire the source/watch after lost demand, including any consumed indications.
Preserve unchanged original measurements and explicit acquisition failure semantics.

Fixed native cases must observe a real acquisition and live OS worker thread, then
prove merged desktop/saver/recorder demand survives desktop/saver release, cancelled
work retains its slot until join, revocation rejects new demand and old completion,
and timeout rejects a late result. A bounded test-only delay after the real read may
hold a result even after cancellation to make these boundaries observable. It must
not rewrite acquisition timestamps. Independently bracket counters and clock values,
observe native thread disappearance before replacement, and retain failure evidence.
Rerun existing collector and consumer-continuity acceptance without changing their
expectations. Typed test policy and this Linux composition do not qualify installed
policy distribution, multi-client wire selection or another native platform.
