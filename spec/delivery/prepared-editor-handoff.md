---
type: "SysPane Work Record"
title: "Prepared initial editor ownership handoff"
description: "Validated worker preparation, current-profile consumption and measured remaining GTK costs."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:39:01.569213+00:00"}
sp_id: "SP-PREPARED-EDITOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-PREPARED-EDITOR", "SP-FRONTEND-PHASES-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared initial editor ownership handoff

The existing frontend client worker now constructs the complete initial EditorDraft
outside the backend mutex. PreparedEditor owns its exact authority, policy, settings,
capabilities and large-command admission. It exposes no mutable preparation and
cannot be copied. EditorForm consumes one unique owner as its only initial semantic
state; the original constructor prepares that same value synchronously. GTK still
owns all controls, native layout/text, SceneSurface binding validation and mutations.

Backend publication rechecks generation/readiness, shutdown, pending request and
superseding reload intent. The current immutable profile and prepared value enter
the existing mutex-protected state together. take_editor accepts the exact current
shared profile identity and consumes the value once. Copied/stale identities,
loading, pending writes, withdrawal and close cannot consume it. Reload, submission,
withdrawal and close discard the stored value. Superseded worker candidates are
discarded before ready publication. An empty GTK take waits for current state;
there is no synchronous fallback that reintroduces the validation stall.

The compiled experimental entry point supplies its existing recovery choice to the
backend; live native recovery admission and exact receipt retirement remain separate.
No protocol/document version, timer, worker, scheduler, public override, acceptance
limit or production recovery gate changed. Existing heartbeat/profile/result
deadlines are checked after preparation. At most one stored value and one candidate
exist; transfer and ordinary destruction use the existing owned output/memory scope.

## Verification

All 323 selected portable checks pass on each of Linux GCC 13, Windows GCC 15 and
v141_xp: 969 total. Both legacy PE checks pass on the modern Windows host; this does
not qualify XP or another historical runtime. Profile revisions are 63, 37 and 28.
Shared construction compiles on all three toolchains. Native preparation/adoption
is currently exercised on Linux, alongside the following passing families:

| Family | Cases |
|---|---:|
| PREPARED-EDITOR | 12 |
| FRONTEND-PREPARED-EDITOR | 7 |
| FRONTEND-RECOVERY | 14 |
| RECOVERY-LIMITS | 6 |
| EDITOR-REPLY-LIFECYCLE | 11 |
| FRONTEND-PHASE-FAILURE | 2 |
| INSTALLED-RECOVERY | 14 |
| INSTALLED-EDITOR | 15 |
| INSTALLED-SETTINGS | 12 |
| EDITOR-RECOVERY | 14 |
| EDITOR-FORM | 20 |
| IMAGE-ERASURE | 3 |

The 12 prepared component cases build on another joined thread, mutate original
input copies, adopt into real GTK controls and retain the original reply lifecycle
expectations; null ownership is refused. Seven backend cases verify one consumption,
copied/stale identity refusal, repeated reloads, pending writes, policy withdrawal,
controller restart and shutdown. The native scene-image component check also passes.
Original installed/recovery/editor/settings/erasure observers retain their exact
stored-byte, private-erasure, process-exit and operation-deadline expectations.

The [checkpoint](checkpoints/prepared-editor.json) binds source/artifact attempts,
fixed inputs and verified native archives. It references the preceding phase
checkpoint as the baseline; that committed source and its archived binaries remain
available. Failed timing attempts are preserved. Raw records and machine bindings
remain local ignored out/ content; a new checkout regenerates its own evidence.

Specification generation and validation pass for 664 inventory files,
51 schemas and 183 fixtures. These checks validate specification
structure separately from the executed product checks above.

## Measured result

The fixed phase experiment observes the following per-case maxima:

| Case | Earlier editor construction (ms) | Current construction (ms) | Current reply settlement (ms) |
|---|---:|---:|---:|
| MAX-WIDGETS | 156.109 | 104.509 | 36.619 |
| MAX-SCENE | 194.743 | 78.249 | 38.028 |
| MAX-RECORD | 176.866 | 78.333 | 35.760 |

These measurements support moving draft construction away from GTK. They do not
qualify the remaining native construction, painting or history/edit callbacks.
Nested phase durations overlap. The ordinary GUI run, without phase attribution,
retains the fixed seven-case outcomes:

| Case | Result | Maximum tick work (ms) | Maximum excess delay (ms) |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 121.724 | 173.368 |
| MAX-SCENE | fail | 95.989 | 174.557 |
| MAX-RECORD | fail | 96.560 | 223.095 |
| MAX-COMMAND-REJECT | pass | 29.888 | 7.335 |
| OVER-RECORD-REJECT | pass | 30.592 | 6.974 |
| CLOSE-PREPARING | pass | 30.727 | 1.917 |
| POLICY | fail | 38.134 | 139.806 |

Maximum-scene and maximum-record tick work now fit the 100 ms bound in this run,
but excess delay still fails. Maximum-widget work also remains over the bound.
The policy case still fails excess delay while its private erasure stays inside
200 ms. Preserve these failures; production recovery remains disabled.

## Next step

Attribute remaining native preview/layout construction and history/edit callbacks
without changing the fixed oracle. Inspect whether initial layout resolution paints
pixels that the first GTK draw immediately recomputes; this is a source-derived
hypothesis requiring an independent trace before changing initial readiness.
Any prepared edit must bind the current draft, policy, resources and topology and
refuse stale consumption. Native inspector, telemetry/desktop integration, other
platform adapters and all five complete 0.1.0 editions remain required. W-11 stays
in progress; this checkpoint is not release qualification.
