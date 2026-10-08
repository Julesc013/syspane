---
type: "SysPane Work Package"
title: "Atomic theme resource history and Apply"
description: "Bounded shared resources, reversible local fonts and exact durable command generation."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T04:09:11.274136+00:00"}
sp_id: "SP-W10-THEME-HISTORY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-THEME-COMMANDS", "SP-W10-EDITOR-DRAFT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Atomic theme resource history and Apply

Connect the existing shared editor/settings draft owners to command 0.8. Preserve
legacy behavior and the current renderer admission gate. This package implements
the resource/history/transaction boundary; native font controls and their independent
pixels/accessibility/erasure integration remain the next required work.

## Admission and ownership

Trusted resource contexts explicitly admit configuration.theme-overrides,
theme.typography, configuration.visibility, configuration.edit-locks, scene.content,
scene.edit-locks and scene.visibility, together with the existing large-command opt-in.
The host must establish command 0.8/result 0.1 and all wire feature dependencies
before providing that admission. Legacy contexts retain legacy selection and command
behavior. A versioned resource selection cannot load without explicit admission.

Retain immutable ResourceSet references with base/draft and each history state.
Expose resources as a borrow with the same lifetime as the scene borrow; it is
invalidated by mutation, policy, reload or close. Do not import assets on this path.
Retained-catalog derivation must share the exact already validated ContentPackage
allocations. Its public inputs are an existing ResourceSet and optional owned new
package bytes, never arbitrary aliased mutable shared pointers. New bytes still
receive all ordinary manifest/hash/closure checks. Exact existing additions reuse
their original allocation; conflicting package identity rejects. All existing content
limits remain. No original images/base packages are copied per history entry.

## Local edits and history

set_theme_fonts takes a complete base font and null or a complete explicit role map.
Null removes font_roles; an empty map preserves an explicit empty map. Validate the
whole proposed theme and use the existing immutable author. Exact no-op leaves
scene, selection, resources and both history stacks unchanged. A change sets the
scene theme ID to the canonical artifact ID and adopts scene/resources as one undo
step. Settings remain unchanged. Source license, tokens, motion and extensions stay
unchanged. SceneThemeEdit may retain the current override or select/reset to a theme
in the original closure, preserving the authored null-versus-ID choice.

Use the committed source when deriving the final command, even after several local
font edits. A draft whose theme cannot be derived from that source by font changes
alone rejects atomically; choosing a different base theme must first be committed
before editing its fonts. This is the existing command 0.8 source contract, not an
implicit reinterpretation of that wire version. Ordinary edits after font changes
retain the same resource selection. A return to the exact accepted documents and
theme reuses the accepted resource snapshot, including a legacy selection shape.

Undo/redo restores scene, selection and resource snapshot together, after current
policy, binding and command representability checks. Invalid operations preserve
both stacks and all existing state. A successful new edit clears redo. Discard
restores exact accepted documents/resources; preview preserves history; accepted
commit advances once, adopts the draft resources as baseline and clears history.
Pending/unknown requests freeze every edit/history operation and retain exact bytes.

Keep 64 entries across undo/redo and the existing 8-MiB history limit. Charge every
entry's before/after scene and selection JSON as before. Also charge once per unique
retained ResourceSet its canonical selection/theme/theme-pin/required-capability JSON,
and once per distinct ContentPackage allocation its manifest, asset paths and asset
bytes. Exclude the accepted baseline ResourceSet and its package allocations because
they are retained independently of history. Count both stacks together. Evict oldest
undo entries on a successful edit until both limits hold; the accepted baseline and
current draft remain bounded separately by existing document/content limits. Temporary
validation copies are bounded and must not become retained history. Do not increase
limits or charge shared base media once per edit.

## Commands, results and policy

When either base or draft uses selection 0.2, emit command 0.8 with the exact draft
selection, one scene.replace for changed scene and normal changed-setting operations.
theme_edit is null for retain/reset. For a changed canonical override, carry the exact
committed theme pin and final complete font/roles; reconstruct through the existing
theme-command preparer and compare the resulting selection before adoption/submission.
Keep body limits, cancellation, conflict, stale-result rejection and cross-epoch
reconciliation. An unknown result cannot release pending state or permit blind retry.
Reload accepts a coherent versioned generation only with current explicit admission.

Apply current source and destination resource policy during edit/history/submit.
Versioned drafts also require current typography/override policy even on reset.
Theme edit permission gates changed font intent; ordinary retained-theme geometry
changes do not invent new font intent. Disclosure loss, policy rollback/unavailability,
or revocation of a required versioned resource capability drops base/draft/history
resources and private request body in the same call. Regrant alone restores nothing;
fresh explicit reload is required. Terminal results after erasure cannot repopulate
the draft. Existing authority/scene/preview/commit gates remain in force.

## Fixed verification

Freeze this package and independent literal artifact/scene/command cases before
production changes. Test shared allocation identity, source lifetime, immutable input
isolation, multiple fonts, role null/empty, no-op, ordinary edits, reset, undo/redo,
discard, preview/commit and exact source-bound command bytes. Exercise history count
and byte eviction with large retained themes, preserving a valid accepted baseline.
Verify invalid input and denied history are atomic; pending, lost acknowledgement,
reconciliation, conflict, reload, policy loss and stale results retain their contracts.

Run affected/full portable suites on all three development profiles. Add an independent
owned Linux store experiment that executes commands from the actual EditorDraft,
compares frozen scene/resource bytes after save/reopen/reset and reconciles a committed
lost acknowledgement. Regress native settings/editor and theme-command storage.
Preserve every failure and source/artifact identity. Native controls, installed ownership,
other storage adapters and all five complete editions remain required.
