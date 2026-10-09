---
type: "SysPane Work Package"
title: "Native form request preparation"
description: "Integrate detached Apply with exact recovery context and cancellation before submission."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T12:14:28.333463+00:00"}
sp_id: "SP-W11-REQUEST-FORM"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-REQUEST-WORKER", "SP-W11-HISTORY-FORM", "SP-W11-RECOVERY-SUBMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native form request preparation

Connect Apply to the existing RequestPreparationFactory. Keep the original
synchronous form path when no factory is supplied. The installed Linux frontend
supplies its existing worker factory independently of production recovery admission;
this does not enable history/recovery controls or qualify a release edition.

## Start and completion

Apply retains the ordinary editable, pending-field and initial-preview checks.
Allocate the final request identifier once, capture detached RequestWork and admit
one native task. Freeze the current optional recovery digest through submitting
only when the existing may_apply predicate permits it. Do not pause/resume recovery
capture: Apply is already excluded while a capture is pending, and authoring is
disabled throughout request preparation. The unchanged ready check can still
resolve the initial preview; this package does not bypass its rendering contract.

Poll the task on the existing 40-ms form timer and stopped path. Poll recovery
before consuming a ready request so withdrawal is observed. Consume only a stopped,
ready, current task on the live GUI owner. Recheck recovery may_apply and equality
of its current digest with the captured value before draft adoption. A changed
digest refuses this attempt without IPC or a live ticket. A later explicit Apply
may proceed under current unavailable-recovery rules with no retirement digest.

Adopt only through EditorDraft's current-owner/current-policy validation. Clear the
clipboard as for synchronous begin, publish pending UI state and dispatch the
exact request and digest once. Preparation/factory/adoption failure clears the
pre-submit recovery marker and preserves authored state, selection, history and
ticket counter. Show a retryable preparation error, not a durable outcome. A
submission callback exception after adoption follows the existing disconnected/
unknown-outcome path; do not replay with a new identifier automatically.

## Input, cancellation and lifetime

While a preparation handle exists, disable authoring, selection, history, Apply
and clipboard edits, including programmatic GTK actions, pointer and keyboard
paths. Retain Cancel, Reload and Cancel request. Cancel request cancels preparation
without discarding the draft or invoking the transport cancellation callback.
After submission it retains the existing transport cancellation behavior.

Cancel/Reload, accepted reload or recovery rebind, topology or policy change,
disconnect and close mark the task obsolete and cancel delivery. Current policy
still erases private UI state immediately. A late result, even from a task that
incorrectly offers a result after cancellation, must not submit or repopulate the
form. Clear the pre-submit recovery marker and captured digest on cancellation.
Do not retain a result outside the form's current-task ownership boundary.

A running task remains held until stopped. can_leave is false while preparation
is pending. stopped and deferred exit include request/history/recovery work and
existing image jobs; an exit callback is delivered once after the required work
stops. Cancel editor retains ordinary draft discard and owned-recovery retirement.
No additional thread, timer, queue, storage write or acceptance-limit change is
authorized. Completion/reconciliation after submission retain the existing paths.

## Fixed verification

Freeze request-form-cases.json and request_form.hpp before implementation. Use real
GTK controls with controlled task completion to check exact command/id/epoch/ticket,
pending input exclusion, repeated Apply, factory/run failure, cancellation in all
phases, reload/topology/policy/disconnect/close, malicious late result, recovery
digest equality and withdrawal/rebind, and post-submit cancellation/unknown state.
The existing native worker cases separately prove actual worker execution.

Measure the Apply capture callback and owner-adoption callback in the form cases;
preserve their 100-ms bound and keep them separate from worker computation. Run
the existing form/history/reply/recovery and installed editor/recovery consumers,
then the unchanged seven ordinary GUI timing/erasure cases. Preserve all failures
and original expectations. Record exact source/artifact/environment identities,
callback evidence where useful and the next unresolved cost. Build all three
development profiles and run affected portable/component checks. Production
recovery/history and all five complete 0.1.0 editions remain gated.
