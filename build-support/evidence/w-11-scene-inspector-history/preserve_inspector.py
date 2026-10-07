from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-11-scene-inspector-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='1d25768390f7629d7a956c9ac945cffed884368c'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-11-scene-inspector').glob('*/result.json')):
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
helpers=['inspector_step.py','inspector_flow.py','inspector_external_flow.py','archive_inspector.py','reclaim_inspector_captures.py',
    'reclaim_inspector_inputs.ps1','reclaim_inspector_prior.ps1','scene-inspector-input-reclamation.json','scene-inspector-prior-reclamation.json',
    'prepare_inspector.py','setup_inspector_build.py','preserve_inspector.py']
for p in [*sorted((r/'out/campaign').glob('scene-inspector-execution-*.json')),*sorted((r/'out/campaign').glob('scene-inspector-external-*.json')),*(r/'out/campaign'/n for n in helpers)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/scene-inspector-original').iterdir():shutil.copyfile(p,history/p.name)
current=None;final={};artifacts={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
    latest=max((a for a in attempts if a['profile']==profile and a['action']=='test'),key=lambda a:a['finished_at']);v=json.loads((r/latest['path']).read_text())
    assert not v['exit'] and not v['source_changed_during_execution']
    if current is None:current=v['source_inputs']
    assert v['source_inputs']==current
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==len(set(cases)) and len(cases)>=73
    assert sum(c.startswith('scene.') for c in cases)==68
    if profile.startswith('linux'):assert len(cases)==84 and 'native.SCENE-INSPECTOR-MODEL' in cases
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
for n in ('syspane_scene_inspector_tests','libsyspane_scene_inspector.a','syspane_scene_tests','syspane_scene_surface_tests','syspane_protocol_tests','syspane_data_view_tests','SysPane.ImageWorker','SysPane.TextProbe','libsyspane_scene_surface.a','libsyspane_scene.a'):
 p=b/n;v[n]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
print(json.dumps(v))"""
        artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
    else:
        binary_root=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
        names=['syspane_scene_tests.exe','syspane_protocol_tests.exe','syspane_data_view_tests.exe']
        artifacts[profile]={n:dict(sha256=sha(binary_root/n),bytes=(binary_root/n).stat().st_size) for n in names if (binary_root/n).exists()}
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][v['test_artifact']]['sha256']
for name,digest in current.items():assert sha(r/name)==digest,('tested input changed',name)
native=json.loads((r/(prefix+'native-index.json')).read_text());final_native={}
families={'SCENE-INSPECTOR':('syspane_scene_inspector_tests','tests/scene/native_inspector.py'),
    **{n+'-ERASURE':('syspane_scene_surface_tests','tests/scene/native_surface.py') for n in ('SCENE','TABLE','CONTENT','CHART','IMAGE')}}
for family,(artifact,oracle) in families.items():
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);report=json.loads((r/row['path']).read_text());assert report['outcome']=='pass'
    assert report['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256'],family
    assert report['oracle_sha256']==sha(r/oracle),(family,oracle)
    assert all(c['outcome']=='pass' for c in report['cases'])
    assert len(report['cases'])==(7 if family=='SCENE-INSPECTOR' else 3)
    with zipfile.ZipFile(r/row['archive']['path']) as z:
        for c in report['cases']:
            raw=z.read(c['case']+'/result.json');assert hashlib.sha256(raw).hexdigest()==c['record_sha256']
            detail=json.loads(raw);assert detail['executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256']
            if family=='SCENE-INSPECTOR':
                assert detail['fixture_sha256']==sha(r/'tests/scene/inspector-cases.json')
                assert detail['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')
                assert detail['worker_sha256']==artifacts['linux-x64-gcc13']['SysPane.ImageWorker']['sha256']
                if c['case'] in ('retain','wrong-selection'):assert c['fault_detected'] and detail['fault_detected']
            else:
                assert detail['text_probe_sha256']==artifacts['linux-x64-gcc13']['SysPane.TextProbe']['sha256']
                assert detail['runtime_identity_sha256']==sha(r/'build-support/text-runtime.json')
                if family=='IMAGE-ERASURE':
                    assert detail['image_worker_sha256']==artifacts['linux-x64-gcc13']['SysPane.ImageWorker']['sha256']
                    assert detail['image_oracle_sha256']==sha(r/'tests/scene/image-cases/surface.json')
    final_native[family]={**{k:row[k] for k in ('path','sha256')},'artifact':artifact,'oracle':oracle,'cases':len(report['cases'])}
original=json.loads((history/'original.json').read_text())
for n,digest in original.items():
    if n!='spec/delivery/packages/w-11-scene-inspector.md':assert sha(r/n)==digest,('fixed expectation changed',n)
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,final_runs=final,artifacts=artifacts,
    originals={n:dict(record=ref(history/(n+'.json')),archive=ref(history/(n+'.zip'))) for n in ('original','native-original')},
    native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,
    scope='Affected scene, policy, DataView and dependency checks on three development profiles; owned Linux GTK inspector and five external scene-erasure families. No installed edition, historical OS or release qualification.'))
print('Preserved',len(attempts),'attempts; final counts:',{p:len(v['cases']) for p,v in final.items()})
