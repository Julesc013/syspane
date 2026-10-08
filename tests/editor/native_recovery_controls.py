"""Real GTK decisions, independent selecting-record identity and exact file oracle."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,select,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,launch_xvfb

CASES=json.loads((ROOT/'tests/editor/recovery-controls-cases.json').read_bytes())
SCOPE=json.loads((ROOT/'tests/editor/recovery-controls-scope-case.json').read_bytes())
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

class RecoveryHarness(Harness):
    def __init__(self,exe,exit_exe,folder,mode):
        super().__init__(exe,exit_exe,folder,mode,draft_recovery=True)
        self.retained=Path(str(self.directory)+'-recovery');self.retained.mkdir(mode=0o700)
        self.record=self.retained/'draft.json'
        if mode=='held-close':
            workers=Path(str(self.directory)+'-worker');workers.mkdir(mode=0o700)
            os.link(exe.parent/'syspane_recovery_worker_probe',workers/'worker-stop-pending_created')
    def recovery_status(self):return self.text(self.find('recovery-status'))
    def ready(self):self.wait(lambda:self.recovery_status()=='Recovery ready. No unsaved draft.',5)
    def expected(self,scene=None,generation=None):
        q=copy.deepcopy(CASES['command'])
        if scene is not None:q['operations'][0]['scene']=scene
        # MoveWidgets has used double coordinates since before this package;
        # preserve its numeric representation in this exact serialized oracle.
        # The frozen literal scene values and all command fields stay unchanged.
        q=copy.deepcopy(q)
        geometry=q['operations'][0]['scene']['widgets'][0]['layout']['base']
        for key in ('x','y'):geometry[key]=float(geometry[key])
        return encoded(dict(format='syspane.editor-recovery',schema_version='0.1.0',identity=dict(profile=CASES['profile'],generation=generation or sha(self.directory/'current.json')),command=encoded(q).decode()))
    def retained_exact(self,expected=None):
        expected=expected or self.expected()
        self.wait(lambda:self.recovery_status()=='Recovery draft retained. Configuration remains unsaved.',5)
        assert self.record.read_bytes()==expected,'exact recovery record differs'
        assert (self.record.stat().st_mode&0o777)==0o600
        assert not (self.retained/'.pending').exists()
        self.report['observations'].append(dict(case='exact-retained',sha256=sha(self.record),status=self.recovery_status()))
        return expected
    def capture(self):
        self.ready();self.point(60,60);self.wait(lambda:self.value('title')=='Editable pane')
        self.drag(60,60,30,20);self.wait(lambda:self.number('x')==70 and self.number('y')==60)
        self.check();return self.retained_exact()
    def reopen(self):
        self.proc.kill();assert self.proc.wait(timeout=5)==-signal.SIGKILL
        self.launch('reopen');self.wait(lambda:'retained recovery draft cannot' in self.recovery_status() or 'unsaved recovery draft is available' in self.recovery_status(),5)
        self.check();assert not self.sensitive('apply') and not self.sensitive('undo')
        assert not self.sensitive('canvas')
        self.screenshot('recovery-offer')
        for key in ('recovery-restore','recovery-discard','recovery-keep','recovery-status'):
            box=self.extents(self.find(key));assert box.width>0 and box.height>0 and 0<=box.x and 0<=box.y and box.x+box.width<=800 and box.y+box.height<=600,(key,box)
    def restore(self):
        self.click('recovery-restore');self.wait(lambda:self.sensitive('undo'))
        self.point(90,80);self.wait(lambda:self.number('x')==70 and self.number('y')==60)
    def apply(self,scene,unknown=False,replacement=None):
        self.wait(lambda:self.sensitive('apply'),5);self.click('apply')
        sent=self.event('event','submitted')['body'];assert sent['operations'][0]['scene']==scene
        self.event('event','held');self.check();assert not self.sensitive('apply')
        if replacement is not None:self.record.write_bytes(replacement)
        self.command('release');result=self.event('event','result')['result']
        assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible']
        if not unknown:self.wait(lambda:'Saved durably' in self.status())
        self.check(scene,'41')

def exercise(h):
    mode=h.mode;h.launch();h.check();h.stage=mode
    if mode=='worker-failure':
        h.wait(lambda:'Recovery unavailable.' in h.recovery_status(),5)
        h.point(60,60);h.drag(60,60,30,20);h.wait(lambda:h.number('x')==70)
        h.apply(CASES['drag']['expected']);assert not h.record.exists();return
    if mode=='private-fields':
        h.ready();h.point(60,60);h.wait(lambda:h.value('title')=='Editable pane')
        h.field('title','Private uncommitted input');h.command('topology');h.pump()
        assert not h.record.exists() and not h.sensitive('apply');h.check()
        h.click('revert-fields');h.wait(lambda:h.value('title')=='Editable pane');return
    if mode=='held-close':
        h.ready();h.point(60,60);h.drag(60,60,30,20)
        def held():
            children=Path(f'/proc/{h.pid}/task/{h.pid}/children').read_text().split()
            for pid in children:
                try:
                    args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
                    worker=str(h.directory)+'-worker/worker-stop-pending_created'
                    if args[:2]==[worker.encode(),str(h.pid).encode()] and Path(f'/proc/{pid}/stat').read_text().split(') ')[1].startswith('T '):return int(pid)
                except FileNotFoundError:pass
            return False
        pid=h.wait(held,5);fd=os.pidfd_open(pid)
        try:
            started=h.command('close');assert select.select([fd],[],[],2)[0],'held helper not reaped after close'
            h.report['closure_ms']=(time.monotonic()-started)*1000
            h.wait(lambda:h.recovery_status()=='');assert not h.record.exists();h.check()
        finally:os.close(fd)
        return
    record=h.capture()
    try:
        assert record==h.expected(CASES['authored']['scene'])
    except AssertionError:h.report['wrong_record_control']='rejected'
    else:raise AssertionError('wrong exact-byte oracle passed')
    if mode=='undo-clean':
        h.click('undo');h.ready();assert not h.record.exists();h.check()
        h.click('redo');h.retained_exact(record);return
    if mode=='cancel':
        h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0
        assert not h.record.exists();h.check()
        h.record.write_bytes(record);h.record.chmod(0o600)
        h.launch('reopen');h.wait(lambda:h.sensitive('recovery-restore'),5)
        h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0
        assert h.record.read_bytes()==record;h.check();return
    if mode=='unknown':
        h.apply(CASES['drag']['expected'],unknown=True)
        h.wait(lambda:'Outcome unknown' in h.status());assert h.record.read_bytes()==record
        h.command('restart');h.event('event','reconciled');h.ready();assert not h.record.exists();h.check(CASES['drag']['expected'],'41');return
    if mode=='replacement':
        foreign=b'Externally replaced recovery record'
        h.apply(CASES['drag']['expected'],replacement=foreign)
        h.wait(lambda:'cannot be restored' in h.recovery_status(),5)
        assert h.record.read_bytes()==foreign and not h.sensitive('recovery-restore');return
    if mode==SCOPE['case']:
        h.apply(CASES['drag']['expected']);h.wait(lambda:'cannot be restored' in h.recovery_status(),5)
        assert h.record.read_bytes()==record and not h.sensitive('recovery-restore');return
    if mode in ('invalid','stale'):
        h.proc.kill();h.proc.wait(timeout=5)
        record=b'Invalid private recovery text' if mode=='invalid' else h.expected(generation='0'*64)
        h.record.write_bytes(record)
        h.launch('reopen');h.wait(lambda:'cannot be restored' in h.recovery_status(),5)
        assert not h.sensitive('recovery-restore') and h.sensitive('recovery-discard') and h.sensitive('recovery-keep')
        assert all('Invalid private recovery text' not in h.text(o) for o in h.objects())
        h.check();h.click('recovery-discard');h.ready();assert not h.record.exists();return
    h.reopen()
    if mode=='discard':
        h.click('recovery-discard');h.ready();assert not h.record.exists() and not h.sensitive('undo');h.check();return
    if mode=='policy':
        h.command('revoke');h.wait(lambda:not h.sensitive('recovery-restore'))
        assert h.record.read_bytes()==record
        h.command('regrant');assert not h.sensitive('recovery-restore')
        h.click('reload');h.event('event','reloaded');h.wait(lambda:h.sensitive('recovery-restore'),5)
        assert h.record.read_bytes()==record;h.check();return
    if mode=='keep-apply':
        h.click('recovery-keep');h.wait(lambda:'kept for later' in h.recovery_status())
        h.point(60,60);h.drag(60,60,10,0);h.wait(lambda:h.number('x')==50)
        scene=copy.deepcopy(CASES['authored']['scene']);scene['widgets'][0]['layout']['base']['x']=50
        assert h.record.read_bytes()==record;h.apply(scene)
        h.wait(lambda:'cannot be restored' in h.recovery_status(),5)
        assert h.record.read_bytes()==record;return
    assert mode=='restore-apply'
    h.restore();h.check();h.click('undo');h.ready();assert not h.sensitive('undo') and not h.record.exists()
    h.click('redo');h.retained_exact(record)
    h.apply(CASES['drag']['expected']);h.ready();assert not h.record.exists()
    h.command('quit');assert h.proc.wait(timeout=5)==0
    h.launch('reopen');h.ready();h.check(CASES['drag']['expected'],'41');assert not h.sensitive('recovery-restore')

def observe(exe,exit_exe,folder,mode):
    h=RecoveryHarness(exe,exit_exe,folder,mode)
    try:
        exercise(h)
        if h.proc.poll() is None:h.command('quit');assert h.proc.wait(timeout=5)==0
        diagnostics=(h.folder/'stderr').read_text()
        known=('gtk_text_buffer_remove_selection_clipboard: assertion','gtk_main_quit: assertion')
        unexpected=[s for s in diagnostics.splitlines() if 'CRITICAL' in s and not any(k in s for k in known)]
        assert not unexpected,unexpected
        h.report['known_preexisting_shutdown_warnings']=[s for s in diagnostics.splitlines() if 'CRITICAL' in s]
        h.report['outcome']='pass'
    except Exception as error:
        h.report.update(error=repr(error),stage=h.stage)
        if h.proc and h.proc.poll() is None:
            h.report['failure_status']=h.status();h.report['failure_recovery_status']=h.recovery_status()
        raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('recovery-controls-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-RECOVERY',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),worker_sha256=sha(exe.parent/'SysPane.RecoveryWorker'),oracle_sha256=sha(Path(__file__)),fixture_sha256=sha(ROOT/'tests/editor/recovery-controls-cases.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_cases']+[SCOPE['case']]:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=70)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5);raise AssertionError('observer timeout')
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err)
            record=folder/mode/'result.json';assert record.is_file(),(mode,err.decode(errors='replace'))
            case=json.loads(record.read_bytes());report['cases'].append(dict(case=mode,outcome=case['outcome'],record_sha256=sha(record)))
            assert child.returncode==0 and case['outcome']=='pass',(mode,err.decode(errors='replace'))
        report['outcome']='pass'
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
