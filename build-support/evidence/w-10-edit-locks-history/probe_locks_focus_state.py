from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid
root=Path('/mnt/d/Projects/SysPane/syspane');build=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
assert os.geteuid()!=0
sys.path[:0]=[str(root/'tests/editor'),str(root/'tests/fault')]
from native_diagnostic import launch_xvfb
if len(sys.argv)>1 and sys.argv[1]=='--observe':
 from native_editor import Harness,observe
 original=Harness.focus_snapshot
 def snapshot(self,id):
  value=original(self,id);rows=[]
  for obj in self.objects():
   try:
    if self.state(obj,self.Atspi.StateType.FOCUSED) or obj.get_role_name()=='frame':rows.append(dict(identity=self.observer.identity(obj),description=obj.get_description(),name=obj.get_name(),role=obj.get_role_name(),states={n:self.state(obj,getattr(self.Atspi.StateType,n)) for n in ('FOCUSED','ACTIVE','SENSITIVE','ENABLED','VISIBLE','SHOWING')}))
   except Exception as error:rows.append(dict(error=str(error)))
  value['focused_objects_and_frame']=rows;return value
 Harness.focus_snapshot=snapshot
 observe(build/'syspane_editor_window',build/'SysPane.EditorExitProbe',Path(sys.argv[2]),'revoke',True)
 sys.exit(0)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
folder=build/'native-evidence'/('locks-focus-state-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700)
report=dict(family='LARGE-COMMANDS-DIAGNOSTIC',outcome='observed',scope='Six bounded reproductions; extra read-only focus-owner observations run only after the original focus assertion has failed. Unchanged acceptance checks and production.',inputs={str(p.relative_to(root)):sha(p) for p in (root/'tests/editor/native_editor.py',root/'tests/editor/native_observation.py',root/'tests/configuration/large-command-cases.json',Path(__file__))},executable_sha256=sha(build/'syspane_editor_window'),cases=[],started_at=datetime.now(timezone.utc).isoformat())
server=None
try:
 server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 for i in range(6):
  name='revoke-'+str(i+1);command=['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(folder/name)]
  child=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  try:out,err=child.communicate(timeout=40)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
  (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err);detail=folder/name/'result.json'
  report['cases'].append(dict(case=name,exit=child.returncode,result=json.loads(detail.read_bytes())['outcome'] if detail.exists() else 'missing',record_sha256=sha(detail) if detail.exists() else None))
finally:
 if server:server.terminate();server.communicate(timeout=5)
 report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(path=str(folder/'result.json'),cases=report['cases'])),flush=True)
