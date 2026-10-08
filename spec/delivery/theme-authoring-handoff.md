---
type: "SysPane Work Record"
title: "Theme authoring input and immutable artifact checkpoint"
description: "Exact font input and license-bound theme artifacts; durable and native integration remain open."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T03:06:00.812250+00:00"}
sp_id: "SP-THEME-AUTHORING-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-AUTHORING", "SP-ROLE-COMPOSITION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Theme authoring input and immutable artifact checkpoint

Baseline ed3adc07f6900846ec347e4019b822f44fce59d7. The
[package](packages/w-10-theme-authoring.md) implements the shared input and immutable
artifact boundary needed for native font editing. It leaves every existing schema,
fixture, command, generation and native admission meaning unchanged.

ThemeInput owns a complete base font and explicit named roles. Hydration is lossless
and locale independent; editing validates exact family/size/weight/style, permits
role reset and upgrades legacy documents only on a change. Parsed no-ops return the
original document, including version and absent versus empty roles. Other authored
values are preserved. Invalid input changes nothing.

Authored theme construction authorizes current resources and theme.typography, permits
only font changes and creates a new dependency-free theme package with exact hashes,
byte counts, source license and pins. Its identity binds the canonical edited content
and license. Identical content reuses identity independently of the source theme ID;
a license difference has a different identity. Original packages remain immutable.
It performs no filesystem I/O, does not append a catalog or preset layer, and does
not claim a font edit has been saved or rendered.

## Verification and design refinement

The initial independent Python examples and package were frozen before production
changes. First executions passed, but review found that a theme-only identity seed
could give two different licensed manifests the same package ID/version. The revised
seed wraps both license and theme. A second independently derived MIT/BSD-2-Clause
pair proves distinct identities and exact preservation. Original contract/examples,
both freezes and the preliminary runs remain. The stronger contract was frozen before
the implementation revision; earlier passes do not establish the stronger claim.

All four authoring families and 166 affected checks pass on each development profile.
Full portable suites pass 343 Linux GCC13, 340 Windows GCC15 and 337 v141_xp checks
(1020 total). Native font and semantic role-composition regressions pass on the pinned
Linux adapter. Tests cover owned input, legacy migration, all roles, reset, exact
no-op, locale independence, negative fields and non-font edits, current policy,
exact package bytes/pins, repeated identity, license distinction and immutable source.

23 source-bound attempts and 4 native archives retain
actual commands, source snapshots, fixed oracles and artifact/runtime identities.
All 184 baseline schema/fixture files remain byte-identical. Specification tooling,
schema/fixture validation, generated navigation, sealed integrity and staged-byte
verification accompany this handoff. The two existing Windows symlink assertions
remain skipped. Historical compiler checks ran on contemporary Windows, not XP.

Cleanup verified committed bytes before removing 24 duplicated native folders
(439813107 bytes) and 23 duplicated attempt folders (40437806 bytes). The 7-GiB
workspace bound is unchanged. Evidence is under out/evidence with prefix
w-10-theme-authoring (attempts, native-index, verification, staging), plus
theme-authoring-handoff.json.

## Next admitted work

Close the versioned resource-selection override and theme command/generation boundary.
Keep one authored theme override separate from the base preset closure, preserving
original image references; repeated edits must not grow dependency depth or accumulate
orphaned theme packages. Validate exact pins, collisions, capacity, current policy,
interruption and lost-acknowledgement/restart against frozen cases before implementation.

Then carry scene and resource contexts through the existing atomic draft/history,
Apply and reconciliation owners. Native base/role font controls need preview, inherit,
reset, Cancel/Set, undo/redo, save/reopen and private-buffer erasure evidence before
trusted EditorForm typography is enabled. Clipboard/recovery drafts, installed desktop
ownership, complete accessibility/performance, other native adapters and all five
complete editions remain required. W-10 and the full release goal remain in progress.
