---
type: "SysPane Work Package Boundary"
title: "W-25 native measurement-clock investigation"
description: "Test a shared native time domain across authenticated local processes before admitting measured telemetry."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T08:29:17+11:00"}
sp_id: "SP-W25-MEASUREMENT-CLOCK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-SUBSCRIPTIONS", "SP-W25-STATE-IMPORT", "SP-W24-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 native measurement-clock investigation

The question is whether the two current development adapters can obtain comparable
clock readings while retaining the existing native peer identity. The decision
criterion is an independently checked causal bracket across real processes and
rejection after the held peer exits. This is an investigation prerequisite to
measured telemetry; it does not enable a new document version or infer measurement
age from receipt time, UTC, heartbeat or process liveness.

## Interface and ownership

The serialized native `Stream` owner gains `measurement_clock()`. A successful
reading contains a fixed clock identifier, an unsigned 64-bit nanosecond count and
the API's representation unit in nanoseconds. The unit is not a claim of hardware
resolution, physical accuracy or scheduling precision. Returned values are local
diagnostic data, not a serializable proof of remote measurement provenance.

Use `windows.interrupt-precise` / `QueryInterruptTimePrecise` (100 ns units) on the
current Windows 10 profile and `linux.boottime` / `CLOCK_BOOTTIME` (1 ns representation)
on the current Linux profile. Do not use wall time or subtract unrelated steady-clock
origins. Existing transport/demand/producer-lease clocks keep their current contract.
Historical adapters remain disabled; no new API is imported into the XP-toolset
executables.

The same native process handle or pidfd that authenticated the stream must report
the peer alive immediately before and after the sample/provenance checks. Failure
rejects that reading as `clock.peer_exited`; a failed native process-state query
instead fails `clock.peer_unavailable`. No numeric value escapes. This proves
only the observed interval, never future liveness or trustworthy remote content.

Linux additionally opens the current thread's `/proc/thread-self/ns/time` and the
authenticated peer's `/proc/<pid>/ns/time`, compares their device/inode identities,
and retains the first successful namespace handle for the stream's clock lifetime.
Recheck both namespaces after sampling and against the retained handle on later
calls. A missing namespace/proc facility fails `clock.namespace_unavailable`;
mismatch/change fails `clock.namespace`. Namespace IDs from a message are not
authority. This profile trusts the native proc mount and the admitted, serialized
producer's clock call; arbitrary peer threads, forwarded timestamps, namespace
migration and hostile mount replacement are outside this experiment's qualification.

Reject negative/invalid native counts or nanosecond conversion overflow as
`clock.range`, native clock read failure as `clock.read`, and a decreasing reading
within one stream as `clock.regressed`. Equal readings are valid; they do not prove
a positive rate interval. Any clock/provenance failure latches this stream's
measurement facility unavailable; subsequent calls fail `clock.unavailable`.
Ordinary inventory IPC can still close normally. A new stream starts a new clock
lifetime; no cross-stream/boot identity or old value validity is inferred.

The adapter owns one optional last count and, on Linux, one retained namespace
descriptor. Temporary descriptors close on every path. Calls perform no waiting,
namespace changes, clock setting, policy modification or background work. File/OS
calls can incur ordinary kernel latency; this is not a real-time bound.

## Fixed acceptance and evidence

Extend the existing synthetic inventory probe, preserving its five existing cases
and the exact 0.1 wire contracts. Clock readings go to test logs, not into invented
telemetry fields. `tests/protocol/native_clock.py` independently asserts:

| Case | Stimulus | Required result |
| --- | --- | --- |
| `NATIVE-CLOCK.ROUNDTRIP` | Client samples before sending hello; server samples after receiving it and before welcome; client samples after welcome | Native PIDs match; all domains/units match the profile; `before <= middle <= after`; generation 1 is imported with no measured tick |
| `NATIVE-CLOCK.PEER-EXIT` | Repeat the bracket, then client sends shutdown and exits while server retains the stream and native handle | Within the bounded observer deadline, first rejection is `clock.peer_exited`, second is `clock.unavailable`; no sample is returned for either; server survives and demand is zero |

The probe's exit observer is bounded to 2 s with 10 ms poll spacing; that is a lab
timeout, not a production promise. Existing native harness process cleanup and owned
endpoint rules apply. The runner records immutable executable/input hashes, exact
process output, native identity, outcome and failures. Assertions are fixed before
execution; an unexpected clock bracket fails rather than receiving an added tolerance.

Configure/build/test using the ordinary development commands and workspace preflight.
The current native profile suites include `native.NATIVE-CLOCK`; the historical
profile retains its portable/import checks with the native adapter disabled. Run
the affected complete suites and record artifacts and original attempts. No new
distribution payload is introduced by this investigation.

Successful live-process tests admit this native source as a candidate for the next
versioned measured-time package. That package must still close exact negotiation,
producer epoch/domain binding, retained/replayed value age, TTL equality, future or
regressed samples, rate intervals, reconnect and policy replacement. It must supply
independent expected outputs before connecting a real collector. Do not make a
freshness claim by adding a clock label to the current 0.1 observation.

## Evidence limits and decision authority

API selection, bounded probe implementation and reversible test engineering are
delegated within the campaign. Public release, privilege and changes to product
acceptance remain outside this package. Native suspend/resume, real namespace
mismatch/change, namespace/proc denial and native overflow/regression are not
executed by these two cases. Report those gaps separately; API documentation is not
execution evidence. No guest/host suspend or privileged namespace action is admitted.

Primary API references: [precise Windows interrupt time](https://learn.microsoft.com/en-us/windows/win32/api/realtimeapiset/nf-realtimeapiset-queryinterrupttimeprecise),
[Windows interrupt-time semantics](https://learn.microsoft.com/en-us/windows/win32/sysinfo/interrupt-time),
[Linux clocks](https://man7.org/linux/man-pages/man2/clock_gettime.2.html) and
[time namespaces](https://man7.org/linux/man-pages/man7/time_namespaces.7.html).
Linux explicitly counts suspend in BOOTTIME; Windows distinguishes biased interrupt
time from working-state-only unbiased time. End-to-end suspend freshness remains a
required later experiment, not a qualification inferred from those descriptions.
