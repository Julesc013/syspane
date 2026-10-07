from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-11-settings-resources-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='252647623e2d56cbc6f2797fb9325d788d9a21d5'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-11-settings-resources').glob('*/result.json')):
 v=json.loads(p.read_text());assert v['source_base']==base;target=history/p.parent.name;target.mkdir(exist_ok=True)
 for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
 assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
 with zipfile.ZipFile(target/'source-inputs.zip') as z:
  assert set(z.namelist())==set(v['source_inputs'])
  for name,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
 row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
 if 'ctest_log_archive_sha256' in v:
  shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip');assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256'];row['ctest_log']=ref(target/'ctest-log.zip')
 attempts.append(row)
helpers=['resource_settings_step.py','resource_settings_flow.py','archive_resource_settings.py','preserve_resource_settings.py','setup_resource_settings_evidence.py','reclaim_resource_settings_prior.ps1','resource-settings-prior-reclamation.json']
for p in [*sorted((r/'out/campaign').glob('resource-settings-execution-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/resource-settings-original').iterdir():shutil.copyfile(p,history/p.name)
current=None;final={};artifacts={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
 latest=max((a for a in attempts if a['profile']==profile and a['action']=='test'),key=lambda a:a['finished_at']);v=json.loads((r/latest['path']).read_text())
 assert not v['exit'] and not v['source_changed_during_execution']
 if current is None:current=v['source_inputs']
 assert v['source_inputs']==current
 cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases))==58
 assert sum(c.startswith('settings.') for c in cases)==17
 build=max((a for a in attempts if a['profile']==profile and a['action']=='build'),key=lambda a:a['finished_at']);b=json.loads((r/build['path']).read_text())
 assert not b['exit'] and b['source_inputs']==current and not b['source_changed_during_execution']
 with zipfile.ZipFile(r/latest['ctest_log']['path']) as z:
  data=z.read('LastTest.log');assert hashlib.sha256(data).hexdigest()==v['ctest_log_sha256']
  for case in cases:assert 'Test: '+case in data.decode()
 final[profile]=dict(record={k:latest[k] for k in ('path','sha256')},build={k:build[k] for k in ('path','sha256')},cases=cases,log=latest['ctest_log'])
 if profile.startswith('linux'):
  code="""from pathlib import Path
import hashlib,json
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');v={}
for n in ('syspane_settings_tests','syspane_settings_window','libsyspane_settings_draft.a','libsyspane_settings_form.a','syspane_authored_tests','syspane_command_session_tests','syspane_protocol_tests','SysPane.ContentProbe','SysPane.ConfigProbe','SysPane.CommandProbe'):
 p=b/n;v[n]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
print(json.dumps(v))"""
  artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
 else:
  binary_root=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
  names=['syspane_settings_tests.exe','syspane_authored_tests.exe','syspane_command_session_tests.exe','syspane_protocol_tests.exe']
  artifacts[profile]={n:dict(sha256=sha(binary_root/n),bytes=(binary_root/n).stat().st_size) for n in names}
 assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
for name,digest in current.items():assert sha(r/name)==digest,('tested input changed',name)
native=json.loads((r/(prefix+'native-index.json')).read_text());final_native={}
families={'SETTINGS-FORM':('syspane_settings_window','native_settings.py')}
for family,(artifact,file) in families.items():
 oracle='tests/configuration/'+file
 row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);report=json.loads((r/row['path']).read_text());assert report['outcome']=='pass'
 assert report['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'],family
 assert report['oracle_sha256']==sha(r/oracle),(family,oracle)
 assert all(c['outcome']=='pass' for c in report['cases'])
 if 'store_executable_sha256' in report:assert report['store_executable_sha256']==artifacts['linux-x64-gcc13']['SysPane.ConfigProbe']['sha256']
 if family=='SETTINGS-FORM':
  assert len(report['cases'])==18
  with zipfile.ZipFile(r/row['archive']['path']) as z:
   for c in report['cases']:
    raw=z.read(c['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==c['record_sha256']
    detail=json.loads(raw);assert detail['executable_sha256']==report['executable_sha256'] and detail['oracle_sha256']==report['oracle_sha256']
    assert detail['fixture_sha256']==sha(r/'tests/configuration/settings-cases.json')
    assert detail['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')
    if c['case'].startswith('resource-'):
     assert detail['resource_fixture_sha256']==sha(r/'tests/configuration/settings-content-fixture.json')
     assert detail['resource_cases_sha256']==sha(r/'tests/configuration/settings-content-cases.json')
    if c['case'] in ('retain','false-saved','resource-wrong-selection'):assert c['fault_detected'] and detail['fault_detected']
 final_native[family]={**{k:row[k] for k in ('path','sha256')},'artifact':artifact,'oracle':oracle,'cases':len(report['cases'])}
original=json.loads((history/'original.json').read_text())
for n,digest in original.items():
 if n not in ('spec/delivery/packages/w-11-settings-resources.md','spec/experience/settings-registry.json'):assert sha(r/n)==digest,('fixed expectation changed',n)
for n in ('tests/configuration/settings-content-fixture.json','tests/configuration/settings_content_fixture.py'):
 assert sha(r/n)==json.loads((history/'resource-fixture.json').read_text())[n]
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,final_runs=final,artifacts=artifacts,
 originals={n:dict(record=ref(history/(n+'.json')),archive=ref(history/(n+'.zip'))) for n in ('original','resource-fixture','native-original')},
 native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,
 scope='58 affected settings/authored/policy/dependency checks on each of three development profiles; 18 owned native settings modes including exact resource selection/bytes and deliberate faults. Installed editions and historical OS qualification remain open.'))
print('Preserved',len(attempts),'attempts; final counts:',{p:len(v['cases']) for p,v in final.items()})
