from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-10-modal-focus-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='1327296abae9e592ad6f20dd0334004c244c67c1'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-10-modal-focus').glob('*/result.json')):
    v=json.loads(p.read_bytes());assert v['source_base']==base;target=history/p.parent.name;target.mkdir(exist_ok=True)
    for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
    assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
    with zipfile.ZipFile(target/'source-inputs.zip') as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for n,h in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
    if 'ctest_log_archive_sha256' in v:
        shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
    attempts.append(row)
helpers=['setup_modal_focus.py', 'prepare_modal_focus_minimal.py', 'prepare_modal_focus_ordered.py', 'modal_focus_probe.py', 'modal_focus_probe_minimal.py', 'modal_focus_probe_ordered.py', 'modal-focus-plan.json', 'modal-focus-plan-v2.json', 'modal-focus-plan-v3.json', 'modal_focus_step.py', 'modal_focus_flow.py', 'modal_focus_minimal_step.py', 'modal_focus_minimal_flow.py', 'modal_focus_ordered_step.py', 'modal_focus_ordered_flow.py', 'prune_modal_focus_duplicates.py', 'modal-focus-pruned-duplicates.json', 'freeze_keyboard_input.py', 'keyboard_step.py', 'keyboard_flow.py', 'document_keyboard.py', 'prepare_keyboard_evidence.py', 'archive_keyboard.py', 'preserve_keyboard.py', 'finish_keyboard_checks.py', 'finish_keyboard.py', 'stage_keyboard.py', 'fetch_keyboard_sources.py']
for p in [*sorted((r/'out/campaign').glob('modal-focus*execution-*.json')),*sorted((r/'out/campaign').glob('keyboard-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
originals=[]
for stem in ('fixed-inputs',):
    for ext in ('.json','.zip'):shutil.copyfile(r/'out/campaign/w-10-modal-focus'/(stem+ext),history/(stem+ext))
    v=json.loads((history/(stem+'.json')).read_bytes());assert sha(history/(stem+'.zip'))==v['archive_sha256']
    with zipfile.ZipFile(history/(stem+'.zip')) as z:
        for n,h in v['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(r/n)
    originals.append(dict(record=ref(history/(stem+'.json')),archive=ref(history/(stem+'.zip'))))
upstream=r/'out/campaign/w-10-modal-focus/upstream.json';shutil.copyfile(upstream,history/'upstream.json')
with zipfile.ZipFile(history/'upstream.zip','w',zipfile.ZIP_DEFLATED) as z:
    for n,v in json.loads(upstream.read_bytes()).items():
        p=upstream.parent/n;assert sha(p)==v['sha256'];z.write(p,n)
last=max((a for a in attempts if a['action']=='large'),key=lambda a:a['finished_at']);inputs=json.loads((r/last['path']).read_bytes())['source_inputs']
current={n:sha(r/n) for n in inputs if not n.startswith('out/')};assert all(inputs[n]==h for n,h in current.items())
executed_helpers={n:dict(sha256=sha(r/n),preserved_as=ref(history/Path(n).name)) for n in inputs if n.startswith('out/')}
final={}
for action in ('layout','calibration','creation','bindings','properties','snap','group','arrange','native','large'):
    row=max((a for a in attempts if a['action']==action),key=lambda a:a['finished_at']);v=json.loads((r/row['path']).read_bytes())
    assert not v['exit'] and not v['source_changed_during_execution'];assert v['source_inputs']==inputs
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']
    final[action]=dict(record={k:row[k] for k in ('path','sha256')},log=row['ctest_log'],artifact=v['test_artifact'],sha256=v['test_artifact_sha256'])
baseline=json.loads((r/'build-support/evidence/w-10-layout-authoring-attempts.json').read_bytes())
artifacts=baseline['artifacts']['linux-x64-gcc13']
for v in final.values():assert v['sha256']==artifacts[v['artifact']]['sha256']
unchanged={}
for n in subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','source','tests','spec/contracts','spec/fixtures','CMakeLists.txt','CMakePresets.json','build-support/components.json'],text=True).splitlines():
    if n=='tests/editor/native_layout_authoring.py':continue
    assert (r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]);unchanged[n]=sha(r/n)
native=json.loads((r/(prefix+'native-index.json')).read_bytes());final_native={}
families={'EDITOR-LAYOUT':21,'EDITOR-OBSERVATION':7,'EDITOR-WIDGET-CREATION':17,'EDITOR-BINDING-AUTHORING':15,'EDITOR-CONTENT-PROPERTIES':15,'EDITOR-SNAP':13,'EDITOR-GROUP':11,'EDITOR-ARRANGE':14,'EDITOR-FORM':20,'LARGE-COMMANDS':24}
for family,count in families.items():
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);v=json.loads((r/row['path']).read_bytes());assert v['outcome']=='pass' and len(v['cases'])==count
    assert all(c.get('outcome',c.get('result'))=='pass' for c in v['cases'])
    final_native[family]={**{k:row[k] for k in ('path','sha256')},'cases':count}
diagnostics=[]
for row in native:
    if row['family'] not in ('MODAL-FOCUS-DIAGNOSTIC','MODAL-FOCUS-MINIMAL-DIAGNOSTIC','MODAL-FOCUS-ORDERED-DIAGNOSTIC'):continue
    v=json.loads((r/row['path']).read_bytes());assert v['outcome']=='observed'
    diagnostics.append({**{k:row[k] for k in ('path','sha256','family')},'cases':len(v['cases'])})
assert len(diagnostics)==3 and sum(v['cases'] for v in diagnostics)==24
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,executed_helpers=executed_helpers,attempts=attempts,final_runs=final,unchanged_source_contracts_fixtures=unchanged,baseline_artifacts=ref(r/'build-support/evidence/w-10-layout-authoring-attempts.json'),artifacts=artifacts,originals=originals,upstream=dict(record=ref(history/'upstream.json'),archive=ref(history/'upstream.zip')),native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,diagnostics=diagnostics,scope='Per-key navigation acknowledgement restores keyboard layout activation; alignment awaits fixed pixel completion before selection changes. All 157 native cases pass. Production source/binary and all existing product expectations remain unchanged; earlier unrelated failures and complete editions remain open.'))
print('Preserved',len(attempts),'attempts and',len(native),'native archives.')
