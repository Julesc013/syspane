from pathlib import Path
from datetime import datetime,timezone
import ctypes as C,hashlib,json,os,signal,subprocess,sys,time,types,uuid,zipfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests/editor'))
import native_editor as editor
from native_observation import PREFIX
PLAN=json.loads((R/'out/campaign/modal-focus-plan.json').read_bytes())
with zipfile.ZipFile(R/PLAN['original_source_archive']) as z:
    raw=z.read('tests/editor/native_layout_authoring.py')
    for name in ('tests/editor/native_editor.py','tests/editor/layout-authoring-cases.json','tests/editor/native_observation.py'):
        assert z.read(name)==(R/name).read_bytes(),name
oracle=types.ModuleType('preserved_layout_oracle');oracle.__file__=str(R/'tests/editor/native_layout_authoring.py');exec(compile(raw,oracle.__file__,'exec'),oracle.__dict__)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def snapshot(h,id):
    result=h.focus_snapshot(id);rows=[];h.observer.deadline=time.monotonic()+3
    try:
        for o in h.objects():
            words=h.observer.call(o,PREFIX+'Accessible','GetState',signature='(au)')[0]
            def state(s):return bool(words[int(s)//32]&(1<<(int(s)%32)))
            role=o.get_role();description=o.get_description()
            if state(h.Atspi.StateType.FOCUSED) or description=='editor.'+id or role in (h.Atspi.Role.FRAME,h.Atspi.Role.DIALOG):
                rows.append(dict(address=h.observer.identity(o),role=str(role),description=description,text=h.text(o),states={str(s):state(s) for s in (h.Atspi.StateType.FOCUSED,h.Atspi.StateType.FOCUSABLE,h.Atspi.StateType.SENSITIVE,h.Atspi.StateType.SHOWING,h.Atspi.StateType.VISIBLE,h.Atspi.StateType.ACTIVE)}))
    except Exception as e:result['snapshot_error']=str(e)
    finally:h.observer.deadline=None
    result['native_objects']=rows;return result

def observe(exe,exit_exe,directory):
    h=oracle.LayoutHarness(exe,exit_exe,directory,'canvas');original=h.focus;steps=[]
    h.report.update(probe_sha256=sha(Path(__file__)),preserved_oracle_sha256=hashlib.sha256(raw).hexdigest(),plan_sha256=sha(R/'out/campaign/modal-focus-plan.json'),focus_steps=steps)
    def focus(id):
        row=dict(id=id,before=snapshot(h,id));steps.append(row)
        try:original(id);row['after']=snapshot(h,id)
        except Exception as e:
            row.update(error=str(e),after=snapshot(h,id));h.screenshot('focus-failure')
            if id=='layout' and h.proc.poll() is None:
                h.input.press(0x20);deadline=time.monotonic()+1
                while time.monotonic()<deadline:h.pump();time.sleep(.01)
                row['after_space']=snapshot(h,id);row['layout_visible']=h.state(h.find('layout.set'),h.Atspi.StateType.SHOWING);row['status']=h.status();h.screenshot('after-space')
            raise
    h.focus=focus
    try:oracle.exercise(h);h.report['diagnostic']='unchanged_pass_inconclusive'
    except Exception as e:h.report.update(diagnostic='observed_failure',error=str(e),stage=h.stage)
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]));return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('modal-focus-probe-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='MODAL-FOCUS-DIAGNOSTIC',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),probe_sha256=sha(Path(__file__)),plan_sha256=sha(R/'out/campaign/modal-focus-plan.json'),executable_sha256=sha(exe),source_ref=PLAN['source'],cases=[])
    try:
        server,env=editor.launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        report['environment']=subprocess.check_output(['dpkg-query','-W','libgtk-3-0t64','libatk-bridge2.0-0t64','libatspi2.0-0t64'],text=True)
        for n in range(3):
            name='repetition-'+str(n+1);child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/name)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise
            (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err);assert child.returncode==0,err.decode(errors='replace')
            detail=json.loads((folder/name/'result.json').read_bytes());report['cases'].append(dict(case=name,diagnostic=detail['diagnostic'],record_sha256=sha(folder/name/'result.json')))
        report['outcome']='observed'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
