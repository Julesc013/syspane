from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-runtime-observation-';hp='build-support/evidence/runtime-observation-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_bytes());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
ps=r/'out/campaign/runtime-observation-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode());subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
subprocess.run(['git','add','--renormalize','--',prefix+'history'],check=True);assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths)
cache={};digests={}
def content(p):
 if p not in cache:cache[p]=subprocess.check_output(['git','show',':'+p])
 return cache[p]
def check(p,digest):
 if p not in digests:digests[p]=hashlib.sha256(content(p)).hexdigest()
 assert digests[p]==digest,('staged identity differs',p)
def refs(v):
 if isinstance(v,dict):
  if 'path' in v and 'sha256' in v:check(v['path'],v['sha256'])
  for child in v.values():refs(child)
 elif isinstance(v,list):
  for child in v:refs(child)
index=json.loads(content(prefix+'attempts.json'));refs(index)
for n,digest in index['current_inputs'].items():check(n,digest)
for row in index['attempts']:
 v=json.loads(content(row['path']));assert v['source_base']==h['source_ref'] and v['exit']==row['exit']
 with zipfile.ZipFile(io.BytesIO(content(row['source_archive']['path']))) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 if 'ctest_log' in row:
  with zipfile.ZipFile(io.BytesIO(content(row['ctest_log']['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
for profile,actions in index['final_runs'].items():
 for action,row in actions.items():
  v=json.loads(content(row['record']['path']));assert not v['exit'] and not v['source_changed_during_execution'] and v['source_inputs']==index['current_inputs']
  if action!='build':assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==index['artifacts'][profile][v['test_artifact']]['sha256']
before=json.loads(content(index['baseline_validation']['path']));assert not before['exit']
assert {n for n in index['current_inputs'] if before['source_inputs'][n]!=index['current_inputs'][n]}=={'source/scene/image.cpp'}
def support(n):return content(index['support']['out/campaign/'+n]['path'])
for name in ('fixed-inputs','validation-oracle'):
 fixed=json.loads(support('runtime-observation/'+name+'.json'));raw=support('runtime-observation/'+name+'.zip');assert hashlib.sha256(raw).hexdigest()==fixed['archive_sha256']
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
 if name=='validation-oracle':
  for n,digest in fixed['inputs'].items():check(n,digest)
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
  for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
  for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
  assert json.loads(z.read('result.json'))==json.loads(content(row['path']))
mapping={'EDITOR-REFRESH':('syspane_editor_window','tests/editor/native_refresh.py'),'EDITOR-BINDING-AUTHORING':('syspane_editor_window','tests/editor/native_binding_authoring.py'),'SCENE-INSPECTOR':('syspane_scene_inspector_tests','tests/scene/native_inspector.py'),'SETTINGS-FORM':('syspane_settings_window','tests/configuration/native_settings.py'),'TEXT-RASTER':('SysPane.TextProbe','tests/scene/native_text.py'),'IMAGE-DECODE':('SysPane.ImageWorker','tests/scene/image_native.py')}
for family,row in index['final_native'].items():
 v=json.loads(content(row['path']));assert v['outcome']=='pass';artifact,oracle=mapping.get(family,('syspane_scene_surface_tests','tests/scene/native_surface.py'))
 check(oracle,v['oracle_sha256']);assert v.get('executable_sha256',v.get('worker_sha256'))==index['artifacts']['linux-x64-gcc13'][artifact]['sha256']
query=json.loads(content(index['query_diagnostic']['path']));assert not query['changed_inputs'] and len(query['cases'])==6 and all(c['outcome']=='pass' and not c['query_errors'] for c in query['cases'])
for n,digest in query['inputs'].items():check(index['support'][n]['path'] if n.startswith('out/campaign/') else n,digest)
verification=json.loads(content(prefix+'verification.json'));refs(verification);assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for group in ('tool_inputs','unchanged_old_contracts'):
 for n,digest in verification[group].items():check(n,digest)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value=dict(outcome='pass',staged_files=len(paths),verified_staged_file_hashes=len(digests),preserved_attempts=len(index['attempts']),native_archives=len(native),unchanged_contract_fixture_files=len(verification['unchanged_old_contracts']),scope='Staged source, fixed acceptance, original/candidate measurements, native traces and artifact identities match their records. Historical accessibility timeout causes and complete-edition gates stay open.')
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass';jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')));(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n');subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))
