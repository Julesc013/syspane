---
type: "SysPane Work Package Boundary"
title: "W-25 measured telemetry and consumer freshness"
description: "Version measurement time and bind received values to a qualified consumer clock without refreshing replayed data."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:00:00+11:00"}
sp_id: "SP-W25-MEASURED-TIME"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-MEASUREMENT-CLOCK", "SP-W25-SUBSCRIPTIONS", "SP-W25-STATE-IMPORT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 measured telemetry and consumer freshness

Extend the existing codecs, session owner, model and data view. Keep 0.1 documents,
fixtures and inventory semantics unchanged. This package admits measured synthetic
native exchanges and the reusable receive boundary; actual collectors and their
metric/source acquisition contracts remain the next work.

## Exact documents and admission

Add experimental observation, snapshot and telemetry **0.2.0** schemas. A 0.2
snapshot contains only 0.2 observations. A 0.2 observation adds mandatory
`measured_at`, either null or exactly `{clock_id, nanoseconds}`. `clock_id` uses the
existing bounded ID grammar; `nanoseconds` uses canonical unsigned decimal string
encoding with the uint64 ceiling. It identifies the retained value's measurement,
not the latest failed attempt. Null means no comparable measurement was supplied.
It cannot accompany a null value. UTC remains metadata and never determines age.

All four 0.2 telemetry bodies add mandatory `clock_id`; other body fields retain
their existing meaning and limits. Non-null observation measurement domains must
equal that body domain and the locally admitted binding. Envelope, snapshot and
observation producer epochs must match. No consumer-local provenance is serialized.

The local source composition explicitly selects one exact triple and clock domain;
there is no implicit version upgrade or downgrade. 0.2 additionally requires the
negotiated `telemetry.measured-time` feature alongside `telemetry.snapshot`. Missing
any exact document/feature denies the measured subscription. A 0.1-only source
advertises no measured-time feature. The same role, policy, queue, lease, callback
ticket and record reservations apply to both versions. Naming a domain in a message
does not establish native clock compatibility.

## Consumer clock scope and state

Extend the native reading with a bounded **local scope ID**, never put on the wire.
Within this in-memory process it identifies Windows' current process clock lifetime
or Linux's current process plus retained namespace device/inode. Reconnecting in
the same qualified local scope preserves it. Process/namespace replacement changes
it. This is not a portable boot identifier, proof of arbitrary peer code, or a
persisted namespace identity. Store no measurement mapping across application
restart, checkpoint migration or reboot. The native stream's peer/namespace checks
remain required before mapping a remote count into this scope.

The trusted session supplies exact version, clock ID and local scope in the consumer
binding. A measured receive additionally supplies a current local `Tick` carrying
that epoch/domain/scope and nanosecond count. Validate token and policy revision
before observing this clock or parsing the payload. 0.1 receives accept no supplied
measurement clock. 0.2 requires one, including for partial/gap documents.

The data owner tracks a nondecreasing local measurement clock. Wrong/missing
epoch/domain/scope or regression latches a measurement-clock fault for that owner,
disconnects its current lease and preserves the last coherent payload as retained.
An invalid old callback cannot poison a successor. Policy replacement removes
payload independently of clock validity and does not reset a latched clock fault.
Recover from a local clock fault by constructing a fresh owner with newly admitted
clock provenance; a remote epoch change does not repair a broken local clock.

Reject a remote measurement later than the current qualified local count, without
replacing state or changing that count into receipt time. Remote invalidity closes
the attachment, but does not latch a healthy local clock as failed. Successful
receives map measurement epoch/domain/count into the consumer's local scope; the
original document and replay bytes remain intact. No conversion through floating
point, UTC, offset estimation or arrival time is permitted for these shared-domain
profiles.

Within the same producer epoch, a newer accepted state cannot move a previously
measured entity/source/field backwards in the same clock domain/scope. Exact older
record replay remains duplicate and cannot roll the current model back. Retained
values preserve their original measurement; unsuccessful acquisition is stale.
Same-epoch reconnect preserves replay and tombstone history and requires the same
document version/domain/local scope as the retained model. Incompatible reattach
is rejected before replacing the attachment. A new producer epoch may start a new
model after its first valid complete state; old state remains visibly retained
while waiting. Mixed versions cannot silently clear history.

## Projection, age and bounds

Keep ordinary projection for inventory and explicitly retained presentation. Add
a measured projection that first checks a qualified current local tick, then
borrows the snapshot/lease with that checked tick. Clock failure supplies no
measured projection; ordinary retained presentation can still expose allowed data.
Consumers combine lease presentation with `freshness_at`: disconnected/retained
data cannot be presented as live merely because its measurement age is small.

For a successful, present value reported current, finite TTL gives current only
when epoch, domain and local scope match, `now >= measured`, and `now-measured < TTL`.
At exact expiry or TTL zero it is stale. Missing/mismatched clocks cannot claim
finite-TTL freshness. No-TTL inventory retains its existing reported semantics.
Heartbeats, duplicate records and full confirmation never replace a measurement
time. Positive rate intervals require matching epoch/domain/scope and strictly
increasing counts; equality or regression has no interval.

Account both added clock strings under existing model candidate/retention bounds;
IDs retain the 256-byte ceiling. A per-field measurement high-water mark survives
temporary absence or a null measurement; at most the observation ceiling of keys
is retained, with key storage charged to the retained-byte limit. Frame, JSON depth/node, graph, queue and replay
ceilings are unchanged. There are no additional timers, threads or unbounded logs
in the shared components. The native probe still uses bounded owned processes.

## Fixed acceptance before implementation

| Family | Fixed stimulus | Required observable result |
| --- | --- | --- |
| `MEASURED-CODEC` | Exact 0.2 triple/feature; missing clock, wrong version/domain, malformed/overflow tick, null value with tick; encode/decode | Valid bodies preserve exact replay bytes; each invalid variant rejects; 0.1 fixtures still pass |
| `MEASURED-AGE` | Measurement 100, local times 100/109/110, TTL 10; TTL zero; null measurement; mismatched domain/scope/epoch; max uint64 | Current/current/stale; zero TTL stale; missing/mismatch stale; checked integer subtraction and matching positive intervals only |
| `MEASURED-REPLAY` | Accept R1 at measurement 100, replay it at 110, confirm with R2, then newer state measured 90 | No refreshed time; still stale at 110; confirming full preserves 100; backwards measurement rejected without replacement |
| `MEASURED-LIFETIME` | Same-epoch reconnect, incompatible scope/version, new epoch, old callback with bad clock, actual local regression, policy replacement | History survives compatible reconnect; incompatible reattach rejected; new epoch needs full; obsolete callback harmless; regression latches; policy erases payload |
| `MEASURED-SESSION` | 0.2 source/hello/subscribe/offer; missing feature or document; wrong subscribe domain; 0.1 peer | Exact admission and body versions; required mismatch fails without data; no silent fallback |
| `NATIVE-MEASURED.FRESH` | Stamp synthetic generation 1 in qualified native domain; deliver without artificial delay; TTL 1 s | Measurement retained exactly; native observed age is below TTL and current; independent producer lease remains separate |
| `NATIVE-MEASURED.DELAYED` | Stamp, delay 200 ms before delivery, TTL 100 ms | Received value is stale immediately despite recent receipt; native measured age is at least TTL |
| `NATIVE-MEASURED.FUTURE` | Send measurement 60 s ahead of native clock | Consumer rejects, imports no payload, and closes its attachment |

These native timing bounds are laboratory assertions, not performance guarantees.
The existing fixed inventory and clock cases remain unchanged. Preserve original
failure evidence; do not add tolerances to make a failing freshness oracle pass.
Run full ordinary profile suites, source/artifact-bound recorders, schema/fixture
checks and local model smoke packages with the current workspace preflight.

Real suspend/resume and namespace mismatch/change/denial remain unexecuted native
qualification. Native read/query/range/regression fault injection also remains
separate from portable injected-clock cases. API units are not physical accuracy.
No privileged action, power-state change, protected policy deployment, existing
guest mutation or public release is admitted. W-25 and the campaign stay open.
