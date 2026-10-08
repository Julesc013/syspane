---
type: "SysPane Work Record"
title: "Resource-aware settings checkpoint"
description: "Exact selected resources survive native edits, policy changes and restart."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T02:53:39Z"}
sp_id: "SP-SETTINGS-RESOURCES-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-SETTINGS-RESOURCES", "SP-NATIVE-SETTINGS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Resource-aware settings checkpoint

Source baseline: `252647623e2d56cbc6f2797fb9325d788d9a21d5`. The
[package](packages/w-11-settings-resources.md) continues admitted W-11. Existing
schemas, fixtures and wire contracts remain unchanged. W-11 and every complete
desktop edition remain in progress.

SettingsDraft and SettingsForm now accept an optional trusted SettingsResources
context: immutable catalog, exact package/preset selection and adapter capabilities.
The host prepares this before entering the UI owner, from the admitted generation.
Settings-only edits retain that selection in command 0.3, preserving scene 0.3
text/table/chart/image content exactly. Resource-free scene 0.2 retains command 0.2.
Bare scene 0.3 and dropping an already-required context on reload are rejected.

Setting edits resolve resources through the existing catalog. Valid themes in the
closure work; a missing effective theme rejects atomically. An explicit scene theme
override remains intact when the requested default changes. Accepted and draft
resource snapshots follow their corresponding documents through Preview, Revert,
commit and reconciliation. Only an explicit valid reload can replace selection.

Existing setting, content.select and required-resource capability checks govern
editing/submission. Readable settings remain inspectable when a required editing
capability is denied. Disclosure revocation clears catalog, resource and document
references and native values. Regrant cannot restore them; a fresh complete snapshot
is required. The existing worker independently rechecks policy before publication.
Durable storage remains distinct from pending activation and unconfirmed visibility.

## Evidence and preserved failures

`out/evidence/w-11-settings-resources-attempts.json` binds exact source
archives, commands, artifacts and CTest logs. The six new portable families cover
selection/version, themes and overrides, capability denial, atomic reload/reference
release, reconciliation and required-context boundaries. Existing settings, authored,
policy and component checks remain applicable on all three development profiles.
Historical-toolset execution on contemporary Windows is not historical OS qualification.
All 58 affected entries pass on each profile. Twenty-two configure/build/test
attempts and two complete eighteen-mode native reports are preserved with their
exact inputs.

The independent native settings runner passes all eighteen modes: the eleven prior
modes plus resource save/reopen, theme change, invalid theme, permission change,
disclosure revocation, controller restart and a wrong-selection control. The fixture
bootstraps a coherent resource generation through the actual transaction API; later
resource requests use stored packages, with import fallback explicitly unavailable.
Reopen reconstructs the catalog from storage under a fresh controller epoch. Final
review corrected the reopen fixture's reused epoch; all three affected suites and
the native trace passed again against the corrected source. The observer reads actual GTK controls,
uses XTest keys and independently checks selected document hashes, resource-index
selection/theme pins and every manifest/asset byte, including a valid PNG.

The wrong-selection control substitutes another valid preset/closure in the native
request owner while the UI requested the original selection. The committed settings
look identical; the independent resource-index comparison detects the wrong pin.
Original retained-value and premature-saved controls remain required and pass their
positive detection checks. Revocation retains the original 200 ms observation bound.
Reconciliation creates no duplicate revision or selecting-record replacement.

The first compile failed strict indentation checks in the fixture's hex decoder;
splitting the statements fixed it without changing data or compiler policy. The
first reference-release test retained a catalog in its own malformed-reload context,
so its weak reference correctly stayed alive. Releasing that test-owned reference
isolates the draft's ownership and proves revocation drops it. Both original failures
and source archives remain preserved; expected lifecycle behavior was not relaxed.

The package, literal expected values and original scene/theme/PNG bytes were archived
before implementation. Exact package serialization/pins and their independent Python
generator were archived after production draft edits began but before resource tests
first ran; this is not claimed as pre-implementation pin preparation. The native
observer and fixture source were archived before first native execution. All fixed
JSON values, source asset bytes and generated resource fixture bytes remain unchanged.
The package clarified requested default versus effective scene override before those
paths were implemented. Screenshots are supporting observations, not pixel or human
accessibility qualification.

Ordinary build/workspace commands retain the 6 GiB allocation. Only 27 byte-identical
committed source-archive duplicates were reclaimed from owned output; the committed
copies remain. Specification/tool checks and the machine handoff record exact final
counts, evidence hashes and the existing Windows symlink skips.

## Next admitted boundary

Close and implement W-10's shared editing draft and typed operations against the
same authored/resource contract: exact scene identities, undo/redo, local previews,
atomic Apply, Cancel, conflicts and pending/unknown results. Connect a native
interactive surface with keyboard alternatives and the already tested independent
escape owner before installed desktop routing. Preserve current settings/inspector
semantics and reuse the common transaction coordinator.

Installed inspector/settings/editor ownership, preset/import controls, inheritance
reset, clipboard/export, full localization, representative screen-reader review,
responsiveness qualification, Windows/AppKit native forms and complete packages remain
required. No complete edition, behind-icons placement, historical OS support or
release publication is qualified by this owned component experiment.
