---
type: "SysPane Work Package"
title: "Native widget content and scene-theme properties"
description: "Expose existing table, chart, image and theme contracts through a bounded native buffer and the shared editor draft."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T06:30:00Z"}
sp_id: "SP-W10-CONTENT-PROPERTIES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-SNAP", "SP-W09-SCENE-CONTENT", "SP-W09-SCENE-IMAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native widget content and scene-theme properties

Continue W-10 through EditorDraft and existing WidgetContentEdit/SceneThemeEdit.
Preserve all existing scene, command, resource, renderer, policy and storage
contracts. This package adds a portable input projection and a native content
dialog, not another authored-state or transaction owner.

## Editable meaning

Tables expose each existing column's source field and editable plain label.
Changing the selected column first retains its buffered label. Move up/down
reorders a binding and its label together, never separates source from label.
The complete permutation contains every original column exactly once. It cannot
add, remove or reinterpret selectors. All 1..256 existing columns are representable,
including multiline labels. Binding creation and new column sources remain the
following binding-authoring boundary.

Charts expose window_ms, max_points, linear/step interpolation, auto/fixed axis,
include_zero and fixed minimum/maximum. Existing content limits and semantics
apply. Auto serialization contains only mode/include_zero; fixed contains only
mode/minimum/maximum. Inactive fields are retained only in the open dialog buffer;
they neither validate nor enter the scene until that axis mode is selected.

Images expose exact asset choice, alternative text, preferred width/height and
contain/cover/stretch fit. Choices enumerate image/png, image/jpeg and image/svg+xml
assets within the selected immutable resource closure. Choice identity includes
manifest pin, canonical path and asset digest; labels identify package/version and
path. Never infer resources from names, load a source directory or import a file.
Enumeration obeys the existing 64-package/1024-total-asset catalog limits. Preserve
the current exact asset selection; an unknown or ambiguous choice rejects.

Scene theme offers Inherit settings (null) and admitted theme IDs. Show human theme
names with identity where needed; retain exact ID independently of display order.
Multiple versions of an ID remain subject to the existing resolver's explicit-pin
and ambiguity rules. Set content revalidates the candidate against that resolver
and current policy, without choosing a different version or silently falling back.

Text body remains available through the existing basic property field. Value,
status and group have no editable content members in scene 0.3. Their bindings
are not changed by this dialog. No implicit scene 0.2 migration is admitted.
The scene theme remains editable even when no widget is selected.

## Inputs, buffering and atomicity

Use shared strict conversion functions. Unsigned integers require canonical
decimal digits without signs, whitespace, leading zeros or exponent. Numeric
dimensions/axis bounds accept signed decimal with optional fraction and optional
e/E exponent with optional sign; maximum 64 ASCII characters, locale-independent,
finite and subject to the existing schema bounds. Formatting existing numeric
values must round-trip them. Labels/alternative text use bounded private native
plain-text controls, preserving Unicode and LF under existing content validation.

Open the native Content dialog only from an editable draft with clean basic fields.
It is modal to the temporary editor and cancels any pointer gesture. It captures
the selected ID, original content/bindings, current scene theme and admitted resource
choices. Its fields and column permutation are private input buffers. No authored
mutation, preview replacement, history entry or storage occurs while typing.

Set content prepares the exact WidgetContentEdit (when applicable) and SceneThemeEdit
as one EditorDraft batch. Validate all input before execution; resource preparation
and current policy remain with the existing owner. Any invalid field, malformed
permutation, unadmitted asset/theme or policy rejection leaves scene, selection,
history and request bytes unchanged and keeps the buffer available for correction.
A successful set closes the dialog, updates the preview and creates at most one
history entry; a value-identical set creates none. Apply remains a separate durable
transaction. Cancel/close the dialog discards only its private buffer. Undo/redo
restores complete content, binding order, theme and selection through normal history.

## Lifetime and disclosure

The main editor cannot change selection, properties or submit while the modal
buffer is open. Pending/unknown/conflict/unavailable states prohibit opening it.
External policy/topology replacement, reload, disconnect and owner close cancel
the dialog and erase input buffers, resource-choice records, model strings,
errors and accessible content. Main editor recovery still belongs to the existing
independent escape owner. Closing the content dialog never asserts durable rollback.

Disclosure loss clears held native text/choice references as well as visible
controls within the existing 200-ms bound. Hide alone is insufficient. Regrant
cannot repopulate the dialog or reconstruct the erased draft; explicit reload is
required. Closed dialog fields also stay empty between sessions/selections.

## Verification and completion

Freeze this package, deterministic package bytes/pins and complete expected scenes
before production edits. Portable checks cover all content mappings, numeric syntax,
table permutation, text limits, exact asset identity, invalid atomic batches,
history, theme inheritance, request equivalence and policy/resource rejection.

Native tests use actual inputs, held accessible references, live synthetic table/
chart observations, image pixels, current-policy storage and reopen. Exercise label
and order changes, chart modes/bounds, image fit/asset/alt, theme/inheritance, invalid
fields and correction, buffer cancellation, undo/redo, Apply/reopen, request cancel,
lost acknowledgement/restart and disclosure erasure. Calibrate altered committed
content, stale preview and retained-dialog faults with positive distinguishing
observations. Existing editor/snapping/grouping/arrangement/large-command matrices
remain regression requirements. Run the affected portable selection on all three
development toolchains and preserve all attempts and exact artifact identities.

W-10 remains in progress. Binding creation/selection, new widget insertion beyond
text, responsive/flow authoring, lock/visibility/typography, clipboard authority,
recovery drafts, installed integration, full accessibility/performance and other
native adapters remain required. No complete edition or historical OS is qualified
by the owned Linux laboratory.
