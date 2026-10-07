from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,uuid,zipfile
r=Path(__file__).resolve().parents[2];profile,action=sys.argv[1:3]
assert profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp')
assert action in ('configure','build','focus','oracle','scalar','table','content','chart','resources','image','native','exit','surface','large','test')
directory=r/'out/campaign/w-08-large-commands'/(profile+'-'+action+'-'+uuid.uuid4().hex[:10]);directory.mkdir(parents=True)
paths=[r/'CMakeLists.txt',r/'CMakePresets.json',r/'spec/delivery/packages/w-08-large-commands.md']
for folder in ('source','tests','build-support','spec/contracts','spec/fixtures','spec/experience'):
    paths.extend(p for p in (r/folder).rglob('*') if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts)
inputs={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
with zipfile.ZipFile(directory/'source-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for name in inputs:z.write(r/name,name)
command={'large':['ctest','--preset',profile,'-R','^native[.]LARGE-COMMANDS$','--output-on-failure'],'native':['ctest','--preset',profile,'-R','^native[.]EDITOR-FORM$','--output-on-failure'],'exit':['ctest','--preset',profile,'-R','^native[.]EDITOR-EXIT$','--output-on-failure'],'surface':['ctest','--preset',profile,'-R','^native[.](SCENE-(SURFACE|IMAGE|CHART|TABLE|INSPECTOR|INSPECTOR-MODEL)|(SCENE|TABLE|CHART|CONTENT|IMAGE)-ERASURE)$','--output-on-failure'],'image':['ctest','--preset',profile,'-R','^native[.]IMAGE-ERASURE$','--output-on-failure'],'resources':['ctest','--preset',profile,'-R','^native[.](CONTENT-READER|RESOURCE-GENERATIONS|SCENE-CONTENT|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC)$','--output-on-failure'],'chart':['ctest','--preset',profile,'-R','^native[.]CHART-ERASURE$','--output-on-failure'],'scalar':['ctest','--preset',profile,'-R','^native[.]SCENE-ERASURE$','--output-on-failure'],'table':['ctest','--preset',profile,'-R','^native[.]TABLE-ERASURE$','--output-on-failure'],'content':['ctest','--preset',profile,'-R','^native[.]CONTENT-ERASURE$','--output-on-failure'],'configure':['cmake','--preset',profile],'build':['cmake','--build','--preset',profile],'focus':['ctest','--preset',profile,'-R','^configuration[.]LARGE-','--output-on-failure'],'oracle':['ctest','--preset',profile,'-R','^native[.]SETTINGS-FORM$','--output-on-failure'],'test':['ctest','--preset',profile,'-R','^(editor[.]|settings[.]|configuration[.]|composition[.]|protocol[.])','--output-on-failure']}[action]
if profile=='linux-x64-gcc13':command=['env','SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498',*command]
artifact_root=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13') if profile.startswith('linux') else r/'out/build'/profile
if profile.endswith('xp'):artifact_root=artifact_root/'Release'
artifact_name='syspane_large_command_tests' if profile.startswith('linux') else 'syspane_large_command_tests.exe'
if profile.startswith('linux'):
    artifact_name={'large':'SysPane.CommandProbe','native':'syspane_editor_window','exit':'SysPane.EditorExitProbe','oracle':'syspane_settings_window','surface':'syspane_scene_surface_tests'}.get(action,artifact_name)
artifact=artifact_root/artifact_name
guarded=action not in ('configure','build')
artifact_before=hashlib.sha256(artifact.read_bytes()).hexdigest() if guarded else None
started=datetime.now(timezone.utc).isoformat();p=subprocess.run(command,cwd=r,capture_output=True,text=True,encoding='utf-8',errors='replace')
value={'profile':profile,'action':action,'command':command,'source_base':subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),'source_inputs':inputs,'test_artifact':artifact_name,'test_artifact_sha256':artifact_before,'source_archive_sha256':hashlib.sha256((directory/'source-inputs.zip').read_bytes()).hexdigest(),'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
value['source_changed_during_execution']=[n for n,h in inputs.items() if hashlib.sha256((r/n).read_bytes()).hexdigest()!=h]
if guarded:
    value['test_artifact_after_sha256']=hashlib.sha256(artifact.read_bytes()).hexdigest()
    if value['test_artifact_after_sha256']!=artifact_before or value['source_changed_during_execution']:value['exit']=1
if action in ('test','focus','oracle','scalar','table','content','chart','resources','image','native','exit','surface','large'):
    log_root=artifact_root.parent if profile.endswith('xp') else artifact_root
    log=log_root/'Testing/Temporary/LastTest.log'
    if log.exists():
        with zipfile.ZipFile(directory/'ctest-log.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(log,'LastTest.log')
        value['ctest_log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest()
        value['ctest_log_archive_sha256']=hashlib.sha256((directory/'ctest-log.zip').read_bytes()).hexdigest()
(directory/'result.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');print(p.stdout[-5000:],p.stderr[-3000:]);print('Attempt:',directory);sys.exit(value['exit'])
