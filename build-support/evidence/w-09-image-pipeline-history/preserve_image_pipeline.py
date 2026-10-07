from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-09-image-pipeline-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return dict(path=p.relative_to(r).as_posix(),sha256=sha(p))
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='e503d290a2c905918abf04e71d85a38642458d1d'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-09-image-pipeline').glob('*/result.json')):
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
helpers=['image_pipeline_step.py','image_pipeline_flow.py','archive_image_pipeline.py','reclaim_image_replies.py','reclaim_image_inputs.ps1','reclaim_image_surface_inputs.ps1','reclaim_image_chart_inputs.ps1','reclaim_image_table_inputs.ps1','image-chart-reclamation.json','image-table-reclamation.json',
         'image-input-reclamation.json','image-surface-reclamation.json','image-reply-reclamation.json','image_jpeg_fixture.cpp','generate_image_jpeg_fixtures.py','image-jpeg-fixture-generation.json','setup_image_pipeline.py']
for p in [*sorted((r/'out/campaign').glob('image-pipeline-execution-*.json')),*(r/'out/campaign'/n for n in helpers),Path(__file__)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/image-pipeline-original').iterdir():shutil.copyfile(p,history/p.name)
current=None;final={};artifacts={}
for profile,count in (('linux-x64-gcc13',77),('windows-x64-gcc15',71),('windows-x86-v141-xp',72)):
    latest=max((a for a in attempts if a['profile']==profile and a['action']=='test'),key=lambda a:a['finished_at']);v=json.loads((r/latest['path']).read_text())
    assert not v['exit'] and not v['source_changed_during_execution']
    if current is None:current=v['source_inputs']
    assert v['source_inputs']==current
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout']);assert len(cases)==count and len(set(cases))==count
    assert len([n for n in cases if n.startswith('scene.IMAGE-')])==3
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
for n in ('syspane_scene_tests','syspane_scene_surface_tests','syspane_image_job_tests','SysPane.ImageWorker','SysPane.RecoveryProbe','SysPane.CommandProbe','SysPane.ConfigProbe','libsyspane_scene.a','libsyspane_native_image.a','libsyspane_image_job.a','libsyspane_child.a'):
 p=b/n;v[n]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
print(json.dumps(v))"""
        artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
    else:
        binary_root=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
        names=['syspane_scene_tests.exe','syspane_scene.lib' if profile.endswith('xp') else 'libsyspane_scene.a']
        if not profile.endswith('xp'):names+=['SysPane.RecoveryProbe.exe','libsyspane_child.a']
        artifacts[profile]={n:dict(sha256=sha(binary_root/n),bytes=(binary_root/n).stat().st_size) for n in names}
    n='syspane_scene_tests'+('' if profile.startswith('linux') else '.exe');assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][n]['sha256']
for name,digest in current.items():assert sha(r/name)==digest,('tested input changed',name)
native=json.loads((r/(prefix+'native-index.json')).read_text());final_native={}
for family,artifact in (('IMAGE-DECODE','SysPane.ImageWorker'),('TRANSACTION-SUPERVISION','SysPane.CommandProbe')):
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime']);report=json.loads((r/row['path']).read_text());assert report['outcome']=='pass'
    assert report['worker_sha256' if family=='IMAGE-DECODE' else 'executable_sha256']==artifacts['linux-x64-gcc13'][artifact]['sha256']
    if family=='IMAGE-DECODE':assert len(report['cases'])==54 and report['oracle_sha256']==sha(r/'tests/scene/image_native.py')
    final_native[family]={k:row[k] for k in ('path','sha256')}
cutoff=min(datetime.fromisoformat(json.loads((r/a['path']).read_text())['started_at']).timestamp() for a in attempts)
root=r/'out/build/windows-x64-gcc15/native-evidence';files=[p for p in root.iterdir() if p.is_file() and p.stat().st_mtime>=cutoff and (p.name.startswith('RECOVERY-01-') or p.name.startswith('failure-'))]
windows_reports=[];zp=history/'windows-recovery.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,p.name)
    for p in files:
        if p.name.startswith('RECOVERY-01-'):
            v=json.loads(p.read_text());assert v['outcome']=='pass' and v['executable_sha256']==artifacts['windows-x64-gcc15']['SysPane.RecoveryProbe.exe']['sha256'];windows_reports.append(p.name)
assert windows_reports
write(r/(prefix+'attempts.json'),dict(source_base=base,recorded_at=datetime.now(timezone.utc).isoformat(),current_inputs=current,attempts=attempts,final_runs=final,artifacts=artifacts,
    originals={n:dict(record=ref(history/(n+'.json')),archive=ref(history/(n+'.zip'))) for n in ('fit-original','native-original')},
    native_index=ref(r/(prefix+'native-index.json')),final_native=final_native,windows_recovery=dict(archive=ref(zp),files={p.name:sha(p) for p in files},reports=windows_reports),
    scope='Affected three-toolchain image/scene/dependency checks and native Linux codec/job/child-supervision evidence; modern Windows child recovery. No operational image scene or historical OS/release qualification.'))
print('Preserved',len(attempts),'attempts; final counts:',{p:len(v['cases']) for p,v in final.items()})
