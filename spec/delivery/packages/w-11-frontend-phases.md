---
type: "SysPane Work Package"
title: "Bounded frontend phase diagnosis"
description: "Attribute remaining GTK stalls without changing the fixed timing oracle or admitting a runtime override."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T05:36:08+00:00"}
sp_id: "SP-W11-FRONTEND-PHASES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-DRAFT-ADMISSION", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded frontend phase diagnosis

The preceding fixed GUI run has four timing failures. Its largest work sample,
288492 microseconds, occurs inside Window::tick. Reply settlement, profile
population and their component construction need separate measurements before
selecting a repair. The possible reconstruction of a preview immediately before
form replacement is a hypothesis, not a verified cause.

## Observer boundary

The existing frontend runtime may accept an optional internal phase observer,
confined to its GTK owner with no reentrancy. Each observation contains only the
current positive tick sequence, a fixed numeric phase, elapsed microseconds and
whether that phase completed normally. There are no authored values, identifiers,
paths, policy details or native addresses. Nested phase durations overlap and must
not be summed as independent costs. Exceptions record an incomplete phase and
retain failure. Observer refusal/exception disables observation, fails the host
and initiates ordinary supervised shutdown; it must not prevent later closing
ticks from observing backend/helper exit.

Fixed phases are: 1 backend take; 2 withdrawal; 3 reply settlement; 4 reply reload;
5 complete repopulation; 6 editor construction; 7 settings construction; 8 recovery
attachment; 9 GTK widget attachment; 10 topology update; 11 final control update.
The observer requires the existing timing observer. No phase clocks or records are
created when absent. The ordinary 20 ms timer and its whole-work/excess-delay
measurements remain unchanged, including observation overhead within measured work.
Do not introduce a native thread, timer, scheduler or filesystem operation in GTK.

Only the separately compiled experimental entry point reads
SYSPANE_TEST_PHASES=1, requiring SYSPANE_TEST_TIMING=1. It reserves storage before
starting the frontend and retains at most 8192 numeric records. Capacity failure
is a failed experiment, never silent truncation. After run_frontend returns and
its owners have closed, write a bounded numeric transcript to inherited stderr:
`phase-begin PID COUNT`, COUNT lines `phase TICK KIND MICROSECONDS COMPLETED`, then
`phase-end PID COUNT RESULT`. Writes are checked. Production does not read this
variable; ordinary fixtures retain no phase buffer and emit no phase transcript.
The fixture may additionally select SYSPANE_TEST_PHASE_FAULT=refuse or throw to
fail its observer on reply settlement. Native negative cases submit a real setting
change, require exit status 2 and observed child/runtime retirement, and verify
that observer failure does not undo the already committed change. No fault selector
is read by production and no product authority is gained by either observer.

## Independent experiment

Reuse native_recovery_gui_limits.py's exact exercise and the existing installed
observer without editing them. The diagnostic wrapper only enables phases and
selects a distinct evidence family. Preserve the original case outcomes, exceptions,
100 ms observations, 200 ms erasure, input hashes and all deadlines. After owned
case processes terminate, independently parse each stderr transcript into a separate
phases.json record bound to the original report and source/artifact identities.
Malformed, missing, duplicated or incomplete transcripts fail diagnostic evidence;
they cannot erase the original case failure. Do not turn a timing failure into a
qualification pass. Add parser cases for those refusals and for nested durations.

Run the diagnostic using ordinary owned output roots and profile commands. Keep
the unchanged GUI family as the qualification check; diagnostic completion alone
cannot enable recovery. Run Linux portable/component checks and installed recovery,
editor/settings and relevant native regressions after a functional repair. Other
profiles whose code is unchanged retain their prior evidence and receive component
checks when build metadata changes. Preserve source-bound attempts and original
failures before cleanup. Any repair needs its own closed behavior/ownership section
before implementation. W-11 and all five complete release editions remain required.

## Accepted reply followed by replacement

The source-bound initial phase experiment confirms separate reply settlement and
editor construction stalls. When an installed recovery editor will be replaced
by a newly downloaded profile, rebuilding its accepted preview serves no visible
purpose. EditorForm may therefore accept an internal ReplyView::close_on_accepted
disposition, with refresh as the default. Complete/reconciled must first perform
the existing ticket, request, epoch, revision, result-fact and current-draft checks.
Return false for an ignored ticket/closed form, propagate validation errors, and
never close because an unvalidated body merely says accepted. Non-accepted results
keep ordinary refresh behavior. A consumed accepted result settles the recovery
session and closes through the ordinary erasure/helper-retirement path, without
constructing another preview. The caller keeps polling until stopped before
destroying the form. This disposition grants no storage or recovery authority.

The installed host selects this disposition only when experimental recovery is
enabled and the accepted result requires reload or a fresh profile is already
loading/awaiting presentation. It publishes the durable notice only after the
editor consumed the reply. Fresh construction, profile authorization, exact
recovery receipt matching and retirement acknowledgment remain unchanged. The
default standalone form continues to refresh after accepted results.

A native component check drives actual form controls to submit a change, then
checks direct/reconciled acceptance, default refresh, cancelled/unknown outcomes,
wrong ticket, invalid epoch/query/revision/facts, policy withdrawal and duplicate
delivery after closure. It verifies authored-row erasure and disabled controls for
closure, and retained rows for ignored/rejected replies. Existing independent
installed recovery cases must still prove exact stored data, lost-result recovery,
receipt retirement, private erasure and child exit. Run the same phase experiment
and the unchanged ordinary GUI limits after this repair; retain any remaining
construction or external-callback latency failures.
