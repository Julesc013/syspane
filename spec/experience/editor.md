---
type: "SysPane Specification"
title: "Direct desktop editing"
description: "Provide reversible WYSIWYG editing without making the passive wall an input hazard."
tags: ["experience"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-EDITOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-RENDERING", "SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Direct desktop editing

## Entry and exit

The user enters Edit Desktop through a native tray/menu command, inspector, keyboard command or the common control API. Create a temporary ordinary interactive surface aligned to the resolved scene. Keep the permanent behind-icons wall passive. The editor owns focus only for the deliberate editing session.

Selection follows scene-object identity, not row number or transient telemetry. Freeze unstable repeated-row arrangement while directly manipulating a pane, or otherwise prevent changing network data from moving the object under the pointer. Live observations can continue updating values independently.

## Operations

The [snapping package](../delivery/packages/w-10-snap.md) defines grid/alignment
projection, deterministic candidate order, native snapshot ownership and transient
guide erasure. It extends fixed-base pointer gestures; arrows and numeric fields
remain precise, unsnapped alternatives. Native snapping preferences are session
state, not authored scene content or a separate mutation path.

The [grouping package](../delivery/packages/w-10-group.md) defines exact
group/ungroup geometry, ownership and drawing order, atomic selection/history,
containment rejection and native eligibility. Responsive container and flowing
child transformations remain required; this checkpoint does not close all W-10.

The [fixed-base arrangement package](../delivery/packages/w-10-arrange.md) defines
exact alignment/spacing arithmetic, scope, rejection and native geometry checks.
It is part of W-10; remaining responsive authoring and other operations below stay
required. Shared draft submission also supports explicitly negotiated command 0.5
under the [complete-scene contract](../delivery/packages/w-08-large-commands.md).

Support add/remove, drag/resize, multi-selection, keyboard movement, snap/grid/guides, align/distribute, group/ungroup, duplicate, copy/paste, lock, monitor assignment, data binding, column choice, chart choice, typography, theme and conditional visibility. Each operation is a typed command; the editor has no private mutation path.

Property panels provide precise numeric entry and accessible alternatives to gestures. Common operations are possible directly on the desktop, not solely in a detached configuration file. The native settings application is still available for detailed policy/source/history controls.

## Working revision

Begin with an explicit scene/settings revision and create a draft. Preview changes are local to that editing session until Apply. Apply validates and commits a transaction; Cancel restores the exact accepted document and removes the editor. Undo/redo modifies reversible authored state, not physical events or diagnostic probes.

Record a recovery draft separately from the last working scene. Crash recovery offers restoration but never automatically activates an unvalidated off-screen or input-blocking layout. The tray/menu application can always exit edit mode and restore a known working scene. A timeout is optional policy, not an unnoticed destructive action.

## Conflicts and topology

A concurrent CLI/API/config edit creates a conflict against the expected revision. Rebase disjoint changes deliberately or explain conflicting fields. An organization policy update is re-evaluated before commit and can reject a now-forbidden widget/source.

Removing a monitor during editing preserves the authored monitor association and relocates the temporary editor safely. Work areas and exclusion regions are shown in preview. Coordinates, IDs and bindings are validated; copy/paste imports never execute scripts or grant provider privileges.

## Acceptance

Test mouse and keyboard equivalence, repeated Apply, Cancel after many operations, undo/redo order, concurrent edits, crash/restart, monitor removal, long text, theme changes, stale values, accessibility and safe exit. The same transaction fixture applied by editor and CLI must produce the same authored document, apart from declared operation metadata.

## Portable authoring and role constraints

Edit authored hierarchy, layout variants and selectors from [scene bindings](scene-bindings.md).
Apply through the existing versioned `scene.replace`: command 0.2 for resource-free
scene 0.2, command 0.3 for resource-backed scene 0.2, and command 0.4 for scene 0.3.
The [shared draft package](../delivery/packages/w-10-editor-draft.md) defines typed
local operations and history; fine-grained wire operations remain unadmitted.
Telemetry changes do not move the selected item; missing monitors retain
intent. Cancellation/crash releases any input-blocking editing surface. Saver scene
editing is an unlocked interactive role, separate from a read-only saver or preview.

Emergency release is distinct from a successful Cancel transaction: it removes the
transient input owner without committing a draft or asserting rollback completion.
An independent recovery owner must confirm that the obstructing native lifetime
ended before reporting release or admitting a replacement. Its escape route must
be available before editor admission. The [X11 lifetime experiment](../delivery/packages/w-25-editor-exit.md)
tests this prerequisite. The [native editor package](../delivery/packages/w-10-native-editor.md)
connects the shared draft, real GTK controls, scene pixels and stored transactions
to that independent owner in a private laboratory. It covers fixed-base gestures,
keyboard editing, buffered properties, policy erasure and frozen-editor release.
Installed desktop entry/restoration and the complete editor remain acceptance gates.
