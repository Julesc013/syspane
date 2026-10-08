"""Independent ext4 bytes, interrupted publication and authenticated IPC oracle."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,os,select,signal,socket,struct,subprocess,sys,time,uuid
from native_large_commands import Store,Supervisor,Client,ROOT,write,encoded,full_body,generation,accepted,sha
CASES=json.loads((ROOT/'tests/configuration/theme-command-cases.json').read_bytes())
FIXTURE=json.loads((ROOT/'tests/configuration/settings-content-fixture.json').read_bytes())
BASE={sha_value:p for p in FIXTURE['packages'] if (sha_value:=__import__('hashlib').sha256(p['manifest'].encode()).hexdigest()) in CASES['base_manifests']}
def exact_resources(directory,body,revision,reset=False):
    g,m=generation(directory);assert m['version']=='0.4.0' and m['revision']==str(revision)
    assert set(m)=={'version','revision','settings','scene','identity','resources'}
    assert set(m['identity'])=={'principal','epoch','request','body_sha256'}
    assert set(p.name for p in g.iterdir())=={'settings.json','scene.json','manifest.json','request.json','resources.json','resources'}
    assert (g/'request.json').read_bytes()==body and sha(g/'request.json')==m['identity']['body_sha256']
    assert sha(g/'settings.json')==m['settings'] and sha(g/'scene.json')==m['scene'] and sha(g/'resources.json')==m['resources']
    index=json.loads((g/'resources.json').read_bytes());assert set(index)=={'version','selection','theme','packages'} and index['version']=='0.2.0'
    assert index['selection']==CASES['base_selection' if reset else 'selection']
    assert index['theme']==(FIXTURE['themes']['theme:native'] if reset else CASES['artifact']['theme_pin'])
    assert index['packages']==CASES['base_manifests' if reset else 'selected_manifests']
    files={}
    for digest,pkg in BASE.items():
        files['m-'+digest+'.json']=pkg['manifest'].encode()
        for h in pkg['assets_hex'].values():
            raw=bytes.fromhex(h);files['a-'+__import__('hashlib').sha256(raw).hexdigest()+'.bin']=raw
    if not reset:
        a=CASES['artifact'];files['m-'+a['package_pin']['sha256']+'.json']=a['manifest'].encode();files['a-'+a['theme_pin']['sha256']+'.bin']=a['asset'].encode()
    assert set(p.name for p in (g/'resources').iterdir())==set(files)
    for name,raw in files.items():assert (g/'resources'/name).read_bytes()==raw
    return g,m
class ThemeStore(Store):
    def __init__(self,exe,folder):
        super().__init__(exe,folder);self.body=full_body(CASES['command']);write(folder/'command.json',self.body)
    def args(self,phase='-'):return [str(self.exe),str(self.path),'theme-commit',str(self.folder/'command.json'),phase]
    def commit(self,phase='-'):return self.call('theme-commit',self.folder/'command.json',phase)['result']
    def inspect(self,revision,fallback=False):
        if revision==40:return super().inspect(revision,fallback)
        actual=self.call('read');expected=copy.deepcopy(CASES['expected']);reset=revision==43
        if reset:expected['scene']=copy.deepcopy(FIXTURE['authored']['scene'])
        if revision>=42:expected['settings']['display']['reduced_motion']=True
        expected['scene']['revision']=expected['settings']['revision']=str(revision)
        assert actual['scene']==expected['scene'] and actual['settings']==expected['settings'] and actual['recovered_previous']==fallback
        exact_resources(self.path,self.body,revision,reset);return actual
class ThemeClient(Client):
    def __init__(self,ready,admit=True):
        self.epoch=ready['epoch'];self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.settimeout(5);self.socket.connect(ready['endpoint'])
        assert struct.unpack('3i',self.socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]==ready['pid']
        docs=[dict(document=n,version=v) for n,v in [('command','0.8.0'),('command-result','0.1.0'),('reconciliation-request','0.1.0'),('reconciliation-result','0.1.0')]]
        features=[x for x in CASES['features'] if admit or x!='configuration.theme-overrides']+['cancel','result.get']
        self.send('hello',dict(wire_major=0,wire_minor=1,role='console',producer_epoch='client',max_frame_bytes=328704,document_versions=docs,required_features=['configuration.transactions','result.reconcile'],optional_features=[x for x in features if x!='configuration.transactions']))
        hello=self.receive();assert hello['type']=='welcome' and ('configuration.theme-overrides' in hello['body']['optional_features'])==admit
    def reconcile(self,epoch):
        q=dict(schema_version='0.1.0',query_id='Q',original_producer_epoch=epoch,request_id='theme:edit');self.send('result.reconcile',q);v=self.receive();assert v['type']=='result.reconciled' and all(v['body'][k]==x for k,x in q.items());return v['body']['result']
class ThemeSupervisor(Supervisor):
    def connect(self,admit=True):
        ready=self.event('ready');self.children[ready['pid']]=os.pidfd_open(ready['pid']);client=ThemeClient(ready,admit);self.clients.append(client);return ready,client
def rewrite_manifest(f,g,m):
    write(g/'manifest.json',encoded(m));pointer=json.loads((f.path/'current.json').read_bytes());pointer['manifest']=sha(g/'manifest.json');write(f.path/'current.json',encoded(pointer))
def main():
    exe,probe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:4]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('theme-commands-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='THEME-COMMANDS',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),executable_sha256=sha(exe),store_executable_sha256=sha(probe),fixture_sha256=sha(ROOT/'tests/configuration/theme-command-cases.json'),cases=[])
    try:
        f=ThemeStore(probe,folder/'success');accepted(f.commit());f.inspect(41);accepted(f.commit());f.inspect(41);accepted(f.call('reconcile','E1','theme:edit')['result'])
        assert f.catalog.resolve().parent==f.folder.resolve();f.catalog.rename(f.folder/'unavailable-imports')
        for key,revision in [('keep',42),('reset',43)]:
            f.body=encoded(CASES[key]);write(f.folder/'command.json',f.body);result=f.commit();assert result['outcome']=='accepted' and result['revision']==str(revision);f.inspect(revision)
        report['cases'].append(dict(case='exact-save-replay-keep-reset-without-imports',outcome='pass',revision=43))
        for phase,revision in CASES['faults'].items():
            f=ThemeStore(probe,folder/('cut-'+phase.replace(':','-')));p=subprocess.Popen(f.args(phase),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                assert select.select([p.stdout],[],[],5)[0];assert json.loads(p.stdout.readline())==dict(transition=phase)
                end=time.monotonic()+3;stopped=None
                while time.monotonic()<end:
                    stopped=os.waitid(os.P_PID,p.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                    if stopped:break
                    time.sleep(.005)
                assert stopped and stopped.si_status==signal.SIGSTOP;p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
                f.inspect(revision);result=f.call('reconcile','E1','theme:edit')['result']
                if revision==41:accepted(result);accepted(f.commit());f.inspect(41)
                else:assert result['outcome']=='unknown' and result['stored'] is None
                report['cases'].append(dict(case='cut-'+phase,outcome='pass',revision=revision,stopped_signal=stopped.si_status,exit=p.returncode))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=3)
        for fault in ('revoke','deny-theme','missing-override','corrupt-override','corrupt-request','old-manifest','old-index','wrong-font-intent'):
            f=ThemeStore(probe,folder/fault)
            if fault in ('revoke','deny-theme'):
                result=f.commit(fault);assert result['outcome']==('conflict' if fault=='revoke' else 'denied');f.inspect(40)
            else:
                accepted(f.commit());g,m=exact_resources(f.path,f.body,41)
                if fault in ('missing-override','corrupt-override'):
                    path=g/'resources'/('a-'+CASES['artifact']['theme_pin']['sha256']+'.bin')
                    if fault=='missing-override':path.rename(path.with_suffix('.missing'))
                    else:write(path,path.read_bytes()+b' ')
                elif fault=='corrupt-request':write(g/'request.json',(g/'request.json').read_bytes()+b' ')
                elif fault=='old-manifest':m['version']='0.3.0';rewrite_manifest(f,g,m)
                elif fault=='old-index':
                    index=json.loads((g/'resources.json').read_bytes());index['version']='0.1.0';write(g/'resources.json',encoded(index));m['resources']=sha(g/'resources.json');rewrite_manifest(f,g,m)
                else:
                    wrong=copy.deepcopy(CASES['command']);wrong['theme_edit']['font']['weight']=900;write(g/'request.json',full_body(wrong));m['identity']['body_sha256']=sha(g/'request.json');rewrite_manifest(f,g,m)
                f.inspect(40,True);assert f.call('reconcile','E1','theme:edit')['result']['outcome']=='unknown'
            report['cases'].append(dict(case=fault,outcome='pass'))
        for mode in ('normal','unnegotiated','prepare','resource','durable'):
            f=ThemeStore(probe,folder/('ipc-'+mode));owner=ThemeSupervisor(exe,f.path,mode if mode in ('prepare','resource','durable') else 'normal');entry=dict(case='ipc-'+mode,outcome='fail');report['cases'].append(entry)
            try:
                ready,client=owner.connect(mode!='unnegotiated');original=ready['epoch'];client.send('command',f.body,True)
                if mode=='unnegotiated':assert client.receive()['body']['error']['code']=='feature.unsupported';revision=40
                elif mode=='normal':
                    accepted(client.receive()['body']);owner.event('finished');client.send('command',f.body,True);accepted(client.receive()['body']);exact_resources(f.path,f.body,41)
                    signal.pidfd_send_signal(owner.children[ready['pid']],signal.SIGKILL);owner.event('fault');owner.event('reaped');assert select.select([owner.children[ready['pid']]],[],[],0)[0]
                    ready,client=owner.connect();assert ready['epoch']!=original;accepted(client.reconcile(original));revision=41
                else:
                    owner.event('armed');end=time.monotonic()+2;held=[]
                    while time.monotonic()<end:
                        held=[dict(tid=int(t.name),wchan=(t/'wchan').read_text().strip()) for t in (Path('/proc')/str(ready['pid'])/'task').iterdir() if int(t.name)!=ready['pid']]
                        if any(t['wchan']=='hrtimer_nanosleep' for t in held):break
                        time.sleep(.005)
                    assert any(t['wchan']=='hrtimer_nanosleep' for t in held);entry['held_worker']=held
                    if mode=='durable':exact_resources(f.path,f.body,41)
                    client.send('heartbeat',dict(sequence='1'));assert client.receive()['type']=='heartbeat';client.send('cancel' if mode=='prepare' else 'result.get',dict(request_id='theme:edit'));assert client.receive()['body']['outcome']=='unknown'
                    fault=owner.event('fault');assert fault['reason']=='transaction.deadline';reaped=owner.event('reaped');assert reaped['pid']==ready['pid'] and select.select([owner.children[ready['pid']]],[],[],0)[0]
                    ready,client=owner.connect();assert ready['epoch']!=original;result=client.reconcile(original)
                    if mode=='durable':accepted(result);revision=41
                    else:assert result['outcome']=='unknown' and result['stored'] is None;revision=40
                owner.stop();f.inspect(revision);entry.update(outcome='pass',revision=revision)
            finally:owner.close();entry['events']=owner.log
        # Independent fixed-byte oracle must reject a deliberately substituted output.
        f=ThemeStore(probe,folder/'wrong-output');accepted(f.commit());g,m=exact_resources(f.path,f.body,41);path=g/'resources'/('a-'+CASES['artifact']['theme_pin']['sha256']+'.bin');write(path,encoded(CASES['artifact']['theme']))
        detected=False
        try:exact_resources(f.path,f.body,41)
        except AssertionError:detected=True
        assert detected;report['cases'].append(dict(case='wrong-output-witness',outcome='pass',fault_detected=True));report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and not p.is_symlink()}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
