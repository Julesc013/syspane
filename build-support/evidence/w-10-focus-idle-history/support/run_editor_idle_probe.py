from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13')
assert os.geteuid()!=0
sys.path.insert(0,str(r/'tests/fault'))
from native_diagnostic import launch_xvfb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
folder=b/'native-evidence'/('editor-idle-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700)
library=r/'out/campaign/focus-idle/editor_idle_probe.so'
inputs=[r/'tests/editor/native_editor.py',r/'tests/editor/native_observation.py',r/'tests/configuration/native_large_commands.py',r/'tests/configuration/large-command-cases.json',r/'out/campaign/editor_idle_probe.c',Path(__file__),library,r/'spec/delivery/packages/w-10-focus-idle.md']
report=dict(family='EDITOR-IDLE-DIAGNOSTIC',outcome='observed',source_ref=subprocess.check_output(['git','-c','safe.directory='+str(r),'rev-parse','HEAD'],cwd=r,text=True).strip(),started_at=datetime.now(timezone.utc).isoformat(),inputs={p.relative_to(r).as_posix():sha(p) for p in inputs},executable_sha256=sha(b/'syspane_editor_window'),cases=[],scope='Read-only actual/native focus and idle-progress traces. Optional 60 ms drawing delay and refresh-priority intervention are explicitly diagnostic; original acceptance checks and production executable remain unchanged.')
server=None
try:
 server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 report['environment']=subprocess.check_output(['dpkg-query','-W','libgtk-3-0t64','libatk-bridge2.0-0t64','libatspi2.0-0t64','libglib2.0-0t64'],text=True)
 for name,low,slow in [('plain-1',False,False),('plain-2',False,False),('loaded-default-1',False,True),('loaded-low-1',True,True),('loaded-default-2',False,True),('loaded-low-2',True,True)]:
  childenv=dict(env,LD_PRELOAD=str(library),SYSPANE_PROBE_TRACE=str(folder/name))
  if low:childenv['SYSPANE_PROBE_LOW']='1'
  if slow:childenv['SYSPANE_PROBE_SLOW']='1'
  command=['dbus-run-session','--',sys.executable,str(r/'tests/configuration/native_large_commands.py'),'--observe',str(b/'syspane_editor_window'),str(b/'SysPane.EditorExitProbe'),str(folder/name),'drag']
  child=subprocess.Popen(command,env=childenv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  try:out,err=child.communicate(timeout=40)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
  (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err);detail=folder/name/'result.json'
  v=json.loads(detail.read_bytes()) if detail.exists() else {}
  report['cases'].append(dict(case=name,priority='low' if low else 'default',slow=slow,exit=child.returncode,outcome=v.get('outcome','missing'),stage=v.get('stage'),error=v.get('error'),record_sha256=sha(detail) if detail.exists() else None,traces=[p.name for p in folder.glob(name+'-*.tsv')]))
finally:
 if server:server.terminate();server.communicate(timeout=5)
 assert all(sha(p)==report['inputs'][p.relative_to(r).as_posix()] for p in inputs)
 assert sha(b/'syspane_editor_window')==report['executable_sha256']
 report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(path=str(folder/'result.json'),cases=report['cases'])),flush=True)
