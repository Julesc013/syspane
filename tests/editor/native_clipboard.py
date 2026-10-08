"""Independent native clipboard peers, real editor input and exact durable output."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,os,signal,subprocess,sys,time,uuid
from native_editor import Harness,ROOT,sha,launch_xvfb
from clipboard_peer import Peer

CASES=json.loads((ROOT/'tests/editor/native-clipboard-cases.json').read_bytes())
def wire(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
class ClipboardHarness(Harness):
    def __init__(self,*args):
        super().__init__(*args,clipboard=True);self.peer=Peer()
        self.report.update(oracle_sha256=sha(Path(__file__)),peer_sha256=sha(ROOT/'tests/editor/clipboard_peer.py'))
    def pump(self):
        self.peer.pump();super().pump()
    def close(self):
        self.report['peer_errors']=self.peer.errors
        self.peer.close();super().close()
    def selected(self):
        self.point(60,60);self.wait(lambda:self.value('title')=='Editable pane')
    def copy(self,keyboard=False):
        before=self.peer.owner()
        if keyboard:self.input.press(ord('c'),control=True)
        else:self.click('copy')
        self.wait(lambda:self.peer.owner()!=before and self.peer.owner()!=0)
    def paste(self,payload,**args):
        owner=self.peer.own(payload,**args);before=len(self.peer.requests);self.click('paste')
        self.wait(lambda:any(q.owner==owner and q.target==self.peer.mime for q in self.peer.requests[before:]))
        self.wait(lambda:not self.sensitive('cancel-paste') and ('Draft changes' in self.status() or 'could not' in self.status() or 'refused' in self.status() or 'timed out' in self.status()),7)
    def unchanged(self):
        assert not self.sensitive('undo') and not self.sensitive('apply'),self.status();self.check()
    def save(self,scene):
        self.click('apply');self.event('event','held');self.command('release');result=self.event('event','result')['result']
        assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible']
        self.wait(lambda:'Saved durably' in self.status());self.check(scene,'41')
    def read_copy(self,target=None,automatic=True):
        start=time.monotonic();row=self.peer.request(target,automatic)
        try:self.wait(lambda:row['complete'] if automatic else row['notified'],CASES['limits']['total_ms']/1000+.8)
        finally:self.report['observations'].append(dict(target=row['target'],refused=row['refused'],notified=row['notified'],complete=row['complete'],incremental=row['incremental'],received_bytes=len(row['data']),chunks=row['chunks'],elapsed_ms=(time.monotonic()-start)*1000))
        return row

def roundtrip(h):
    primary=h.peer.own(b'foreign primary',selection=h.peer.atom('PRIMARY'))
    h.selected();h.copy(keyboard=True)
    row=h.read_copy();assert row['data']==wire(CASES['copied_fragment'])
    targets=h.read_copy(h.peer.atom('TARGETS'));assert set(targets['data'])=={h.peer.mime,h.peer.atom('TARGETS'),h.peer.atom('TIMESTAMP')}
    timestamp=h.read_copy(h.peer.atom('TIMESTAMP'));assert timestamp['format']==32 and len(timestamp['data'])==1 and timestamp['data'][0]>0
    assert h.read_copy(h.peer.atom('UTF8_STRING'))['refused']
    assert h.peer.owner(h.peer.atom('PRIMARY'))==primary
    h.focus('canvas');h.input.press(ord('v'),control=True);h.wait(lambda:h.sensitive('undo') and not h.sensitive('cancel-paste'))
    h.check();h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.click('redo');h.wait(lambda:h.sensitive('apply'))
    h.save(CASES['pasted_scene'])
    assert h.peer.owner()==0,'Apply retained a clipboard snapshot'
    wrong=copy.deepcopy(CASES['pasted_scene']);wrong['widgets'][-1]['id']='wrong:id'
    detected=False
    try:h.check(wrong,'41')
    except AssertionError:detected=True
    assert detected;h.report['wrong_scene_witness_detected']=True
    h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(CASES['pasted_scene'],'41')
    assert h.peer.owner(h.peer.atom('PRIMARY'))==primary

def incoming(h):
    data=wire(CASES['incoming_fragment']);maximum=CASES['limits']['bytes']
    for index,options in enumerate([{},dict(mode='incr',hint=0,chunk=73),{}],1):
        h.paste(data if index<3 else data+b' '*(maximum-len(data)),**options)
        assert h.sensitive('undo') and h.sensitive('apply');h.check()
        if index<3:h.click('undo');h.wait(lambda:not h.sensitive('apply'))
    expected=copy.deepcopy(CASES['incoming_scene']);expected['roots'][-1]='native:3';expected['widgets'][-1]['id']='native:3';h.save(expected)

def invalid(h):
    maximum=CASES['limits']['bytes'];data=wire(CASES['incoming_fragment'])
    missing=copy.deepcopy(CASES['copied_fragment']);missing['widgets']=[copy.deepcopy(CASES['authored']['scene']['widgets'][2])];missing['roots']=['widget:image'];missing['widgets'][0]['content']['asset']['sha256']='0'*64
    examples=[(b'{}',{}),(b'{broken',{}),(data,dict(kind=h.peer.atom('UTF8_STRING'))),
        (data,dict(fmt=32)),(data,dict(mode='bad-incr')),
        *((data,dict(mode=mode)) for mode in ('wrong-time','wrong-target','wrong-selection','wrong-property')),
        (data+b' '*(maximum+1-len(data)),{}),(data,dict(mode='incr',hint=maximum+1)),
        (data+b' '*(maximum+1-len(data)),dict(mode='incr',hint=0,chunk=16384)),(wire(missing),{})]
    for index,(payload,options) in enumerate(examples):
        h.stage='INVALID-'+str(index);h.paste(payload,**options);h.unchanged();h.report['observations'].append(dict(case=h.stage,status=h.status()))

def cancel_timeout(h):
    data=wire(CASES['incoming_fragment'])
    for action in ('cancel-paste','escape','policy','regrant','topology','reload','disconnect','owner-change','timeout'):
        h.stage='PENDING-'+action;h.peer.own(data,mode='hold');before=len(h.peer.requests);h.click('paste')
        h.wait(lambda:len(h.peer.requests)>before and h.sensitive('cancel-paste'));q=h.peer.requests[-1]
        assert not h.sensitive('apply') and not h.sensitive('copy') and not h.sensitive('undo')
        start=time.monotonic()
        if action=='cancel-paste':h.click('cancel-paste')
        elif action=='escape':h.focus('cancel-paste');h.input.press(0xff1b)
        elif action=='reload':h.click('reload');h.event('event','reloaded')
        elif action in ('policy','regrant','topology','disconnect'):h.command(action)
        elif action=='owner-change':h.peer.own(data);h.peer.deliver(q)
        h.wait(lambda:not h.sensitive('cancel-paste'),2)
        if action=='timeout':assert 'timed out' in h.status() and .75<=time.monotonic()-start<=1.8
        # A delayed response targets the destroyed request window. A fresh request
        # is made only after asserting the old one could not mutate the draft.
        h.peer.deliver(q,{**h.peer.current,'mode':'direct'});h.pump();h.check()
        if action=='disconnect':h.click('reload');h.event('event','reloaded')
        h.wait(lambda:h.sensitive('paste'));h.unchanged()
    h.stage='ABSOLUTE-DEADLINE';h.peer.own(data,mode='incr',hint=0,chunk=1,interval=.25)
    start=time.monotonic();h.click('paste');h.wait(lambda:h.sensitive('cancel-paste'))
    h.wait(lambda:not h.sensitive('cancel-paste'),6)
    assert 'timed out' in h.status() and 4.6<=time.monotonic()-start<=5.8
    h.unchanged()

def ownership_policy(h):
    h.selected();h.copy();assert h.read_copy()['data']==wire(CASES['copied_fragment'])
    foreign=h.peer.own(wire(CASES['incoming_fragment']));h.command('policy');assert h.peer.owner()==foreign
    h.copy();h.command('deny-clipboard');h.wait(lambda:h.peer.owner()==0)
    assert not h.sensitive('copy') and not h.sensitive('paste');h.command('regrant');h.wait(lambda:h.sensitive('copy'));assert h.peer.owner()==0
    h.copy();h.command('disconnect');h.wait(lambda:h.peer.owner()==0)
    h.click('reload');h.event('event','reloaded');h.selected();h.copy()
    foreign=h.peer.own(wire(CASES['incoming_fragment']),mode='hold');before=len(h.peer.requests);h.click('paste')
    h.wait(lambda:len(h.peer.requests)>before and h.sensitive('cancel-paste'));q=h.peer.requests[-1]
    h.command('close');assert h.peer.owner()==foreign
    h.peer.deliver(q,{**h.peer.current,'mode':'direct'});h.pump();h.check()

def outgoing(h):
    fragment=copy.deepcopy(CASES['incoming_fragment']);fragment['widgets'][0]['extensions']['large']='q'*200000
    h.paste(wire(fragment));assert h.sensitive('undo');h.copy()
    expected=copy.deepcopy(fragment);expected['roots']=['native:1'];expected['widgets'][0]['id']='native:1'
    row=h.read_copy();assert row['data']==wire(expected) and row['incremental'] and max(row['chunks'])<=16384
    held=[h.peer.request(automatic=False) for _ in range(8)];h.wait(lambda:all(r['notified'] for r in held));assert all(r['incremental'] for r in held)
    for target in (h.peer.mime,h.peer.atom('TIMESTAMP')):
        before=len(h.peer.refusals);h.peer.duplicate(held[-1],target);h.wait(lambda:len(h.peer.refusals)>before)
        assert h.peer.refusals[-1]==dict(window=held[-1]['window'],target=target)
        assert h.peer.read(held[-1]['window'],held[-1]['property'])[0]==h.peer.incr
    assert h.read_copy()['refused'],'outgoing capacity was not bounded'
    h.peer.destroy(held[0]['window']);h.pump()
    replacement=h.peer.request(automatic=False);h.wait(lambda:replacement['notified']);assert replacement['incremental']
    row=held[1];h.peer.advance(row);h.wait(lambda:len(row['chunks'])==1);assert row['chunks']==[16384]
    h.command('deny-clipboard');h.wait(lambda:row['complete']);assert row['chunks']==[16384,0] and len(row['data'])==16384
    h.command('regrant');assert h.peer.owner()==0
    h.copy();stalled=h.peer.request(automatic=False);h.wait(lambda:stalled['notified']);h.wait(lambda:stalled['complete'],2);assert stalled['data']==b''
    assert h.read_copy()['data']==wire(expected),'timed-out slot did not recover'
    slowly=h.peer.request(automatic=False);h.wait(lambda:slowly['notified']);start=time.monotonic()
    while not slowly['complete']:
        release_at=time.monotonic()+.55;h.wait(lambda:slowly['complete'] or time.monotonic()>=release_at,.8)
        if slowly['complete']:break
        count=len(slowly['chunks']);h.peer.advance(slowly);h.wait(lambda:len(slowly['chunks'])>count,.8)
    assert 4.5<=time.monotonic()-start<=5.8 and len(slowly['data'])<len(wire(expected))
    h.report['outgoing_absolute_deadline_ms']=(time.monotonic()-start)*1000

def observe(exe,exit_exe,folder,mode):
    h=ClipboardHarness(exe,exit_exe,folder,mode)
    try:
        h.launch();h.check();h.stage=mode
        {'roundtrip':roundtrip,'incoming':incoming,'invalid':invalid,'cancel-timeout':cancel_timeout,'ownership-policy':ownership_policy,'outgoing-incr':outgoing}[mode](h)
        h.command('quit');assert h.proc.wait(timeout=5)==0
        assert all(e['code']==3 for e in h.peer.errors),h.peer.errors
        known=('gtk_text_buffer_remove_selection_clipboard: assertion', 'gtk_main_quit: assertion')
        diagnostics=(h.folder/'stderr').read_text()
        unexpected=[line for line in diagnostics.splitlines() if 'CRITICAL' in line and not any(k in line for k in known)]
        assert not unexpected,unexpected
        h.report['known_preexisting_shutdown_warnings']=[line for line in diagnostics.splitlines() if 'CRITICAL' in line]
        h.report['outcome']='pass'
    except Exception as error:
        h.report.update(error=repr(error),stage=h.stage)
        if h.proc and h.proc.poll() is None:
            h.report['failure_status']=h.status()
        raise
    finally:h.close()

def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve())
    folder=evidence/('clipboard-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-CLIPBOARD',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)),peer_sha256=sha(ROOT/'tests/editor/clipboard_peer.py'),fixture_sha256=sha(ROOT/'tests/editor/native-clipboard-cases.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=75)
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
