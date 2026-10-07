from pathlib import Path
from datetime import datetime,timezone
import faulthandler,json,os,signal,subprocess,sys,uuid
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'tests/editor'));import native_editor as n
if '--observe' in sys.argv:
 faulthandler.dump_traceback_later(10,repeat=True)
 n.observe(*map(Path,sys.argv[2:5]),'frozen-preview');sys.exit()
b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');assert os.geteuid()!=0
folder=b/'native-evidence'/('editor-diagnostic-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
exe=b/'syspane_editor_window';exit_exe=b/'SysPane.EditorExitProbe'
report=dict(family='EDITOR-FORM',diagnostic=True,outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=n.sha(exe),exit_executable_sha256=n.sha(exit_exe),oracle_sha256=n.sha(r/'tests/editor/native_editor.py'),helper_sha256=n.sha(Path(__file__)),cases=[])
try:
 server,env=n.launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/'frozen-preview')],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 timeout=False
 try:out,err=child.communicate(timeout=40)
 except subprocess.TimeoutExpired:timeout=True;os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
 (folder/'stdout').write_bytes(out);(folder/'stderr').write_bytes(err)
 assert not timeout and child.returncode==0,err.decode(errors='replace')
 case=folder/'frozen-preview/result.json';v=json.loads(case.read_text());assert v['outcome']=='pass' and v['fault_detected']
 report.update(outcome='pass',cases=[dict(case='frozen-preview',outcome='pass',fault_detected=True,record_sha256=n.sha(case))])
except Exception as e:report['error']=repr(e);raise
finally:
 if server:server.terminate();server.communicate(timeout=5)
 report['files']={p.relative_to(folder).as_posix():n.sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
 (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
