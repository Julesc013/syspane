from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,uuid,shlex
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');assert os.geteuid()!=0
sys.path.insert(0,str(r/'tests/fault'));from native_diagnostic import launch_xvfb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lib=r/'out/campaign/focus-idle/refresh_animation_probe.so';source=r/'out/campaign/refresh_animation_probe.cpp'
command=['g++','-std=c++17','-shared','-fPIC','-Wall','-Wextra','-Werror',str(source),'-o',str(lib),*shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0'],text=True)),'-ldl']
build=subprocess.run(command,capture_output=True,text=True);(r/'out/campaign/focus-idle/animation-build.json').write_text(json.dumps(dict(command=command,exit=build.returncode,stdout=build.stdout,stderr=build.stderr),indent=2)+'\n');assert build.returncode==0,build.stderr
folder=b/'native-evidence'/('refresh-animation-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
report=dict(family='EDITOR-REFRESH-ANIMATION-DIAGNOSTIC',outcome='observed',started_at=datetime.now(timezone.utc).isoformat(),inputs={p.relative_to(r).as_posix():sha(p) for p in (source,lib,Path(__file__),r/'tests/editor/native_refresh.py',r/'tests/editor/native_editor.py')},probe_sha256=sha(b/'libsyspane_editor_refresh_probe.so'),executable_sha256=sha(b/'syspane_editor_window'),cases=[],scope='Compare the unchanged loaded-revoke oracle with and without native GTK animations in a private process. This is diagnostic only; no product or acceptance change.')
try:
 server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 for name,animation in [('normal-1',True),('disabled-1',False),('normal-2',True),('disabled-2',False)]:
  childenv=dict(env,LD_PRELOAD=('' if animation else str(lib)+':')+str(b/'libsyspane_editor_refresh_probe.so'),SYSPANE_REFRESH_TRACE=str(folder/name))
  command=['dbus-run-session','--',sys.executable,str(r/'tests/editor/native_refresh.py'),'--observe',str(b/'syspane_editor_window'),str(b/'SysPane.EditorExitProbe'),str(folder/name),'revoke']
  child=subprocess.Popen(command,env=childenv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
  try:stdout,stderr=child.communicate(timeout=40)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
  (folder/(name+'.stdout')).write_bytes(stdout);(folder/(name+'.stderr')).write_bytes(stderr);detail=folder/name/'result.json';d=json.loads(detail.read_bytes());report['cases'].append(dict(case=name,outcome=d['outcome'],exit=child.returncode,error=d.get('error'),erase_ms=d.get('erase_ms'),record_sha256=sha(detail)))
finally:
 if server:server.terminate();server.communicate(timeout=5)
 report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(path=str(folder/'result.json'),cases=report['cases'])))
