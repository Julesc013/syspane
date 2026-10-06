from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,zipfile
r=Path.cwd();prefix='build-support/evidence/w-09-native-chart-';history=r/(prefix+'history');history.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def ref(p):return {'path':p.relative_to(r).as_posix(),'sha256':sha(p)}
base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert base=='6cabd2c30ccdad1d97423dfaea643574cb6f840b'
subprocess.run([str(r/'.venv/Scripts/python.exe'),'-X','utf8','build-support/check_workspace_budget.py','--action','package'],check=True)
attempts=[]
for p in sorted((r/'out/campaign/w-09-native-chart').glob('*/result.json')):
    v=json.loads(p.read_text());assert v['source_base']==base
    target=history/p.parent.name;target.mkdir(exist_ok=True)
    for name in ('result.json','source-inputs.zip'):shutil.copyfile(p.parent/name,target/name)
    assert sha(target/'source-inputs.zip')==v['source_archive_sha256']
    with zipfile.ZipFile(target/'source-inputs.zip') as z:
        assert set(z.namelist())==set(v['source_inputs'])
        for name,digest in v['source_inputs'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    row={**ref(target/'result.json'),'profile':v['profile'],'action':v['action'],'exit':v['exit'],'finished_at':v['finished_at'],'source_archive':ref(target/'source-inputs.zip')}
    if 'ctest_log_archive_sha256' in v:
        shutil.copyfile(p.parent/'ctest-log.zip',target/'ctest-log.zip')
        assert sha(target/'ctest-log.zip')==v['ctest_log_archive_sha256']
        with zipfile.ZipFile(target/'ctest-log.zip') as z:assert hashlib.sha256(z.read('LastTest.log')).hexdigest()==v['ctest_log_sha256']
        row['ctest_log']=ref(target/'ctest-log.zip')
    attempts.append(row)
for p in [*sorted((r/'out/campaign').glob('native-chart-execution-*.json')),
          *(r/'out/campaign'/n for n in ('native_chart_step.py','native_chart_flow.py','archive_native_chart.py','reclaim_native_chart_captures.py','chart-native-reclaimed.json')),Path(__file__)]:shutil.copyfile(p,history/p.name)
for p in (r/'out/campaign/native-chart-original').iterdir():shutil.copyfile(p,history/p.name)
final={};current=None;artifacts={}
for profile,count in (('linux-x64-gcc13',70),('windows-x64-gcc15',67),('windows-x86-v141-xp',69)):
    latest=max((a for a in attempts if a['profile']==profile and a['action']=='test'),key=lambda a:a['finished_at'])
    v=json.loads((r/latest['path']).read_text());assert v['exit']==0 and not v['source_changed_during_execution']
    if current is None:current=v['source_inputs']
    assert v['source_inputs']==current
    cases=re.findall(r'Test\s+#\d+:\s+(\S+)\s+\.+\s+Passed',v['stdout'])
    assert len(cases)==count and len(set(cases))==count
    assert len([n for n in cases if n.startswith('scene.CHART-')])==11
    assert len([n for n in cases if n.startswith('scene.PLOT-')])==4
    build=max((a for a in attempts if a['profile']==profile and a['action']=='build'),key=lambda a:a['finished_at'])
    b=json.loads((r/build['path']).read_text());assert b['exit']==0 and b['source_inputs']==current and not b['source_changed_during_execution']
    final[profile]={'record':{k:latest[k] for k in ('path','sha256')},'build':{k:build[k] for k in ('path','sha256')},'cases':cases}
    if profile.startswith('linux'):
        code="""from pathlib import Path
import hashlib,json
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');v={}
for n in ('syspane_scene_tests','syspane_scene_surface_tests','SysPane.TextProbe','libsyspane_scene.a','libsyspane_scene_surface.a'):
 p=b/n;v[n]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
print(json.dumps(v))"""
        artifacts[profile]=json.loads(subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','ir4runner','--','python3','-c',code],text=True))
    else:
        binary_root=r/'out/build'/profile/('Release' if profile.endswith('xp') else '')
        names=('syspane_scene_tests.exe','syspane_scene.lib' if profile.endswith('xp') else 'libsyspane_scene.a')
        artifacts[profile]={n:{'sha256':sha(binary_root/n),'bytes':(binary_root/n).stat().st_size} for n in names}
    artifact_name='syspane_scene_tests'+('' if profile.startswith('linux') else '.exe')
    assert v['test_artifact_sha256']==v['test_artifact_after_sha256']==artifacts[profile][artifact_name]['sha256']
    if 'ctest_log' in latest:
        with zipfile.ZipFile(r/latest['ctest_log']['path']) as z:
            log=z.read('LastTest.log').decode('utf-8')
            for case in cases:assert 'Test: '+case in log
for name,digest in current.items():assert sha(r/name)==digest,('changed tested source',name)
native=json.loads((r/(prefix+'native-index.json')).read_text());final_native={}
for family in ('CHART-ERASURE','SCENE-ERASURE','TABLE-ERASURE','CONTENT-ERASURE'):
    row=max((n for n in native if n['family']==family),key=lambda n:n['finished_mtime'])
    report=json.loads((r/row['path']).read_text());assert report['outcome']=='pass'
    assert report['executable_sha256']==artifacts['linux-x64-gcc13']['syspane_scene_surface_tests']['sha256']
    assert report['oracle_sha256']==sha(r/'tests/scene/native_surface.py')
    assert {v['case'] for v in report['cases']}=={'normal','ignore-pixels','ignore-accessible'}
    assert all(v['outcome']=='pass' for v in report['cases'])
    final_native[family]={k:row[k] for k in ('path','sha256')}
index={'source_base':base,'recorded_at':datetime.now(timezone.utc).isoformat(),'current_inputs':current,'attempts':attempts,'final_runs':final,'artifacts':artifacts,
       'originals':{n:{'record':ref(history/(n+'.json')),'archive':ref(history/(n+'.zip'))} for n in ('original','surface-original','native-original')},
       'native_index':ref(r/(prefix+'native-index.json')),'final_native':final_native,
       'scope':'Affected scene/component checks on three development profiles; independent Linux synthetic native chart/scalar/table/content pixels and accessibility. Earlier attempts retain complete stdout; CTest logs were additionally captured by later runner versions. No installed desktop, historical OS or release qualification.'}
write(r/(prefix+'attempts.json'),index)
print('Preserved',len(attempts),'attempts; final counts:',{p:len(v['cases']) for p,v in final.items()})
