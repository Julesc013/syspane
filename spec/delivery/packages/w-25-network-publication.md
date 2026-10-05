---
type: "SysPane Work Package Boundary"
title: "W-25 supervised measured network publication"
description: "Connect real network counters to measured state with independent child recovery and current policy."
tags: ["delivery", "telemetry", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:00:24Z"}
sp_id: "SP-W25-NETWORK-PUBLICATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-NETWORK-RECONCILIATION", "SP-W25-MEASURED-TIME", "SP-W25-SUBSCRIPTIONS", "SP-W25-PACKAGE", "SP-NETWORK"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 supervised measured network publication

Own the source-to-document adapter in `source/runtime/`, the finite native
composition in `source/application/` and fixed portable/native cases. Reuse
NetworkState, NetworkWatch, Sessions, DataView, HealthLink, Child and RestartGate.
Do not fork those owners or change existing document/contract identities.
Linux runs the native composition now; Windows notification coverage and historical
native readers remain independent gates. Shared projection runs on all profiles.

## Document and metric meaning

Project accepted network state into the existing complete snapshot/observation 0.2
documents. Producer is `producer:network`, source is `provider:native-network`,
source kind `native.network.counters`, scope `host:local`. Each entity ID is
`network:interface:<lifetime>` within its producer epoch. Its kind is
`network.interface`; its generic display label includes only the lifetime number.
Identity metadata records decimal `native_index` and `native_type` as ephemeral
lookup facts, not persistent selector evidence. Do not include names, addresses,
packet data or unrelated host identity. Sort by native key as the source owner does.

Publish four fields per interface: `network.receive_bytes`,
`network.transmit_bytes` (uint64/`byte`, observed cumulative counters), and
`network.receive_bytes_per_second`, `network.transmit_bytes_per_second`
(number/`byte/second`, derived interval averages). Preserve the receive descriptor's
identity; add the other descriptors to the existing registry. Initial cadence is
1,000 ms and TTL 3,000 ms. These fields do not attest connection state or throughput
at a physical instant, and do not complete the larger network inventory/join view.
Their acquisition cost conservatively records potentially blocking native sampling;
the arithmetic alone is cheap. Independent worker supervision remains mandatory.

Rate is double(delta) / double(interval_ns) * 1e9, with finite nonnegative output;
acceptance compares against an independent rational calculation with relative
tolerance 4e-15 and absolute tolerance 1e-9 byte/second. Counters remain exact decimal
uint64 strings. First/reset/replaced/missing/equal-time samples have no rate value,
pending acquisition, unknown freshness and null measured/observed time. A valid
zero interval delta gives a successful zero rate. `sample_interval_ns` is the actual
positive interval for rates and null for cumulative counters.

Observation `measured_at` is the acquisition start tick, never receipt/publication
time. The native owner samples UTC separately at that attempt for descriptive
`observed_at`; UTC does not order samples or drive leases/rates. Retain that UTC with
the accepted sample. Every attempt has its own UTC `attempted_at`/`captured_at`.
Snapshot, entity and observation generation identify the publication state revision;
retained value age is carried by original measured/observed time. Publication revision
increases for each new state, including a reported acquisition failure, without
changing NetworkState's accepted acquisition generation. Exact replay retains the
same record, snapshot generation, values and original body bytes.

A failed acquisition after a successful one publishes the prior complete table,
counter/rate values and original times with failed acquisition, stale freshness and
a fixed bounded retryable `network.acquisition_failed` error. Missing values remain
null/unknown. Failure before any accepted table sends no invented inventory.
Dirty acquisitions are not published; continuity or clock faults end the worker.
The next successful rate spans the actual interval since the last accepted sample.
Successful removal drops the old entity; reappearance uses the new source lifetime.

The adapter receives only source-owned samples. Validate basic IDs, revision,
timestamps and row/lifetime bounds, then use the existing codec and consumer model
for graph and observation validation. Construct the document before offering it;
never expose a partial prefix. Limit serialized snapshot bytes to frame_limit-8192,
reserving envelope overhead. Account bounded fragments before appending them.
Exceeding the complete-frame budget fails explicitly and retains prior consumer
state; do not silently cap inventory, chunk under an unnegotiated format, or claim
large-inventory qualification. Retained/replay capacity stays under existing limits.

## Native composition and ownership

The finite `SysPane.CollectorProbe` launches only its own exact child through Child.
The parent owns two private listeners, independently authenticates the child PID
on both, and keeps their endpoint lifetime even if the child is terminated.
The child arms parent-death cleanup and connects both streams to the exact parent.
One stream uses unmodified recovery-health with collector role. The other reuses
Sessions' existing console server and a desktop-role development consumer with
typed operational policy. This explicitly named test composition is not a new
product authorization rule or an installed collector/controller service.

The child serializes source demand, watch, identity, acquisition, projection and
Sessions. It creates the watch/identity owner only after an authorized subscription;
captures the demand ticket and watch revision before acquisition; applies delivered
indications before commit; and rechecks active subscription/current policy before
offer/dequeue. Demand loss clears pending data and destroys source owners. The
experiment does not restart a retired source within the same epoch. A closed watch
or failed qualification cannot become an unobserved raw-reader fallback.

Sample the already-qualified data stream clock before and after each native read;
bind the source owner to its local scope. The consumer uses its own qualified local
scope, the same native clock domain and existing 0.2 receive/high-water checks.
No local process/namespace scope is transmitted as a wire authority claim.

The parent never performs the potentially blocking acquisition. Its health loop
ticks producer/data leases independently, sends increasing heartbeats at least once
per second, and polls bounded native reads. Real data alone cannot renew a lease.
Child health and data demand are renewed separately. Parent loss, policy denial,
unsubscribe and shutdown discard applicable queues/owners. Typed revocation is a
fixture, not proof of installed policy propagation or whole-product cache erasure.

On child hang/exit, mark the consumer retained without rewriting observation times.
Quarantine the child slot while stop is unconfirmed. Request cooperative shutdown,
then stop only that held child if necessary; require OS-confirmed exit before
RestartGate admits a replacement after its existing backoff. Replace producer epoch
and require a complete measured snapshot. Hold the consumer's old epoch unchanged
until the new full is accepted. Ordinary graceful stop has no restart.

The test parent has a 30-second bound, at most two child launches, 1,000 ms initial
restart delay and no circuit reset. Each acquisition has a 2-second native deadline;
independent producer expiry stays 3,000 ms. Reserve 250 ms after announcing a child
for an external held-PID observer, and 500 ms after demand release for independent
confirmation that the child's route-netlink socket closed. Neither is a product SLA.
Do not mutate interfaces, namespaces, policy installation, VMs or desktop content.

## Fixed acceptance before implementation

| Case | Required observation |
| --- | --- |
| `PUBLICATION-VALUES` | Keys/lifetimes map exactly; uint64 max remains exact; 30/60 bytes over 10 ns gives 3e9/6e9 byte/second; first/reset/missing rates are pending, valid zero succeeds. |
| `PUBLICATION-FAILURE` | Failure retains exact values and original measurement/UTC times, changes attempted time and failed/stale status; successful recovery uses the full elapsed interval. |
| `PUBLICATION-BOUNDARY` | Actual codec and DataView accept the document, exact replay is duplicate, removal/replacement remains distinct, denied policy erases it, and an insufficient complete-document byte limit rejects the whole candidate. |
| `NATIVE-COLLECTOR.LIVE` | Two real subscribed acquisitions, imported counters within independent sysfs brackets, derived rates agree with independently computed deltas/intervals, qualified measurement age < TTL, graceful child exit. |
| `NATIVE-COLLECTOR.FAILURE` | One injected source-error result between real reads produces retained values/timestamps; next real success has the correct longer rate interval. This is not induced kernel failure. |
| `NATIVE-COLLECTOR.REPLAY` | Duplicate publication imports as duplicate with identical body and measurement time, followed by a newer real sample. |
| `NATIVE-COLLECTOR.HANG` | Child hangs after a real full; health expires in [3000,4000] ms from last heartbeat; consumer retains old values/times; external held PID proves exit before replacement; new epoch full then succeeds. |
| `NATIVE-COLLECTOR.CRASH` | After importing the first real full, the parent sends existing data heartbeat sequence 0; this scenario sends no earlier data heartbeat. Receipt triggers child exit 73 without graceful teardown. Consumer retains the exact old state; held native exit proof admits a replacement only after at least 1,000 ms backoff; no forced stop; a new epoch full succeeds. This is an injected process exit, not a native acquisition fault. |
| `NATIVE-COLLECTOR.UNSUBSCRIBE` | Unsubscribe/heartbeat barrier retires demand; external procfs inspection observes no owned route-netlink socket; no later data is imported; graceful exit. |
| `NATIVE-COLLECTOR.REVOKE` | Typed policy change discards pending source/data and emits policy gap; consumer revocation erases payload; external inspection observes watch release; no later data is imported. |
| `NATIVE-COLLECTOR.PARENT-LOSS` | After a real full, stop only the owned parent; the externally held child identity exits under native parent-death protection. |

Before and after each native scenario, independently read full sysfs index/type/
counter tables. Match every imported entity using its ephemeral index and check
fixed counter brackets. Native topology changes make the case fail/inconclusive,
not permission to revise its oracle. Native output may contain operational values
only in the owned pipe/private ignored failure record. Commit aggregate outcomes,
counts, held process identity and timing evidence; never raw counters or interface
metadata. Preserve failures and exact source/package/artifact identities.

Use ordinary configure/build/test commands on all three profiles, modern Linux
native cases, historical import audits, relocated smoke packages and spec/tooling
checks. Product service composition, renderer recovery, complete network fields,
general demand planning, native fault induction and the other platform tracks
remain required by the campaign; this package does not redefine their completion.
