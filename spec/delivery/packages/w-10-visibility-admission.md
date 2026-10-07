---
type: "SysPane Work Package"
title: "Versioned visibility authoring and durable admission"
description: "Preserve conditional scene meaning through typed edits, negotiation and coherent recovery."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T23:00:00Z"}
sp_id: "SP-W10-VISIBILITY-ADMISSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-VISIBILITY", "SP-W10-EDIT-LOCKS", "SP-W08-LARGE-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Versioned visibility authoring and durable admission

Continue the visibility evaluator checkpoint through the existing scene, resource,
transaction and shared editor owners. This package admits authored storage and
typed draft operations. Native conditional rendering/input remain the next required
integration, with their independent pixel/accessibility/erasure acceptance intact.

## Documents, capabilities and bounds

Scene 0.5 retains every scene 0.4 meaning and adds optional widget visibility, an
exact visibility 0.1 rule. Missing means unconditional content; null is invalid.
All seven widget kinds may carry it. The entire scene stays at 256 KiB and each
rule at 64 KiB; graph, layout, content, binding and lock bounds remain unchanged.
Validate embedded rules semantically as well as structurally. Preserve every old
schema/fixture byte; unsupported versions and fields must not be silently dropped.

A scene 0.5 resource closure requires scene.content, scene.edit-locks and
scene.visibility, including when all rules/locks are absent. These indicate authored
resource understanding, not external visible activation. Policy may deny any required
capability. The existing exact package/asset closure remains bound to the candidate.

Command 0.7 retains command 0.6 bounds, cancellation, ledger and result semantics and
accepts scenes 0.2 through 0.5. Replacing a scene 0.3/0.4/0.5 requires content selection.
Command 0.7 always requires negotiation of configuration.visibility, edit-locks,
large-commands, content, scene-content and transactions, plus command-result 0.1 and
the existing 328704-byte frame floor. It is never sent on older negotiation. Servers
offer it only with an explicit visibility-capable resource provider, edit-lock support
and the existing large-command owner. Missing required dependencies reject the hello;
missing optional dependencies remove the derived feature and reject later 0.7 requests
with feature.unsupported before publication. Existing 0.2–0.6 clients keep their
behavior. Denial of configuration.visibility rejects 0.7 authorization as policy.denied.

The command body ceiling stays 327680 bytes, frame ceiling and 128 admission slots
stay unchanged, and stored identity remains the original bytes. Linux uses existing
manifest 0.3/request.json, including exact replay and reconciliation across epochs.
Storage durability never asserts renderer activation or visibility. Current policy is
rechecked before publication. Resource-free owners cannot accept a scene 0.5 closure.

## Typed local editing

SetWidgetVisibility contains 1..256 distinct existing IDs and optional rule. A present
rule sets it on every target; absence removes each own rule. Targets are validated
before adoption. A present rule on scene 0.3 or 0.4 promotes to 0.5 without changing
other values. Removal never downgrades and is a no-op if absent. Scene 0.2 rejects;
its content migration remains an explicit separate operation. Capability/current
policy checks apply even to removal/no-op. Require large command support, explicit
configuration.visibility/edit-locks and scene.visibility/edit-locks context.

Visibility is an ordinary protected edit: reject own/inherited locks and an ancestor
of an independently locked descendant. Explicit unlock followed by a rule edit is
allowed in one atomic batch. Invalid target/rule, later failure, forbidden policy,
pending request or conflict preserves scene, selection, history and redo exactly.
Identical Set is a no-op. Undo/redo restores exact rule/version through the existing
current-policy/resource checks. Apply sends command 0.7 for a scene 0.5 replacement.
Settings-only edits may retain their existing command version while preserving the
scene and its required resources; they must never drop a rule.

Locking a scene 0.5 widget must not downgrade it to 0.4. Group/Wrap create an
unconditional parent and retain every child rule. Ungroup/Unwrap of a group with an
own rule rejects editor.visibility_container; explicitly clear that rule first if
discarding the parent condition is intended. Reparenting retains the child's own
rule; the later native dialog must explain any change in inherited conditions.
Duplication retains rule bytes; entity pins are not scene IDs and are not rewritten.
Removal deliberately deletes the selected branch, including its rules. Other
properties/content/layout edits preserve rules unchanged.

## Rendering gate

The current SceneSurface must return alternative/surface.visibility_unavailable
with no frame/cache for scene 0.5 until native condition composition is implemented,
even if a trusted setup lists scene.visibility. Current policy denial keeps its
existing priority. This prevents an understood stored document from being rendered
as if its conditions did not exist. The editor may retain authored recovery/history
paths; this package does not claim WYSIWYG visibility editing.

## Verification and remaining work

Freeze new schemas, exact authored/expected scenes, commands and negative version/
type/collection cases before production changes. Shared checks cover version and
size rejection, resource/preset admission, no-op/promotion, exact undo/redo, atomic
rollback, all lock/container guards, settings-only preservation, policy/pending
states, required/optional negotiation dependencies, original-body replay and
cross-epoch reconciliation. Verify scene/layout resolution does not rewrite rules.

An owned non-root ext4 experiment must commit and independently read exact scene,
resources, request and selecting hashes. Interrupt actual processes at request,
selector_ready, selected and durable; observe held stopped/exited lifetimes and
recover coherent revision 40 or 41 as appropriate. Lost acknowledgement must reconcile
once without revision 42. Cover revoked policy and corrupt request/scene selecting
fallback without repair or invented success. No install or user desktop is involved.
Verify the native rendering gate and regress relevant storage/IPC/renderer/editor
components. Run affected and full non-native suites on all three development profiles.

Keep failures and source/artifact/environment-bound evidence in the existing owned
workspaces. Reclaim only verified committed duplicates and retain the 7 GiB maximum
and measured native growth reservation. Ordinary reversible engineering is delegated.
Historical host execution, native visibility controls/pixels/accessibility, typography,
clipboard/recovery drafts, installed ownership and all five complete release editions
remain required. Do not mark W-09/W-10 or the release complete at this checkpoint.
