---
type: "SysPane Handoff"
title: "Shared native measurement ownership checkpoint"
description: "One serialized clock facility across acquisition workers, with contention controls and native controller regression evidence."
tags: ["delivery", "telemetry"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T09:11:22.173323+00:00"}
sp_id: "SP-MEASUREMENT-OWNER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W14-MEASUREMENT-OWNER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared native measurement ownership checkpoint

The shared measurement-owner checkpoint closes
the controller's concurrent access to one serialized authenticated clock facility.
One owner per connection returns exact native ticks/exceptions and is shared by
both source workers and initial controller clock reads. Two contention/exception
cases plus 85 controls pass on each development profile, and both strict historical
audits cover 24 executables. Five affected Linux native families pass, including
installed CPU values, policy/cancellation and uncooperative-worker/guardian exit.
Preserve the initial strict compiler fixture failure and all earlier native failures.
Next reuse these owners with Windows polling, native workers and independent
guardian supervision, then actual native inspector/settings/editing/desktop work.
All five complete editions, remaining providers and target/lifecycle/release gates
stay open; retain the unresolved mixed GTK loss. Keep fixed workspace reservations:
archive verified inactive evidence before a future build if the 9 GiB check stops.
Shared tools stay in source/build; raw/machine/generated data stay ignored under
out/ and the retired root remains absent.

The [package](packages/w-14-measurement-owner.md) records the ownership gap and
fixed observable behavior. The [checkpoint](checkpoints/measurement-owner.json)
binds ten executions to complete verified source archives, manifests, logs,
workspace checks, current profile artifacts and native records. The unsuccessful
compiler run remains alongside the final passes. Existing source-bound handoffs
remain historical records at their named revisions.

The existing native measurement facility mutates fault/provenance/highwater state
and requires serialization. Previously, network and processor workers shared a
callback that called it concurrently. The controller now constructs one shared
MeasurementOwner for each admitted client; all three former direct clock-use sites
route through that owner. Worker callback copies retain the same owner/lock. Each
invocation returns the native model Tick unchanged or propagates its exception.
No clock domain, source epoch, timestamp cache, fallback, retry or fault recovery is
introduced. Native source identity and sticky failure remain the provider's rules.

The lock covers the native clock/provenance lookup only. Acquisition work remains
on the existing workers; health, policy and I/O remain on the controller. The
Stream/owner outlive every worker through join or actual owned-process exit.
Initial connection/hello lookups happen before dispatch. A blocked native lookup
still requires the existing job timeout, two-second controller stop and independent
guardian; synchronization is not preemption. Fixed clocks, measurement intervals,
publication/selector identities and policy permissions remain unchanged.

| Execution | Coverage | Result |
| --- | --- | --- |
| Windows x64 GCC 15 | 2 ownership + 85 existing controls | pass |
| Linux x64 GCC 13 | same 87 checks | pass |
| Windows x86 v141_xp on current host | same 87 checks | pass |
| Historical pinned-input/PE/import audits | both strict cases, 24 executables | pass |
| Linux controller/installed regressions | CPU publication, installed CPU inspector, network service/consumer/supervisor | pass |

The ownership case synchronizes eight callers. The direct unguarded callback
control exposes overlapping entry; the actual shared owner excludes it and returns
all eight exact results with unchanged domain strings. This is a controlled callback
concurrency oracle, not a claim of native Windows or low-end performance. The failure
case proves there is no implicit retry or invented timestamp, provider exceptions
remain exact, ownership is released after throwing, and an empty callback is invalid.
Live Linux cases retain independently computed CPU values/timestamps, policy erasure,
failed/gap recovery, cancellation and actual termination of noncooperative work.

The initial GCC build rejects the test's unbraced wait loop followed on the same
line by barrier release as misleading indentation. Braces and a separate release
statement resolve only that construction; strict warnings and expected behavior
stay fixed. Keep the original source archive and build error. No native result or
acceptance criterion is rewritten to turn that attempt into a pass.

This closes the identified shared-clock access gap in the current Linux controller
and supplies the reusable ownership primitive for the Windows port. Windows native
controller/demand/worker/guardian/UI composition remains required. Historical guest,
native multi-group, physical/low-end/hotplug, remaining resource providers and all
complete desktop/package/lifecycle/release gates stay open. Preserve the original
inverse PDH timer, transport fixture and mixed GTK failures; no narrower passing
control establishes their missing qualification. All five 0.1.0 editions remain
the objective. No privilege, publication or sensor authority is added.

The active workspace remains within the admitted 9 GiB ceiling; its remaining
headroom can stop a new build reservation. Inspect/preflight and preserve that
stop before archiving verified quiescent owned native evidence. Do not enlarge
product limits or remove failures. Tools remain in source/build; raw/machine data
are ignored under owned output roots, and the retired root remains absent.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
