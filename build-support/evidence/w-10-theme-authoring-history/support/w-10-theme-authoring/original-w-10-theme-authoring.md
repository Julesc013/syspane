---
type: "SysPane Work Package"
title: "Theme authoring input and immutable artifact boundary"
description: "Lossless font input and deterministic private theme artifacts before durable native integration."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T05:00:00Z"}
sp_id: "SP-W10-THEME-AUTHORING"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-ROLE-COMPOSITION", "SP-W09-TYPOGRAPHY", "SP-W10-VISIBILITY-CONTROLS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Theme authoring input and immutable artifact boundary

Native theme editing must reach the existing durable resource owner. Currently
EditorDraft only changes scene/settings and selects existing immutable packages;
SettingsDraft has one fixed resource context and the command schemas cannot upload
new themes. Do not present a font dialog as saved authoring while those boundaries
remain absent. This package implements their shared input/artifact prerequisite,
then specifies the integration work still required. It does not enable the editor's
experimental_typography flag or complete W-10.

## Shared private input

ThemeInput contains one base FontInput and zero to four explicit role FontInputs,
keyed by body, label, value and diagnostic. A FontInput contains literal family,
size_dip text, weight text and style. Hydration validates the source theme and
returns owned values. Legacy fonts hydrate weight 400/style normal; role absence
stays absent, not an explicit copy of the base. Display finite sizes with the
locale-independent max_digits10 representation used by existing content controls.

Editing parses size using the existing bounded decimal/exponent grammar (64 bytes),
weight using canonical unsigned decimal (100..900 in steps of 100), and style as
normal/italic/oblique. Existing theme 0.2 family, Unicode, DIP, whole-document and
role limits apply. No trimming, comma conversion, native-font substitution or
partial role inheritance. Each explicit role must be complete. Unknown role names
reject. Removing a role means use the base font, not another role or a copied font.

If all parsed fonts and explicit role membership equal the hydrated source, return
the exact original Json value: keep theme 0.1, absent versus empty font_roles and
integer versus floating authored representation. Otherwise upgrade only the theme
document to 0.2, replace the complete base/roles, omit font_roles if all roles are
absent, and validate. Preserve theme_id, name, tokens, motion and extensions exactly.
Invalid input returns no candidate and never mutates either source or input.
Hydration/edits have no filesystem, font-loading, draft-history or publication effect.

## Immutable authored artifact

The configuration helper accepts the selected ResourceSet, a complete proposed theme,
current Policy and admitted capabilities. First authorize source resources, then
require theme.typography admitted and not denied. Compare proposal to the source:
no-op returns no artifact. Only schema_version, font and font_roles may differ;
the original theme_id and every other value must remain exactly equal. A changed
proposal must validate as theme 0.2. No downgrade, color edit, renamed source or
extension edit is smuggled through font authoring.

For a changed proposal, copy it and remove theme_id. Canonical bytes for this
identity seed are the pinned Json library's compact, lexicographically ordered,
UTF-8 serialization followed by LF (no indentation, ASCII escaping or locale).
Compute lowercase SHA-256 over ASCII `SysPane authored theme 1` followed by LF,
then the seed bytes. Let H denote that hash. The result's theme_id is
`theme:authored:H`; its package_id is `package:authored-theme:H`, replacing H with
all 64 lowercase digits. Identity excludes the input theme_id so editing an already
authored copy back to the same exact content reuses the same identity. Different
other authored data, including extensions, remains part of identity. This is not
an assertion that numerically equivalent JSON representations have identical bytes.

The artifact has one theme.json asset: compact ordered UTF-8 document plus LF.
Manifest 0.1 uses version 0.1.0, kind theme, the selected source package's exact
license string, no dependencies, required_capabilities [theme.typography], empty
optional_capabilities, the exact SHA-256/byte count and application/json media type.
Serialize the manifest with the same compact-plus-LF rule. Return owned theme,
package bytes, exact package pin and document pin. Validate the generated package
through ContentCatalog before returning. Do not copy source assets, mutate the
source package, replace a package at its existing identity or write any file.
Source theme selection must match the exact pinned asset and package version.

Repeated construction of identical edited content is byte-identical. Constructing
an artifact does not append it to a catalog, increase a preset's dependency depth,
grant command authority or claim stored/durable/visible. Existing 256-KiB document
and package limits remain; allocation/error paths return no partial artifact.

## Required native and durable integration

After this prerequisite, introduce a versioned exact resource-selection override and
an admitted command/store boundary for one authored theme. Keep the base preset
closure and original image references intact; repeated edits must replace that one
override rather than accumulating another preset/dependency layer. Old command and
generation schemas must continue rejecting new fields. Freeze override resolution,
collision/capacity handling, policy guards, publication interruption and replay
examples before implementing that next boundary.

Then extend the existing SettingsDraft/EditorDraft resource context and history
atomically with the scene change. Native font input must expose base/role controls,
inherit/reset, exact family/size/weight/style, preview, Cancel and Set. Set stages one
reversible operation; Apply persists the exact generated artifact with the scene.
Undo, regrant, disconnect, unknown acknowledgement, restart/reconcile and reopen must
preserve exact pins or erase private state as appropriate. Only their independent
native/durable evidence may enable trusted EditorForm typography. All earlier
role-composition, visibility, source-failure and layout diagnostics remain mandatory.

## Frozen evidence

Freeze this package and literal expected input, document, manifest bytes and hashes
before production edits. Independently derive artifacts with a separate Python
serializer for the fixed representable numbers, validate documents/manifests against
the schemas and verify hashes. Portable INPUT/NOOP/INVALID/ARTIFACT cases cover
legacy migration, all roles, reset, exact fractional sizes, locale independence,
original ownership, invalid fields and non-font changes, policy/capability refusal,
license preservation, exact content pins and stable repeated identity. Existing
schemas/fixtures are unchanged. Run affected and full portable suites on the three
development profiles; the native font/role-composition oracles remain regressions.
Record source/artifact identity, all failed attempts and real outcomes. Reclaim only
verified committed duplicates within the existing 7-GiB allocation. Historical
toolset execution is not historical-system qualification. Native authoring, durable
integration, installed ownership and all five complete editions remain unfinished.
