from pathlib import Path
from datetime import datetime,timezone
import json
r=Path(__file__).resolve().parents[2]
def write(p,text):(r/p).write_text(text,encoding='utf-8',newline='\n')
def prepend(p,heading,content):
 s=(r/p).read_text();assert heading in s;s=s.replace(heading,heading+'\n\n'+content,1);write(p,s)
stamp=datetime.now(timezone.utc).isoformat()
write('spec/delivery/arrange-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native alignment and spacing checkpoint"
description: "Deterministic shared arrangement with native controls and independently observed persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-ARRANGE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-ARRANGE", "SP-LARGE-COMMANDS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native alignment and spacing checkpoint

Source baseline: `62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1`. The
[package](packages/w-10-arrange.md) closes fixed-base alignment and equal spacing
through the existing EditorDraft, GTK form, renderer and transaction owner.
W-10 remains in progress and every complete-edition release gate remains open.

Typed AlignWidgets and DistributeWidgets operate atomically on disjoint siblings
with matching authored display intent. Six alignments use a common original bounding
interval. Two spacing actions preserve endpoints and distribute integer remainders
deterministically. Positions use nearest 1/64-DIP rounding with ties away from zero;
extents use ceiling. Negative spacing, invalid intermediate values and incompatible
selections reject without partial edits or history changes. Untouched properties,
breakpoints, pins and selection remain exact.

The native form resolves current geometry before arrangement and rejects inactive
responsive bases or native metric expansion. It supplies eight labeled native
buttons, count/field/pending gates and useful rejection messages. Arrange changes
the draft and preview; Apply uses the original resource-aware scene.replace owner.
Undo/redo, cancellation, policy erasure and reconciliation retain their existing
semantics. No new schema, wire operation, import authority or persistent cache exists.

## Verification

The package and complete expected scenes were archived before production edits.
Independent literal cases cover all eight actions, negative and positive half-unit
rounding, ceiling extents, fractional endpoints and zero gaps. Six new portable
families also exercise invalid/atomic edits, hierarchy and ownership order, flow,
breakpoint preservation, history, current policy and exact command submission.

The affected selection passes 94 CTest entries on each of Linux GCC 13, Windows
GCC 15 and v141_xp on contemporary Windows. Fourteen private Linux native cases
exercise all buttons via native selection and keys, actual preview pixels,
undo/redo, stored documents/resources, save/reopen, cancellation, policy denial,
200 ms disclosure erasure and lost-result restart. Deliberate frozen preview and
altered committed geometry controls are positively detected. The existing 20-case
native editor matrix and 24-case complete-scene/storage/IPC matrix also pass.

The first strict build found misleading indentation in a test. The first native
oracle incorrectly expected clicking an already-selected widget to collapse a
multiselection; it now explicitly clears selection before inspecting one widget.
Original failed runs and their source archives are retained. Neither correction
changes the frozen geometry or expected product behavior.

Evidence: [attempts and artifact identities](../../build-support/evidence/w-10-arrange-attempts.json),
[native archive index](../../build-support/evidence/w-10-arrange-native-index.json),
[specification/tool checks](../../build-support/evidence/w-10-arrange-verification.json),
[staged identity checks](../../build-support/evidence/w-10-arrange-staging.json) and
[machine handoff](../../build-support/evidence/arrange-handoff.json).

## Next admitted boundary

Close snapping/grid/guides and grouping semantics, remaining binding/content/theme
and lock/visibility/typography properties, responsive arrangement, clipboard authority
and recovery drafts. Then connect installed controller/catalog/policy ownership to
scene-aligned desktop entry and restoration with independent escape before mapping.
Continue other adapters and historical native qualification independently.

These owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, representative accessibility/performance
or a complete edition. Specification tools still have two existing Windows symlink
skips. Full Windows 9x, Windows NT, X11, Wayland and Mac OS X scope is unchanged.
''')
prepend('README.md','These are development targets; supported versions and release qualification remain open.',
'''The [arrangement checkpoint](spec/delivery/arrange-handoff.md) adds six alignment
and two equal-spacing actions to the shared draft and Linux native editor. Exact
geometry cases and independent native pixels/storage checks cover undo, save,
cancellation, policy changes and restart. Responsive authoring and the remaining
editor controls are still required.''')
prepend('spec/delivery/current-state.md','# Current state and next admitted boundary',
'''The latest [arrangement checkpoint](arrange-handoff.md) adds deterministic shared
alignment/spacing and native controls with independent geometry, pixel and storage
evidence. Next close snapping/grid/guides, grouping and remaining authoring/property
contracts, then installed controller/catalog/policy routing and scene-aligned
entry/restoration. Complete editions and historical native qualification remain open.''')
prepend('docs/developers/build.md','# Developer setup and checks',
'''The [arrangement package](../../spec/delivery/packages/w-10-arrange.md) adds typed
AlignWidgets and DistributeWidgets through EditorDraft::execute. Provide stable IDs;
alignment needs two disjoint siblings and spacing needs three. Only fixed base
origins change. Ownership order breaks spacing ties; current policy and ordinary
atomic/history limits apply. Native hosts must check active resolved base geometry
and native metric expansion before offering a WYSIWYG arrange operation.

After ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])'
--output-on-failure`. In the declared non-root Linux workspace also run `ctest
--preset linux-x64-gcc13 -R '^native[.](EDITOR-ARRANGE|EDITOR-FORM|LARGE-COMMANDS)$'
--output-on-failure`. Frozen inputs are tests/editor/arrange-cases.json; native
reports preserve independently observed pixels and stored scenes, including fault
controls. See the [handoff](../../spec/delivery/arrange-handoff.md) for remaining gates.''')
prepend('docs/users/configuration.md','is tested in a private laboratory and is not yet an installed desktop edition.',
'''Select at least two fixed widgets in the same group and display to align their
edges or centers. Select at least three for equal horizontal or vertical spacing.
Spacing keeps the endpoints in place and reports when there is insufficient room.
Arrange changes are reversible with Undo and become persistent only after Apply.
Finish or revert property fields before arranging. Responsive or size-expanded
widgets need explicit layout editing; this initial arrange control leaves them alone.''')
prepend('spec/experience/editor.md','## Operations',
'''The [fixed-base arrangement package](../delivery/packages/w-10-arrange.md) defines
exact alignment/spacing arithmetic, scope, rejection and native geometry checks.
It is part of W-10; remaining responsive authoring and other operations below stay
required. Shared draft submission also supports explicitly negotiated command 0.5
under the [complete-scene contract](../delivery/packages/w-08-large-commands.md).''')
for p in ('spec/delivery/packages/w-10-editor-draft.md','spec/delivery/packages/w-10-native-editor.md'):
 s=(r/p).read_text();pos=s.index('\n## ');s=s[:pos]+'''\nThe [arrangement extension](w-10-arrange.md) now closes fixed-base align/distribute
operations and native controls through this same owner. Its deterministic arithmetic
and geometry eligibility apply alongside the remaining authoring requirements.
'''+s[pos:];write(p,s)
s=(r/'TODO.md').read_text().replace('- [ ] W-10 complete editor:', '- [x] W-10 fixed-base arrangement: six alignments, two equal-spacing actions, deterministic fractional geometry and native save/recovery evidence. See the [handoff](spec/delivery/arrange-handoff.md).\n- [ ] W-10 complete editor:').replace('snap/align/distribute, remaining property/authoring contracts','snap/grid/guides, grouping, responsive arrangement, remaining property/authoring contracts');write('TODO.md',s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());row=next(x for x in v['work_units'] if x['id']=='W-10') if 'work_units' in v else next(x for x in v['units'] if x['id']=='W-10')
row['specs'].append('SP-W10-ARRANGE');row['package']='delivery/packages/w-10-arrange.md';row['evidence']='delivery/arrange-handoff.md';row['notes']+=' Fixed-base alignment and equal spacing now use typed atomic operations and native controls with exact rounding, selection scope, pixel/storage checks and preserved failure controls. Snap/grid/guides, grouping, responsive arrangement and the remaining authoring/installed boundaries remain open.';write(p,json.dumps(v,indent=2)+'\n')
p='.gitattributes';s=(r/p).read_text();write(p,s+'# Preserve exact arrangement attempts, original inputs and execution helpers.\nbuild-support/evidence/w-10-arrange-history/** -text whitespace=cr-at-eol\n')
print('Updated specification, user/developer docs, README, TODO and the existing W-10 route.')
