---
type: "SysPane Work Package Boundary"
title: "One serialized measurement owner across collector workers"
description: "Close the native clock facility ownership before sharing controller execution with Windows."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T09:00:00+00:00"}
sp_id: "SP-W14-MEASUREMENT-OWNER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W14-PROCESSOR-PUBLICATION", "SP-W24-WINDOWS-POLL", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# One serialized measurement owner across collector workers

Continue W-14 from af3aec67. Source inspection identifies network and processor
workers calling the same Stream::measurement_clock concurrently. That facility
mutates sticky fault, provenance and measurement highwater state and requires a
serialized owner. Existing native passes did not qualify concurrent access.
Close this ownership before the Windows controller port; keep the same clocks,
native peer provenance, epochs, measurement values, interval definitions and
publication/demand/policy/guardian owners. Do not add a clock domain or scheduler.

Introduce one shared serialized measurement owner per admitted controller client
connection. It owns one supplied native-to-model Tick callback, permits only one
callback invocation at a time, and returns the exact native result or exception.
Copying the worker callable shares that owner and lock rather than copying its
synchronization state. All controller and acquisition uses of that connection's
measurement facility pass through this owner. It performs no implicit retry,
fallback, clock repair, value cache, epoch rewrite or conversion of failure to a
successful timestamp. Empty callbacks fail construction. Callback exceptions
release ownership so later calls can observe the provider's own sticky failure.
The native provider continues to enforce clock/provenance and fault semantics.

The controller keeps the Stream and shared owner alive until all admitted workers
have joined or the owned process has terminated. A queued clock read belongs to
its acquisition worker; it does not move health/policy/I/O onto that worker or
make an unpreemptible native clock callable safe. Keep the existing two-second
controller stop, job timeout and independently proved guardian termination.
No controller clock lookup occurs in normal health servicing while workers run;
initial connection/hello clock reads occur before dispatch. Do not weaken native
peer identity or source-bound measurement provenance to avoid the ownership.

Portable acceptance synchronizes eight competing callers of the same actual owner
and requires exclusive callback entry, complete exact results and immutable domain
strings. A direct unguarded callback control must trigger the overlap oracle; it is
a diagnostic control, not a passing implementation. Check callback exceptions,
no implicit retry, absence of fabricated values, later lock release and an empty
callback. Run both cases on all three development profiles with existing 85
processor/publication/model/demand/network/graph controls and strict historical
artifact/import checks including the new executable. Native Linux controller,
CPU publication/installed inspector and network service/consumer/supervisor must
retain exact values, original timestamps, policy erasure, cancellation and real
uncooperative-worker/guardian exit. Thread contention controls do not qualify
low-end/physical/native Windows clock or complete desktop releases.

Record source/artifact/environment identities and preserve failures. Then continue
the common controller ownership and Windows platform/worker/guardian adaptation,
native UI/desktop integration, remaining providers and all five full editions.
Shared inputs remain in source/build; raw/machine/generated evidence remains in
owned ignored out/ roots and the retired root remains absent.
