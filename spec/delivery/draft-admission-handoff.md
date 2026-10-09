---
type: "SysPane Work Record"
title: "Current draft admission and preview resource handoff"
description: "Measured repeated eligibility cost, immutable resource ownership and preserved full GUI qualification."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T05:28:54.384266+00:00"}
sp_id: "SP-DRAFT-ADMISSION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-DRAFT-ADMISSION", "SP-TEXT-SESSION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Current draft admission and preview resource handoff

SettingsDraft now retains at most two optional structural-validation results for
its internally generated preview/commit eligibility commands. Mutation boundaries
clear them, including policy, reload, adopted scenes/resources, request transitions
and accepted revisions. Copies start empty. Every eligible call still constructs
and authorizes the current command and its resources. Actual begin/submission
performs full validation independently; these UI hints cannot authorize a write.
No authored data, command bytes or permission result is cached.

EditorForm now passes the draft's existing immutable ResourceSnapshot to its
SceneSurface. This avoids reconstructing a catalog and equivalent resource set.
The owner conveys lifetime only; SceneSurface still validates the full authored
binding, layout and native text backend and checks current disclosure policy.
History, reload and theme changes select the actual draft snapshot. Existing
surface erasure and retirement remain in place. No timer, worker, scheduler or
product limit changed. Clipboard behavior is unchanged: the diagnostic recovery
profile refuses clipboard before its expensive preparation path.

## Independent checks

The new portable admission expectations passed on the original Linux production code
before optimization. They cover current-policy changes, scene versions, requests,
rejected edits and valid/oversized/valid eligibility through undo/redo. The initial
negative case incorrectly assumed a 300-character title was invalid; its failure
is preserved. A numeric title supplies the corrected structural rejection case.
The final test source is identical to the passing pre-change source. Original
binaries, source inputs and measurements remain in ignored local evidence.

The owning accessor has explicit identity/lifetime tests across theme changes,
history, reload, policy loss and final release. All 322 selected portable checks
pass on Linux GCC 13, Windows GCC 15 and v141_xp: 966 checks total. Both legacy PE
checks pass on the modern host; no historical runtime support is inferred. Profile
revisions are respectively 60, 36 and 27.

All 12 selected native renderer/erasure checks, native clipboard and theme-history
families, and seven recovery families (83 named cases) pass. Source/artifact
identities, fixed input hashes, original failures and verified native archives are
indexed by the [checkpoint](checkpoints/draft-admission.json). Raw evidence stays
local; a fresh checkout runs the declared checks with its own admitted environment.

## Measurement and remaining qualification

The same fixed maximum scenes produce these submit-eligibility measurements. These
are observed costs, not cross-machine performance guarantees.

| Case | Previous repeated check (ms) | Current repeated check (ms) | Current first check (ms) |
|---|---:|---:|---:|
| MAX-WIDGETS | 37.271 | 1.259 | 37.155 |
| MAX-SCENE | 53.843 | 1.442 | 54.125 |

The diagnostic still records the old catalog/resource reconstruction stages for
comparison. The actual EditorForm no longer performs those stages; its owning
snapshot transfer is separately measured as snapshot_us. The renderer's binding,
layout and paint validation remain. The maximum-text scene retains its existing
alternative preview; its short paint is not a claim that all text fits the display.

The complete fixed GTK family records 3 passes and 4 failures:

| Case | Outcome | Maximum tick work (ms) | Maximum excess gap (ms) |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 288.5 | 162.1 |
| MAX-SCENE | fail | 183.0 | 176.8 |
| MAX-RECORD | fail | 174.0 | 174.8 |
| MAX-COMMAND-REJECT | pass | 30.0 | 5.2 |
| OVER-RECORD-REJECT | pass | 30.0 | 6.0 |
| CLOSE-PREPARING | pass | 30.2 | 2.8 |
| POLICY | fail | 36.7 | 127.9 |

MAX-WIDGETS maximum tick work increased from the previous 209.836 ms sample to
288.492 ms in this run. Reduced repeated eligibility cost does not establish a
whole-loop improvement. All three valid maximum cases completed exact Restore,
capture, Undo, Redo, Apply and accepted-draft retirement before failing timing.
POLICY erasure measured 70.483 ms against the unchanged 200 ms limit. All 32
observed native children exited; no forced native-child cleanup was recorded.

All detailed failures, timing samples, erasure results and native child observations
remain in the checkpoint. Failed observers may terminate their owned frontend;
this is not a clean-close claim for failed cases. Earlier transient Apply/controller
replacement and native timeout failures remain unexplained and preserved. Production
recovery remains disabled; the 100 ms GUI samples, 200 ms erasure and all native,
helper, storage, heartbeat, input and resource limits remain unchanged.

## Next boundary

The existing observer measures work inside Window::tick and excess delay outside
it. The largest work samples therefore require inspection of reply settlement and
profile population as well as validation; callbacks/painting outside tick appear
as delay. Current logs contain no phase attribution. Add bounded diagnostic phase
measurements without changing the oracle. In particular, check whether settling a
reply reconstructs a preview immediately before closing/repopulating that form;
this is a source-derived hypothesis, not an established cause.

Inspect remaining first-admission, history/edit, preview/layout and native-control
costs in the fixed GUI traces. Close the ownership/invalidation contract before
reusing validated scene/command proofs or moving preparation off the GUI owner.
Retain current-policy checks, exact output, atomic undo/redo and source-bound
failures. Complete qualification and production/fixture checks before enabling
recovery. W-11, native inspector, installed desktop/provider/lifecycle integration,
remaining platform adapters and all five full 0.1.0 editions remain open.
