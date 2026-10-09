---
type: "SysPane Work Package"
title: "Native history preparation ownership"
description: "Bound history work on the existing helper worker and preserve current-draft adoption."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T09:00:00+00:00"}
sp_id: "SP-W11-HISTORY-WORKER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-HISTORY-PREPARATION", "SP-W11-EDITOR-HELPER-WORKER", "SP-W11-RECOVERY-PREPARATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native history preparation ownership

Use the existing Linux editor helper worker for detached HistoryWork. The GUI
owns the task handle and remains the only owner allowed to adopt its opaque
HistoryPrepared result. This package closes the native computation boundary;
form scheduling, recovery capture suspension and preview refresh still require
integration before enabling asynchronous history in the installed frontend.

## Task contract

The GUI factory accepts one non-null, unconsumed detached work object only while
the channel is attached and open. There is exactly one history slot and one
independent recovery-preparation slot. A retained completed handle still reserves
its slot. A second admission returns helpers.capacity and changes neither the
existing task nor the draft. No request queue, extra worker, thread or timer is
introduced. Each input retains only the bounds already specified for its work type.

Each worker poll services existing image and recovery I/O and then executes at
most one pending pure computation. Select the oldest admitted eligible work
across history and recovery preparation; new work cannot overtake an older task.
Use the existing checked channel sequence. Claim and publication use the mutex;
validation and destruction of the running input occur outside that mutex.

Task states are queued (not running, ready or stopped), running, and stopped.
Success is stopped and ready with exactly one transferable result. take returns
that result once and clears ready, retaining the reservation until handle release.
Before readiness, after consumption, or after cancellation, take fails with
history.not_ready. A failed run is stopped, not ready, and carries the bounded
existing protocol error or history.preparation for an unexpected exception.
The opaque work still enforces its one-shot computation rule.

Cancellation is idempotent. Before claim it erases the queued input and stops
immediately. After publication it erases the undelivered result. During computation
it withdraws delivery immediately but cannot claim stopped until that computation
and its input destruction finish. Dropping a running handle retains the slot
until this acknowledgment; dropping a stopped handle releases it immediately.
No cancelled task can return a result, including after the worker finishes.

Channel close cancels both preparation types and rejects new admissions. stopped
requires both computations and existing native children to have drained. Worker
destruction performs existing native cleanup and leaves surviving GUI handles
stopped and cancelled. Factory and status/take/cancel methods enforce GUI owner
identity; worker methods enforce their native owner. Handle destruction never
joins or starts a worker. Completed results do not retain a channel or draft.

Taking a result is not adoption permission. A changed policy, selection, authored
state, draft identity or closed/destroyed origin continues to invalidate adoption
under SP-W11-HISTORY-PREPARATION. Concurrent recovery preparation does not bypass
either proof: requesting history invalidates an earlier recovery proof even when
both computations complete. A future form must cancel/suspend obsolete capture
before requesting history and resume capture from its final authoritative state.

## Fixed verification and handoff

Freeze tests/configuration/history-worker-cases.json and its Python expectations
before implementing the native bridge. Use the existing relocated verified helper
probe and independent OS observer. Verify exact scenes, selection, stack counts,
held progress, null/consumed inputs, capacity, one-shot take, wrong-thread refusal,
queued/completed/running cancellation and drop, close, stale adoption and both
orders of recovery coexistence. Running cases must observe running before acting;
a computation that finishes too early is a failed observation, never a substitute
queued-cancellation pass. Observe orderly process/thread exit for every case.

Task-interface calls retain the existing 100-ms bound. Test fixture construction
and synchronous oracle preparation are recorded separately and do not establish
GUI qualification. Run native.HISTORY-WORKER and the original helper-worker,
recovery-preparation, recovery-admission and installed editor/recovery regressions.
Run affected portable history checks and component checks on all three development
profiles. Preserve source/artifact-bound attempts and failures under owned ignored
out/ roots; keep the existing workspace allowance and report archives separately.

No changes to fixed native GUI timing/erasure expectations are authorized here.
Completion of this boundary does not enable production recovery or finish W-11,
the native inspector, other platform adapters or any complete release edition.
