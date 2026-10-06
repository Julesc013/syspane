from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,uuid,zipfile
r=Path(__file__).resolve().parents[2];profile,action=sys.argv[1:3]
assert profile in ('linux-x64-gcc13','windows-x64-gcc15','windows-x86-v141-xp')
assert action in ('configure','build','focus','oracle','test')
directory=r/'out/campaign/w-09-chart-history'/(profile+'-'+action+'-'+uuid.uuid4().hex[:10]);directory.mkdir(parents=True)
paths=[r/'CMakeLists.txt',r/'CMakePresets.json',r/'spec/delivery/packages/w-09-chart-history.md']
for folder in ('source','tests','build-support','spec/contracts','spec/fixtures','spec/experience'):
    paths.extend(p for p in (r/folder).rglob('*') if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts)
inputs={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
with zipfile.ZipFile(directory/'source-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for name in inputs:z.write(r/name,name)
command={'configure':['cmake','--preset',profile],'build':['cmake','--build','--preset',profile],'focus':['ctest','--preset',profile,'-R','^(scene[.]CHART-|components[.]|component[.])','--output-on-failure'],'oracle':['ctest','--preset',profile,'-R','^native[.](SCENE-(SURFACE|ERASURE|TABLE)|TABLE-ERASURE|CONTENT-ERASURE)$','--output-on-failure'],'test':['ctest','--preset',profile,'-R','^(scene[.]|composition[.]|legacy[.]|native[.]SCENE-(SURFACE|TABLE)$)','--output-on-failure']}[action]
if profile=='linux-x64-gcc13':command=['env','SYSPANE_LINUX_BUILD_ROOT=/home/ir4runner/.cache/syspane/campaign-229a498',*command]
artifact_root=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13') if profile.startswith('linux') else r/'out/build'/profile
if profile.endswith('xp'):artifact_root=artifact_root/'Release'
artifact=artifact_root/('syspane_scene_tests'+('' if profile.startswith('linux') else '.exe'))
artifact_before=hashlib.sha256(artifact.read_bytes()).hexdigest() if action in ('test','focus') else None
started=datetime.now(timezone.utc).isoformat();p=subprocess.run(command,cwd=r,capture_output=True,text=True,encoding='utf-8',errors='replace')
value={'profile':profile,'action':action,'command':command,'source_base':subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),'source_inputs':inputs,'test_artifact_sha256':artifact_before,'source_archive_sha256':hashlib.sha256((directory/'source-inputs.zip').read_bytes()).hexdigest(),'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
value['source_changed_during_execution']=[n for n,h in inputs.items() if hashlib.sha256((r/n).read_bytes()).hexdigest()!=h]
if action in ('test','focus'):
    value['test_artifact_after_sha256']=hashlib.sha256(artifact.read_bytes()).hexdigest()
    if value['test_artifact_after_sha256']!=artifact_before or value['source_changed_during_execution']:value['exit']=1
(directory/'result.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n');print(p.stdout[-5000:],p.stderr[-3000:]);print('Attempt:',directory);sys.exit(value['exit'])
