---
type: "SysPane Work Package"
title: "Native editor recovery controls and capture lifetime"
description: "Connect verified editor identity to bounded captures and explicit recovery decisions."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T03:00:00+11:00"}
sp_id: "SP-W10-RECOVERY-CONTROLS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-RECOVERY-QUEUE", "SP-W10-RECOVERY-DRAFT", "SP-W10-RECOVERY-APPLY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor recovery controls and capture lifetime

Connect the existing EditorDraft, LinuxRecoveryQueue and GTK EditorForm. Keep
recovery-directory I/O in the helper and authored transactions in their existing
owner. This closes the admitted Linux development editor integration, not installed
profile ownership, other native adapters or complete-edition qualification.

## Trusted admission

The host explicitly supplies the helper path, existing private directory, session,
profile, verified generation token, current policy revision and erase grant. The
form compares the revision with its current policy and requires recovery_available.
Never infer an identity or grant from the retained record. Admission is optional;
ordinary callers retain disabled recovery. A fresh binding is required after any
policy, disconnect, reload or committed-generation change. The previous queue must
be closed and reaped before a new one starts. Denial never implies deletion.

## Initial offer and decisions

Initial load blocks authored editing until the result is known. Absence enables
automatic capture. A present record is inspected with EditorDraft and the separate
trusted identity. Show Restore, Discard recovery draft and Keep for later. Invalid,
stale or otherwise unrestorable records permit only Discard and Keep. Do not show
raw untrusted text, change committed selection or activate a desktop at startup.

Restore requires a pristine destination and current authorization, creates exactly
one ordinary undo step, clears selection, and enters the existing editor preview.
It enables capture of subsequent edits. Apply remains the sole durable commit path.
Keep releases the in-memory record and permits editing, but disables automatic
capture for this binding: later edits and Apply must preserve that kept record.
Discard conditionally retires the loaded record using explicit erase authority,
then enables capture of the current draft. It never changes the authored scene.
Failure is visible and cannot be reported as successful deletion.

## Capture and acceptance

After each atomic authored change, including undo/redo, capture the current dirty
draft with the existing canonical recovery encoder. Private property/modal buffers,
selection and held gestures do not constitute authored changes. There is no delay
timer; the existing queue coalesces pending captures. Skip an identical latest digest.
Show capture pending until durable completion and verified helper exit. A recovery
capture is never called a saved configuration or visible desktop.

Apply waits while a capture is outstanding, so its matching durable recovery digest
is known. Recovery failure leaves ordinary Apply usable with recovery-unavailable
status. Keep also allows Apply without replacing its retained record. At submission,
retain only the matching captured digest as request metadata; policy/disconnect may
erase record buffers without losing that bounded reconciliation fact.

An accepted result closes the old generation's queue immediately. The host supplies
the newly verified generation separately. A fresh load may retire only the digest
associated with that accepted request, with current read and erase authority. An
unexpected replacement is offered, never deleted as if it belonged to the request.
No capture runs under the previous generation after acceptance. Unknown results keep
their existing query/reconciliation path; rejection alone does not retire a draft.

Undo to a clean baseline fences and retires this session's matching captures, then
opens a fresh queue so a later Redo can capture normally. During that short fence,
authored controls wait. Cancel session similarly retires only an owned capture; it
does not discard a kept or undecided startup record. Wait for successful retirement
before reporting discard and exiting. On failure retain the open editor and explicit
unavailable status; an independent window close remains possible.

## Closure and bounds

Policy/disconnect/reload invalidation drops offer bytes, queued captures and pending
automatic decisions immediately, closes the held queue, and consumes no completion
from the old context. Regrant alone does not restore content or restart capture.
The host may explicitly supply a new verified binding and receive a new offer.

Closing the form is nonblocking and preserves existing coherent storage; it makes no
claim that an unfinished capture survived. The host continues polling closure until
the recovery child is reaped before destroying the form or stopping its event loop.
Normal GTK teardown must not enter the emergency blocking Child destructor.

Retain at most one offer of 786432 bytes plus the existing queue's bounded buffers;
digests and one pending trusted binding are bounded metadata. Never maintain a second
history or request ledger. Existing five-second helper deadlines and guard semantics
remain unchanged. UI recovery status is separate from commit/activation status.

## Fixed native acceptance

Freeze literal scenes, expected recovery command fields and this package before
production edits. Drive actual GTK controls through native input and AT-SPI; inspect
exact recovery bytes and committed files independently. Test edit/capture/crash/
reopen, no automatic restoration, Restore/Undo/Redo/Apply, Keep followed by edits and
Apply, Discard without authored changes, private uncommitted fields, clean Undo,
Cancel session, malformed/stale records, policy denial/regrant, lost-result
reconciliation, replacement conflict, recovery-worker failure and held-child close.
Compare exact scene/resources after Apply and prove matching retirement; a deliberately
wrong expected record must fail. Observe held helper exit on closure and no later write.
Retain failures. Re-run existing editor, clipboard, storage/queue and shared recovery
checks appropriate to the changed boundaries, plus all three component graphs.
