---
type: "SysPane Work Package"
title: "Bounded immutable theme resource overrides"
description: "Keep one authored theme beside the original preset closure before versioned durable integration."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T03:14:48.566917+00:00"}
sp_id: "SP-W10-THEME-OVERRIDES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-THEME-AUTHORING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded immutable theme resource overrides

This package closes resource selection and replacement for saved font authoring.
The new resolver is an explicit component API; existing command schemas, provider,
store recovery and SettingsDraft continue using the legacy resolver. It does not
enable native controls or admit a new wire command. The next package must connect
this boundary to versioned command/store publication and restart/reconciliation.

## Selection and ownership

Resource selection 0.2 contains exactly schema_version (0.2.0), package, preset and
theme_override. Package/preset retain the original exact manifest/document pins.
theme_override is null or exactly {package: manifest pin, theme: document pin}.
Pins have the existing identifier, semantic-version and lowercase SHA-256 grammar.
The whole selection is at most 4096 canonical JSON bytes. Unknown fields, omitted
theme_override, another version, partial pins and an array of overrides reject.
Legacy {package,preset} retains its exact meaning and shape. The legacy resources
API rejects versioned selections. The separate theme_resources API rejects legacy
selections. No caller can infer admission from merely possessing resource bytes.

Resolve and validate the original preset dependency closure first, with all
existing pin, parent, document-ambiguity, depth and content checks. Retain that
closure byte-for-byte, including original themes and images even when an override
is active. ResourceSet owns immutable shared references to both base_packages and
the complete selected packages. Their order follows the validated catalog order;
selection/pins and exact bytes, rather than vector order, establish identity.

For a non-null override, require the exact package pin and exact theme pin to name
the same catalog entry. It must be the canonical authored theme artifact defined
by SP-W10-THEME-AUTHORING: theme 0.2, content-and-license-bound IDs, version 0.1.0,
one theme.json asset, no dependencies, exact manifest capabilities and compact
UTF-8-plus-LF bytes. Reconstruct and compare all bytes and returned fields; never
trust the mutable AuthoredTheme struct or a matching filename alone. Arbitrary
external theme packages and noncanonical copies cannot use this authoring boundary.

The effective scene/settings theme ID must equal the override's document ID.
Never silently fall back to the preset if an override is missing, damaged or does
not match the candidate. Reject a different entry with the same document ID/version
inside the union. If the exact override is already in the base closure, retain it
once. Null resolves the candidate's effective theme by the existing base rules.
Every image reference continues to resolve against the retained base closure.

The union retains all existing limits: 64 packages, 1024 assets, 64 MiB of asset
bytes, depth 8, and existing per-document/manifest bounds. The override does not
consume another preset/dependency depth. Capacity exhaustion rejects atomically;
do not discard original dependencies, evict a base theme or raise product limits.

## Replacement, reset and authority

replace_theme_resources accepts a source ResourceSet, a complete candidate Authored,
an optional complete authored artifact, current Policy and admitted capabilities.
An artifact means select it; absence means explicitly reset to base resolution.
The caller supplies the corresponding candidate theme ID. The helper never changes
settings or scenes, writes files, changes revisions or grants transaction authority.

Authorize the source first, then require configuration.theme-overrides admitted and
not denied. Validate the artifact before using its pins. Build from source.base_packages
and the one requested artifact, excluding the previous external override. A base
package ID/version collision rejects unless every manifest/asset byte is identical.
Resolve the versioned selection, validate candidate binding and authorize the entire
result before returning. Both null and non-null selections require
configuration.theme-overrides; active modern fonts additionally require
theme.typography. Original required capabilities still apply even if their theme
is no longer selected. Unavailable policy, revoked source/result capabilities,
missing images, invalid input or allocation failure returns no partial publication.

Replacement, repeated replacement and reset preserve source snapshots. Repeated
edits retain at most one external override and never append a preset layer. An
already selected exact artifact yields equivalent selection and bytes; callers
decide draft no-op behavior. Returning to earlier authored content reuses its exact
identity. Reset retains the versioned contract and drops only the external override;
resetting to an ID absent from the base rejects instead of guessing a theme.

## Fixed examples and verification

Freeze this package, resource-selection schema and independently derived literal
selections before implementation. Reuse the already independently derived artifact
bytes, with their hashes captured in the new freeze. For the settings-content fixture,
the output contains exactly its selected preset closure plus the new artifact;
its image pin and all base bytes remain unchanged. Reset returns exactly that base
closure. Test malformed selections and pins, wrong effective ID, tampered artifact
fields/bytes, noncanonical manifests, dependencies, document/package collisions,
duplicate exact reuse, capability loss, all old command versions and bounded repeat.

Synthetic base closures exercise 63+1 admission, 64+1 rejection, an eight-deep base
with an independent override, asset-count and byte capacity. A failed replacement
must leave the original selection, packages and candidate unchanged. Run affected
and full portable suites on Linux GCC13, Windows GCC15 and v141_xp, plus native
resource-generation/content-command regressions for unchanged consumers. Preserve
all attempts and exact source/oracle/artifact identities. Historical compiler tests
on contemporary Windows do not qualify XP or any complete release edition.

## Required next boundary

Admit a command version only after defining exact artifact transport, capability
negotiation, frame limits, source-theme authorization, current-policy publication
guards and replay identity. A new generation/resource format must distinguish these
selections from old readers, retain coherent bytes and reconcile lost acknowledgements
without duplicate revisions. Test interruption before/after selecting-record publication,
corrupt/missing overrides, unavailable imports and reset/repeated-edit recovery.
Then integrate resource context into atomic editor history and native font controls.
The original oracle must remain independent of implementation; proposed contract
corrections retain the original discrepancy and receive explicit recorded review.
