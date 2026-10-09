---
type: "SysPane Work Package"
title: "Prepared editor history transitions"
description: "Validate undo/redo off the GUI without transferring stale draft or permission proofs."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T07:35:00+00:00"}
sp_id: "SP-W11-HISTORY-PREPARATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INITIAL-PREVIEW", "SP-W11-RECOVERY-PREPARATION", "SP-W11-DRAFT-ADMISSION", "SP-W10-THEME-HISTORY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared editor history transitions

The initial-preview checkpoint leaves full scene/resource validation and the first
structural submit-eligibility check in history callbacks. Preserve synchronous
EditorDraft undo/redo as the reference behavior. Add detached preparation and exact
current-owner adoption before connecting it to the installed worker and GUI.

## Portable contract

Requesting a history transition invalidates older recovery and history preparations,
including empty or rejected attempts. An empty source stack returns no work and
leaves authored state, selection and stacks unchanged. An admitted request captures
the selected target scene, its immutable resources, target selection and direction,
plus the bounded detached settings context required for ordinary full validation.
It copies neither history stacks, clipboard, request tickets nor result payloads.
No native object or live draft pointer crosses the worker boundary.

Preparation is a one-shot computation. It runs the existing full prepare_scene
checks against that detached state, then evaluates structural preview/commit
eligibility for the resulting authored state. Results retain only structural hints,
never permission decisions. Ordinary begin still performs all command and resource
validation. Clean/no-op and legacy oversized local previews retain their original
submit behavior; a false eligibility hint does not reject a valid local history step.

An opaque result belongs to one originating draft identity and one exact mutation
generation. Selection attempts invalidate history results, including rejected and
same-selection attempts; selection continues to leave recovery proofs unaffected.
All existing recovery-invalidating operations also invalidate history results.
Copies, assignments, moves and destruction cannot transfer the original identity.
Starting another transition invalidates the earlier result. Work may finish after
invalidation, but its result cannot be adopted.

Adoption requires an unconsumed result, exact live identity/generation and current
editable state. Recheck current preview authority and current source/target resource
authorization. Reuse only the opaque proof of full validation of those exact values.
On refusal, no scene, selection, resource, request or history entry changes; invalidate
other outstanding preparation. On success, restore the original target selection,
move exactly one entry between the existing stacks, preserve exact resource ownership
and existing 64-entry/8-MiB accounting, and invalidate prior preparations. Do not create
a second history. Preserve request numbering, accepted revision and epoch. Transfer
the validated structural hints explicitly; ordinary draft copies still lose hints.

## Native integration boundary

The installed frontend must execute admitted work on its existing editor worker,
outside shared channel locks. No additional thread, timer or live scheduler is
authorized. Before enabling that path, close its finite task-slot ownership,
cancellation, recovery-preparation coexistence and shutdown acknowledgment rules.
While a transition is pending, disable conflicting authoring/Apply actions and show
preparation status; reload, withdrawal, disconnect, topology replacement and close
must cancel it. Late results cannot repopulate a replaced form or restore authority.
Successful adoption must rebuild the native preview using the current topology,
telemetry and authority; a validated authored scene is not a native-frame proof.

The portable checkpoint alone cannot claim GUI latency improvement or enable this
native path. Native integration must exercise held worker progress, pending action
refusal, cancellation before/after computation, exact undo/redo and child closure.
Freeze those cases before changing native behavior. General asynchronous authoring
and native preview handoff remain separate required work, not silently delegated
to synchronous GTK callbacks as a completed solution.

## Fixed verification and completion

First run fixed observable trace/theme/history-capacity/legacy-envelope/transaction
expectations against synchronous undo/redo. Then run unchanged expectations through
prepared transitions. Verify independent exact scenes, selections, resources,
history counts, submit eligibility and serialized requests; equality to the other
implementation alone is insufficient. Cover policy denial/regrant, all invalidating
operations both before and after computation, cross-draft/copy/assignment/move,
origin destruction, duplicate/failed runs, no-op and current recovery-proof behavior.
Run computation on a separate joined test thread and confirm it does not mutate the
origin. Invalid/replayed adoption must fail without altering observable draft state.

Run affected portable families on all three development profiles and their component
checks, then existing native preparation/recovery/editor consumers. Record exact
commands, source/artifact identities and original failures under owned ignored out/.
Keep the existing active workspace allowance and report retained archives separately.
Native enablement additionally requires the integration cases above and unchanged
ordinary GUI timing/erasure qualification. Production recovery, W-11 and all five
complete release editions remain open until their full gates pass.
