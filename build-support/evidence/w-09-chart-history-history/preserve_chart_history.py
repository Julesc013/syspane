from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,sys,zipfile
r=Path.cwd();prefix='build-support/evidence/w-09-chart-history-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return {'path':p.relative_to(r).as_posix(),'sha256':sha(p)}
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert base=='b3d7bf22f696cc00e615a7686298ea63f952b29e'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-09-chart-history').glob('*/result.json')):
    v=json.loads(p.read_text());assert v['source_base']==base
    target=history/p.parent.name;target.mkdir(exist_ok=True)
    for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
    assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
    with zipfile.ZipFile(target/'source-inputs.zip') as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for name,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    attempts.append({**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')})
for p in [*sorted((r/'out/campaign').glob('chart-history-execution-*.json')),r/'out/campaign/chart-history-conflict-artifact.json',
          r/'out/campaign/chart_history_step.py',r/'out/campaign/chart_history_flow.py',Path(__file__)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/chart-history-original').iterdir():shutil.copyfile(p,history/p.name)
final={};current=None;artifacts={};logs={}
for profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp'):
    latest=max((a for a in attempts if a['profile']==profile and a['action']=='test'),key=lambda a:a['finished_at'])
    v=json.loads((r/latest['path']).read_text());assert v['exit']==0 and not v['source_changed_during_execution']
    if current is None:current=v['source_inputs']
    assert v['source_inputs']==current
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout'])
    assert len(cases)==(63 if profile=='windows-x64-gcc15' else 65) and len(set(cases))==len(cases)
    assert len([n for n in cases if n.startswith('scene.CHART-')])==11
    build=max((a for a in attempts if a['profile']==profile and a['action']=='build'),key=lambda a:a['finished_at'])
    b=json.loads((r/build['path']).read_text());assert b['exit']==0 and b['source_inputs']==current and not b['source_changed_during_execution']
    final[profile]={'record':{k:latest[k] for k in ('path','sha256')},'build':{k:build[k] for k in ('path','sha256')},'cases':cases}
    if profile.startswith('linux'):
        code='''from pathlib import Path
import hashlib,json,zipfile
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');r=Path('/mnt/d/Projects/SysPane/syspane');v={}
for n in ('syspane_scene_tests','syspane_scene_surface_tests','SysPane.TextProbe','libsyspane_scene.a'):
 p=b/n;v[n]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
with zipfile.ZipFile(r/'out/campaign/chart-history-linux-log.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(b/'Testing/Temporary/LastTest.log','LastTest.log')
print(json.dumps(v))'''
        artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
        target=history/(profile+'-LastTest.zip');shutil.copyfile(r/'out/campaign/chart-history-linux-log.zip',target)
    else:
        build_root=r/'out/build'/profile;binary_root=build_root/('Release' if profile.endswith('xp') else '')
        names=('syspane_scene_tests.exe','syspane_scene.lib' if profile.endswith('xp') else 'libsyspane_scene.a')
        artifacts[profile]={n:{'sha256':sha(binary_root/n),'bytes':(binary_root/n).stat().st_size} for n in names}
        target=history/(profile+'-LastTest.zip')
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:z.write(build_root/'Testing/Temporary/LastTest.log','LastTest.log')
    artifact_name='syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][artifact_name]['sha256']
    with zipfile.ZipFile(target) as z:
        data=z.read('LastTest.log');log=data.decode('utf-8')
        for case in cases:assert 'Test: '+case in log
    logs[profile]={**ref(target),'log_sha256':hashlib.sha256(data).hexdigest()}
for name,digest in current.items():assert sha(r/name)==digest,('changed tested source',name)
index={'source_base':base,'recorded_at':datetime.now(timezone.utc).isoformat(),'current_inputs':current,'attempts':attempts,'final_runs':final,'artifacts':artifacts,'logs':logs,
       'original':ref(history/'original.json'),'original_archive':ref(history/'original.zip'),
       'scope':'Affected scene/component checks on three development profiles. Linux scalar/table regressions and historical PE controls included. No native chart drawing, historical OS or release qualification.'}
write(r/(prefix+'attempts.json'),index)
print('Preserved',len(attempts),'attempts; final counts:',{p:len(v['cases']) for p,v in final.items()})
