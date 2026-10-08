from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-09-native-visibility-';hp='build-support/evidence/native-visibility-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_bytes());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
ps=r/'out/campaign/native-visibility-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode());subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
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
verification=json.loads(content(prefix+'verification.json'));assert all(c['exit']==0 for c in verification['checks'])
for n,digest in index['current_inputs'].items():check(n,verification['post_test_documentation_updates'].get(n,digest))
for n,digest in index['unchanged_old_contracts'].items():check(n,digest)
for n,digest in verification['tool_inputs'].items():check(n,digest)
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
fixed=json.loads(content(index['support']['out/campaign/native-visibility-frozen.json']['path']))
for n,digest in fixed['inputs'].items():check(n,digest)
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
  for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
  for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
  v=json.loads(z.read('result.json'));assert v==json.loads(content(row['path'])) and v['outcome']==row['outcome']
 if 'oracle_sha256' in v:
  owner=json.loads(content(row['attempt']['path']));matches=[n for n,digest in owner['source_inputs'].items() if n.startswith('tests/') and digest==v['oracle_sha256']];assert matches,(row['family'],'oracle identity')
  if row['source_is_final']:
   for n in matches:check(n,v['oracle_sha256'])
 for key in ('executable_sha256','store_executable_sha256','editor_executable_sha256','worker_sha256'):
  if key in v and row['source_is_final']:assert v[key] in {item['sha256'] for item in index['artifacts']['linux-x64-gcc13'].values()},(row['family'],key)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value=dict(outcome='pass',staged_files=len(paths),verified_staged_file_hashes=len(digests),preserved_attempts=len(index['attempts']),native_archives=len(native),unchanged_contract_fixture_files=len(index['unchanged_old_contracts']),scope='Staged production/test sources, frozen expectations, archived failures and final artifact identities verified. Native controls, installed enablement and full editions remain open.')
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass';jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')));(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n');subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))
