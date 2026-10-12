---
type: "SysPane Handoff"
title: "Native Windows processor acquisition checkpoint"
description: "Complete native group topology, explicit accounted-time denominator and independently verified raw intervals."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T07:06:43.260935+00:00"}
sp_id: "SP-WINDOWS-PROCESSOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W14-WINDOWS-PROCESSOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native Windows processor acquisition checkpoint

The Windows processor checkpoint implements
complete active group/core/package topology and read-only native x64 PDH acquisition.
The explicit Windows definition uses busy user-plus-privileged time divided by total
user-plus-privileged-plus-idle accounting. The independent native runner verifies
all 12 CPUs on this one-group Windows 10 host, raw bounds, PDH component formulas,
GetSystemTimes bounds and exact per-CPU/group/aggregate intervals. Six new portable
cases plus 71 controls pass on each of three development profiles; both historical
artifact audits pass. Preserve the rejected inverse timer interval, compiler failure
and 8 GiB preflight stop. Native Windows publication/demand/UI and worker isolation,
remaining providers and all five full desktop/release editions remain open. Two-group
128-CPU synthetic coverage is not native large-server qualification. Keep the mixed
GTK accumulation loss and prior failures open. Shared tooling stays in source/build;
raw/machine/generated data stay ignored under out/ and the retired root is absent.

The [package](packages/w-14-windows-processor.md) defines the bounded acquisition
and accounting contract. The [checkpoint](checkpoints/windows-processor.json) binds
13 executions to complete verified source archives, workspace checks and hashed
logs. It records three native attempts, selected SDK headers, system PDH module and
actual executable identities, component graphs and strict historical linker/import
evidence. The current native probe matches the final native pass; later portable
regression additions do not compile into that probe. All raw records remain local
under ignored owned output roots rather than becoming repository build inputs.

The collector reads every active group mask and all reported core/package relations
before and after one PDH query. The portable decoder validates exact x64 variable
record sizes, processor membership, mask bounds and complete coverage. It normalizes
ordering without inventing physical IDs, then rejects differing topology brackets.
Equal brackets do not prove atomicity or exclude hotplug ABA. All 128 processors in
two synthetic 64-processor groups, including bit 63, are covered; an omitted group
fails. This host reports one group, six cores and one package, with twelve logical
processors. Those are native OS reports, not independently qualified hardware facts.

For each active CPU, the collector uses language-neutral local User Time,
Privileged Time and Idle Time counters. It verifies raw PERF_100NSEC_TIMER,
statuses and coherent provider timestamps, retains all three contributing values
and checks arithmetic. The DLL is loaded through its full System32 path; the
independent runner verifies the actual loaded module path and digest. Native errors,
unavailable counters, capacity, topology interruption, cancellation and timeout stay
distinct. No counter repair, permission changes or service configuration is attempted.
Native calls remain unpreemptible in this helper; product worker/guardian integration
is still required before Windows collection activation.

The definition windows:pdh-accounted-time-v1 computes the busy fraction of cumulative
OS-accounted user, non-idle privileged and idle time. It does not substitute a PDH
wall-time denominator, add interrupt/DPC subsets twice, average CPU percentages or
claim 100-ns measurement accuracy. The shared ProcessorState owns first/reset/gap/
topology/demand/clock semantics and exact weighted denominators. Raw contributing
component decreases cannot hide inside an increasing sum. Acquisition start-to-start
monotonic ns remain separate from the accounting unit and provider time base.

| Development execution | Coverage | Result |
| --- | --- | --- |
| Windows x64 GCC 15 | 6 Windows decoder cases + 71 processor/publication/model/demand/graph controls | pass |
| Linux x64 GCC 13 | same 77 portable controls | pass |
| Windows x86 v141_xp on current host | same 77 portable controls | pass |
| Windows 10 x64 native acquisition | 12 complete CPUs, topology, exact intervals and independent native oracle | pass |
| Historical PE/pinned-input/import audits | both strict cases, including the new portable executable | pass |

The native runner obtains its own topology/PDH brackets through Python ctypes,
derives expected exact intervals independently with integer arithmetic and Fraction,
and cross-checks each raw component formula with uncapped
PdhCalculateCounterFromRawValue. On this one-group host, GetSystemTimes independently
bounds summed accounted total and idle time. The latter is deliberately not a
multi-group fallback. Changed-denominator and missing-CPU controls fail the oracle;
the reader's actual cancellation and expired-deadline calls have distinct outcomes.
The fixed two-CPU portable interval remains 120/160 = 75 percent, with a measured
100-to-200-ns start interval; zero/full utilization and hidden decreases are covered.

The original inverse-timer % Processor Time candidate first passes a native interval,
then fails: two idle deltas of 10,781,250 exceed a provider time-base delta of
10,700,031. The shared owner rejects the complete interval without clipping it.
The observed Idle Time counter uses the same time base rather than a precision
timer. Preserve both original native records, source archives and executable hash.
The final accounting definition explicitly changes the denominator; it does not
turn the original failed candidate into a pass. A fixed regression preserves that
invalid inverse-timer interval. GCC 15 rejects temporaries in the initial regression
construction under the existing dangling-pointer warning; named const results/ticks
resolve the construction without changing flags, expected values or acceptance.

The initial 8 GiB build preflight stops before launch: checkout outputs 3,161,013,824
plus Linux outputs 5,170,219,925 and the unchanged 268,435,456-byte reservation exceed
that allocation. The recorded reversible 9 GiB development allocation keeps those
artifacts and standard reservations. Product resource and acceptance limits do not
change. Selected topology/PDH SDK headers are fingerprinted at configure; complete
vendor and transitive-header reproduction remains outside the existing compiler lock.

Next integrate Windows descriptors/publication, continuous demand and native worker
isolation through the existing policy/session/guardian owners and native UI. Continue
macOS and historical Windows providers, memory/commit/swap/paging and admitted GPU
capabilities, physical/large-server/low-end/hotplug qualification and the complete
desktop/lifecycle/packaging gates. Portable tests on a current host do not qualify
Windows 9x, older NT or XP guests. The unresolved mixed GTK accumulation failure
and every previous failure stay preserved. W-14 and all five complete release
editions remain in progress. No privilege, sensor grant or release authority is added.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
