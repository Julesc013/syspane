---
type: "SysPane Work Package Boundary"
title: "Linux processor telemetry in the existing native inspector"
description: "Close descriptor, publication, demand continuity and policy boundaries before connecting native CPU acquisition."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T05:15:00+00:00"}
sp_id: "SP-W14-PROCESSOR-PUBLICATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W14-LINUX-PROCESSOR", "SP-STATE", "SP-RESOURCES", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Linux processor telemetry in the existing native inspector

Continue W-14 from 2ccb456c. Use the existing native controller, authenticated
stream, demand/session owners, guardian and inspector delivery path. No second
runtime, controller scheduler or source checkout is admitted. Existing producer
and document identities remain; additional CPU source/entities are negotiated.

## Descriptors, identity and observable values

Register linux.cpu.execution_percent (percent), linux.cpu.interval_busy_ticks
(USER_HZ tick) and linux.cpu.interval_total_ticks (USER_HZ tick). Their exact
definition remains linux:execution-ticks-v1 from the linked acquisition package.
Busy excludes idle, iowait and steal; guest subcategories are not added twice.
Publish all three for every online logical CPU, the one Linux online scheduling
domain and the aggregate. Percentage is 100*busy/total with presentation rounding
only. Exact integer deltas remain decimal uint64 observations with the actual
start-to-start sample_interval_ns. Do not substitute elapsed wall time for total
accounting ticks, average per-CPU percentages or invent physical topology.

CPU source scope is the kernel-visible proc/sysfs online inventory, not process
affinity or cgroup/quota entitlement. Descriptors disclose scope, denominator,
gap/reset rules, one-second default cadence, three-second freshness, operational
sensitivity and potentially blocking cost. Entity identity metadata retains USER_HZ,
reported kernel index/package/core/peers and definition; defaults remain reported
values. Native calls cannot claim a preemptible deadline.

Wire logical IDs are monotonically allocated source lifetimes, separate from raw
linux:cpu:N indices. Removing and reintroducing an index allocates a fresh ID so
model retirement cannot revive old selectors. Aggregate and online domain IDs
remain stable. Admit at most 8190 logical lifetimes per epoch, plus two summary
entities, subject to existing combined entity/observation/frame limits. Capacity
fails atomically without truncating processors or weakening the 1 MiB frame bound.
Further segmentation/large-target qualification remains required where complete
inventory cannot fit; such a target is not qualified by a smaller fixture.

First/reset/topology/gap/zero-interval/no-progress values are null and pending,
with an explicit error/reason, never successful zero. Failed acquisition retains
previous ratios only as stale, preserving observed_at/measured_at/interval while
attempted_at advances. Denied is distinct. Unsupported has null values and
not_applicable freshness, including after prior success. Before any sample, only
summary entities with null unknown/pending values exist. CPU policy denial exposes
disabled/null summary state and performs no CPU read; it cannot expose old values.

## Negotiation, ownership and demand

Add telemetry.processor as an optional trusted source capability requiring 0.2.0
snapshot/observation and measured-time negotiation. Existing peers without it
retain network-only traffic and behavior. The production frontend requests it
when a validated scene binds one of the three CPU fields. Selecting a CPU scene
can operate when network collection is denied; each source's own capability is
checked independently. Relevant capabilities are collection.processor,
collection.network and existing telemetry/disclosure roles. Peers never select
worker callables or authorize themselves by naming a field.

Use DemandSessions with its existing cadence, lease, fair scheduling and forced
worker limits. CPU has a one-second minimum, sampling.resources_ms policy cadence,
2500-ms job timeout and a two-second reader deadline. A joined worker owns one
acquisition. Heartbeat/policy/I/O remain on the controller thread. The guardian
retains termination proof for uncooperative calls. Cancel both source workers on
unsubscribe, disconnect, lease expiry, shutdown and policy change; the existing
two-second controller stop and bounded external reap remain unchanged.

CPU state continuity is the stable admitted plan revision, not the ever-changing
job ticket. Complete each scheduler ticket exactly once; commit only its current
plan/policy result. Repeated jobs in one plan yield intervals. Replacement plans,
gaps and reported topology changes rebase. No cancelled/obsolete completion may
publish. Check current protected policy before dispatch, result admission and
queue/write. Source failure does not prevent independently admitted network work.

Cache each source's complete document with its actual observation/attempt times.
Every outgoing state merges current reported documents under one producer epoch
and publication generation. A CPU completion cannot rewrite network measurement
or attempt timestamps, remove interfaces or resurrect retired CPU IDs. Combined
size/count overflow fails closed; it never sends a partial healthy snapshot.

## Fixed acceptance and native execution

Portable cases cover literal 120/160=75% aggregate, exact denominator fields,
first/pending/zero/full execution, retained failure and gap recovery, denied and
unsupported, index removal/reintroduction, capacity rollback, immutable retained
documents, merged measurement times, typed model import/replay and policy erasure,
feature negotiation dependencies and continuous demand jobs versus replacement.
Run on all three development profiles with existing processor/model/demand/session/
network/graph controls and expanded strict historical executable/import audits.

Native peers must exercise the actual controller/worker/stream: no CPU request
without negotiated demand; complete all visible CPUs; exact per-CPU/aggregate
denominators; current-policy denial/revocation; failure/gap/recovery; independent
network progression; unsubscribe and uncooperative worker termination. Preserve
independent proc/sysfs evidence and semantic-oracle rejection controls. Use the
installed native inspector with a CPU scene to verify observable values and gaps,
actual source stopping and erasure through the existing harness. Preserve all
failures and missing target qualification, including the unresolved GTK loss.

Publish a source-bound checkpoint and update routing/README/TODO/build commands.
This enables the admitted Linux CPU inspector path only. W-14, Windows/macOS CPU,
memory/GPU, persistent native desktop/lifecycle and all five full 0.1.0 editions
remain open. Generated evidence/machine data stay in owned ignored out/ roots;
shared build tools stay in source/build and the retired root remains absent.
