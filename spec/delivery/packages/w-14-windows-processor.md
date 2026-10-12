---
type: "SysPane Work Package Boundary"
title: "Native Windows processor groups, topology and PDH accounting"
description: "Bounded native x64 Windows acquisition with complete active group masks, explicit PDH semantics and independent raw evidence."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T06:30:00+00:00"}
sp_id: "SP-W14-WINDOWS-PROCESSOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RESOURCES", "SP-W14-PROCESSOR-STATE", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native Windows processor groups, topology and PDH accounting

Continue W-14 from ce997844. This package admits read-only native x64 acquisition
on the existing Windows development host and portable topology/accounting checks
on the three development profiles. It is not Windows 9x, XP, older NT, macOS,
native Windows UI/desktop or full release qualification. Those providers and all
five complete editions remain required. No API fallback may silently select one
group or replace per-CPU data with an aggregate counter.

## Acquisition and meaning

Use GetLogicalProcessorInformationEx for RelationGroup, RelationProcessorCore
and RelationProcessorPackage before and after acquisition. Validate complete
variable-sized x64 little-endian records before interpreting members. Enumerate
every set bit in each active group mask; group numbers are the GroupInfo array
indices. Never derive membership from process affinity, count alone or ordering
of unrelated records. Preserve reported core/package group masks, flags and
efficiency classes without inventing hardware IDs or architectural core labels.
Normalize relationship/mask ordering for equality. A differing complete topology
is interrupted with no partial result; equal brackets do not prove atomicity or
exclude hotplug ABA. Native topology is what the OS exposes, including virtualization.

For each active (group,processor-number), add the language-neutral local PDH
paths \Processor Information(group,number)\% User Time, % Privileged Time and
% Idle Time to one query. No wildcard, remote machine path or localized-name
assumption is used. Load pdh.dll only through its full System32 path with
LOAD_LIBRARY_SEARCH_SYSTEM32 and require the selected exports. Close the query
before releasing the module. Missing API/object/counter is unsupported, permission
failure is denied and missing active instance is interrupted. Never repair counters,
services, registry configuration or permissions as a side effect.

Require raw type PERF_100NSEC_TIMER (0x20510500) for all three components,
successful PDH API status and CStatus VALID_DATA or NEW_DATA. Preserve signed
FirstValue/SecondValue, TimeStamp, MultiCount and both statuses for each component.
Reject negative raw values, nonpositive SecondValue, FirstValue larger than
SecondValue and MultiCount other than one. All components in one CPU sample must
share the provider time base and timestamp; disagreement is interrupted. Unknown
type is unsupported, not a formula guessed from its name.

The definition windows:pdh-accounted-time-v1 uses cumulative FirstValue user,
non-idle privileged and idle accounting, in 100-ns units. Total is their checked
sum; busy interval is delta user + delta privileged, and percentage is 100 times
busy delta divided by total accounted delta. Retain all three components in fixed
order so a decrease cannot hide within a growing sum. Do not add interrupt/DPC
subcategories a second time. The SecondValue provider timestamp is retained as
raw metadata, not substituted as the accounted denominator or called uptime.
Actual acquisition start/completion ticks remain a separate monotonic domain;
record their start-to-start ns interval. Units do not claim 100-ns measurement
accuracy: observed accounting is quantized. This is an explicitly named fraction
of OS-accounted processor time, not PDH's wall-time % Processor Time, % Processor
Utility, frequency, load average or process/quota entitlement.

The first experiment uses PERF_100NSEC_TIMER_INV on % Processor Time. Its first
native interval passes, but a later interval reports two idle deltas 10,781,250
against provider time-base delta 10,700,031. The shared owner correctly rejects
the complete interval rather than clipping it. Preserve the original artifacts,
raw counter statuses, source archives and failure. The observed % Idle Time uses
the same system time base, not a precision timer, so it does not repair this
candidate. The final definition instead uses coherent raw user/privileged/idle
accounting and names the different denominator explicitly. This is an evidence-led
package revision, not a correction of the original failure into a pass.

Raw source IDs are windows:cpu:group:number; domains are windows:group:group.
Feed complete normalized counters into the existing ProcessorState and preserve
all first/reset/topology/gap/no-progress/clock/demand rules. Sum exact busy and
total deltas across every intended CPU for group/aggregate ratios, without averaging
percentages. A topology change notifies that owner before the successor commit.
Retain the complete native result and status separately. No observation publisher,
policy grant, worker scheduler or product UI activation is introduced here.

## Bounds, invalid input and authority

Admit 1..8192 active CPUs, or the caller's smaller row budget. Each group has
1..64 active and maximum processors, active<=maximum, with exact active mask
popcount and no bit beyond maximum. At most 8192 core and package records per
kind; at most 8192 group affinities per relationship. Affinities have nonzero masks,
unique known groups and no bit outside their maximum processor range. Preserve
inactive membership bits as reported metadata. Every active CPU belongs to exactly
one reported core and one package; active core membership cannot cross packages.
Missing, duplicated, overlapping or contradictory membership fails atomically.

Bound each topology input to 8 MiB, record count/size before indexing, and total
topology input to 24 MiB. Perform a size probe then at most three bounded native
allocation/read attempts per relationship while deadline/cancel permit. An exhausted
size race is interrupted. Malformed size, truncated arrays, trailing bytes, wrong
relationship kind or contradictory masks fail; no unvalidated pointer is dereferenced.
Check cancellation/deadline before and after each native call and before successful
return. Native PDH/kernel calls are not preemptible inside this helper; later native
worker/guardian integration remains required. Allocation failure is capacity.

The native collector is compiled only in windows-x64-gcc15. Do not use WOW64
affinity folding, add modern mandatory imports to the historical executable or
infer old-system support from portable tests. Pin the selected Windows/PDH header
fingerprints through a build check; record actual system DLL and host identities
with native evidence. The existing compiler lock's incomplete vendor-archive
reproduction remains disclosed. No privileged or public release authority is added.

## Fixed acceptance and evidence

Portable cases independently build x64 record bytes and verify sparse masks,
shuffled physical relationships, all 128 CPUs in two groups, malformed/oversized
records, count/popcount/range/coverage/overlap errors and topology interruption.
Accounting cases require literal busy/total 40/60 and 80/100 => aggregate 120/160
=75%, valid zero/full utilization, first/reset/gap/no-progress and invalid idle
delta, wrong counter type/status, native-error propagation and complete row coverage.

The Windows probe obtains two actual captures and commits them through the shared
owner with monotonic ticks. An independent Python runner calls topology and PDH
directly, brackets every native raw value, verifies the same complete masks and
relationships and derives exact per-CPU/group/aggregate integer intervals. Also
cross-check each component raw-counter formula through PdhCalculateCounterFromRawValue
without a 100-percent cap; the accounted fraction uses the separate exact sum. Preserve unavailable/invalid/pending outcomes honestly;
missing performance counters cannot become a pass or trigger system changes.
Actual reader calls verify cancellation and an expired deadline. Oracle controls
must reject a changed denominator and omitted CPU/group.

Run ordinary preflight/configure/build, Windows decoder/shared processor/model/
graph controls on all three profiles, strict historical PE/pinned-input audits
including the new portable executable, and the native Windows runner. Record exact
source/artifact/environment identities and preserve failures. Native success on
this one-group host is not a multi-group/large-server, physical hotplug, low-end,
legacy or release claim. Next add Windows descriptors/publication/demand/native
UI and remaining platform/resource providers. W-14 and all full editions stay open.
Shared inputs stay under source/build; generated/raw/machine data stay in owned
ignored out/ roots and the retired root remains absent.

Primary references: [processor topology](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getlogicalprocessorinformationex),
[group structure](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-group_relationship),
[language-neutral counters](https://learn.microsoft.com/en-us/windows/win32/api/pdh/nf-pdh-pdhaddenglishcounterw),
[raw status](https://learn.microsoft.com/en-us/windows/win32/perfctrs/checking-pdh-interface-return-values),
and [counter formulas](https://learn.microsoft.com/en-us/windows/win32/perfctrs/calculating-counter-values).

Accounting references: [user, privileged and idle modes](https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/troubleshoot-performance-problems-in-windows)
and [precision timer semantics](https://learn.microsoft.com/en-us/windows/win32/wmisdk/precision-timer-algorithm-counter-types).
