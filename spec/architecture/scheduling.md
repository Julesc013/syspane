---
type: "SysPane Specification"
title: "Acquisition planning, reconciliation and backpressure"
description: "Share collection work, use notifications where suitable and report evidence loss."
tags: ["architecture"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-SCHEDULER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ARCHITECTURE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-06T08:15:42+11:00", "scope": "Link bounded native inventory subscription and remaining product demand/clock work"}
---

# Acquisition planning, reconciliation and backpressure

## Acquisition classes

Notifications invalidate a source/domain. Sampling measures interval quantities. Inventory runs at startup, relevant change or explicit refresh. Active diagnostics require separate authorization. Declare the class for every field; do not describe all collection as zero polling.

Consumers request fields, entity scope, maximum age, priority and recording needs. The planner merges compatible requests, so five widgets do not query the same counters five times. Policy caps frequency and active-probe load. A hidden widget can release demand while an admitted history recording continues.

## Race-safe source lifecycle

Subscribe first. Enumerate into a staging snapshot while tracking dirty generations. Apply indications received during enumeration. Publish a coherent accepted generation. If the dirty generation advanced during a query, reconcile again. Reject results tied to a destroyed source/entity generation.

Callbacks copy necessary identifiers and timestamps, increment dirty state or enqueue a bounded indication, and return. They do not render, block on I/O or hold model locks during native queries. Cancellation and notification registration lifetimes are explicit parts of each provider contract.

Use leading work plus bounded coalescing, not an indefinitely reset trailing debounce. Initial proposal: combine a short burst within 50–150 ms where that fits the source; guarantee a maximum waiting bound through the scheduler. These numbers are tunable hypotheses, not measured results. Urgent terminal states may bypass ordinary coalescing.

## Queues and overload

Separate coalescible current-state invalidations from ordered evidence. A current-state mailbox may replace an older pending value. A history queue must retain sequence and explicitly record overflow. Under overload, lower update frequency for nonessential samples, preserve health/error signals, emit a gap and trigger resynchronization. Never claim a complete event history after dropping records.

Per-source concurrency is bounded. Do not create a thread or periodic timer for every metric or adapter. A source has a health circuit breaker, attempt timeout, retry budget and backoff; it cannot starve unrelated providers. Equal priority work uses a fair queue, not strict starvation-prone ordering.

## Time

Use monotonic elapsed time for rates, deadlines and durations. Record UTC with explicit offset for audit timestamps; wall-clock changes must not reorder monotonic event sequences. Across boots or producers, do not compare monotonic times without a mapping. Rate calculations use the actual elapsed interval and detect counter reset/wrap instead of reporting negative traffic.

## Suspension

Drawing, sampling and recording have independent policies. Display off or lock suspends unnecessary presentation. An explicitly admitted overnight recording may continue. Resumption forces reconciliation and publishes any gap. Timer resolution is not raised merely to draw one-second statistics; timestamp precision and wake frequency are distinct choices.

## Demand leases and profile budgets

Desktop, inspector, saver and recorder requests have independent leases and share
source acquisition. Saver exit does not stop an enabled recorder. Descriptors expose
minimum sample interval, cost, permission and cancellation scope. Bound queue bytes,
entity/string work, concurrency, deadlines and retries before enabling a source.
Reserve progress for policy revocation, health and final-state publication during
sustained storms; explicit evidence gaps survive coalescing. A stuck unkillable
operation cannot spawn unlimited replacement workers. See [recovery](recovery.md)
and [metric descriptors](../telemetry/metric-registry.md).

The [initial subscription boundary](../delivery/packages/w-25-subscriptions.md) now
connects one fixed inventory source per authenticated connection to bounded demand
and current-policy queues. Its [native checkpoint](../delivery/subscriptions-handoff.md)
uses synthetic inventory; general demand aggregation, measured-field clock mapping
and independently supervised real collection/rendering remain required.
