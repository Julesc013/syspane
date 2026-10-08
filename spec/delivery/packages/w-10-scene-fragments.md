---
type: "SysPane Work Package"
title: "Bounded authored scene fragments"
description: "Portable copy ownership and atomic paste without implicit package import."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T06:21:41.184029+00:00"}
sp_id: "SP-W10-SCENE-FRAGMENTS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-EDITOR-DRAFT", "SP-W10-THEME-HISTORY", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded authored scene fragments

Implement the shared copy/paste boundary in EditorDraft before enabling native
clipboard controls. This package does not qualify an OS clipboard adapter or
complete W-10. Native transfers, recovery drafts and installed ownership remain
required. Reuse existing scene validation, resource snapshots, history and commit
owners. Do not introduce a second import pipeline or persist clipboard contents.

## Format and exact meaning

A fragment is UTF-8 JSON, at most 262144 bytes before parsing, with exactly these
five members: format="syspane.scene-fragment", schema_version="0.1.0",
scene_version="0.3.0", "0.4.0" or "0.5.0", roots, and widgets. No BOM, duplicate
keys, invalid UTF-8, nonfinite numbers or unknown envelope members are accepted.
Existing bounded JSON parsing (32 container levels and 16384 nodes) applies.
Trailing JSON whitespace is allowed. The writer emits compact sorted-key JSON,
without trailing whitespace. The fragment is a forest with 1..256 widgets and at
least one root, using the specified scene version's exact widget schema and
ownership/depth rules. Validate it as a scene with scene_id="scene:fragment",
revision="0", theme_id=null; that synthetic scene also fits the 256 KiB limit.

Copy uses the current canonical selection. Drop a selected descendant when an
ancestor is selected; reject an empty selection. Roots and widget records retain
their relative source widgets-array order. Include complete selected subtrees,
preserving every widget field, extension, direct binding, selector, resource pin,
layout variant, display intent, own lock and own visibility rule. Copy is read-only:
locks do not prevent copying. Ancestor properties outside the fragment are not
inherited into it. In particular, selecting a child alone does not copy its parent's
lock, condition, clipping or transform. Coordinates remain authored parent-local
values. Opaque extension strings are not interpreted as references.

No scene identity/revision/theme, settings, installation binding map, telemetry,
history, package bytes, observations, private modal text or authority enters this
format. Direct authored bindings are copied literally and can be unresolved in a
different environment; no name-based rebinding is implied. All fragment contents,
including extension values and resource identifiers, are classified sensitive.

## Admission and ownership

The trusted resource context must explicitly admit editor.clipboard; current
available policy must grant sensitive disclosure on the clipboard channel to the
authenticated desktop or console role. Denied editor.clipboard, denied clipboard
projection, missing resource permission, unavailable draft, pending request or
conflict prevents copy, serving bytes and paste. Reuse current scene-edit authority
checks. Legacy context/default construction does not enable this feature.

EditorDraft owns at most one serialized copied snapshot. Copy replaces it only
after full validation succeeds; a failed copy preserves the previous snapshot.
Ordinary local edits/selection changes do not rewrite the copied snapshot. A fresh
permission check is mandatory each time clipboard bytes are borrowed. The borrow
expires at the next draft operation. Do not cache it in an adapter or retain it
across an event-loop turn; each outgoing chunk must obtain a fresh borrow.

Erase the owned snapshot on every policy update (including regrant or rejected
generation), disconnect, successful reload/discard, successful request admission,
close and explicit ownership loss. A denied read erases before refusing. Regrant
does not recreate old data. Logical erasure removes all accessible owned values;
this is not a guarantee of allocator memory scrubbing. No clipboard manager or
other recipient can be forced to forget bytes already delivered.

## Paste and failure atomicity

PasteWidgets is one typed local operation containing bounded fragment bytes, an
exact old-to-new ID map, optional destination parent and insertion index. Require a
fresh valid destination ID for every fragment widget: no omissions, extras,
duplicates or collision with any existing destination ID. Rewrite only widget IDs
and children references. Root references use that same map. Append widget records
in fragment order; insert roots in fragment-root order at the explicit destination
index. Parent must be an existing unlocked group, including inherited locks;
index must be in 0..destination-size. Existing protected siblings do not prevent
insertion. Pasted own locks and conditions remain intact. Selection becomes the
pasted roots in destination widgets-array order as part of the same history step.

Destination scene identity, revision, theme and extensions remain unchanged. Its
scene version becomes the higher of its current version and scene_version, within
0.3..0.5; no downgrade or implicit 0.2 content migration is allowed. Required
configuration/scene capabilities and current policy must permit the resulting
version. Preserve parent-local coordinates, responsive rules and authored display
intent exactly; no offsets, snapping, placement guesses or display substitution.

Use only the destination's admitted immutable resources. Exact pins must resolve
there, or the entire edit fails. Never fetch a URL, open a referenced path, import
a package, change the destination theme or grant provider/export authority. The
existing scene 256 KiB, 256-widget, depth-16 and history 64-entry/8-MiB limits apply.
One PasteWidgets can insert more than 128 nodes without bypassing the 128-operation
batch bound. Every failed edit preserves scene, selection, history, resource
identity, accepted revision and pending request. Apply uses existing commands and
durable reconciliation, not a clipboard-specific persistence operation.

## Verification and native admission gate

Freeze this package and independently constructed complete fragment/pasted scenes
before production edits. Portable tests must cover selection overlap/order,
round-trip of every kind, extensions and resource pins, nested locks/conditions,
explicit placement, version promotion, malformed/cyclic/deep/oversized input,
mapping collisions, missing resources, atomic multi-operation failure, history,
save/reconcile, all permission gates and each erasure boundary. Include positive
witnesses that wrong ID remapping and leaked scene metadata fail fixed expectations.
Run affected and full portable suites on all three development profiles.

A later native package must expose explicit Copy/Paste actions and the custom
target application/vnd.syspane.scene-fragment+json, never automatic PRIMARY or
generic text export. Close its bounded asynchronous transfer, chunk, timeout,
late-callback, cancellation and policy-change contracts before implementation.
Its native reader must enforce the byte ceiling before accepting or allocating an
unbounded peer payload, including incremental transfers. Freeze independent native
requester/owner cases and prove that revocation prevents future serving and paste,
foreign clipboard ownership is preserved, and save/reopen is exact. Until that
evidence passes, existing private text export and native clipboard actions stay
disabled. None of these checks qualify a complete edition or a historical OS.
