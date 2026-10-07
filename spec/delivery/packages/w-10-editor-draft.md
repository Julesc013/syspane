---
type: "SysPane Work Package"
title: "Shared editor draft and typed local operations"
description: "Reversible scene editing through the existing authored transaction owner."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T03:05:50Z"}
sp_id: "SP-W10-EDITOR-DRAFT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-EDITOR", "SP-W11-SETTINGS-RESOURCES", "SP-W09-SCENE-CONTENT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Shared editor draft and typed local operations

The complete release instruction admits W-10 using the implemented W-08/W-09
boundaries. Implement a portable serialized EditorDraft in source/interfaces.
Reuse the settings draft's transaction, resource and result owner; do not duplicate
its ledger, persistence, reconciliation or current-policy checks. The ordinary
shared transaction API remains the only commit path. This package establishes the
draft for the native interactive editor; the native surface, independent escape
attachment, installed routing and full editor acceptance remain required.

The [arrangement extension](w-10-arrange.md) now closes fixed-base align/distribute
operations and native controls through this same owner. Its deterministic arithmetic
and geometry eligibility apply alongside the remaining authoring requirements.

## Inputs and ownership

Construction/reload takes coherent validated Authored documents, native Authority,
current Policy, producer epoch and the existing optional immutable resource context.
Preserve scene identity, schema version, all untouched fields/extensions, exact
resource selection and authored monitor intent. Never read live telemetry to change
authored order, coordinates or selection. A missing display does not rewrite intent.
Resource-backed edits use their admitted catalog; no UI import or fallback.

Selection is an ordered set of existing scene IDs, canonicalized in widgets-array
order. Reject duplicates, missing IDs or more than 256 IDs atomically. Selection
never changes authored state. Expose a const scene borrow only while available;
all borrows expire on any mutation, policy call or close and may not be retained by
the native adapter. The adapter owns its separately revocable rendered caches.

## Typed operations and atomic batches

Accept 1..128 typed local operations as one undo step. These are in-process typed
commands, not new wire operation names. Apply the ordered operations to a copy,
then validate the complete candidate and current policy/resources before adoption.
No intermediate hierarchy/content mismatch is published. Any error preserves the
scene, selection, history, active request and accepted revision exactly.

* Set widget title, display assignment, complete layout or priority using a closed
  property enum. Identity, kind, extensions and ownership cannot be patched this way.
* Set a widget's bindings and content together, with the existing kind-specific
  validator. All seven scene 0.3 kinds retain their existing meanings.
* Set the scene theme override to an ID or null; resolve the effective theme through
  the existing resource catalog. A null override resumes the requested default.
* Insert a complete widget with a fresh ID at a specified root/group-child index.
  Index is in 0..size; parent must be an existing group. Added group children must
  be empty; populate them explicitly by later insert/reparent operations.
* Remove specified disjoint subtree roots and all descendants, preserving relative
  order of surviving widgets and ownership arrays. Reject ancestor/descendant
  overlap in a single target set, duplicates, empty sets and missing targets.
* Reparent disjoint subtree roots to an existing group or the scene roots. Preserve
  their supplied target order. Index is in the destination after removing targets.
  Reject cycles. Coordinates remain authored parent-local values; a batch may
  explicitly set layouts to preserve visual positions. Never guess a transform.
* Duplicate disjoint subtrees using an exact caller-supplied old-to-new ID map for
  every cloned node. Reject missing/extra map entries, reused IDs and collisions.
  Copy all properties/extensions; rewrite only node IDs and child references.
  Insert each cloned root immediately after its original in the same owner array;
  append cloned widget records in original widgets-array order. Selection stays on
  original IDs until explicitly changed.
* Move disjoint fixed-base targets by finite DIP deltas; resize one fixed-base
  target to finite DIP dimensions. Modify only layout.base, preserving breakpoints
  and descendants. Reject non-fixed bases and schema-limit violations, without
  clamping. Pointer and keyboard adapters must call these same operations. Editing
  a responsive variant uses the explicit complete-layout property operation.

Group/ungroup can compose insert/reparent/remove in one atomic batch. This package
does not invent storage for persistent locking, conditional visibility or per-widget
typography: those still need admitted contracts and native controls. Clipboard
imports/export, snap/align/distribute gestures and complete property panels remain
required by SP-EDITOR, not implicitly completed by these primitives.

## Preview, history, Apply and Cancel

The current scene is the local preview; it writes nothing. Keep at most 64 history
entries across undo/redo and 8 MiB of their canonical scene/selection JSON bytes.
Each entry retains before/after scene and selection. Evict oldest undo entries
when a successful new edit exceeds a limit, keeping the accepted baseline separately.
A new non-no-op edit clears redo. Invalid and no-op edits preserve redo/history.
Undo/redo validates the destination under current policy/resources before moving
the cursor; denial preserves both stacks. Selection-only changes are not undo steps.
Removal prunes deleted IDs; undo restores the selection recorded before that edit.

Use existing command 0.4 for changed scene 0.3 with resource context, command 0.3
for resource-backed scene 0.2 and command 0.2 for resource-free scene 0.2. Emit one
scene.replace carrying the base revision. No fine-grained wire contract is invented.
Local validation supports the existing 256 KiB scene bound. The existing command
envelope is still 16 KiB: an oversized Apply/remote Preview rejects before admission
without discarding the valid local draft/history. Closing this envelope gap remains
a mandatory complete-editor gate; do not silently shrink the supported scene size.

A clean draft emits nothing. At most one unresolved request; freeze edit, selection,
undo/redo and discard while pending/unknown. Retain exact ticket/request/epoch through
disconnect, cancellation request and cross-epoch reconciliation. Accepted commit
advances revision once and clears history; preview preserves it. Conflict requires
explicit fresh reload, with no automatic rebase or retry. Result facts and malformed
result handling reuse the existing tested draft owner.

Discard restores the exact accepted scene, clears history and prunes selection;
it writes nothing. Native Cancel must discard and remove its surface; emergency
release merely ends the native lifetime. Close drops local state and cannot undo a
submitted transaction. The external command owner retains unresolved-request duties.
Disclosure loss drops all scene/history/selection/resource references in the same
call. Regrant alone cannot restore content; only fresh explicit reload can. Policy
rollback/reuse and unavailable policy fail closed. Permission loss for scene.replace,
preview, commit, content.select or required resources cannot be bypassed by history.

## Execution and evidence

Before implementation, preserve the package, literal operations and complete
independently prepared expected scenes in tests/editor/cases.json, together with
the unchanged resource fixture. Cover operations, batch hierarchy, invalid atomicity,
selection, undo/redo/eviction, discard, command equivalence, policy/disclosure,
conflict, lost acknowledgement/restart, stale results and the envelope limit.
Compare actual commits using Transactions, not just a serialized UI command.

Use ordinary workspace preflight/configure/build and all three development profiles.
Run editor.*, settings.*, affected configuration/policy/component cases and the
existing independent native.SETTINGS-FORM regression after changing the shared owner.
Preserve every failure and exact source/oracle/artifact identity. Native settings
regression is not evidence of a native editor. Keep W-10 in progress, then attach
this draft to the interactive surface and independently prove pixels/input, mouse/
keyboard equivalence, topology changes and safe exit before installed admission.
