---
type: "SysPane Work Record"
title: "Explicit container authoring checkpoint"
description: "Wrap and Unwrap preserve authored rules with explicit native reflow and atomic history."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T11:38:29.791582+00:00"}
sp_id: "SP-CONTAINERS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-CONTAINERS", "SP-W10-CONTAINER-PREVIEW", "SP-KEYBOARD-INPUT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Explicit container authoring checkpoint

Source baseline: `faba4663be62ff4790ea31b540d03c9f10bc2ce2`. The [package](packages/w-10-containers.md)
adds typed WrapWidgets/UnwrapWidget and native dialogs through existing draft,
layout, policy, resource, renderer and transaction owners. Existing document/wire
identities and fixed-geometry Group/Ungroup semantics remain unchanged.

Wrapping preserves every existing widget field, including fixed coordinates and
flow/response rules. The new group occupies the first selected sibling position;
children keep ownership order. Unwrap removes the container and retains children
in that position. Both intentionally reflow in the new parent. Native input exposes
all group layout kinds, ordered variants, title/priority and a clear reflow action.
Undo restores exact scene and selection. Private input is erased on cancellation,
policy/owner change and topology replacement, with the existing 200-ms bound.

The [preview recovery supplement](packages/w-10-container-preview.md) freezes a
clipped-canvas case before correcting its misleading display-absence status.
The original failure is retained. The editor now reports an unavailable preview
alongside draft/storage status and retains authored Layout and Undo recovery.
The native case restores the original scene, repairs the canvas, exercises both
history steps and verifies durable save/reopen without changing resources.

## Executed evidence

Six new portable test families cover full expected scenes, independently specified
geometry, responsive/nested/nonadjacent rules, atomic rejection, bounds, policy,
pending requests and scene 0.2. All 138 affected checks pass on each development
toolchain: Linux GCC13, contemporary Windows GCC15 and v141_xp on contemporary
Windows. These runs do not qualify historical Windows execution.

All 173 native cases pass across eleven matrices: containers 16, layout 21,
observation calibration 7, creation 17, binding 15, content 15, snap 13, group 11,
arrangement 14, editor 20 and large-command 24. Container cases operate real native
controls and compare full submitted/stored scenes, pixels, history, save/reopen,
topology/policy erasure and lost-result reconciliation. Deliberate wrong hierarchy,
retained private input and frozen preview are positively detected.

The first Unwrap pixel oracle incorrectly compared an overlapping translucent pair
with an isolated second caption. An attempted sparse-opaque check then rejected
its own arbitrary sample-count requirement. Both failures are preserved. The final
oracle derives the exact premultiplied source-over composite from the two isolated
baseline captions and the pinned theme. Every sampled color must resolve to one
alpha; unavailable/ambiguous calibration fails. All 4,480 composite pixels and
erasure at the old location are checked. The frozen scenes, geometry, deadlines
and storage expectations did not change, and no production change addressed these
oracle failures. The independent calibration and original snapshots are retained.

Records: `out/evidence/w-10-containers-attempts.json`,
`w-10-containers-native-index.json`, `w-10-containers-verification.json`,
`w-10-containers-staging.json` and `out/evidence/containers-handoff.json`.
Exact source snapshots, frozen inputs, executable identities, every attempt and
oracle corrections are preserved. Workspace cleanup removed only duplicates
verified against committed archives; the existing output limit is unchanged.

## Remaining boundary

W-10 and every complete edition remain in progress. Continue lock/visibility/
typography, clipboard authority, recovery drafts, installed controller/catalog/policy
ownership and scene-aligned entry/restoration with independent escape. Complete
accessibility/performance, earlier unrelated focus/interface failures, historical
labs and all five release gates remain open. Explicit reflow is not a claim of an
automatic appearance-preserving conversion between arbitrary responsive layouts.
