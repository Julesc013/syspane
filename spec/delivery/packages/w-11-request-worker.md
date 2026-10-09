---
type: "SysPane Work Package"
title: "Native request preparation ownership"
description: "Bound request preparation on the existing native worker without granting submission authority."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T11:53:49.045312+00:00"}
sp_id: "SP-W11-REQUEST-WORKER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-REQUEST-PREPARATION", "SP-W11-HISTORY-WORKER", "SP-W11-EDITOR-HELPER-WORKER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native request preparation ownership

Use the existing Linux editor helper worker for RequestWork. A GUI-owned handle
transfers its opaque result to the owner; only EditorDraft adoption can create a
pending live request. This package closes task execution and ownership. Form
scheduling, recovery-digest binding and submission remain the next integration
boundary; completing this package does not repair installed Apply by itself.

## Admission and execution

There is exactly one request-preparation slot, independent of the existing history
and recovery-preparation slots. Null input fails with request.work. An unattached
or closing channel fails with helpers.unavailable; an occupied slot fails with
helpers.capacity, including a completed or consumed handle still held by the GUI.
An already-consumed non-null work object can be admitted but its one-shot run fails
with editor.request_consumed. These errors cannot allocate a live ticket or mutate
the originating draft. Factory access and task status/take/cancel require the GUI
owner and otherwise fail with helpers.owner.

Each native poll first services existing image/recovery I/O, then executes at most
one eligible pure computation. Choose the oldest admitted request, history or
recovery preparation using the existing checked sequence. Never overtake older
eligible work. Claim and publication hold the channel mutex; computation and
destruction of the running input do not. Introduce no worker, thread, timer, queue,
cache, larger document limit or second source tree. Request snapshots/results keep
the existing portable bounds; report their separate handle count, not a fabricated
encoded-helper byte count. Shared build files stay under source/build and raw
evidence stays under ignored out/.

## States, cancellation and lifetime

A queued task is neither running, ready nor stopped. A claimed task is running
until computation and input destruction finish. Success is stopped and ready with
one transferable result. take clears ready, returns that result once and retains
the slot reservation until handle destruction. Premature, repeated or cancelled
take fails with request.not_ready. A failed run is stopped and not ready; preserve
bounded protocol errors, or report request.preparation for unexpected exceptions.

Cancel is idempotent and immediately prevents result delivery. Before claim it
destroys the queued input and acknowledges stopped. After completion it destroys
the untaken result. During computation it reports running, not stopped, and
request.cancelled until computation and input destruction finish. Never claim a
running computation was interrupted. A running handle's destruction retains its
slot until that acknowledgement; a queued/stopped handle releases it immediately.
No GUI destructor starts or joins a worker. A taken result belongs to its caller;
task cancellation cannot revoke it, so current-draft proof checks remain mandatory.

Channel closure cancels all three kinds, refuses new work and reports stopped only
after all computations and existing native children drain. Native-owner destruction
performs the existing cleanup and leaves surviving handles stopped and cancelled.
Taking a result confers no authority: edits, selection, policy denial/regrant,
reload, disconnection, replacement and closure still fence stale adoption. The
worker never submits IPC, publishes storage or allocates a live request ticket.

## Verification and continuation

Freeze request-worker-cases.json and native_request_worker.py before implementing
the bridge. Use the existing relocated probe and independent OS observer. Require
exact prepared command/request/epoch/ticket values, unchanged originating state
before adoption, one-shot transfer, capacity through queued/ready/taken states,
null/consumed input, owner refusal, cancellation/drop in each phase, close and
worker exit, stale/current-policy rejection and all six three-kind admission orders.
Calibrate the oracle with an intentionally incorrect command expectation.

Running cancellation/drop/close must observe a running worker stopped by the
kernel before acting. An already-completed computation fails that observation;
it is not evidence for the running case. GUI task calls retain the existing
100-ms bound. Fixture setup and deliberate consumed-work construction are recorded
separately. Require orderly process/thread exit and no new computation thread.

Build the affected Linux targets and run native.REQUEST-WORKER, existing history,
helper-worker, recovery-preparation/admission and installed recovery/editor cases.
Run portable request/history and component checks on all three development
profiles. Preserve source/artifact identity, failed attempts and the original
ordinary GUI limits. Then connect the form's pending state, cancellation, current
policy and recovery digest to this task before submitting exactly once. Production
recovery/history and all five full 0.1.0 editions remain unqualified.
