---
type: "SysPane Work Package Boundary"
title: "Shared processor interval ownership and denominators"
description: "Deterministic complete-processor counter reconciliation before native resource acquisition and publication."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T04:10:00+00:00"}
sp_id: "SP-W14-PROCESSOR-STATE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RESOURCES", "SP-STATE", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared processor interval ownership and denominators

Begin W-14 from 703963a3. This admitted shared implementation does not require a
desktop or privileged operation. The existing model/demand primitives supply its
prerequisites; W-07's full completion is not inferred. W-14 retains all processor,
memory and graphics requirements. Native acquisition, physical topology,
descriptors/publication, demand integration and real metric verification remain
required before a resource capability is enabled or a release is qualified.

## Inputs, state and authority

One serialized source owner receives complete processor counter batches under
explicit demand tickets and topology revision. Each row has a nonempty stable
logical-processor ID, scheduling-domain/group ID, cumulative total and idle ticks.
IDs and domains use the same bounded opaque identifier alphabet as other initial
source owners, at most 256 bytes. Sort by ID and reject duplicates; never infer
identity from enumeration order. Admit 1..8192 rows, or a declared smaller budget;
an excess is capacity, not truncation. Total ticks include idle, idle is no larger
than total, and all rows use the owner's fixed comparable counter definition.
Changing that definition requires a new source epoch/owner and descriptor.

Each attempt has acquisition-start/completion ticks in the fixed producer epoch,
clock ID and clock scope. Completion is at/after start, and the next accepted
attempt starts at/after the last accepted completion. A clock-domain/backward
fault is sticky until a new owner. Reject obsolete demand or dirty topology
callbacks before inspecting their clock or data, so they cannot poison a successor.
Native errors and unsuccessful acquisition are distinct from a successful zero.

The owner is confined to its construction thread; immutable successful samples
may be retained/transferred after retrieval. No observation publisher, worker,
native API, policy grant or new scheduler is introduced. A demand ticket grants
no policy authority. Repeated active tickets are idempotent, newer tickets replace
the old demand, zero stops it, and retired tickets cannot reactivate.

## Intervals and denominators

The first successful complete batch is pending. Adjacent compatible batches use
the actual start-to-start nanosecond interval, while completion timestamps remain
recorded. For each processor, busy delta equals total delta minus idle delta.
The exact utilization ratio retains busy/total deltas and interval. Percentage is
100 times that ratio without presentation rounding; valid zero requires positive
total delta and zero busy delta. A zero denominator is pending, never zero percent.

Aggregate and per-domain utilization sum exact busy deltas and exact total deltas
over all admitted processors; do not average percentages or silently select one
group. Checked uint64 addition prevents overflow. Preserve exact integers even
when floating presentation cannot distinguish adjacent very large values.

Any changed ID/domain set, explicit topology notice, demand replacement, prior
failed/malformed/capacity attempt, decreasing counter, or equal start timestamp
rebases the complete batch with no utilization values. Record its pending reason.
No interval may bridge an unavailable attempt. If any processor has no positive
counter interval, the complete utilization projection is pending. Idle delta larger
than total delta is invalid, not clamped. A malformed or overflowing candidate
does not replace the prior immutable sample, makes it noncurrent, and requires a
new basis on the next successful attempt. A retained old sample is not authority
to present current data.

Generation advances once per accepted complete sample. Successful generations
and counter metadata remain immutable. Failure does not advance generation or
replace the previous raw sample. Actual acquisition status/native error is retained
separately, and clock faults cannot be repaired by silently resetting the epoch.

## Fixed observable cases

The executable cases must cover first sample; shuffled complete IDs; weighted
aggregate/domain math; valid 0/100 percent; 128 processors across two groups;
counter decrease; hotplug and group reassignment; explicit topology notice and
dirty callback; nonadvancing/equal timestamp; gap/denied/unsupported acquisition;
malformed/duplicate/empty/oversized rows; invalid idle deltas; checked aggregate
overflow; obsolete bad-clock callback; clock domain/backward faults; demand stop
and replacement; wrong-thread rejection; and immutable retained samples.

The fixed two-processor interval is start 100 to 200 ns, not completion 110 to
205 ns. Processor A changes total/idle 100/60 to 160/80 (40/60 busy); B changes
200/50 to 300/70 (80/100 busy). Total utilization is 120/160 = 75 percent;
unweighted averaging is wrong. The 128-processor case includes every processor
and both 64-processor domains. Extreme values and failure/recovery cases retain
literal expected results independently of the implementation.

## Execution and completion

Add one shared source component and explicit dependency on syspane_model, with
portable executable cases in the three existing development profiles. Run ordinary
workspace preflight/configure/build and processor/model/network/graph controls.
Preserve source/artifact/environment identities and any failed compiler or case.
Three development executions are not XP guest, Windows 9x, large-server, physical
topology, Linux/macOS native acquisition or full resource qualification.

The component is ready only when its complete fixed cases execute and pass on the
declared profiles. Continue with native CPU/topology acquisition, metric descriptor/
publication and memory/GPU semantics; do not mark W-14 or any of the five complete
release editions done based on this shared state alone. Original contracts and
native authority boundaries remain. Generated outputs stay in owned ignored out/
roots, shared build inputs in source/build, and the retired root remains absent.
