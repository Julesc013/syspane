---
type: "SysPane Work Record"
title: "Frontend phase diagnosis and accepted reply closure"
description: "Attribute remaining GUI stalls and avoid rebuilding an editor that is being replaced."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:03:51.878799+00:00"}
sp_id: "SP-FRONTEND-PHASES-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-FRONTEND-PHASES", "SP-DRAFT-ADMISSION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Frontend phase diagnosis and accepted reply closure

The optional frontend phase observer attributes work inside the existing GTK tick.
The experimental entry point reserves a bounded numeric journal before startup and
emits it only after the frontend owners close. Production reads no diagnostic
environment variable. Absent observers create no phase clocks or journal entries.
Refusal or exception disables the observer before ordinary supervised shutdown;
two native cases verify exit status 2, committed settings and child/runtime closure.
The strict independent decoder rejects malformed, truncated and duplicate records.

EditorForm now offers an internal close_on_accepted reply disposition, with ordinary
refresh as its default. Original request validation still precedes all use of the
outcome. Ignored tickets return false, invalid results throw, and non-accepted
results keep their original behavior. Accepted replacement closes and erases the
old form without constructing another preview. The installed host reports the
durable result only after consumption; it still waits for helper exit, downloads
a fresh authorized profile, matches the exact recovery receipt and acknowledges
retirement. No storage, protocol, authorization or activation rule changed.

## Evidence

All 323 selected Linux portable checks pass. Both existing Windows development
profiles pass their component graph checks; their compiled implementation is
unchanged and retains the preceding checkpoint's broader evidence. The Linux
profile is revision 62 (the original phase experiment was revision 61); Windows
GCC 15 and v141_xp remain revisions 36 and 27. Native families pass as follows:

| Family | Cases |
|---|---:|
| EDITOR-REPLY-LIFECYCLE | 11 |
| FRONTEND-PHASE-FAILURE | 2 |
| INSTALLED-RECOVERY | 14 |
| INSTALLED-EDITOR | 15 |
| INSTALLED-SETTINGS | 12 |
| EDITOR-RECOVERY | 14 |
| EDITOR-FORM | 20 |
| IMAGE-ERASURE | 3 |

The native scene-image component check also passes.

The 11 reply component cases use actual GTK controls for submission and separately
check direct/reconciled acceptance, default refresh, non-accepted outcomes, stale
tickets, invalid epoch/query/revision/facts, policy withdrawal and duplicate delivery.
The initial attempt lacked required fixture callbacks and failed editor.actions
before reply execution. Its source and artifact are retained. Completing those
callbacks changed no expected result. Installed regressions independently observe
saved bytes, reconciliation, recovery retirement, private erasure and native exit.

The [checkpoint](checkpoints/frontend-phases.json) binds every attempt to source
archives, binaries, fixed input hashes and verified local native archives. Earlier
failed attempts and the unchanged acceptance oracles remain preserved. Generated
recordings and machine bindings remain ignored out/ content.

Specification validation passes for 51 schemas and 183 fixtures; the generated
inventory contains 661 files. These checks do not execute native product tests.

## Timing result

The same maximum inputs, instrumented before and after the reply repair, yield:

| Case | Earlier reply (ms) | Current reply (ms) | Current editor construction (ms) |
|---|---:|---:|---:|
| MAX-WIDGETS | 145.758 | 34.946 | 156.109 |
| MAX-SCENE | 108.483 | 37.575 | 194.743 |
| MAX-RECORD | 110.858 | 34.852 | 176.866 |

These are per-case maxima on the recorded laboratory, not portable guarantees.
Nested phase durations overlap and cannot be summed. Reply settlement no longer
rebuilds the soon-to-be-closed preview; fresh editor construction and work in other
callbacks/painting remain separate costs. The complete ordinary GUI qualification
with phase observation disabled still records the following fixed-limit outcomes:

| Case | Result | Maximum tick work (ms) | Maximum excess delay (ms) |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 211.923 | 161.559 |
| MAX-SCENE | fail | 184.282 | 168.312 |
| MAX-RECORD | fail | 169.927 | 183.924 |
| MAX-COMMAND-REJECT | pass | 29.034 | 5.493 |
| OVER-RECORD-REJECT | pass | 28.895 | 6.292 |
| CLOSE-PREPARING | pass | 28.759 | 3.837 |
| POLICY | fail | 35.468 | 128.419 |

All seven original cases and their 100 ms work/delay and 200 ms erasure limits are
unchanged. A diagnostic run retains timing failures; it cannot qualify recovery.
Production recovery remains disabled. W-11 and all five complete 0.1.0 editions
remain open.

## Next boundary

Close the ownership and current-policy contract for preparing fresh editor state on
the existing worker before GTK construction. Profile serial, epoch, capabilities,
resources, revision and withdrawal must bind any prepared result; it cannot bypass
native layout/text validation or revive stale recovery authority. Independently
attribute remaining history/edit callbacks before moving more work. Preserve the
fixed oracles and failed attempts, then rerun ordinary qualification. Inspector,
telemetry/desktop integration, other native adapters and release evidence remain
required parts of the full objective.
