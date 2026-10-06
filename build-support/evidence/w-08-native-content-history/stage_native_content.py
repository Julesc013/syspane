from pathlib import Path
import hashlib,io,json,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-08-native-content-';hp='build-support/evidence/native-content-handoff.json';sp=prefix+'staging.json'
h=json.loads((r/hp).read_text());paths=h['changed_files']
allowed=set(json.loads((r/'out/campaign/native-content-allowed.json').read_text()))
assert all(p in allowed or p.startswith(prefix) for p in paths),set(paths)-allowed
assert not any('.private.' in p for p in paths)
(r/sp).write_text('{"outcome":"pending"}\n',encoding='utf-8',newline='\n')
ps=r/'out/campaign/native-content-staging-paths.txt';ps.write_bytes(('\0'.join(paths)+'\0').encode())
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
   assert '.private.' not in n and not n.startswith(('/','\\')) and '..' not in n.split('/')
   assert hashlib.sha256(z.read(n)).hexdigest()==digest;archived.add(n)
for profile,count in [('linux-x64-gcc13',170),('windows-x64-gcc15',152),('windows-x86-v141-xp',139)]:
 row=index['full_runs'][profile];v=json.loads(content(row['record']['path']))
 assert v['exit']==0 and len(row['cases'])==count and all(c['outcome']=='pass' for c in row['cases'])
 assert v['source_inputs']==index['current_inputs']
for family,count,exe,oracle in [('CONTENT-COMMANDS',9,'SysPane.CommandProbe','native_content_commands.py'),('RESOURCE-GENERATIONS',31,'SysPane.ConfigProbe','native_resources.py'),('CONTENT-READER',17,'SysPane.ContentProbe','native_content.py'),('TRANSACTION-SUPERVISION',7,'SysPane.CommandProbe','native_supervision.py'),('RECONCILIATION',6,'SysPane.CommandProbe','native_reconciliation.py'),('COMMAND-IPC',6,'SysPane.CommandProbe','native_command.py'),('CONFIG-STORE',20,'SysPane.ConfigProbe','native_store.py')]:
 native=json.loads(content(index['final_'+family]['path']));assert native['outcome']=='pass' and len(native['cases'])==count
 if 'store_executable_sha256' in native:assert native['store_executable_sha256']==index['artifacts']['linux-x64-gcc13']['SysPane.ConfigProbe']['sha256']
 assert native['executable_sha256']==index['artifacts']['linux-x64-gcc13'][exe]['sha256'];check('tests/configuration/'+oracle,native['oracle_sha256'])
audit=json.loads(content(index['historical_audit']['path']));assert audit['outcome']=='pass' and len(audit['artifacts'])==17
for n,digest in audit['verification_inputs'].items():check(n,digest)
check(prefix+'history/audit_native_content_legacy.py',audit['helper_sha256'])
assert index['artifacts']['windows-x86-v141-xp']['syspane_authored_tests.exe']['sha256']==audit['artifacts']['syspane_authored_tests.exe']['sha256']
verification=json.loads(content(prefix+'verification.json'));references(verification)
assert all(c['exit']==0 for c in verification['checks']) and verification['final_workspace_budget']['status']=='pass'
for n,digest in verification['tool_inputs'].items():check(n,digest)
for p in paths:
 if p.startswith('spec/'):assert content(p)==(r/p).read_bytes(),('sealed bytes normalized',p)
subprocess.run(['git','diff','--cached','--check'],check=True)
result={'outcome':'pass','staged_files':len(paths),'verified_staged_file_hashes':len(digests),'archived_input_paths':len(archived),
 'full_suite_counts':{p:len(v['cases']) for p,v in index['full_runs'].items()},'native_final_cases':{'CONTENT-COMMANDS':9,'RESOURCE-GENERATIONS':31,'CONTENT-READER':17,'TRANSACTION-SUPERVISION':7,'RECONCILIATION':6,'COMMAND-IPC':6,'CONFIG-STORE':20},
 'scope':'Final source/package/schema/fixture/oracle inputs match all three passing full runs. Every attempt archive, native/historical artifact bindings and sealed specification identity are verified against staged bytes.'}
(r/sp).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
subprocess.run(['git','add','--',sp],check=True);subprocess.run(['git','diff','--cached','--check'],check=True);print(json.dumps(result))
