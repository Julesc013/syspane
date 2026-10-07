---
type: "SysPane Work Record"
title: "Native grouping checkpoint"
description: "Exact hierarchy transformations, selection history and independently observed native persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T05:47:11.436763+00:00"}
sp_id: "SP-GROUP-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-GROUP", "SP-ARRANGE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native grouping checkpoint

Source baseline: `bd964bd465265a274dffe34b666994835cd3e643`. The
[package](packages/w-10-group.md) closes reversible group/ungroup transformations
through the existing EditorDraft, GTK form, renderer and resource-aware transaction.
W-10 remains in progress; this component checkpoint does not complete an edition.

GroupWidgets creates one fixed container around disjoint siblings with equal
authored display intent. Its bounds include every fixed base/breakpoint variant;
root origins become local 1/64-DIP positions. All other child properties and
descendants remain exact. The container enters at the first selected ownership
position, so a nonadjacent selection becomes contiguous in drawing order.
UngroupWidget translates direct children back and removes only the container.
It rejects clipping-dependent geometry, flowing children and responsive container
origins. Selection, scene and history change together after complete validation.

Native Group/Ungroup controls resolve fresh geometry and reject metric expansion
or an ineligible parent. The new container can be selected in empty canvas space,
moved, renamed, undone, saved and reopened. Disclosure loss erases group names,
fields, held authored accessibility references and pixels. The shared batch,
scene, depth, history, policy and resource limits still apply. No schema version,
wire operation, storage owner or privilege was added.

## Verification

The package and complete expected scenes were frozen before production changes.
Seven portable families cover nested groups, ownership order, fractional origins,
fixed responsive variants, containment, depth/capacity, atomic rollback, selection
history, current policy, exact requests and resource-free scene 0.2 compatibility.
The affected selection passes 101 CTest entries on each of Linux GCC 13,
Windows GCC 15 and v141_xp on contemporary Windows.

Eleven private Linux native cases exercise group, move, ungroup, nested groups,
nonadjacent drawing order, cancellation, denial, 200-ms disclosure erasure,
lost-result restart, corrupted stored hierarchy and a frozen preview. Native keys,
AT-SPI, actual pixels and externally read stored documents provide the observations.
The 14-case arrangement, 20-case editor and 24-case complete-scene/storage/IPC
regressions also pass. These are executed cases, not merely acceptance definitions.

The first overlap probe incorrectly compared a complete isolated text crop with
the same crop over another widget, despite the authored translucent background.
The preserved screenshot shows the expected drawing order. The corrected probe
derives fully opaque white glyph locations from the isolated native baseline,
requires the reversed order to fail, and requires those locations to match after
grouping and reopening. A second failed probe assumed eight opaque pixels;
antialiasing leaves three in this fixed crop. It now requires a nonempty sample
and demonstrated order discrimination. Neither correction changes product code,
the original complete-scene fixture or the separately frozen overlapping scene.
Both failed executions and their exact observers remain archived.
An arrangement regression also hit an AT-SPI geometry-query timeout during
concurrent Windows builds. Its unchanged native matrix was rerun after those
builds finished; the failed record remains evidence of laboratory timing limits.

Repository evidence paths (outside the standalone specification bundle):
`build-support/evidence/w-10-group-attempts.json`,
`build-support/evidence/w-10-group-native-index.json`,
`build-support/evidence/w-10-group-verification.json`,
`build-support/evidence/w-10-group-staging.json` and
`build-support/evidence/group-handoff.json`.

## Next admitted boundary

Close snapping/grid/guides, responsive/flow container transformations and remaining
binding/content/theme, lock/visibility/typography properties. Complete clipboard
authority and recovery drafts, then installed controller/catalog/policy ownership
and scene-aligned entry/restoration with independent escape before mapping.
Continue other adapters and historical native qualification independently.

Owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, full accessibility/performance or a
complete edition. Two existing Windows symlink tooling assertions remain skipped.
Windows 9x, Windows NT, X11, Wayland and Mac OS X release scope is unchanged.
