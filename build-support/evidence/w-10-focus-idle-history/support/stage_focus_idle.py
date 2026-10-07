from pathlib import Path
import hashlib,io,json,subprocess,zipfile,jsonschema
r=Path.cwd();prefix='build-support/evidence/w-10-focus-idle-';hp='build-support/evidence/focus-idle-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_bytes());paths=h['changed_files'];assert not any('xauthority' in p or '.private.' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/focus-idle-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode());subprocess.run(['git','--literal-pathspecs','add','--pathspec-from-file='+str(ps),'--pathspec-file-nul'],check=True)
subprocess.run(['git','add','--renormalize','--',prefix+'history'],check=True)
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
 if 'ctest_log' in row:
  with zipfile.ZipFile(io.BytesIO(content(row['ctest_log']['path']))) as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
for profile,actions in index['final_runs'].items():
 for action,row in actions.items():
  v=json.loads(content(row['record']['path']));assert not v['source_changed_during_execution'] and v['source_inputs']==index['current_inputs']
  assert bool(v['exit']) if action in ('editors','rendering') else not v['exit']
  if action not in ('build','configure'):assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==index['artifacts'][profile][v['test_artifact']]['sha256']
for profile,row in index['configured_windows_graphs'].items():
 assert b'syspane_editor_form|' not in content(row['path']) and b'syspane_editor_refresh_probe|' not in content(row['path'])
 before=json.loads(content('build-support/evidence/w-10-edit-locks-attempts.json'))['artifacts'][profile];assert index['artifacts'][profile]==before
def support(n):return content(index['support']['out/campaign/'+n]['path'])
for name in ('fixed-inputs','fixed-regression'):
 fixed=json.loads(support('focus-idle/'+name+'.json'));raw=support('focus-idle/'+name+'.zip');assert hashlib.sha256(raw).hexdigest()==fixed['archive_sha256']
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
fixed=json.loads(support('focus-idle/fixed-inputs.json'))
for n,digest in fixed['inputs'].items():
 if n=='source/interfaces/editor_form_linux.cpp':continue
 check(index['support'][n]['path'] if n.startswith('out/campaign/') else n,digest)
correction=json.loads(support('focus-idle/oracle-correction.json'))
for n,digest in correction['new'].items():check(n,digest)
check('tests/editor/refresh-cases.json',correction['unchanged_fixture_sha256'])
before=next(json.loads(content(a['path'])) for a in index['attempts'] if 'refresh-989a48ef0f' in a['path'])
after=next(json.loads(content(a['path'])) for a in index['attempts'] if 'refresh-9db840f9da' in a['path'])
assert {n for n in before['source_inputs'] if before['source_inputs'][n]!=after['source_inputs'][n]}==set(correction['new'])
for n,digest in correction['old'].items():assert before['source_inputs'][n]==digest
for n,digest in correction['new'].items():assert after['source_inputs'][n]==digest
native=json.loads(content(index['native_index']['path']));refs(native)
for row in native:
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  assert set(z.namelist())==set(row['files'])|set(row.get('links',{}))
  for n,digest in row['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest
  for n,target in row.get('links',{}).items():assert z.read(n).decode()==target
  assert json.loads(z.read('result.json'))==json.loads(content(row['path']))
for family,row in index['final_native'].items():
 report=json.loads(content(row['path']));assert report['outcome']=='pass'
 assert report['executable_sha256']==index['artifacts']['linux-x64-gcc13'][row['artifact']]['sha256'];check(row['oracle'],report['oracle_sha256'])
 assert all(c.get('outcome',c.get('result'))=='pass' for c in report['cases']) and len(report['cases'])==row['cases']
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  for case in report['cases']:
   if 'record_sha256' not in case:continue
   raw=z.read(case['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==case['record_sha256']
   detail=json.loads(raw)
   if 'observation_helper_sha256' in detail:check('tests/editor/native_observation.py',detail['observation_helper_sha256'])
   if 'executable_sha256' in detail:assert detail['executable_sha256']==index['artifacts']['linux-x64-gcc13']['syspane_editor_window']['sha256']
for family,row in index['failed_native'].items():
 report=json.loads(content(row['path']));assert report['outcome']=='fail'
 check(row['oracle'],report['oracle_sha256']);assert report['executable_sha256']==index['artifacts']['linux-x64-gcc13'][row['artifact']]['sha256']
 with zipfile.ZipFile(io.BytesIO(content(row['archive']['path']))) as z:
  mode='selector' if family=='EDITOR-BINDING-AUTHORING' else 'translated'
  detail=json.loads(z.read(mode+'/result.json'));error=z.read(mode+'.stderr').decode();assert detail['outcome']=='fail' and 'timeout from dbind' in error
  assert ('o.get_role()' if mode=='selector' else 'table.get_selected_rows()') in error
verification=json.loads(content(prefix+'verification.json'));refs(verification);assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for group in ('tool_inputs','unchanged_old_contracts'):
 for n,digest in verification[group].items():check(n,digest)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
value=dict(outcome='pass',staged_files=len(paths),verified_staged_file_hashes=len(digests),preserved_attempts=len(index['attempts']),native_archives=len(native),final_editor_cases=sum(v['cases'] for v in index['final_native'].values()),unchanged_contract_fixture_files=len(verification['unchanged_old_contracts']),scope='Staged source, fixed inputs, original failures, native observations and executable/environment identities match their records. Complete editions and remaining acceptance gates stay open.')
(r/sp).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');next(c for c in h['checks'] if c['evidence']==sp)['outcome']='pass';jsonschema.validate(h,json.loads(content('spec/contracts/handoff.schema.json')));(r/hp).write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp,hp],check=True);print(json.dumps(value))
