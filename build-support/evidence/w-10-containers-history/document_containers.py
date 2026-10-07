from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
 s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
change('README.md','The [keyboard-input checkpoint]', '''The [container checkpoint](spec/delivery/containers-handoff.md) adds explicit Wrap
and Unwrap for flowing, nested and responsive layout rules. Native dialogs show the
reflow choice before applying one reversible draft operation. Existing fixed-geometry
Group/Ungroup keep their meaning. Installed integration and full editions remain open.

The [keyboard-input checkpoint]''')
change('TODO.md','- [x] W-10 layout-button focus investigation:', '- [x] W-10 explicit container transformations: typed Wrap/Unwrap retain authored child rules and intentionally reflow; native modal input, exact history, pixels, persistence, recovery and erasure have independent checks. See the [handoff](spec/delivery/containers-handoff.md).\n- [x] W-10 layout-button focus investigation:')
change('spec/delivery/current-state.md','The latest [keyboard-input checkpoint]', '''The latest [container checkpoint](containers-handoff.md) adds explicit Wrap and
Unwrap for flowing children, nested containers and responsive rules. Children keep
every authored value and resolve in their new parent; native dialogs explain reflow
before one atomic draft operation. Fixed-geometry Group/Ungroup remain unchanged.
Continue lock/visibility/typography, clipboard/recovery drafts and installed ownership,
then complete native accessibility/performance and all five release tracks. W-10
remains in progress; no complete edition or historical qualification is claimed.

The earlier [keyboard-input checkpoint]''')
p='spec/delivery/current-state.md';write(p,re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Explicit reflowing container checkpoint and remaining editor/release boundaries')),(r/p).read_text(),count=1,flags=re.M))
p='spec/delivery/work-units.json';d=json.loads((r/p).read_bytes());w=next(x for x in d['work_units'] if x['id']=='W-10');assert w['status']=='in_progress';w['specs'].append('SP-W10-CONTAINERS');w['package']='delivery/packages/w-10-containers.md';w['evidence']='delivery/containers-handoff.md';w['notes']+=' Explicit Wrap/Unwrap now preserve authored child rules and intentionally reflow inside a chosen container or its enclosing parent. Existing fixed-geometry Group/Ungroup remain unchanged. Native modal lifetime, full scenes, pixels, history, storage and recovery have source-bound checks. Continue lock/visibility/typography, clipboard/recovery drafts and installed ownership; complete editions remain open.';write(p,json.dumps(d,indent=2)+'\n')
p='spec/experience/editor.md';write(p,(r/p).read_text()+'''
## Explicit container reflow

The [container package](../delivery/packages/w-10-containers.md) adds Wrap/Unwrap
for flowing, responsive and nested children. These explicit commands retain every
child's authored rules and resolve them in the new parent. The native dialog explains
reflow and possible clipping changes before adoption; no pixel-preserving conversion
is inferred. Existing fixed-geometry Group/Ungroup semantics remain unchanged.
The [checkpoint](../delivery/containers-handoff.md) records component evidence and
remaining editor, installed-integration and complete-edition acceptance.
''')
p='docs/developers/build.md';write(p,(r/p).read_text()+'''
### Explicit container transformations

`WrapWidgets` takes disjoint sibling IDs, a fresh group ID/title, complete group
layout and priority. `UnwrapWidget` removes one group and promotes its children.
Both preserve surviving authored values exactly and intentionally resolve them in
the new parent. Selection/history change atomically through EditorDraft. Existing
GroupWidgets/UngroupWidget retain their fixed-geometry rules. The native Layout
modal reuses its parser/buffers for Wrap and an explicit Unwrap confirmation.

After workspace preflight/configure/build, use `ctest --preset <profile> -R
"^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])" --output-on-failure`.
The owned non-root Linux laboratory additionally runs `ctest --preset linux-x64-gcc13
-R "^native[.]EDITOR-CONTAINERS$" --output-on-failure` and existing editor matrices.
See the [package](../../spec/delivery/packages/w-10-containers.md) and
[handoff](../../spec/delivery/containers-handoff.md) for exact scope and evidence.
''')
write('spec/delivery/containers-handoff.md',f'''---
type: "SysPane Work Record"
title: "Explicit container authoring checkpoint"
description: "Wrap and Unwrap preserve authored rules with explicit native reflow and atomic history."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-CONTAINERS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-CONTAINERS", "SP-KEYBOARD-INPUT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Explicit container authoring checkpoint

Source baseline: `{base}`. The [package](packages/w-10-containers.md)
adds typed WrapWidgets/UnwrapWidget and native dialogs through existing draft,
layout, policy, resource, renderer and transaction owners. Existing document/wire
identities and fixed-geometry Group/Ungroup semantics remain unchanged.

Wrapping preserves every existing widget field, including fixed coordinates and
flow/response rules. The new group occupies the first selected sibling position;
children keep ownership order. Unwrap removes the container and retains children
in that position. Both intentionally reflow in the new parent. Native input exposes
all group layout kinds, ordered variants, title/priority and a clear reflow action.
Undo restores exact scene and selection. Private input is erased on cancellation,
policy/owner change and topology replacement, with the existing 200-ms bound.

## Executed evidence

Six new portable test families cover full expected scenes, independently specified
geometry, responsive/nested/nonadjacent rules, atomic rejection, bounds, policy,
pending requests and scene 0.2. All 138 affected checks pass on each development
toolchain: Linux GCC13, contemporary Windows GCC15 and v141_xp on contemporary
Windows. These runs do not qualify historical Windows execution.

All 172 native cases pass across eleven matrices: containers 15, layout 21,
observation calibration 7, creation 17, binding 15, content 15, snap 13, group 11,
arrangement 14, editor 20 and large-command 24. Container cases operate real native
controls and compare full submitted/stored scenes, pixels, history, save/reopen,
topology/policy erasure and lost-result reconciliation. Deliberate wrong hierarchy,
retained private input and frozen preview are positively detected.

The first Unwrap pixel oracle incorrectly compared an overlapping translucent pair
with an isolated second caption. An attempted sparse-opaque check then rejected
its own arbitrary sample-count requirement. Both failures are preserved. The final
oracle derives the exact premultiplied source-over composite from the two isolated
baseline captions and the pinned theme. Every sampled color must resolve to one
alpha; unavailable/ambiguous calibration fails. All 4,480 composite pixels and
erasure at the old location are checked. The frozen scenes, geometry, deadlines
and storage expectations did not change, and no production change addressed these
oracle failures. The independent calibration and original snapshots are retained.

Records: `build-support/evidence/w-10-containers-attempts.json`,
`w-10-containers-native-index.json`, `w-10-containers-verification.json`,
`w-10-containers-staging.json` and `build-support/evidence/containers-handoff.json`.
Exact source snapshots, frozen inputs, executable identities, every attempt and
oracle corrections are preserved. Workspace cleanup removed only duplicates
verified against committed archives; the existing output limit is unchanged.

## Remaining boundary

W-10 and every complete edition remain in progress. Continue lock/visibility/
typography, clipboard authority, recovery drafts, installed controller/catalog/policy
ownership and scene-aligned entry/restoration with independent escape. Complete
accessibility/performance, earlier unrelated focus/interface failures, historical
labs and all five release gates remain open. Explicit reflow is not a claim of an
automatic appearance-preserving conversion between arbitrary responsive layouts.
''')
