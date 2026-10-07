from pathlib import Path
import json
r=Path.cwd()
def edit(name,old,new):
 p=r/name;s=p.read_text();assert old in s,name;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('out/campaign/container_step.py',"r/'spec/delivery/packages/w-10-containers.md']","r/'spec/delivery/packages/w-10-containers.md',r/'spec/delivery/packages/w-10-container-preview.md']")
edit('spec/delivery/containers-handoff.md','All 172 native cases','All 173 native cases')
edit('spec/delivery/containers-handoff.md','containers 15,','containers 16,')
edit('spec/delivery/containers-handoff.md','"SP-W10-CONTAINERS", "SP-KEYBOARD','"SP-W10-CONTAINERS", "SP-W10-CONTAINER-PREVIEW", "SP-KEYBOARD')
edit('spec/delivery/containers-handoff.md','## Executed evidence','The [preview recovery supplement](packages/w-10-container-preview.md) freezes a\nclipped-canvas case before correcting its misleading display-absence status.\nThe original failure is retained. The editor now reports an unavailable preview\nalongside draft/storage status and retains authored Layout and Undo recovery.\nThe native case restores the original scene, repairs the canvas, exercises both\nhistory steps and verifies durable save/reopen without changing resources.\n\n## Executed evidence')
edit('spec/experience/editor.md','The [container package](../delivery/packages/w-10-containers.md)', 'A renderer alternative must show an unavailable preview alongside the existing\ndraft/request/durable facts. Retain authored Layout and Undo recovery and avoid\na false display-absence message; see the [recovery supplement](../delivery/packages/w-10-container-preview.md).\n\nThe [container package](../delivery/packages/w-10-containers.md)')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());row=next(x for x in v['work_units'] if x['id']=='W-10') if isinstance(v,dict) and 'work_units' in v else None
if row is None:
 def find(x):
  if isinstance(x,dict):
   if x.get('id')=='W-10':return x
   for y in x.values():
    z=find(y)
    if z is not None:return z
  elif isinstance(x,list):
   for y in x:
    z=find(y)
    if z is not None:return z
 row=find(v)
assert row is not None
for value in row.values():
 if isinstance(value,list) and 'SP-W10-CONTAINERS' in value:value.append('SP-W10-CONTAINER-PREVIEW')
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
edit('out/campaign/finish_containers.py','172','173')
edit('out/campaign/preserve_containers.py',"native_containers.py',15)","native_containers.py',16)")
edit('out/campaign/preserve_containers.py',"'prepare_container_inputs.py',", "'prepare_container_inputs.py', 'prepare_container_preview.py', 'complete_container_preview.py', 'prepare_container_extra_prune.py', 'prune_container_extra_attempts.ps1', 'container-extra-prune-plan.json', 'container-extra-pruned-attempts.json',")
edit('out/campaign/preserve_containers.py',"'fixed-inputs.zip','oracle-correction.json'","'fixed-inputs.zip','preview-inputs.json','preview-inputs.zip','oracle-correction.json'")
edit('out/campaign/preserve_containers.py','def latest(profile,action):',"preview=json.loads((history/'preview-inputs.json').read_bytes());assert sha(history/'preview-inputs.zip')==preview['archive_sha256']\nwith zipfile.ZipFile(history/'preview-inputs.zip') as z:\n    for n,h in preview['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(r/n)\n\ndef latest(profile,action):")
edit('out/campaign/preserve_containers.py',"originals=dict(record=ref(history/'fixed-inputs.json'),archive=ref(history/'fixed-inputs.zip')),","originals=dict(record=ref(history/'fixed-inputs.json'),archive=ref(history/'fixed-inputs.zip')),preview_originals=dict(record=ref(history/'preview-inputs.json'),archive=ref(history/'preview-inputs.zip')),")
edit('out/campaign/preserve_containers.py',"if family=='EDITOR-CONTAINERS':assert v['fixture_sha256']", "if family=='EDITOR-CONTAINERS':assert v['preview_fixture_sha256']==sha(r/'tests/editor/container-preview-cases.json') and v['fixture_sha256']")
edit('out/campaign/stage_containers.py',"native=json.loads(content(index['native_index']['path']));refs(native)","preview=index['preview_originals'];frozen=json.loads(content(preview['record']['path']))\nwith zipfile.ZipFile(io.BytesIO(content(preview['archive']['path']))) as z:\n    for n,digest in frozen['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)\npre=next(json.loads(content(a['path'])) for a in index['attempts'] if 'containers-462ca9e3a8' in a['path'])\nassert pre['exit']==1 and pre['source_inputs']['source/interfaces/editor_form_linux.cpp']==frozen['before_production_sha256']\nnative=json.loads(content(index['native_index']['path']));refs(native)")
edit('out/campaign/stage_containers.py',"if family=='EDITOR-CONTAINERS':check('tests/editor/container-cases.json',report['fixture_sha256'])", "if family=='EDITOR-CONTAINERS':check('tests/editor/container-cases.json',report['fixture_sha256']);check('tests/editor/container-preview-cases.json',report['preview_fixture_sha256'])")
edit('out/campaign/stage_containers.py',"if family=='EDITOR-CONTAINERS':check('tests/editor/native_layout_authoring.py',detail['layout_helper_sha256'])", "if family=='EDITOR-CONTAINERS':check('tests/editor/native_layout_authoring.py',detail['layout_helper_sha256']);check('tests/editor/container-preview-cases.json',detail['preview_fixture_sha256'])")
# Additional cleanup has its own immutable plan and receipt.
s=(r/'out/campaign/prepare_container_prune.py').read_text().replace("('w-10-modal-focus','w-10-layout-authoring')","('w-10-native-observation',)").replace('container-prune-plan.json','container-extra-prune-plan.json')
(r/'out/campaign/prepare_container_extra_prune.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_container_attempts.ps1').read_text().replace('container-prune-plan.json','container-extra-prune-plan.json').replace('container-pruned-attempts.json','container-extra-pruned-attempts.json').replace("'w-10-modal-focus'","'w-10-native-observation'").replace("'w-10-layout-authoring'","'w-10-native-observation'")
(r/'out/campaign/prune_container_extra_attempts.ps1').write_text(s,encoding='utf-8',newline='\n')
