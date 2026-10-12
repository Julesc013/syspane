---
type: "SysPane Handoff"
title: "Shared processor interval state checkpoint"
description: "Exact complete-processor denominators and failure semantics before native acquisition and resource publication."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T04:28:16.837378+00:00"}
sp_id: "SP-PROCESSOR-STATE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W14-PROCESSOR-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared processor interval state checkpoint

The shared processor state begins W-14 with exact
complete-processor counter intervals, explicit pending/gap/reset/hotplug reasons,
weighted aggregate/domain denominators, checked overflow and immutable samples.
Eleven fixed processor cases and 28 model/network/graph controls pass on each of
the Linux, Windows GCC and historical-toolset development profiles. Preserve the
initial compiler and used-symbol import failures. The new historical executable
passes the strict pinned-input/import audit after two documented XP thread APIs
are declared; this is not XP guest or native metric qualification. No native CPU
acquisition, descriptor publication, memory/GPU or UI activation is inferred.
Next implement native complete-processor/topology acquisition and OS-specific
metric descriptors through the existing demand/policy/publication owners, then
memory and other mandatory resource capabilities. Keep the mixed GTK accumulation
loss and all existing installed/desktop/lifecycle failures open. W-14 and all five
full release editions remain in progress. Shared tools stay in source/build;
generated/raw/machine data stay ignored under out/ and the retired root is absent.

The [checkpoint](checkpoints/processor-state.json) records exact source snapshots,
commands, build/test outcomes, libraries/executables, profile locks, component
graphs and pinned historical linker inputs. The [package](packages/w-14-processor-state.md)
closes the shared behavior and literal expectations before implementation. This
is part of W-14's full processor/memory/graphics scope, not a replacement release
goal or a claim that native providers already exist.

The source owner validates complete, bounded stable logical IDs and scheduling
domains. Demand replacement, topology changes, gaps and clock faults cannot
silently reuse an interval. Obsolete or dirty callbacks are rejected before their
bad clock can poison a successor. Only one construction thread accesses the
owner, while immutable samples may transfer to other readers. Acquisition and
native error remain separate from utilization availability; an old sample becomes
noncurrent after failure rather than being relabeled healthy or zero.

Compatible adjacent batches retain exact busy and total deltas and actual
start-to-start nanoseconds. Aggregate/domain utilization sums all admitted
processors, without averaging percentages or selecting one group. First, reset,
hotplug, demand/gap recovery, equal-time and no-progress projections have no
utilization value. Positive denominator with zero busy delta is valid zero.
Invalid idle deltas are not clamped. Checked integer addition rejects overflow
atomically, leaving the old immutable sample unchanged. Floating percentage is
derived only from a valid exact ratio, without presentation rounding.

| Development profile | Processor cases | Model/network/graph controls | Outcome |
| --- | --- | --- | --- |
| Linux x64 GCC 13 | 11 | 28 | pass |
| Windows x64 GCC 15 | 11 | 28 | pass |
| Windows x86 v141_xp on current host | 11 | 28 | pass |

The fixed 100-to-200-ns two-processor interval yields 120/160 busy/total = 75
percent; completion times 110/205 do not change its 100-ns interval. The group
case includes 128 processors across two 64-processor domains. Other fixed cases
cover shuffled IDs, 0/100 percent, resets, topology notice/reassignment, denied/
unsupported/cancelled/timed-out/malformed failures, duplicate/empty/oversized rows,
invalid idle delta, uint64 extremes, demand replacement/stop, sticky clock faults,
obsolete bad callbacks, wrong-thread rejection and retained immutable snapshots.
Synthetic group coverage is not large-server native verification.

The first Linux build fails strict misleading-indentation checks and a mixed-type
auto declaration in the test. Exact logs/source remain. Formatting and the fixture
declaration are corrected without weakening compiler flags or numeric oracles.
The first expanded historical audit catches ExitThread/GetExitCodeThread in the
new standard-thread test's static runtime closure. These symbols were absent from
the earlier used-symbol list. Microsoft documents Windows XP as their supported
client floor: [ExitThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-exitthread)
and [GetExitCodeThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getexitcodethread).
The amended list adds exactly those two symbols and the checker now includes the
new executable. Both import/rejection cases pass, with inspected PE32 data and
actual pinned static CRT/SDK linker inputs. XP/7 guest behavior, older NT and
Windows 9x compatibility remain unproven; no generic SDK-selection message is
substituted for the actual linker audit.

Next close native processor/topology acquisitions and OS-specific descriptor/
publication semantics, preserving all intended groups, physical/logical identity,
actual intervals and source errors. Connect them through existing policy and
demand owners before enabling UI use. Memory total/available/used, commit, swap/
pagefile/paging and separately admitted GPU capabilities remain mandatory work.
No native sensor or privileged probe is added. Keep the prior mixed GTK failure
and all installed/human/desktop/lifecycle/target qualification open. W-14 stays
in progress and every requested full release edition remains required.

Shared build inputs stay under source/build. Complete raw source/log/linker data
remain in owned ignored output roots; only the compact checkpoint is versioned.
The retired root remains absent. There is no public release or privilege grant.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
