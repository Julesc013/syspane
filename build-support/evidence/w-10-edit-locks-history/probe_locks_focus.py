from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid
root=Path('/mnt/d/Projects/SysPane/syspane')
build=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
assert os.geteuid()!=0
sys.path.insert(0,str(root/'tests/fault'))
from native_diagnostic import launch_xvfb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
folder=build/'native-evidence'/('locks-focus-diagnostic-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700)
report=dict(family='LARGE-COMMANDS-DIAGNOSTIC',outcome='observed',started_at=datetime.now(timezone.utc).isoformat(),scope='Three bounded reproductions of the failing large-scene revoke case, with unchanged production and acceptance checks. A pass does not explain or repair the original focus failure.',original='large-commands-046364558a9d/gui-revoke',inputs={str(p.relative_to(root)):sha(p) for p in (root/'tests/configuration/native_large_commands.py',root/'tests/editor/native_editor.py',root/'tests/editor/native_observation.py',root/'tests/configuration/large-command-cases.json',Path(__file__))},executable_sha256=sha(build/'syspane_editor_window'),cases=[])
server=None
try:
 server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 for i in range(3):
  name='revoke-'+str(i+1)
  command=['dbus-run-session','--',sys.executable,str(root/'tests/configuration/native_large_commands.py'),'--observe',str(build/'syspane_editor_window'),str(build/'SysPane.EditorExitProbe'),str(folder/name),'revoke']
  child=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  try:out,err=child.communicate(timeout=40)
  except subprocess.TimeoutExpired:
   os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
  (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err)
  detail=folder/name/'result.json'
  report['cases'].append(dict(case=name,exit=child.returncode,result=json.loads(detail.read_bytes())['outcome'] if detail.exists() else 'missing',record_sha256=sha(detail) if detail.exists() else None))
finally:
 if server:server.terminate();server.communicate(timeout=5)
 report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
 report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(path=str(folder/'result.json'),cases=report['cases'])),flush=True)
