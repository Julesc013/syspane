---
type: "SysPane Work Package Boundary"
title: "Windows processor observations through shared telemetry and model import"
description: "Explicit accounted-time metrics, complete group publication and nonreused lifetimes before native controller/UI activation."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T07:20:00+00:00"}
sp_id: "SP-W14-WINDOWS-PUBLICATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W14-WINDOWS-PROCESSOR", "SP-W14-PROCESSOR-PUBLICATION", "SP-STATE", "SP-RESOURCES", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Windows processor observations through shared telemetry and model import

Continue W-14 from bd737d46. Extend the existing processor publication component,
shared interval owner and measured telemetry/model import. Retain the Linux
metric identities, values, domain and native delivery behavior. This is the
Windows publication boundary required by the complete Windows desktop edition;
it does not qualify a standalone probe as that edition. Native Windows controller,
supervised demand/isolation, settings/editor/desktop/lifecycle and historical
providers remain required. No second scheduler, source tree or policy authority.

## Observable values and scope

Register windows.cpu.accounted_busy_percent (percent),
windows.cpu.interval_busy_100ns (100 ns) and windows.cpu.interval_total_100ns
(100 ns). The exact definition is windows:pdh-accounted-time-v1: busy interval
is delta user + delta non-idle privileged; total is delta user + delta privileged
+ delta idle. Do not substitute PDH wall-time, double-add DPC/interrupt subsets,
average percentages or claim 100-ns accuracy from the accounting unit. Publish
all three for every active logical CPU, every native processor group and the
aggregate, with exact decimal uint64 interval amounts and acquisition-start
sample_interval_ns. Sources describe the OS-visible active group inventory,
including virtualized reports, not process affinity or entitlement.

Use provider:windows-processor, native.windows.processor and scope
kernel:visible-active-processor-groups. Separate explicit Windows descriptor,
host-metric and validated-scene field-selection functions leave existing Linux
callers unchanged. Optional telemetry.processor retains its existing measured
0.2.0 negotiation and policy requirements; field names never grant collection.
Collection permission remains collection.processor. The declared cadence is
one second with three-second freshness and potentially blocking native cost;
no native worker or controller activation is implied by descriptor registration.

## Identity, failure and bounds

Keep processor:aggregate stable within the producer epoch. Group and logical
wire IDs are allocated lifetimes, separate from native group/processor numbers.
A group or CPU that disappears and returns receives a new ID. Clearing disabled
publication retires every group/CPU; regrant cannot revive their IDs. Allocate
groups first in normalized native order, then logical CPUs in normalized order.
One monotonically increasing issuance counter admits at most 8191 group/logical
lifetimes per epoch, plus the aggregate, and never resets on disable. Identity
allocation and retirement commit only after the complete bounded document succeeds.
Exhaustion or combined frame/count capacity fails atomically, never truncates or
revives retired IDs. Keep the existing 1 MiB transport ceiling and snapshot counts;
complete large targets needing segmentation remain unqualified until it exists.

Group identity preserves native group number, active/maximum processor counts and
active mask. Logical identity preserves native group/processor number, reported
core/package ordinal within normalized topology, flags, efficiency class and
complete reported core/package affinity masks as bounded decimal strings. These
ordinals/masks are reported metadata, not persistent hardware IDs. Metadata strings
must fit the existing model's limits, or publication fails without partial output.
All entities identify the accounted definition and accounting unit. A topology
capture must be valid, complete and counter-identical to the committed sample;
a wrong definition/epoch/clock/scope, missing capture, changed raw values or invalid
topology fails before consuming identities. Recovery uses the last successful
capture matching the retained sample, not an unsuccessful successor capture.

Before a successful sample, publish only the aggregate with null unknown/pending
values. First/topology/demand/reset/gap/zero-time/no-progress is null pending with
the shared explicit reason, never successful zero. Genuine zero/full utilization
requires a positive valid interval. Failed acquisition retains previous values
only as stale and preserves observed_at, measured_at and interval; attempted_at
advances. Denied remains distinct. Unsupported has null values and not_applicable
freshness. Disabled publication exposes only null aggregate state, no old group/CPU
inventory, raw masks, measurements or ratios. Use the existing shared observation
encoder for both OS definitions and existing host_document for complete network
merging; a CPU update cannot rewrite network observation/attempt timestamps.

## Fixed acceptance and native evidence

Portable cases independently construct complete Windows capture data. Require
two CPUs in two groups with busy/total 40/60 and 80/100 => 120/160 = 75%, plus
per-group/per-CPU exact intervals. Cover null first/no-progress/reset/gap, valid
zero/full, retained errors/denial/unsupported, policy disable/regrant, CPU/group
remove/reintroduce, capacity rollback and immutable retained documents. Import
the real measured envelopes through DataView; verify duplicate/replay handling,
retirement, current-policy erasure and independent network merge metadata.
The existing DataView requires independent inspector and accessibility disclosure
for operational projection; fixtures must grant both explicitly and prove denied
attachment when accessibility disclosure is absent. Do not weaken that gate.
The existing DemandOwner must admit the explicit Windows fields under processor
permission, preserve plan continuity across jobs and reject denied dispatch.
No new native scheduling implementation is qualified by that portable case.

Extend the existing native Windows probe to publish its actual two captures and
import both snapshots through the measured model path. The independent ctypes
runner derives raw expected intervals and checks every published CPU/group/
aggregate field, native metadata, relationship, source, status, unit and original
measurement. It must reject changed publication arithmetic and omitted group/CPU
in addition to the existing raw-denominator controls. Actual model replay and
policy erasure are part of the probe. Preserve original inverse-timer failures and
existing evidence; missing counters remain unqualified rather than repaired.

Run the new portable cases on all three development profiles with the existing
77 processor/publication/model/demand/network/graph controls, strict historical
PE/pinned-input/import audits including the new executable, and expanded native
Windows runner. Since shared observation emission changes, rerun Linux native
controller/CPU publication and installed CPU inspector plus network service/
consumer/supervisor controls. Freeze source/archive/artifact/environment identities
and preserve failures before fixing them. Old NT/9x/macOS, native multi-group,
physical/low-end/hotplug and full release qualification remain open.

Next connect Windows publication to native controller/demand/guardian and native
settings/inspector/desktop owners; continue remaining providers and all five full
editions. Shared tooling stays in source/build, machine/raw/generated data in
owned ignored out/ roots, and the retired root remains absent.
