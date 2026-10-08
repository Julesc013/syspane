---
type: "SysPane Work Package"
title: "Native editor helper worker bridge"
description: "Move verified image and recovery execution behind bounded GUI-owned task handles."
tags: ["delivery", "architecture", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T22:48:00+00:00"}
sp_id: "SP-W11-EDITOR-HELPER-WORKER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W26-EDITOR-HELPERS", "SP-W10-RECOVERY-CONTROLS", "SP-W10-RECOVERY-QUEUE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor helper worker bridge

Provide bounded image/recovery task handles for existing SceneImages and
EditorRecoverySession consumers. Keep ImageJob and LinuxRecoveryQueue as the native
execution owners. The worker side uses the existing shared LinuxInstallation on its
strict owner thread. It introduces no thread pool, helper pathname fallback, second
editor history or authored request ledger. The installed frontend's supervisory
thread can pump this owner alongside configuration supervision. This package closes
the reusable worker/consumer boundary; installing the actual editor, profile-bound
recovery directory selection, telemetry and desktop activation remain required.

## Ownership and interfaces

Extract minimal task interfaces from the existing image and recovery owner APIs;
their concrete path-based experimental callers keep their current behavior. Allow
SceneSurface/EditorForm and EditorRecoverySession to receive trusted task factories.
A default caller keeps its existing native path experiment. A verified factory has
no helper pathname parameter. Factories are trusted host objects, never authored
configuration, and cannot confer policy or recovery retention authority.

The application-layer client and its handles belong to one GUI thread. Construction,
poll/status, cancellation, completion consumption and destruction perform only
bounded memory/state operations. They never open files, verify installations, spawn
or wait for children, join threads or call arbitrary callbacks under the shared
mutex. Input copies remain bounded by the existing image/recovery byte ceilings.
The native owner is explicitly attached on another serialized worker, with a verified
bundle. Calls before attachment or after closure refuse admission. Only that worker
constructs, polls and destroys concrete native tasks. No filesystem/native work is
performed while holding the shared mutex. Host code pumps at least every 10 ms in
the development profile; this cadence is not a real-time scheduling guarantee.

Client closure and each task's cancellation/close erase undispatched input and
deliverable result buffers synchronously, refuse new work and mark closure pending.
If the worker already acquired an intent, it may complete startup, but must stop the
exact child and discard its output before acknowledging closure. No result can be
published after a concurrent cancellation won the shared-state lock. Regrant creates
a new task/context; it never revives cancelled work. A closed handle is reaped only
after the worker has accounted for queued/acquired work and any actual child exit.
Do not interpret an initially empty process ID as completion.

Dropping an active handle schedules cancellation without blocking the GUI. Its slot
remains reserved until the native owner confirms closure. A completed consumed or
closed handle releases its slot when destroyed. Keep the client and worker alive
until all closing work drains; the normal worker destructor runs only after this
proof. Emergency native cleanup belongs on the worker, never a GUI destructor.

## Image bounds and outcomes

Allow at most four retained image handles, with at most two active native ImageJobs.
Queued jobs start in admission order. Each input retains the existing 8 MiB ceiling;
four queued inputs total at most 32 MiB. Each completed raster keeps the existing
16 MiB ceiling, so four unconsumed results total at most 64 MiB. Existing native job
input/output buffers and temporary startup copies remain separately bounded by
their original contracts; these accounting limits are not process RSS guarantees.
Full capacity refuses admission before acquiring input or launching a child.

An image handle starts running with reaped=false, even while queued. Poll exposes
only a snapshot; it does not pump native work. Ready requires validated exact pixels
and actual native exit. Take moves those pixels once and becomes consumed. Cancel
immediately removes deliverable pixels, then becomes cancelled/reaped only after
worker acknowledgment. Installation/decode/launch failure reports failed/reaped
after any child is closed, with a bounded code, never arbitrary native diagnostics.
The native owner's existing three-second deadline starts at native launch; queued
time does not consume that deadline. Client closure cancels queued work as well.

## Recovery semantics across the bridge

Allow one retained recovery handle. It has one immutable context/directory, starts
with load ticket 1, and cannot replace/retire before successful load completion is
consumed by the GUI. Preserve read/retain/erase admission, 786432-byte captures,
uint64 ticket exhaustion, one latest pending capture and retirement fencing.

The bridge coalesces only undispatched captures. It maps its monotonically increasing
public tickets onto the existing queue's native tickets; at most active/pending and
one being-published completion mapping are needed. A newer GUI capture suppresses
older deliverable completion even when the worker has already completed it. Native
storage expectations still advance through every completed native operation. Never
replace the underlying queue or force a file overwrite to bypass a conflict.

Retirement seals the GUI handle immediately, replaces pending capture intent and
waits behind the active native operation. Only matching durable retirement plus
actual child exit yields retired. Loaded bytes and each latest completion move to
the GUI once, carrying the exact immutable context and public ticket. At most one
GUI pending record and one deliverable completion exist, in addition to the native
queue's existing bounded active/pending buffers. Bound error codes as before.

Close/invalidation erases those GUI buffers and suppresses later completion. The
worker observes closure before its next native poll and closes the queue. A guard
already dispatched before that observation may race with publication, as in the
existing storage contract; closure is not rollback. No later mutation is possible
after closed/reaped. Native launch/storage failure makes the handle unavailable,
preserves unchanged/unknown outcome where known and drops obsolete pending intent.

## Fixed acceptance and handoff

Freeze this package and literal worker cases, image expectations and recovery records
before implementation. Exercise a relocated five-file consumer and real production
helpers. The independent observer must compare exact image/file bytes and observe
native helper identity and exit. Use a test host with independently controllable
worker pumping; production tasks contain no pause/fault hooks.

Prove GUI operations return while native pumping is held, queued cancellation never
launches, active cancellation/close waits for actual exit, closure erases completed
results, late acquired results cannot reappear, slot limits include abandoned tasks,
and image ordering/concurrency are bounded. Check invalid media/input and wrong-thread
access. Recovery cases cover exact load and capture, latest-only completion, public
ticket mapping, retirement while pending, denial, context erasure, failed helper
verification and actual files after worker closure. Deliberately wrong pixel and
record expectations must fail. Preserve failures and exact source/artifact identity.

Connect the factories to real SceneImages and EditorRecoverySession consumers, then
run the affected rendering/recovery and installed-settings regressions plus all three
component graphs. New native cases have a 30-second deadline each and a five-minute
family ceiling; existing product timeouts and workspace reservations do not change.
Next integrate the worker into the actual frontend with independently verified
profile/session/directory authority and native editor interaction. Keep W-11/W-26
in progress until their complete outcomes and all release gates are met.
