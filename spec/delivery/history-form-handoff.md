---
type: "SysPane Handoff"
title: "Prepared history form handoff"
description: "Experimental native history adoption and capture coexistence are implemented; GUI qualification remains open."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T08:57:53.435058+00:00"}
sp_id: "SP-HISTORY-FORM-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-HISTORY-FORM", "SP-HISTORY-WORKER-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared history form handoff

The existing experimental frontend now passes its native history factory into
EditorForm. Undo/Redo prepares on the existing worker, while the current form owns
adoption and preview refresh. The [package](packages/w-11-history-form.md) defines
the interaction; the [checkpoint](checkpoints/history-form.json) records source and
artifact identities, complete archived observations, fixed-oracle reviews and failures.

Pending history disables conflicting actions, native fields, selection and Apply.
Programmatic commands and input callbacks also refuse conflicting changes. Cancel
session and Reload remain available. The form keeps the task until stopped and
rejects obsolete completion after reload, topology/policy change, disconnect, recovery
rebind or close. Cancel waits for task acknowledgment before dispatching exit.
Successful adoption uses the exact current draft and the original native preview
validation/geometry path. There is no additional worker, timer or request queue.

EditorRecoverySession now suspends obsolete pure capture without relinquishing its
binding, durable ownership or admitted storage operation. Apply stays unavailable
during the pause. Resume captures the final authoritative draft and waits for the
cancelled preparation to release its slot. Invalidation, retirement and close clear
the pause without restoring permission or automatic retention. The component cases
verify exact retained scenes and unchanged write counts across these transitions.

The factory is enabled through the existing experimental frontend admission only.
Production still uses synchronous history and keeps recovery disabled. No production
environment override, privileged operation or release publication was introduced.

## Executed verification

All 17 native form cases pass against actual GTK controls, actual detached work and
controlled task completion. They verify exact serialized scenes/selection, pending
input refusal, factory/run failure, queued/ready/running cancellation, reload,
topology/policy/disconnect/close, late publication and recovery capture coexistence.
The real worker separately passes its 13 kernel-observed ownership cases. The
13 passing native families total 157 named cases, plus SCENE-IMAGE; the
checkpoint lists the standalone, installed, recovery, reply and initial-input runs.
All nine unchanged portable history checks and both component checks pass on each
of the three development profiles: 27 history checks and six component checks.
Native changes were rebuilt on Linux; portable Windows binaries were unchanged and
rerun. Profile revisions are Linux 67, Windows GCC 38 and v141_xp 29.

The first form run exposed reentrant text restoration inside GTK's change callback.
That invalidated an iterator. Pending field edits are now stopped at insert/delete
signals before buffer mutation, and the new native mode rejects GTK warnings.
The same attempt exposed an incorrect new disconnect expectation: existing
SettingsDraft changes to unknown only when a request is active. The corrected case
preserves local authoring and checks the exact unchanged second scene after history
cancellation. The unchanged source comparison, original oracle bytes and failure
are retained. A fixture-only aggregate-order correction also preserves the original
form exercise. Removing the new test-mode additions restores the prior frozen
initial-input/reply driver bytes exactly; their original expectations are unchanged.

## Ordinary GUI qualification

The original installed GUI timing/erasure exercise ran unchanged after integration.
It still has 4 failing cases. These are qualification failures, not passes
or evidence that a complete native edition is ready. Maximum observed values are
microseconds; the existing work/delay limit remains 100000 microseconds.

| Case | Outcome | Maximum work | Maximum excess delay |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 78446 | 135382 |
| MAX-SCENE | fail | 95689 | 135758 |
| MAX-RECORD | fail | 96276 | 143017 |
| MAX-COMMAND-REJECT | pass | 25571 | 5615 |
| OVER-RECORD-REJECT | pass | 32788 | 6863 |
| CLOSE-PREPARING | pass | 25532 | 5666 |
| POLICY | fail | 36218 | 134288 |

The checkpoint retains every case's exact failure, timing samples, erasure result
and source/artifact binding. Earlier GUI failures remain preserved independently.
The active workspace allowance remains 8 GiB with unchanged action reservations;
completed native attempts were archived, byte-verified and removed only from their
owned duplicate output directories. Retained archives are measured separately.

## Next boundary

Inspect the failed ordinary GUI case records before selecting the next repair.
Distinguish authored preparation from current native preview validation, composition,
painting and event-loop scheduling. Preserve the original timing and erasure oracle;
diagnostic timing alone cannot qualify a production path. Keep production recovery
and asynchronous history gated until their required ordinary qualification passes.

General asynchronous authoring and native preview handoff remain required, alongside
the native inspector, telemetry/desktop integration, lifecycle, other platform
adapters and all five full 0.1.0 editions. W-11 remains in progress.
