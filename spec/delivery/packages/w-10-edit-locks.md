---
type: "SysPane Work Package"
title: "Persistent native editor locks"
description: "Versioned authored locks, explicit unlock, protected direct editing and durable native verification."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T12:20:00Z"}
sp_id: "SP-W10-EDIT-LOCKS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-CONTAINERS", "SP-W08-LARGE-COMMANDS", "SP-W09-SCENE-CONTENT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Persistent native editor locks

Continue W-10 with an authored editing guard, not a disclosure or authorization
mechanism. A lock prevents accidental local edits; it does not freeze telemetry,
responsive layout, theme measurement or topology. Policy remains authoritative.
An explicitly authorized complete-scene replacement can change locks through the
common API. A lock cannot grant access or conceal mandatory status information.

## Document and command admission

Scene 0.4 copies all scene 0.3 semantics and adds optional boolean edit_locked to
each widget. Missing and false mean unlocked; true means independently locked.
A group lock applies to descendants. Old scene schemas remain byte-identical and
reject the new version. Content resources require scene.content and scene.edit-locks
for scene 0.4, even when every lock is false or absent. Rendering remains identical;
locking has no passive wall hit-testing or visibility effect.

Command 0.6 retains command 0.5 limits, cancellation, replay and durable request
identity, and accepts scene 0.2, 0.3 and 0.4. Scene 0.3/0.4 replacement requires the
existing content selection. Negotiate command 0.6, configuration.edit-locks,
configuration.large-commands, configuration.content and configuration.scene-content
before using command 0.6. The server only offers edit-locks with resource support
for scene.edit-locks and a large-command owner. Missing required negotiation fails;
unsupported optional negotiation cannot admit 0.6. Existing clients retain their
existing versions, bounds and outcomes. Never downgrade or discard a lock silently.

SetWidgetLocks supplies 1..256 distinct existing IDs and a boolean. Set true stores
true. Set false removes the own flag; inherited locks remain effective. It does not
rewrite descendant flags. Multiple selected ancestors/descendants may be changed
together. Validate all IDs and permissions before adoption. Setting the first true
flag explicitly promotes scene 0.3 to 0.4, preserving every other value. A false
operation on scene 0.3 is a no-op. Never implicitly promote scene 0.2. Undo restores
the prior exact scene version; unlocking a scene 0.4 object does not downgrade it.
Require negotiated editing support before either lock operation, including no-op.

## Protected operations

Selection remains possible through the canvas and authored Scene objects list.
Every ordinary operation targeting an effectively locked object rejects with
editor.locked. Operations targeting an ancestor of an independently locked object
also reject, preventing indirect removal, movement, regrouping or replacement of
the protected branch. This includes title/content edits to such a branch owner;
unlock the protected descendant before changing the owner. Ordinary operations
include properties, content, move/resize, align/distribute, duplicate, remove,
group/ungroup, wrap/unwrap and source-side reparenting.

Insertion and a reparent destination require an effectively unlocked parent;
an independently locked sibling does not prevent insertion beside it. Direct
root insertion and scene-theme changes remain allowed. Explicit SetWidgetLocks
is the only local lock exception. Undo/redo may restore recorded states across a
lock but retain ordinary current-policy/resource/pending-request checks. A batch
is sequential and atomic: explicit unlock followed by an edit is deliberate;
failed later edits roll back scene, selection, version and history together.

## Native behavior

Add one accessible editor.lock action alongside Wrap/Unwrap. With a nonempty
selection, show Unlock when all selected objects have their own true flag;
otherwise show Lock. The button changes own flags as one history entry. Indicate
own/inherited lock in accessible status. An inherited-only object can set its own
lock; clearing that flag cannot clear an ancestor. The authored list always allows
the ancestor to be selected and explicitly unlocked.

Disable ordinary mutating fields/actions for protected selections. Keep selection,
Undo/Redo, Apply, cancel/reload, insertion and scene-wide controls subject to their
existing gates. Shared command guards remain authoritative even if input is queued
before a native sensitivity change. Do not start pointer move/resize for protected
selection. Keyboard movement cannot mutate it. Cancel any gesture before toggling
a lock. Lock requires clean fields, no active modal/request/conflict and admitted
scene 0.3/0.4 support. Policy loss erases retained scene, selections and controls;
regrant alone cannot restore them. Existing erasure deadlines remain fixed.

## Verification and completion

Freeze this package, both new schemas, complete authored/expected lock scenes and
negative version/type cases before production changes. Shared tests must verify
all guard families, nested/inherited/independent locks, insertion beside a lock,
explicit unlock/edit batches, rollback, scene promotion, no-op, exact history,
policy/capability/pending rejection, all schema versions and command negotiation.
Include large envelope parsing/admission and resource-backed durable/replay checks.

An independent non-root Linux native matrix must select, lock, attempt pointer and
keyboard changes, inspect disabled native fields, unlock, move and undo/redo; compare
exact scene/pixels, unchanged storage before Apply, durable save/reopen and retained
locks. Cover nested inheritance, mixed selection, policy erasure, lost results and
deliberately wrong stored locks. Run all affected suites on three development
profiles and native editor regressions. Preserve original failures and exact
source/artifact/environment identities in the existing bounded workspaces.

This boundary closes persistent edit locks; visibility/typography, clipboard,
recovery drafts, installed ownership, full accessibility/performance, historical
laboratories and all five complete editions remain required. No privileged install
or publication is admitted. Routine implementation choices are delegated.
