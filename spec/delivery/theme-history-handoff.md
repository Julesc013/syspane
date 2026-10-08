---
type: "SysPane Work Record"
title: "Atomic theme resource history checkpoint"
description: "Shared package lifetimes, bounded undo/redo and exact durable editor requests."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T05:09:49.857875+00:00"}
sp_id: "SP-THEME-HISTORY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-HISTORY", "SP-THEME-COMMANDS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Atomic theme resource history checkpoint

Baseline 5e043779be1734d13e65e533d0d4b2789a713107. The [package](packages/w-10-theme-history.md)
closes the shared editor resource boundary. Scene, selection and immutable resource
snapshots now move together through local fonts, undo/redo, discard, Preview, Apply,
unknown-result reconciliation and reload. Multiple local font edits generate one
command 0.8 against the accepted source. Exact no-ops preserve both stacks; invalid
or unrepresentable edits leave the draft unchanged. Policy/resource revocation drops
private state and retained resources; a result cannot repopulate erased state.

Retained catalog derivation shares the original internally owned immutable package
allocations and validates new owned bytes. Ordinary edits with unchanged resource
identity reuse the snapshot while rechecking candidate binding and current policy.
Acceptance replaces the context with the committed resources so obsolete overrides
are released. The 64-entry and 8-MiB history limits remain; accounting now includes
unique additional resource snapshots and package bytes, excluding the separately held
accepted baseline. Original content/package/asset limits are unchanged.

## Executed verification

The package and independent literal first/second theme artifacts, scenes, selections
and commands were frozen before production edits. Eight portable families cover
allocation identity/lifetime and input isolation; exact fonts, role null/empty and
no-op/reset/history behavior; baseline-derived commands and durable results; pending,
conflict, lost acknowledgement and reload; admission/policy/erasure; count eviction,
large-scene eviction and large-theme resource-byte eviction. Changing the base theme
before an uncommitted font edit rejects when command 0.8 cannot represent its result.

All 183 affected tests pass on each development profile. Full portable suites pass
360 Linux GCC13, 357 Windows GCC15 and 354 v141_xp checks (1071 total). The historical
toolset ran on contemporary Windows and does not qualify XP. Six native families pass:
THEME-HISTORY, THEME-COMMANDS, RESOURCE-GENERATIONS, CONTENT-COMMANDS, SETTINGS-FORM and
EDITOR-FORM. The new owned ext4 experiment drives actual EditorDraft requests through
the store, independently compares exact request/documents/artifact bytes, saves two
themes and resets, reloads from disk, reconciles a committed lost acknowledgement,
and detects a deliberately false theme report. This does not demonstrate native font
controls; existing native settings/editor checks cover their established behavior.

Failed attempts remain preserved: the new probe's copied-loop compiler warning,
the command test's reused Preview/Apply request identity, a no-op settings change
incorrectly treated as a request, combined/large-scene test deadlines and the Windows
resource-history deadline, the v141_xp fixture's null generated theme pin (including
the diagnostic run which identified it), and the native probe's accidentally reused
full-capacity bootstrap scene. The native
bootstrap now uses this package's frozen baseline and checks its exact initial state.
The generated stress fixture now copies its pin ID from an explicitly retained parsed
document, replacing the temporary JSON subscript that produced a null pin under
v141_xp; fixture schemas are checked before constructing the catalog.
Count, scene-byte and resource-byte checks are now separate; the scene-byte case retains
one authored theme while editing a large scene, and the other cases still cover 75
font replacements and 35 large-theme replacements. Redundant unchanged-resource
preparation was removed; immutable resource metadata sizes are captured with history
states instead of repeatedly serializing retained themes. Current binding/policy
validation remains. Fixed artifact expectations, history limits and the existing
test deadline were not changed.

Evidence under build-support/evidence uses prefix w-10-theme-history: attempts,
native-index, verification, staging and theme-history-handoff.json. The attempts
index retains 35 source-bound executions and original outcomes,
fixed inputs, source archives and artifact identities. All 199 baseline schema/fixture
files retain their bytes. Generated navigation, schema/fixture checks, specification
tool tests and sealed integrity accompany the handoff. Two existing Windows symlink
assertions remain skipped. Verified committed duplicate output copies were reclaimed
within the unchanged 7-GiB development allocation; cleanup receipts retain their scope.
Older duplicate source archives were also deduplicated by verified SHA-256, retaining
one identical archive and a restoration map; their result records and this checkpoint's
original attempts were preserved.

## Next admitted work

Add native base/role font controls using the existing lossless input adapter and
shared draft. Render previews from the draft's matching borrowed resource snapshot,
preserve mandatory diagnostics, and expose precise current admission/failure states.
Independently prove pixels, accessibility, null/empty role choices, undo/redo,
save/reopen, lost-result handling and private-input erasure before trusted EditorForm
typography is enabled. Preserve all existing visibility/edit-lock and recovery gates.

Installed ownership, other native/storage adapters, unresolved observation causes,
full accessibility/performance and all five complete editions remain required. W-10
and the full release goal remain in progress.
