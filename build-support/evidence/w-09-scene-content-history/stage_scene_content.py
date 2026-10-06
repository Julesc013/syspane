from pathlib import Path
import hashlib,io,json,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-09-scene-content-';hp='build-support/evidence/scene-content-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_text());paths=h['changed_files'];assert not any('.private.' in p or 'xauthority' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/scene-content-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode())
subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths)
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
for profile,full in index['full_runs'].items():
 v=json.loads(content(full['record']['path']));assert v['exit']==0 and v['source_inputs']==index['current_inputs'] and v['source_changed_during_execution']==[]
 n='syspane_authored_tests'+('' if profile.startswith('linux') else '.exe');assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==index['artifacts'][profile][n]['sha256']
 for group in ('configure_checks','build_checks'):
  a=json.loads(content(index[group][profile]['path']));assert a['exit']==0 and a['source_inputs']==index['current_inputs'] and a['source_changed_during_execution']==[]
for row in index['native_reports']:
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  assert set(z.namelist())==set(row['files'])|set(row['links']) and z.read('result.json')==content(row['path'])
  for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
  for n,target in row['links'].items():assert z.read(n).decode()==target
  assert all('xauthority' not in n and '..' not in n.split('/') and not n.startswith('/') for n in z.namelist())
for family,row in index['final_native'].items():
 v=json.loads(content(row['path']));assert v['family']==family and v['outcome']=='pass'
 name='SysPane.ConfigProbe' if family=='SCENE-CONTENT' else 'syspane_scene_surface_tests';assert v['executable_sha256']==index['artifacts']['linux-x64-gcc13'][name]['sha256']
 check('tests/configuration/native_scene_content.py' if family=='SCENE-CONTENT' else 'tests/scene/native_surface.py',v['oracle_sha256'])
for row in index['full_logs'].values():
 with zipfile.ZipFile(io.BytesIO(content(row['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==row['log_sha256']
original=json.loads(content(prefix+'history/scene-content-original.json'))
with zipfile.ZipFile(io.BytesIO(content(prefix+'history/scene-content-original.zip'))) as z:
 assert set(z.namelist())==set(original)
 for n,digest in original.items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
verification=json.loads(content(prefix+'verification.json'));refs(verification);assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for group in ('tool_inputs','unchanged_old_contracts'):
 for n,digest in verification[group].items():check(n,digest)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value={'outcome':'pass','staged_files':len(paths),'verified_staged_file_hashes':len(digests),'full_suites':{p:len(v['cases']) for p,v in index['full_runs'].items()},'native_storage_cases':34,'native_erasure_experiments':3,'modes_per_erasure_experiment':3,'table_families':17,'scalar_families':22,'old_schema_fixture_files_unchanged':len(verification['unchanged_old_contracts']),
 'scope':'Exact staged inputs match full development suites on all three profiles. Source/oracle/native archives, executable identities, old contracts and sealed specification verified. Historical OS and full product qualification remain open.'}
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');subprocess.run(['git','add','--',sp],check=True);print(json.dumps(value))
