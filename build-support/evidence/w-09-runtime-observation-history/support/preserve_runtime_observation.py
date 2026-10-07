from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();e=r/'build-support/evidence';prefix='w-09-runtime-observation-';h=e/(prefix+'history');h.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='330c9772c73928d83a974b051c599190006d60f8'
attempts=[]
for p in sorted((r/'out/campaign/w-09-runtime-observation').glob('*/result.json')):
 v=json.loads(p.read_bytes());assert v['source_base']==base;target=h/p.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
 assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
 if 'ctest_log_archive_sha256' in v:
  shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
 attempts.append(row)
def latest(profile,action):
 row=max((a for a in attempts if a['profile']==profile and a['action']==action),key=lambda a:a['finished_at']);return row,json.loads((r/row['path']).read_bytes())
current=latest('linux-x64-gcc13','bindings')[1]['source_inputs']
for n,digest in current.items():assert sha(r/n)==digest
final={};artifacts={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
 final[profile]={}
 for action in ('build','test','portable')+(('rendering','refresh','bindings') if profile.startswith('linux') else ()):
  row,v=latest(profile,action);assert not v['exit'] and not v['source_changed_during_execution'] and v['source_inputs']==current
  cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))
  final[profile][action]=dict(record={k:row[k] for k in ('path','sha256')},cases=cases)
 command=['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','/mnt/d/Projects/SysPane/syspane/out/campaign/capture_lock_artifacts.py',profile] if profile.startswith('linux') else [str(r/'.venv/Scripts/python.exe'),'-X','utf8','out/campaign/capture_lock_artifacts.py',profile]
 artifacts[profile]=json.loads(subprocess.check_output(command,text=True))
 for action,row in final[profile].items():
  v=json.loads((r/row['record']['path']).read_bytes())
  if action!='build':assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
 assert len(final[profile]['test']['cases'])==6
 assert len(final[profile]['portable']['cases'])=={'linux-x64-gcc13':312,'windows-x64-gcc15':309,'windows-x86-v141-xp':306}[profile]
assert len(final['linux-x64-gcc13']['rendering']['cases'])==15
baseline=next(a for a in attempts if 'test-41d7544281' in a['path']);before=json.loads((r/baseline['path']).read_bytes())
assert not before['exit'] and set(before['source_inputs'])==set(current)
assert {n for n in current if before['source_inputs'][n]!=current[n]}=={'source/scene/image.cpp'}
support={};out=r/'out/campaign'
helpers=[p for p in out.iterdir() if p.is_file() and ('runtime_observation' in p.name or p.name in ('setup_runtime_runs.py','setup_runtime_evidence.py','image_poll_probe.cpp','run_image_poll_probe.py','native_query_probe.py','capture_lock_artifacts.py'))]
paths=[*helpers,*out.glob('runtime-observation-*.json'),*(p for p in (out/'runtime-observation').rglob('*') if p.is_file())]
for p in paths:
 target=h/'support'/p.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);support[p.relative_to(r).as_posix()]=ref(target)
for name in ('fixed-inputs','validation-oracle'):
 fixed=json.loads((out/'runtime-observation'/(name+'.json')).read_bytes());archive=out/'runtime-observation'/(name+'.zip');assert sha(archive)==fixed['archive_sha256']
 with zipfile.ZipFile(archive) as z:
  for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
for n,digest in json.loads((out/'runtime-observation/validation-oracle.json').read_bytes())['inputs'].items():assert sha(r/n)==digest
native=json.loads((e/(prefix+'native-index.json')).read_bytes());selected={}
for family in ('EDITOR-REFRESH','EDITOR-BINDING-AUTHORING','SCENE-INSPECTOR','SETTINGS-FORM','TEXT-RASTER','IMAGE-DECODE','SCENE-ERASURE','CHART-ERASURE','IMAGE-ERASURE','TABLE-ERASURE','CONTENT-ERASURE'):
 row=max((a for a in native if a['family']==family),key=lambda a:a['finished_mtime']);assert row['outcome']=='pass';selected[family]={k:row[k] for k in ('path','sha256','archive')}
diagnostic=next(a for a in native if a['family']=='NATIVE-QUERY-DIAGNOSTIC');v=json.loads((r/diagnostic['path']).read_bytes());assert len(v['cases'])==6 and all(c['outcome']=='pass' and not c['query_errors'] for c in v['cases'])
write(e/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,baseline_validation=baseline,final_runs=final,artifacts=artifacts,support=support,native_index=ref(e/(prefix+'native-index.json')),final_native=selected,query_diagnostic={k:diagnostic[k] for k in ('path','sha256','archive')},scope='Complete pixel validation is retained with lower development-build overhead. New rejection examples passed before implementation. Current relevant suites pass; six observation trials do not explain the historical binding/inspector timeouts. Full editions and remaining qualification stay open.'))
print('Preserved',len(attempts),'attempts,',len(native),'native archives and',len(support),'support files.')
