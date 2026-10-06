---
type: "SysPane Work Package"
title: "Pinned content and preset preview"
description: "Resolve immutable content bytes into a validated authored preview without granting installation or activation."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:00:00Z"}
sp_id: "SP-W08-CONTENT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PRESETS", "SP-CONFIG-RESOLUTION", "SP-W08-AUTHORED", "SP-PERSISTENCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Pinned content and preset preview

W-08 now admits a shared content resolver in `source/configuration/`, a bounded
Linux directory reader in `source/platform/`, and an independent native exercise.
The output is an explicit preview candidate using existing command 0.2, settings
0.1 and scene 0.2. This is not installation, a new settings engine or permission to
publish external resources through the current settings/scene-only store.

## Identity and byte ownership

Use content-package, preset and theme 0.1 schemas compiled into the existing
authored validator. Package identity is `(package_id, version, SHA256(manifest
bytes))`. Dependency pins name this identity. Preset references instead name
`(document identity, package version, SHA256(entry bytes))`. The entry is exactly
`preset.json`, `scene.json` or `theme.json` according to kind, with media type
`application/json`. Document identity is preset_id, scene_id or theme_id. A preset's
own version equals its package version; scene schema version is independent.
Selection supplies both the root package pin and its preset document pin; matching
only the document bytes cannot substitute a changed dependency manifest.
Widget packages remain unadmitted until their executable/data boundary is closed.

Hash exact input bytes, including whitespace. JSON documents may end in whitespace;
remove only JSON whitespace for parsing, never hashing. Duplicate keys, BOMs,
non-finite numbers and existing parser depth/node violations fail. Retain owned
immutable bytes for the complete selected closure: subsequent filesystem changes
cannot alter an already prepared result. No URL fetch or global fallback is allowed.

All supplied packages are validated before use. At most 64 packages, 1024 assets
and 64 MiB of asset bytes in total; each manifest at most 64 KiB, each asset at most
16 MiB and each JSON asset at most 256 KiB. Declared byte counts, total and SHA256
must match. No undeclared or missing assets. Paths are ASCII relative slash paths,
at most 512 bytes, at most 16 segments; no empty/dot/dot-dot segment, leading slash,
backslash, colon, Windows reserved basename, trailing dot/space, ASCII case alias
or file/directory prefix conflict. `manifest.json` is reserved, case-insensitively.
Non-JSON assets remain opaque verified bytes: no media decoder or script executes.

Package id/version pairs are unique in a catalog. Dependency IDs are unique within
each manifest; missing pins, digest mismatch, cycles and dependency depth above
eight packages fail. Preset references must resolve within their owning package's
transitive pinned closure, never a sibling supplied incidentally. Repeated document
identity/version pairs in the selected closure are rejected, even with equal bytes.
Required capabilities must be supplied by the caller's trusted capability set and
not denied by current policy. Missing optional capabilities are reported as sorted
unique IDs; importing never grants them. Manifest and preset requirements both apply.

## Deterministic preview

Resolve at most eight presets from root parent to selected leaf. Settings arrays
contain no duplicate paths; validate each layer's values against the existing
command constraints even if a later layer replaces the value. The most derived
specified scalar wins. Missing paths retain the caller's baseline. This is a
materialized application preview, not persistence of user override provenance or
the complete multi-layer/reset/three-way-update engine.

Each preset's scene and non-null theme pin is validated, including parent presets
whose scene is replaced. The selected leaf scene replaces its parent's scene. A
non-null leaf theme explicitly overrides the candidate scene's theme_id. A null
leaf theme means no preset theme override; it does not inherit a parent theme or
delete the scene's own choice. The scene's null theme_id inherits the effective
display.theme_id setting. Resolve that final ID to exactly one theme in the leaf
closure; no implicit built-in fallback or newest-version selection. An explicit
leaf pin disambiguates that same final theme identity. Theme tokens are preserved;
actual OS/policy motion resolution belongs to activation.

Normalize only the materialized candidate scene revision to the caller's current
authored revision. Preserve the original pinned scene bytes and revision separately.
Emit settings.set operations in ASCII path order, then one scene.replace; set
intent preview, exact current policy generation and caller request ID. The existing
16 KiB command ceiling still applies; a larger scene cannot use this command profile
even if its package document satisfies the separate 256 KiB document limit. Validate and
authorize with prepare_authored. Return the command, candidate, selected theme,
sorted package pins, parent-to-leaf preset pins, missing optional capabilities and
the winning preset pin per changed setting. No storage/activation/visibility success
is claimed. Failure returns no partial plan and leaves input state unchanged.

For example, parent sampling.resources_ms=1000 and leaf=1500 yield 1500 from the
leaf. Parent display.enabled=false remains false if absent in the leaf. A scene
authored at revision 3 previews at caller revision 40; its pinned bytes remain at 3.
A denied settings.preview, forced conflicting setting, unavailable policy or saver
settings role attempting scene.replace refuses the entire preview.

## Native input and completion

The Linux adapter accepts explicit absolute uncompressed package directories,
walking every component without following links. Package directories and descendants
must belong to the effective user with no group/other or special mode bits. Files
must be regular, single-link, non-executable and size bounded. Read through held
directory descriptors with no-follow/nonblocking opens. Reject undeclared entries,
links, special files and file identity/size/time changes observed during reading.
The manifest is pinned by the caller's selection; the copied bytes, not a later
path lookup, supply resolution. Concurrent changes are never evidence of a durable
filesystem snapshot. Archive extraction and non-Linux native readers remain open.

Acceptance covers independently computed hashes, exact composed results/provenance,
pin scope, parent/dependency bounds, schema/path/size/digest/capability failures,
policy/role refusal and unchanged input state. Native cases exercise actual private
files, symlinks, hardlinks, permissions, special files, undeclared entries and
snapshot ownership. Use ordinary bounded configure/build/test commands on all three
development profiles. Historical-toolset host checks are not historical runtime
qualification. Preserve failures, source identities and the next boundary: durable
resource closure, installed ownership, native controls and renderer activation.
