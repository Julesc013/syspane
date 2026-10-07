from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
r=Path('/mnt/d/Projects/SysPane/syspane');b=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path[:0]=[str(r/'tests/editor'),str(r/'tests/scene'),str(r/'tests/fault')]
if len(sys.argv)>1 and sys.argv[1]=='--observe':
 import gi
 gi.require_version('Atspi','2.0')
 from gi.repository import Atspi,GLib,Gio
 from native_observation import Observations,PREFIX
 family,mode,directory=sys.argv[2:5];folder=Path(directory);trace=folder.with_suffix('.queries.jsonl').open('x');wire=Observations({})
 def instrument(name,method,signature):
  original=getattr(Atspi.Accessible,name)
  def query(obj,*args):
   row=dict(method=method,started=time.monotonic(),pid=os.getpid())
   try:row['address']=list(wire.identity(obj))
   except Exception as e:row['address_error']=str(e)
   try:
    value=original(obj,*args);row['value']=int(value) if name=='get_role' else list(value);return value
   except Exception as error:
    row['error']=str(error);row['duration_ms']=(time.monotonic()-row['started'])*1000
    began=time.monotonic()
    try:row['explicit_reply']=wire.call(obj,PREFIX+('Accessible' if name=='get_role' else 'Table'),method,signature=signature)
    except Exception as e:row['explicit_error']=str(e)
    row['explicit_duration_ms']=(time.monotonic()-began)*1000
    # The independent follow-up read never replaces the original failure.
    raise
   finally:
    row.setdefault('duration_ms',(time.monotonic()-row['started'])*1000);trace.write(json.dumps(row)+'\n');trace.flush()
  setattr(Atspi.Accessible,name,query)
 instrument('get_role','GetRole','(u)');instrument('get_selected_rows','GetSelectedRows','(ai)')
 try:
  if family=='binding':
   from native_binding_authoring import observe
   observe(b/'syspane_editor_window',b/'SysPane.EditorExitProbe',folder,mode)
  else:
   from native_inspector import observe
   observe(b/'syspane_scene_inspector_tests',folder,mode)
 finally:trace.close()
 sys.exit(0)
from native_diagnostic import launch_xvfb
assert os.geteuid()!=0
folder=b/'native-evidence'/('query-probe-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
files=[Path(__file__),r/'tests/editor/native_binding_authoring.py',r/'tests/editor/native_observation.py',r/'tests/editor/native_editor.py',r/'tests/scene/native_inspector.py',r/'tests/editor/binding-authoring-cases.json',r/'tests/scene/inspector-cases.json']
report=dict(family='NATIVE-QUERY-DIAGNOSTIC',outcome='observed',started_at=datetime.now(timezone.utc).isoformat(),inputs={p.relative_to(r).as_posix():sha(p) for p in files},binaries={p.name:sha(p) for p in (b/'syspane_editor_window',b/'syspane_scene_inspector_tests',b/'SysPane.EditorExitProbe')},cases=[])
try:
 server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
 for family,mode in [('binding','selector'),('inspector','translated')]:
  for trial in range(3):
   name=family+'-'+str(trial+1);child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',family,mode,str(folder/name)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
   try:out,err=child.communicate(timeout=40)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGCONT);os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
   (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err)
   detail=folder/name/'result.json';queries=folder/(name+'.queries.jsonl');rows=[json.loads(s) for s in queries.read_text().splitlines()] if queries.exists() else []
   report['cases'].append(dict(case=name,exit=child.returncode,outcome=json.loads(detail.read_bytes())['outcome'] if detail.exists() else 'setup_failure',record_sha256=sha(detail) if detail.exists() else None,query_errors=[q for q in rows if 'error' in q],queries=len(rows),max_query_ms=max((q['duration_ms'] for q in rows),default=0)))
finally:
 if server:server.terminate();server.communicate(timeout=5)
 report['changed_inputs']=[str(p) for p in files if sha(p)!=report['inputs'][p.relative_to(r).as_posix()]];report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(path=str(folder/'result.json'),cases=report['cases'])))
