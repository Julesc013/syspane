from pathlib import Path
from datetime import datetime,timezone
import json
r=Path(__file__).resolve().parents[2]
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def prepend(p,heading,s):
    old=(r/p).read_text();assert heading in old;write(p,old.replace(heading,heading+'\n\n'+s,1))
stamp=datetime.now(timezone.utc).isoformat()
write('spec/delivery/group-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native grouping checkpoint"
description: "Exact hierarchy transformations, selection history and independently observed native persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
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
''')
prepend('README.md','These are development targets; supported versions and release qualification remain open.',
'''The [grouping checkpoint](spec/delivery/group-handoff.md) adds Group/Ungroup
to the shared draft and Linux native editor. Exact hierarchy, fractional and
responsive-variant cases accompany native drawing-order, undo, save/reopen,
policy-erasure and restart checks. Full authoring and installed editions remain open.''')
prepend('spec/delivery/current-state.md','# Current state and next admitted boundary',
'''The latest [grouping checkpoint](group-handoff.md) adds atomic group/ungroup,
selection history and native controls with exact hierarchy and pixel/storage evidence.
Next close snapping/grid/guides, responsive/flow container transforms and remaining
authoring/property contracts, then installed ownership and scene-aligned entry with
independent recovery. Complete editions and historical qualification remain open.''')
p='spec/delivery/current-state.md';s=(r/p).read_text().replace('The latest [arrangement checkpoint]','The earlier [arrangement checkpoint]',1).replace('snapping/grid/guides, grouping and remaining','snapping/grid/guides and remaining',1);write(p,s)
prepend('docs/developers/build.md','# Developer setup and checks',
'''The [grouping package](../../spec/delivery/packages/w-10-group.md) adds
GroupWidgets and UngroupWidget to EditorDraft::execute. Supply sibling IDs and
a fresh group ID/title. Group bounds cover every fixed variant; selection changes
atomically with the scene. Ungroup requires contained fixed variants and a fixed
container origin. Native hosts must check current resolved geometry and parent
eligibility before using these transformations as direct-edit operations.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. In the declared non-root Linux laboratory also run `ctest
--preset linux-x64-gcc13 -R '^native[.](EDITOR-GROUP|EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen scenes live in tests/editor/group-cases.json and
tests/editor/group-overlap-cases.json. See the [handoff](../../spec/delivery/group-handoff.md)
for executed evidence and remaining boundaries.''')
prepend('docs/users/configuration.md','is tested in a private laboratory and is not yet an installed desktop edition.',
'''Select two or more fixed widgets in the same parent and display, then choose
Group. The new container becomes selected; click its empty area or its list row
to select it later. Ungroup releases its direct children while preserving their
positions. Undo restores both the hierarchy and selection. Apply saves the draft.
Grouping nonadjacent objects places them together at the first selected drawing
position, which can change overlaps with intervening objects. Ungroup reports
clipped or unsupported layouts instead of changing their visible meaning.''')
prepend('spec/experience/editor.md','## Operations',
'''The [grouping package](../delivery/packages/w-10-group.md) defines exact
group/ungroup geometry, ownership and drawing order, atomic selection/history,
containment rejection and native eligibility. Responsive container and flowing
child transformations remain required; this checkpoint does not close all W-10.''')
for p in ('spec/delivery/packages/w-10-editor-draft.md','spec/delivery/packages/w-10-native-editor.md'):
    s=(r/p).read_text();pos=s.index('\n## ');s=s[:pos]+'''\nThe [grouping extension](w-10-group.md) adds reversible fixed-container hierarchy
operations and selection history through this same owner. Its variant bounds,
containment and native geometry requirements apply alongside remaining authoring.
'''+s[pos:];write(p,s)
p='TODO.md';s=(r/p).read_text().replace('- [ ] W-10 complete editor:', '- [x] W-10 grouping: exact fixed-variant group/ungroup, nested selection history, explicit overlap order and native persistence/recovery checks. See the [handoff](spec/delivery/group-handoff.md).\n- [ ] W-10 complete editor:').replace('snap/grid/guides, grouping, responsive arrangement','snap/grid/guides, responsive/flow container transforms, responsive arrangement');write(p,s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());row=next(x for x in v.get('work_units',v.get('units')) if x['id']=='W-10')
row['specs'].append('SP-W10-GROUP');row['package']='delivery/packages/w-10-group.md';row['evidence']='delivery/group-handoff.md';row['notes']=row['notes'].replace('Snap/grid/guides, grouping, responsive arrangement','Snap/grid/guides, responsive arrangement')+' Group/ungroup now have exact all-fixed-variant geometry, atomic selection history, explicit drawing order and independent native persistence/recovery evidence. Responsive/flow container transforms and all remaining editor/installed boundaries stay open.';write(p,json.dumps(v,indent=2)+'\n')
p='.gitattributes';write(p,(r/p).read_text()+'# Preserve exact grouping attempts, original inputs and execution helpers.\nbuild-support/evidence/w-10-group-history/** -text whitespace=cr-at-eol\n')
print('Updated specs, docs, README, TODO and existing W-10 route.')
