from pathlib import Path
from datetime import datetime,timezone
import json,re,subprocess
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
def write(p,s):(r/p).write_text(s,encoding='utf-8',newline='\n')
def change(p,old,new):
 s=(r/p).read_text();assert old in s,p;write(p,s.replace(old,new,1))
def append(p,s):write(p,(r/p).read_text()+s)
change('README.md','The [binding-authoring checkpoint]', '''The [widget-creation checkpoint](spec/delivery/widget-creation-handoff.md) adds
native creation of text, value, status, table, chart, image and group widgets.
Root/group placement, explicit image choices and selection share one reversible
insertion. Independent native checks cover preview, save/reopen, cancellation,
restart and erasure. Installed routing and complete editions remain open.

The [binding-authoring checkpoint]''')
change('TODO.md','- [ ] W-10 complete editor:', '- [x] W-10 widget creation: all seven primitives, explicit resource choices and parent-local geometry, atomic selection history and independent native storage/recovery/erasure checks. See the [handoff](spec/delivery/widget-creation-handoff.md).\n- [ ] W-10 complete editor:')
change('docs/users/configuration.md','New non-text\nwidgets, remaining properties and installed desktop routing are still pending.','All seven widget kinds now have creation controls below. Remaining properties and\ninstalled desktop routing are still pending.')
append('docs/users/configuration.md','''
## Adding widgets in the development editor

Choose **Add widget**, then text, value, status, table, chart, image or group.
Placement sets the title and fixed size/position. Choose Scene roots or an existing
group; coordinates inside a group are local to that group. A selected group is
the initial parent. Each kind keeps its own input while the dialog is open.

Content edits text or source fields. New counters/charts start with this host's
network receive counter; tables start with receive/sent columns. These visible
defaults do not acquire a source or grant access. Use **Bindings** to choose other
selectors/pins and **Content** for further options. Images require an explicit
choice from the admitted resource catalog; there is no automatic image selection.

**Add widget** inserts and selects one draft object. Undo restores the prior scene
and selection; Redo selects the restored object. **Apply** saves separately.
Cancel creation discards private input; invalid input stays available for correction.
Policy or owner changes erase the dialog, including hidden kind buffers. The older
**Add text** shortcut remains available. These controls currently run in the owned
Linux development editor, as scoped in the [handoff](../../spec/delivery/widget-creation-handoff.md).
''')
append('docs/developers/build.md','''
### Native widget creation

`editor_create.*` projects bounded private input into InsertWidget. The optional
`select_inserted` flag makes object insertion and selection one EditorDraft history
entry; its default preserves existing callers. The GTK creation dialog uses the
existing immutable resource choices, validator, renderer and request owner.

After profile build and workspace preflight, run `ctest --preset <profile> -R "^editor[.]CREATE-" --output-on-failure`.
Six families compare fixed full objects/scenes, parent display intent, selection
history, exact command scenes, limits and atomic rejection. In the unprivileged
Linux laboratory run `ctest --preset linux-x64-gcc13 -R "^native[.]EDITOR-WIDGET-CREATION$" --output-on-failure`.
Seventeen cases operate actual controls and inspect pixels, accessibility, coherent
stored resources, reopen, cancellation, restart and erasure. Existing native
binding/content/snap/group/arrange/editor and large-command matrices cover shared
ownership regressions. See the [evidence handoff](../../spec/delivery/widget-creation-handoff.md).
''')
append('spec/experience/editor.md','''
## Native creation boundary

The [widget-creation package](../delivery/packages/w-10-widget-creation.md) defines
all seven primitives, explicit parent-local geometry and image choice, bounded
per-kind buffers and one insertion/selection history step. Existing policy,
resource, layout and transaction owners remain authoritative. The
[checkpoint](../delivery/widget-creation-handoff.md) records scoped evidence;
responsive authoring, installed routing and complete editions remain open.
''')
change('spec/delivery/current-state.md','The latest [binding-authoring checkpoint]', '''The latest [widget-creation checkpoint](widget-creation-handoff.md) adds all seven
primitive kinds, explicit parent-local geometry and resource choice, per-kind
private input and atomic insertion/selection history. Next close responsive/flow
transforms and remaining property controls, then installed controller/catalog/policy
ownership and independent entry/restoration. W-10 and all complete editions remain
in progress.

The earlier [binding-authoring checkpoint]''')
p='spec/delivery/current-state.md';s=(r/p).read_text().replace('Next close non-text insertion, responsive/\nflow transforms','Creation now has the checkpoint above. Next close responsive/\nflow transforms').replace('Next close non-text insertion,\nresponsive/flow transforms','Creation now has the checkpoint above. Next close\nresponsive/flow transforms');s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Native creation of all seven primitives and remaining editor boundaries')),s,flags=re.M);write(p,s)
p='spec/delivery/work-units.json';v=json.loads((r/p).read_text());w=next(w for w in v['work_units'] if w['id']=='W-10');w['specs']+=['SP-W10-WIDGET-CREATION'];w['package']='delivery/packages/w-10-widget-creation.md';w['evidence']='delivery/widget-creation-handoff.md';w['notes']+=' Native creation now covers all seven primitives, explicit image/parent choices and atomic insertion/selection history with independent persistence and erasure evidence. Responsive/flow transforms, remaining properties and installed ownership remain open.';write(p,json.dumps(v,indent=2)+'\n')
write('spec/delivery/widget-creation-handoff.md',f'''---
type: "SysPane Work Record"
title: "Native widget-creation checkpoint"
description: "All seven primitives through existing draft, resource, policy and transaction owners."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
sp_id: "SP-WIDGET-CREATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-WIDGET-CREATION", "SP-BINDING-AUTHORING-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native widget-creation checkpoint

Source baseline: `{base}`. The [package](packages/w-10-widget-creation.md)
adds native creation of text, value, status, table, chart, image and group widgets.
It preserves the existing renderer, validator, immutable catalog and transaction.
W-10 remains in progress; this is a component checkpoint, not a complete edition.

Explicit root/group ownership and parent-local geometry determine placement. A
child copies its parent's exact authored display assignment. Image choice is
mandatory; counter defaults remain editable and do not grant source access.
Each kind has a private buffer; Cancel and owner/policy changes erase it. Insertion
and selection form one atomic undo step. Apply separately persists the draft.
Existing InsertWidget callers retain their prior selection behavior by default.

## Verification

The package, complete default objects/root/nested scenes and unchanged resource
fixture were frozen before implementation. Six portable families cover all kinds,
parent intent, geometry/resource/identity/depth/capacity bounds, atomic rejection,
selection history, exact submitted documents and policy loss.

All 124 affected checks pass on Linux GCC 13, Windows GCC 15 and v141_xp on
contemporary Windows. This is not historical Windows runtime qualification.
Seventeen owned Linux creation cases exercise native controls, rendered content,
selection, Undo/Redo, coherent persistence, reopen, cancellation, lost acknowledgement
and held-reference erasure. Deliberate wrong-object, frozen-preview and retained-text
faults require positive distinguishing observations. Existing binding (15), content
(15), snap (13), group (11), arrangement (14), editor (20) and large-command (24)
matrices pass: 129 native cases across eight matrices.

Detailed attempts preserve source snapshots, binary identities, original failures,
native records and frozen inputs. See the [attempt index](../../build-support/evidence/w-10-widget-creation-attempts.json),
[native archive index](../../build-support/evidence/w-10-widget-creation-native-index.json),
[verification](../../build-support/evidence/w-10-widget-creation-verification.json),
[staged identities](../../build-support/evidence/w-10-widget-creation-staging.json)
and [machine handoff](../../build-support/evidence/widget-creation-handoff.json).

## Remaining work

Close responsive/flow transforms, lock/visibility/typography, clipboard authority
and recovery drafts. Connect installed controller/catalog/policy ownership and
scene-aligned entry/restoration with independent escape. Complete accessibility,
performance, other adapters, historical laboratories and every release gate.
Owned ext4/Xvfb/DBus checks do not qualify an installed desktop or physical power
loss. Continue Windows 9x, Windows NT, X11, Wayland and Mac OS X independently.
''')
