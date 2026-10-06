from pathlib import Path
import hashlib,io,json,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-09-table-';hp='build-support/evidence/table-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_text());paths=h['changed_files'];allowed=set(json.loads((r/'out/campaign/table-allowed.json').read_text()))
assert all(p in allowed or p.startswith(prefix) for p in paths),set(paths)-allowed
assert not any('.private.' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/table-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode())
subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())==set(paths)
cache={};digests={}
def content(p):
 if p not in cache:cache[p]=subprocess.check_output(['git','show',':'+p])
 return cache[p]
def check(p,digest):
 if p not in digests:digests[p]=hashlib.sha256(content(p)).hexdigest()
 assert digests[p]==digest,('staged identity differs',p)
def references(v):
 if isinstance(v,dict):
  if 'path' in v and 'sha256' in v:check(v['path'],v['sha256'])
  for child in v.values():references(child)
 elif isinstance(v,list):
  for child in v:references(child)
index=json.loads(content(prefix+'attempts.json'));references(index)
for n,digest in index['current_inputs'].items():check(n,digest)
archived=set()
for row in index['attempts']:
 v=json.loads(content(row['path']));assert v['source_base']==h['source_ref'] and v['exit']==row['exit']
 with zipfile.ZipFile(io.BytesIO(content(row['source_archive']['path']))) as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for n,digest in v['source_inputs'].items():
   assert not n.startswith(('/','\\')) and '..' not in n.split('/')
   assert hashlib.sha256(z.read(n)).hexdigest()==digest;archived.add(n)
v=json.loads(content(index['full_run']['record']['path']))
assert v['exit']==0 and len(index['full_run']['cases'])==225 and v['source_inputs']==index['current_inputs'] and v['source_changed_during_execution']==[]
assert v['test_artifact_after_sha256']==v['test_artifact_sha256']==index['artifacts']['syspane_scene_tests']['sha256']
for profile,row in index['configure_checks'].items():
 v=json.loads(content(row['path']));assert v['exit']==0 and v['source_inputs']==index['current_inputs']
for row in index['native_reports']:
 v=json.loads(content(row['path']))
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  assert set(z.namelist())==set(v['files'])|{'result.json'} and z.read('result.json')==content(row['path'])
  assert all('xauthority' not in n and '..' not in n.split('/') and not n.startswith('/') for n in z.namelist())
  for n,digest in row['archived_files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
  actual={n for n,digest in row['archived_files'].items() if v['files'][n]!=digest};assert actual==set(row['post_report_differences'])
  if v['outcome']=='pass':assert not actual
for family,row in index['final_native'].items():
 v=json.loads(content(row['path']));assert v['family']==family and v['outcome']=='pass' and len(v['cases'])==3
 assert v['executable_sha256']==index['artifacts']['syspane_scene_surface_tests']['sha256'];check('tests/scene/native_surface.py',v['oracle_sha256'])
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  for mode in ('normal','ignore-pixels','ignore-accessible'):
   case=json.loads(z.read(mode+'/result.json'));assert case['outcome']=='pass'
   assert case['text_probe_sha256']==index['artifacts']['SysPane.TextProbe']['sha256']
   check('build-support/text-runtime.json',case['runtime_identity_sha256']);check('build-support/surface-runtime.json',case['surface_runtime_sha256'])
   if mode=='normal':
    assert {x['case'] for x in case['observations']}=={'INITIAL','REPLACE','REVOKE','STALE','REGRANT','FRESH','DISCONNECT'}
    for name in {x['case'] for x in case['observations']}:assert any(x['case']==name and x['pixels'] and x['accessible'] and x['elapsed']<=(2 if name=='INITIAL' else .2) for x in case['observations'])
   else:assert not case['observations'][-1]['pixels' if mode=='ignore-pixels' else 'accessible']
with zipfile.ZipFile(io.BytesIO(content(index['full_ctest_log']['path']))) as z:
 raw=z.read('LastTest.log');assert hashlib.sha256(raw).hexdigest()==index['full_ctest_log']['log_sha256'] and b'SURFACE-FAMILIES 22' in raw and b'TABLE-FAMILIES 16' in raw
original=json.loads(content(prefix+'history/table-original.json'));assert original['before_implementation'];check(prefix+'history/table-original.zip',original['archive_sha256'])
with zipfile.ZipFile(io.BytesIO(content(prefix+'history/table-original.zip'))) as z:
 for n,digest in original['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
verification=json.loads(content(prefix+'verification.json'));references(verification)
assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for n,digest in verification['tool_inputs'].items():check(n,digest)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
result={'outcome':'pass','staged_files':len(paths),'verified_staged_file_hashes':len(digests),'archived_input_paths':len(archived),
 'full_linux_tests':225,'table_families':16,'scalar_families':22,'native_experiments':2,'modes_per_experiment':3,
 'scope':'Final inputs match full Linux regression run and all three configure checks. Staged current inputs, original oracles, attempt/native archives, artifact identities and sealed specification verified; Windows suites not rerun.'}
(r/sp).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp],check=True);subprocess.run(['git','diff','--cached','--check'],check=True);print(json.dumps(result))
