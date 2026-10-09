---
type: "SysPane Work Package"
title: "Prepared history in the current native form"
description: "Integrate bounded history tasks with current-form adoption, capture suspension and preview refresh."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T08:38:00+00:00"}
sp_id: "SP-W11-HISTORY-FORM"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-HISTORY-WORKER", "SP-W11-HISTORY-PREPARATION", "SP-W11-INSTALLED-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared history in the current native form

EditorForm may receive the existing helper worker's history factory. Its absence
preserves synchronous Undo/Redo. Use the factory in the already admitted experimental
frontend only until the original ordinary GUI timing/erasure qualification passes.
Do not add a production environment override, thread, timer or request queue.

## Admission and ownership

An admitted Undo/Redo requires the same editable draft, applied property fields,
closed modals and resolved input geometry as the original command. Reset gestures,
suspend recovery capture, request one detached transition and pass it to the factory.
An empty history, null task or factory failure leaves authored state and history
unchanged and resumes capture of that current state. Show a bounded failure message
for failed preparation. Do not silently perform synchronous history after failure.

While a task is held, disable authoring, property fields, selection, movement,
clipboard actions, Undo/Redo and Apply. Refuse programmatic command/key callbacks
as well as ordinary native input; do not enqueue repeated intents. Cancel session
and Reload remain available. The native status identifies pending preparation.
can_leave remains false. Existing painting and telemetry can continue; preparation
does not supply geometry or a rendered-frame proof.

Poll the task from the existing form timer and stopped() path. Only after stopped
may the form take and release it. Adopt a ready result once, only for this still
current, open form and its unchanged draft; recheck ordinary current policy and
resource authorization through adopt_history. A failed task or adoption leaves
history and authored state unchanged. Refresh list/fields and the existing fully
validated native preview after success, with current topology, telemetry and policy.
Do not alter scene validation, first-input geometry or preview fallback rules.

## Cancellation and replacement

Cancel session, Reload command, host reload, policy update, disconnect, topology
replacement, recovery rebind and close mark the task obsolete and cancel delivery.
Keep its handle until stopped; no replacement history may be admitted meanwhile.
An obsolete result is never taken/adopted, including a late ready publication.
Cancel session keeps its existing discard/retirement behavior and delays its exit
callback until history work has acknowledged closure. Reload/topology replacement
must not let old work mutate the newly current state. Close erases native form data
and stopped remains false while a cancelled computation still owns input.

## Recovery coexistence

pause_capture cancels pending/running pure capture and prevents changed() from
creating another capture. It preserves current binding, durable ownership and any
already admitted storage operation. It is allowed only when ordinary recovery
editing is allowed. may_apply is false while paused. Late obsolete preparation is
discarded without treating it as a new recovery failure. Already durable storage
completion retains its original exact-result checks.

resume_capture clears the pause and captures the final authoritative draft using
the existing coalescing path, waiting for obsolete preparation to stop before
reusing its slot. Invalidation, close or retirement clears the pause; resume cannot
restore automatic retention or a revoked binding. Cancellation/closing forms do
not schedule fresh capture. A kept or unavailable recovery session stays so.

## Fixed verification and completion

Freeze native form expectations before product changes. Exercise real GTK controls
with a controllable implementation of the existing task interface; execute actual
detached work on a joined test thread, keeping contract states under test control.
These component tests do not replace the independently observed native worker.
Verify exact serialized scenes and selection after Undo/Redo, pending input refusal,
factory/run failure without fallback, queued/ready/running cancellation, command and
host reload, topology/policy/disconnect/close and withheld stop acknowledgment.
Include recovery capture suspension/resumption, cancellation and withdrawal with
exact capture output. Preserve original independent expectations and failures.

Run native.EDITOR-HISTORY, native.HISTORY-WORKER, existing recovery preparation,
standalone editor/recovery, reply/initial-input and installed editor/recovery cases.
Run portable history and component checks across all development profiles. Finally
run the original native.RECOVERY-GUI-LIMITS unchanged against the installed fixture;
failures remain qualification failures and keep the production gate closed. Record
source/artifact/environment identity, archive complete attempts under owned ignored
out/ roots, and retain the current workspace allowance. Completing this boundary
does not finish general asynchronous authoring, native inspector or any full edition.
