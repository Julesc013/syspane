---
type: "SysPane Work Package"
title: "W-25 independent recovery and producer leases"
description: "Close bounded recovery state before connecting native processes and diagnostic entry."
tags: ["delivery", "architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:27:59+11:00"}
sp_id: "SP-W25-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-RECOVERY", "SP-TRANSPORT", "SP-COMPOSITION"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05", "SRC-AUDIT-2026-10-04"]
---

# W-25 independent recovery and producer leases

Prerequisites are W-01 and the initial W-24 native adapter gate recorded in the
[native handoff](../native-transport-handoff.md). The existing user campaign grant
admits implementation. Own `source/diagnostics/`, recovery composition roots in
`source/application/`, required platform adapters and `tests/fault/`. Ordinary
reversible choices remain delegated; no privilege, shell termination, unrelated
process termination, capture of private desktop content or release is admitted.

## Scope and gates

W-25 must deliver independent producer expiry, rendering-progress supervision,
bounded isolated-child recovery and a diagnostic entry that starts without the
controller, optional content/history/providers, renderer or GPU. The diagnostic
composition retains mandatory policy and has a conservative native inspector.
Native keyboard/exit recovery must remain usable when the editor stalls.

The portable state boundary below is ready to implement using the existing
Windows/Linux development profiles and C++17. It is a required component of W-25,
not the complete implementation gate. Native process composition, diagnostic
startup, policy integration and independent visible recovery remain mandatory.
Close their message/launch/handle contracts before enabling them. In particular,
this component does not enable W-24's currently disabled snapshot/delta messages
or advertise a new role/feature based only on typed unit-test fixtures.

## Portable ownership and time

`syspane_recovery` has no JSON, model, GUI, provider or native handle dependency.
One owner serializes each object's calls on an independent health/event loop.
Guard objects are neither copied nor moved; their identity stays with that owner.
Milliseconds come from that owner's monotonic clock, never a producer timestamp.
Every operation advances expiry before handling its input. Equality with a deadline
is expired. Compute elapsed differences without adding potentially overflowing
deadlines. A clock regression latches a fault; only construction in a new clock
domain recovers it. Removal of retained metadata remains allowed after clock fault;
it grants no recovery or disclosure. Neither wall-clock changes nor remote time renew anything.

The owner must tick at least every 100 ms while runnable; scheduling gaps and suspend
are reported by native evidence, not hidden by fabricated ticks. Actual elapsed
monotonic time after a gap is used. An OS clock that excludes suspend needs a
separate resume invalidation before a native profile may claim sleep recovery.
These algorithms establish decisions at observed times, not hard-real-time display
or kernel guarantees. Views are snapshots of the last observed time; they do not
sample a clock themselves. A caller must advance time before using a view.

## Producer lease

One lease owns one authenticated connection attachment and at most two bounded
producer/epoch identities: current attachment and last accepted update. IDs follow
the existing ASCII opaque-ID syntax with 256-byte ceiling. Attach grants a 3,000 ms
initial lease, allocates a strictly increasing local uint64 token and requires a
full snapshot. Reattachment always requires a snapshot, including the same epoch;
old callbacks carry the old token and cannot mutate or fault the new attachment.
Tokens are lifetime guards, never authentication or authorization. Token exhaustion
fails closed rather than wrapping. The native composition authenticates before attach.

An increasing heartbeat sequence renews only the 3,000 ms producer lease. The first
sequence may be zero. Exact duplicates do not renew it; sequence regression closes
the attachment. Snapshot/delta traffic alone does not extend the lease. A heartbeat
arriving at or after expiry cannot resurrect that connection: reconnect, authenticate
and resynchronize. Disconnect expires immediately, even when the deadline is later.

The model/data owner validates an entire publication before notifying this guard.
An accepted snapshot notification supplies current producer/epoch and generation;
a mismatched identity closes the attachment. A snapshot cannot regress an already
accepted generation in that attachment. Same-generation replay while synchronized
is duplicate and leaves last-accepted time unchanged. A full snapshot after a gap
may re-establish the same generation. A new attachment/epoch has no inherited
generation floor and must still receive a full snapshot before any delta.

A delta notification supplies exact current base and a strictly greater next
generation. Before a snapshot, or on a base/order mismatch, request a full snapshot
and retain the previous accepted metadata. No invalid notification replaces it.
A gap marks snapshot-required without extending the lease. New heartbeats cannot
turn that retained generation into synchronized data.

Views distinguish lease-alive, snapshot-required and presentation: waiting (no
accepted data, attached), active (attached and synchronized), retained (previous
accepted data but unsynchronized/closed), empty (no accepted data, closed).
Retained metadata includes its own producer, epoch, generation and local acceptance
time; attaching a new producer never relabels old data. Metric observation times,
freshness and values remain owned by the model and are never rewritten by a lease.
An active producer may have stale metrics. Retained data must be visibly identified
as retained by the future surface; this helper alone proves no pixels.

Policy remains authoritative over all retained data. A `forget` operation discards
accepted metadata and requires a new filtered snapshot without renewing the lease.
Its caller also drops prohibited payloads/caches before presentation. The helper
stores no payload and cannot grant disclosure. Clock fault, expired producer and
policy-unavailable state must never be interpreted as fresh/authorized telemetry.

## Render progress

One render watchdog owns at most one outstanding, strictly increasing uint64
challenge generation. Issue starts a 3,000 ms deadline. Another issue while pending
is busy and cannot move that deadline. Only completion of that exact challenge
before expiry clears it; old, future or duplicate completions do not count.
After completion a new larger challenge may be issued. IPC heartbeat processing
does not call completion. At timeout, stall is latched for that surface lifetime;
late acknowledgement cannot clear it. Replacement constructs a new watchdog.

Completion is an instrumented renderer fact, not independently observed visibility.
W-02 must still observe changing pixels and stale state externally. A native owner
must establish that completion comes from the render path, not the health loop.
Issue challenges at least once per second while a presentation is expected; omit
them only when that presentation is explicitly suspended and not claimed visible.

## Restart budget and process lifetime

A restart gate owns one child slot and three restart timestamps, never a growing
worker pool. Initial launch is allowed once without counting as a restart. A failed
launch counts as a failure of that slot. Failure records a bounded enum reason and
whether the native adapter has confirmed that the exact owned child is stopped.
If stop is unconfirmed, quarantine the slot: no replacement or reset is allowed.
A timeout or request to cancel/terminate is not stop confirmation. The adapter must
hold the child identity/handle and observe termination before confirming it.

After confirmed failure, delays are 1,000, 2,000, then 4,000 ms for consecutive
failures, plus a per-instance jitter in [0,250] ms selected by the composition.
The fixed jitter makes test outcomes reproducible without removing production
jitter. A running interval of at least 60,000 ms resets the consecutive-failure
backoff before processing the next failure. Every admitted replacement records
its timestamp. At most three replacements are allowed in a rolling 60,000 ms
window; a timestamp ages out at exactly 60,000 ms.

If all three reservations remain at a confirmed failure or at attempted restart,
open the circuit. An open circuit never automatically closes after time passes.
Explicit diagnostic reset is allowed only after the child is confirmed absent;
it clears the retry window/backoff and permits one initial launch. Reset does not
erase the last failure record or repair a monotonic-clock fault. Graceful stop
closes the slot without a failure/restart; deliberate relaunch requires reset.
Duplicate failure, stop or start callbacks cannot consume extra reservations.

## Fixed portable acceptance cases

Each ID binds to `tests/fault/recovery_tests.cpp` and the CTest name `recovery.<ID>`.
Tests use literal expected outcomes, independent of the implementation's constants.

| ID | Required observable result |
|---|---|
| LEASE-01 | Attach at 100; snapshot at 101; heartbeat 7 at 1,100; duplicate at 3,000; active through 4,099, retained at 4,100; late heartbeat cannot revive. |
| LEASE-02 | Disconnect immediately retains generation/identity; reattach new epoch needs snapshot; old-token callbacks cannot poison the new clock or state. |
| LEASE-03 | Gap/base mismatch retains metadata; delta is rejected until full snapshot; generation regression and wrong epoch never replace accepted data. |
| LEASE-04 | Heartbeats keep producer alive while an actual model observation becomes stale; forget removes metadata and requires resync. |
| LEASE-05 | Bad IDs, sequence regression, clock regression and arithmetic near uint64 maximum fail safely; no allocation proportional to reconnect count. |
| RENDER-01 | Challenge at 100 cannot be postponed by busy issue or unrelated/old completion; completion at 3,100 is late and stall latches. |
| RENDER-02 | Exact completion permits next challenge; repeated/old generations do not; producer heartbeat remains alive while rendering stalls. |
| RETRY-01 | Initial failure; replacements at 1,000, 3,000 and 7,000; fourth failure opens circuit; later elapsed time cannot close it; explicit reset preserves last error. |
| RETRY-02 | Unconfirmed stop quarantines; no start/reset while occupied; confirmed exit permits bounded recovery; duplicates do not multiply attempts. |
| RETRY-03 | Exact 60-second expiry, successful-run backoff reset, jitter boundary and maximum-time arithmetic obey the declared limits. |
| RECOVERY-CLOCK | Clock regression latches each guard and prevents later mutation/restart; stale attachment tokens alone cannot trigger it. |

## Execution and evidence

From the repository root, configure/build/test the checked-in development presets
using the developer commands in `docs/developers/build.md`.
Expected new outputs are `libsyspane_recovery.a`, `syspane_recovery_tests` (plus
`.exe` on Windows), component graph and CTest case results. A bad/unknown case exits
nonzero. Keep source/artifact/profile digests, exact commands, logs and failures in
the existing `build-support/evidence/` ownership. Profile qualification stays at the
observed development environment; no older target floor is inferred.

W-25 remains in progress until native producer freeze/crash and renderer stall
tests prove independent progress, owned-process stop/restart and circuit behavior;
the independent diagnostic entry passes damaged optional input/current-policy
tests; and its native exit/visible recovery integration is executed in an admitted
desktop lab. Missing lab access blocks those claims without converting portable
tests into native qualification. The next handoff must retain each unmet gate.
