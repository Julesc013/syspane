from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();now=datetime.now(timezone.utc).isoformat()
def edit(n,a,b):
 p=r/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8',newline='\n')
edit('README.md','The [container checkpoint]', 'The [edit-lock checkpoint](spec/delivery/edit-locks-handoff.md) adds persistent\nwidget/group locks, explicit unlock and inherited protection in the native editor.\nScene 0.4 and command 0.6 preserve existing contracts and require negotiation.\nInstalled integration, remaining authoring and all complete editions remain open.\n\nThe [container checkpoint]')
edit('TODO.md','- [x] W-10 explicit container transformations:', '- [x] W-10 persistent edit locks: versioned scenes, negotiated commands, inherited guards, atomic history and native durable/recovery checks. See the [handoff](spec/delivery/edit-locks-handoff.md).\n- [x] W-10 explicit container transformations:')
edit('spec/delivery/current-state.md','The latest [container checkpoint]', 'The latest [edit-lock checkpoint](edit-locks-handoff.md) adds persistent locks\nthrough scene 0.4, negotiated command 0.6 and the existing resource/transaction\nowners. Native selection remains available while ordinary protected edits reject;\nexplicit unlock and Undo/Redo preserve exact authored state. Continue conditional\nvisibility/typography, clipboard/recovery drafts and installed ownership, then\nfull accessibility/performance and all five complete-edition release tracks.\n\nThe earlier [container checkpoint]')
for n,text in {
 'spec/contracts/commands.md':'\n## Persistent editor locks\n\n[Command 0.6](command-v0.6.schema.json) retains the complete-command 0.5 bounds and\nadds scene 0.4 to its versioned replacement union. It requires configuration.edit-locks\nalongside large-command, resource and scene-content negotiation. [The package](../delivery/packages/w-10-edit-locks.md)\nowns admission and exact guard semantics. Old command schemas remain unchanged.\n',
 'spec/experience/scene-bindings.md':'\n## Persistent editing guards\n\n[Scene 0.4](../contracts/scene-v0.4.schema.json) retains scene 0.3 content and adds\noptional edit_locked. A group lock is inherited during editing; it changes neither\nrendering nor disclosure. The [lock package](../delivery/packages/w-10-edit-locks.md)\ndefines explicit promotion, unlock, protected operations and capability admission.\nOlder consumers must reject unsupported versions without dropping flags.\n',
 'spec/experience/editor.md':'\n## Persistent edit locks\n\nThe [edit-lock package](../delivery/packages/w-10-edit-locks.md) defines own/inherited\nlocks, protected branches, explicit unlock, exact history and negotiated durable\nsubmission. Keep selection and recovery paths usable. A lock guards ordinary editor\ncommands; authorization, disclosure and dynamic scene resolution keep their owners.\nThe [checkpoint](../delivery/edit-locks-handoff.md) records scoped validation.\n',
 'docs/developers/build.md':'\nPersistent editor locks use SetWidgetLocks through EditorDraft. Scene 0.4 retains\ncontent and adds edit_locked; command 0.6 requires the resource, scene-content,\nlarge-command and edit-lock negotiation gates. Use `editor.LOCK-*` and native\n`native.EDITOR-LOCKS` in the existing presets. The [package](../../spec/delivery/packages/w-10-edit-locks.md)\nand [handoff](../../spec/delivery/edit-locks-handoff.md) record scope and evidence.\n'
}.items():
 p=r/n;p.write_text(p.read_text()+text,encoding='utf-8',newline='\n')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes())
def visit(x):
 if isinstance(x,dict):
  if x.get('id')=='W-10':
   for y in x.values():
    if isinstance(y,list) and 'SP-W10-CONTAINERS' in y:y.append('SP-W10-EDIT-LOCKS')
   x['package']='delivery/packages/w-10-edit-locks.md';x['evidence']='delivery/edit-locks-handoff.md';x['notes']+=' Persistent own/inherited edit locks now use scene 0.4 and negotiated command 0.6, with explicit unlock, shared guards and native durable history/recovery verification. Continue visibility/typography, clipboard/recovery drafts and installed ownership; all complete editions remain open.'
  else:
   for y in x.values():visit(y)
 elif isinstance(x,list):
  for y in x:visit(y)
visit(v);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
body='''---
type: "SysPane Work Record"
title: "Persistent editor lock checkpoint"
description: "Versioned own/inherited locks through shared guards, native editing and durable transactions."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "TIME"}
sp_id: "SP-EDIT-LOCKS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-EDIT-LOCKS", "SP-CONTAINERS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Persistent editor lock checkpoint

Source baseline: `83da967d8a7311b8124c3beae304af103730eccd`. The
[package](packages/w-10-edit-locks.md), schemas and complete input/expected scenes
were frozen before production edits. Scene 0.4 adds optional edit_locked without
changing scene 0.3. Command 0.6 retains complete-command bounds and requires explicit
edit-lock/resource/scene-content/large-command negotiation. Prior schemas and
fixtures remain byte-identical; the fixture registry gains the new cases.

SetWidgetLocks changes own flags atomically; group locks are inherited. Explicit
unlock never clears an ancestor. Ordinary edits to protected objects/branches reject;
selection, independent sibling insertion, scene theme and history retain their
specified roles. Native controls expose Lock/Unlock and accessible lock status,
disable protected fields/actions and prevent pointer gestures. Apply remains a
separate durable transaction. Locks affect editing, not policy or live rendering.

## Executed evidence

Eight shared families cover schemas/types/versions, exact promotion/history,
operation guards, inheritance, rollback, policy/capability/pending states,
negotiation and durable replay. All 146 affected checks pass on Linux GCC13,
contemporary Windows GCC15 and v141_xp on contemporary Windows. These are
development runs, not historical Windows execution qualification.

All 180 native cases pass across twelve matrices, including seven lock cases and
all existing editor/container/layout/creation/binding/content/arrangement/regression
matrices. Native lock cases compare full scenes, pixels, guarded pointer/keyboard
input, own/inherited/multiple selection, undo/redo, storage before Apply, durable
save/reopen, lost-result reconciliation and policy erasure. A deliberately removed
stored lock must be positively detected.

Initial schema/header admission and compile failures are preserved. The first native
unlock/move test wrongly expected the numeric label string 60, while the captured
native field showed 60.0 at the correct origin. Its correction uses the existing
independent numeric read with unchanged values, frozen scenes, pixels, deadlines
and production behavior. The original failure and correction record are retained.

Records: `build-support/evidence/w-10-edit-locks-attempts.json`,
`w-10-edit-locks-native-index.json`, `w-10-edit-locks-verification.json`,
`w-10-edit-locks-staging.json` and `build-support/evidence/edit-locks-handoff.json`.
Exact source archives, input identities, executable identities and failed/successful
native observations are preserved. Cleanup removed only duplicates verified against
committed archives, within the unchanged workspace bound.

## Remaining boundary

W-10 and the full 0.1.0 release remain in progress. Continue conditional visibility,
typography, clipboard authority, recovery drafts, installed controller/catalog/policy
ownership and scene-aligned entry/restoration with independent escape. Complete
accessibility/performance, earlier unrelated focus/interface causes, other platform
adapters, historical laboratories and all five edition/release gates remain open.
'''.replace('TIME',now)
(r/'spec/delivery/edit-locks-handoff.md').write_text(body,encoding='utf-8',newline='\n')
