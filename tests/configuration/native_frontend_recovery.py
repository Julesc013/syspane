"""Observe the actual frontend backend, original-request metadata and native files."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,select,shutil,signal,stat,subprocess,sys,time,traceback,uuid,zipfile
ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'tests/configuration/frontend-recovery-cases.json').read_bytes())
INITIAL=json.loads((ROOT/CASES['initial_documents']).read_bytes())
COMMAND=json.loads((ROOT/CASES['expected_command']).read_bytes())
EXPECTED=json.loads((ROOT/CASES['expected_scene']).read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
sys.path.insert(0,str(ROOT/'tests/configuration'))
from native_settings import stored

def main(extension=None,definitions=None):
    global CASES
    if definitions is not None:CASES=json.loads(definitions.read_bytes())
    probe,helper,evidence=[Path(p).resolve() for p in sys.argv[1:4]];build=probe.parent
    assert os.geteuid() and helper.parent==evidence.parent==build
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    runtime=build.parent/'F';marker=encoded(dict(format='SysPane.InstalledSettingsLab',root=str(build.parent)))
    if not runtime.exists():runtime.mkdir(mode=0o700);(runtime/'.owner.json').write_bytes(marker)
    assert runtime.resolve()==runtime and (runtime/'.owner.json').read_bytes()==marker and stat.S_IMODE(runtime.stat().st_mode)==0o700
    folder=evidence/(('rl-' if extension else 'fr-')+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700)
    report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),cases=[],runs=[],
        oracle_sha256=sha(Path(__file__).read_bytes()),cases_sha256=sha((definitions or ROOT/'tests/configuration/frontend-recovery-cases.json').read_bytes()),command_sha256=sha((ROOT/CASES['expected_command']).read_bytes()))
    def save():(folder/'result.json').write_bytes(encoded(report))
    stage=folder/'original';stage.mkdir(mode=0o700)
    files={'bin/syspane':probe,'libexec/syspane/syspane-configuration-host':helper,'libexec/syspane/syspane-image-worker':build/'SysPane.ImageWorker',
        'libexec/syspane/syspane-recovery-worker':build/'SysPane.RecoveryWorker','share/syspane/helpers.json':build/'generated/frontend-fixture/helpers.json'}
    for name,source in files.items():
        p=stage/name;p.parent.mkdir(mode=0o755,parents=True,exist_ok=True);shutil.copyfile(source,p);p.chmod(0o644 if name.endswith('.json') else 0o755)
    manifest=json.loads((stage/'share/syspane/helpers.json').read_bytes())
    for v in manifest['helpers'].values():assert sha((stage/v['path']).read_bytes())==v['sha256']
    archive=folder/'bundle.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name in files:z.write(stage/name,name)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())==set(files)
        for name in files:assert z.read(name)==(stage/name).read_bytes()
    report['package']=dict(sha256=sha(archive.read_bytes()),files={n:sha(p.read_bytes()) for n,p in files.items()})
    relocated=folder/'relocated';assert stage.parent==relocated.parent==folder;stage.rename(relocated);exe=relocated/'bin/syspane'
    started=time.monotonic()
    class Run:
        def __init__(self,name,history='allow',enforce_timing=True):
            self.enforce_timing=enforce_timing
            self.root=folder/name;self.root.mkdir(mode=0o700);self.deadline=time.monotonic()+CASES['case_timeout_seconds'];self.children={};self.events=[];self.buffer=b'';self.queue=False;self.closed=False
            for n,v in dict(policy='allow',history=history,phase='',release='',reconcile='allow').items():(self.root/n).write_text(v+'\n')
            self.runtime=runtime;self.runtime_roots=set(runtime.glob('sp-*'));(self.root/'home').mkdir(mode=0o700)
            env=dict(os.environ,HOME=str(self.root/'home'),XDG_CONFIG_HOME=str(self.root/'config'),XDG_DATA_HOME=str(self.root/'data'),XDG_STATE_HOME=str(self.root/'state'))
            self.err=(self.root/'stderr').open('wb');self.proc=subprocess.Popen([str(exe),str(self.runtime)],cwd=self.root,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err)
            self.record=dict(case=name,pid=self.proc.pid,events=self.events,children=[]);report['runs'].append(self.record)
        def left(self):
            assert time.monotonic()<self.deadline,'case deadline'
            assert time.monotonic()-started<CASES['family_timeout_seconds'],'family deadline'
        def inspect_children(self):
            if self.proc.poll() is not None:return
            children=set()
            for task in Path('/proc',str(self.proc.pid),'task').iterdir():
                try:children.update(map(int,(task/'children').read_text().split()))
                except FileNotFoundError:pass
            for pid in children:
                if pid in self.children:continue
                try:
                    fd=os.pidfd_open(pid);name=os.readlink('/proc/'+str(pid)+'/exe')
                    self.children[pid]=(fd,name)
                except ProcessLookupError:continue
                except FileNotFoundError:
                    if 'fd' in locals():os.close(fd)
        def call(self,op,**args):
            self.left();self.inspect_children();payload=dict(op=op,**args);self.proc.stdin.write(encoded(payload)+b'\n');self.proc.stdin.flush()
            while b'\n' not in self.buffer:
                self.left();assert select.select([self.proc.stdout],[],[],min(5,max(.001,self.deadline-time.monotonic())))[0],('response timeout',op)
                raw=os.read(self.proc.stdout.fileno(),65536);assert raw,(op,self.proc.poll(),(self.root/'stderr').read_text());self.buffer+=raw
            line,self.buffer=self.buffer.split(b'\n',1);value=json.loads(line);self.events.append(dict(op=op,response=value));self.inspect_children()
            if value['elapsed_us']>=CASES['gui_operation_limit_ms']*1000:
                self.record.setdefault('timing_violations',[]).append(dict(op=op,elapsed_us=value['elapsed_us']))
                assert not self.enforce_timing,(op,value['elapsed_us'])
            return value['result']
        def wait(self,predicate):
            while True:
                self.left();value=predicate()
                if value:return value
                time.sleep(.005)
        def ready(self,after=0):
            def sample():
                v=self.call('view');p=v['profile'];return p if p and not v['loading'] and not v['pending'] and p['serial']>after else None
            return self.wait(sample)
        def load(self,old=False):self.call('load',old=old);self.queue=True;return self.completion()
        def completion(self):return self.wait(lambda:self.call('poll')['completion'])
        def drop(self):
            if self.queue:
                self.call('stop');self.wait(lambda:self.call('poll')['reaped']);self.call('drop');self.queue=False
        def controller(self):
            self.inspect_children();alive=[(p,fd) for p,(fd,n) in self.children.items() if 'memfd:syspane-configuration-host' in n and not select.select([fd],[],[],0)[0]]
            assert len(alive)==1,alive;return alive[0]
        def kill_controller(self):
            _pid,fd=self.controller();signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
        def close(self):
            self.call('close');self.wait(lambda:self.call('view')['stopped']);self.drop();self.call('end');self.proc.stdin.close();self.proc.wait(timeout=5);assert self.proc.returncode==0
            assert set(self.runtime.glob('sp-*'))==self.runtime_roots,'runtime still present'
            self.closed=True
        def finish(self):
            if self.proc.poll() is None:
                self.record['forced_cleanup']=True;self.proc.kill();self.proc.wait(timeout=5)
            for pid,(fd,name) in self.children.items():
                exited=bool(select.select([fd],[],[],2)[0]);self.record['children'].append(dict(pid=pid,name=name,exited=exited))
                if not exited:signal.pidfd_send_signal(fd,signal.SIGKILL)
                os.close(fd)
            self.err.close();self.record.update(exit=self.proc.returncode,stderr=(self.root/'stderr').read_text(),closed=self.closed);save()
    def generations(q):return q.root/'config/syspane/configuration'/sha(CASES['profile'].encode())/'generations'
    def documents(q,edited=False):
        expected=copy.deepcopy(INITIAL['documents'])
        if edited:expected['scene']=EXPECTED;expected['settings']['revision']='1'
        assert stored(generations(q))==expected
        assert not any(json.loads(p.read_bytes())['revision']=='2' for p in generations(q).glob('*/scene.json'))
    def scope(q,p):
        v=p['recovery'];assert v and v['epoch']==p['epoch'] and v['profile']==CASES['profile'] and v['revision']==p['revision'] and v['policy']==7
        assert v['generation']==sha((generations(q)/'current.json').read_bytes())
        path=q.root/'state/syspane/state'/sha(CASES['profile'].encode())/'recovery';assert v['directory']['path']==str(path)
        a=path.parent.stat();b=path.stat();assert v['directory']==dict(path=str(path),uid=os.geteuid(),state_device=a.st_dev,state_inode=a.st_ino,recovery_device=b.st_dev,recovery_inode=b.st_ino)
        assert stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==0o700
        return path/'draft.json'
    def raw(p):return encoded(dict(format='syspane.editor-recovery',schema_version='0.1.0',identity=dict(profile=CASES['profile'],generation=p['recovery']['generation']),command=encoded(COMMAND).decode()))
    def capture(q,p):
        path=scope(q,p);assert q.load()==dict(operation='load',outcome='loaded',digest=None,bytes=None)
        data=raw(p);q.call('replace',bytes=data.decode());done=q.completion();assert done==dict(operation='replace',outcome='durable',digest=sha(data),bytes=None);assert path.read_bytes()==data
        return path,data
    def submit(q,data,digest=True,command=None):
        value=copy.deepcopy(command or COMMAND);value['intent']='commit';return q.call('submit',command=value,digest=sha(data) if digest else None)
    def accepted(q):
        def sample():
            value=q.call('view');reply=value['reply'];body=reply and reply['body'];result=body and (body['result'] if 'result' in body else body)
            if result:assert result['outcome']=='accepted' and result['stored'] and result['durable'] and result['revision']=='1';return reply
        return q.wait(sample)
    try:
        if extension:
            extension(dict(Run=Run,report=report,folder=folder,save=save,documents=documents,scope=scope))
            report['outcome']='pass';return
        for case in CASES['cases']:
            begin=time.monotonic();q=Run(case,'none' if case=='NULL-CONTEXT' else 'erase-denied' if case=='ERASE-DENIED' else 'allow')
            try:
                p=q.ready();documents(q)
                if case=='NULL-CONTEXT':assert p['recovery'] is None and p['retirement'] is None and q.call('load')=={'error':'probe.state'}
                elif case=='SCOPED-CONTEXT':
                    scope(q,p);assert p['retirement'] is None;assert q.call('ack',serial=p['serial'])=={'error':'frontend.retirement_scope'}
                    q.call('reload');fresh=q.ready(p['serial']);scope(q,fresh);assert fresh['recovery']['session']!=p['recovery']['session'] and fresh['epoch']==p['epoch']
                    q.call('prepare',bytes=raw(fresh).decode());prepared=q.wait(lambda:(lambda v:v if v['ready'] else None)(q.call('prepared')));assert prepared['scene']==COMMAND['operations'][0]['scene']
                else:
                    path,data=capture(q,p)
                    if case=='INVALID-METADATA':
                        command=copy.deepcopy(COMMAND);command['intent']='commit';assert q.call('submit',command=command,digest='bad')=={'error':'frontend.recovery_capture'};documents(q)
                        q.call('submit',command=command,digest='0'*64);q.drop();fresh=q.ready(p['serial']);documents(q);assert fresh['retirement'] is None and path.read_bytes()==data
                        command['operations']=[dict(op='settings.set',path='sampling.resources_ms',value=1500)];q.call('submit',command=command,digest=sha(data));q.ready(fresh['serial']);documents(q);assert path.read_bytes()==data
                    elif case=='RELOAD-WITHDRAWAL':
                        q.call('remember');q.call('reload');q.wait(lambda:q.call('poll')['reaped']);q.drop();fresh=q.ready(p['serial']);assert fresh['recovery']['session']!=p['recovery']['session']
                        q.call('load',old=True);q.queue=True;q.wait(lambda:(lambda v:v['reaped'] and v['state'] in (5,7))(q.call('poll')));assert path.read_bytes()==data;q.drop();assert q.load()['bytes']==data.decode()
                    elif case=='POLICY-WITHDRAWAL':
                        (q.root/'policy').write_text('deny\n');q.wait(lambda:q.call('view')['profile'] is None);q.wait(lambda:q.call('poll')['reaped']);assert path.read_bytes()==data
                        q.drop();(q.root/'policy').write_text('allow\n');fresh=q.ready(p['serial']);assert fresh['recovery']['session']!=p['recovery']['session'];assert q.load()['bytes']==data.decode()
                    elif case=='CLOSE':
                        q.call('replace',bytes=(data+b' ').decode());q.close();assert path.read_bytes() in (data,data+b' ')
                    elif case=='ORACLE':
                        detected=False
                        try:assert path.read_bytes()==data+b'\n'
                        except AssertionError:detected=True
                        assert detected;report['wrong_oracle_detected']=True
                    else:
                        if case in ('LOST-ACCEPTANCE','UNKNOWN-RESULT'):(q.root/'phase').write_text(('store.durable' if case=='LOST-ACCEPTANCE' else 'store.selector_ready')+'\n')
                        result=submit(q,data,case!='KEPT-RECORD');assert 'request' in result,result
                        if case in ('LOST-ACCEPTANCE','UNKNOWN-RESULT'):
                            q.wait(lambda:(q.root/'held').exists());(q.root/'phase').write_text('');q.kill_controller()
                        if case=='UNKNOWN-RESULT':
                            q.wait(lambda:'Outcome unknown' in q.call('view')['status']);assert q.call('view')['pending'];documents(q);assert path.read_bytes()==data
                        else:
                            reply=accepted(q);assert bool(reply['query'])==(case=='LOST-ACCEPTANCE');q.drop();documents(q,True)
                            if case=='DIRECTORY-REPLACED':
                                q.kill_controller();directory=path.parent;old=q.root/'recovery-original';assert directory.resolve().is_relative_to(q.root.resolve()) and old.parent.resolve()==q.root.resolve() and not old.exists();directory.rename(old);directory.mkdir(mode=0o700);path.write_bytes(data);path.chmod(0o600)
                            elif case!='LOST-ACCEPTANCE':q.call('reload')
                            fresh=q.ready(p['serial']);scope(q,fresh)
                            if case in ('KEPT-RECORD','ERASE-DENIED','DIRECTORY-REPLACED'):assert fresh['retirement'] is None and path.read_bytes()==data
                            else:
                                assert fresh['retirement']==sha(data) and fresh['recovery']['generation']!=p['recovery']['generation']
                                assert q.call('ack',serial=p['serial'])=={'error':'frontend.retirement_scope'}
                                if case=='REPLACEMENT-RECORD':path.write_bytes(b'replacement');path.chmod(0o600)
                                loaded=q.load()
                                if case=='REPLACEMENT-RECORD':assert loaded['digest']!=fresh['retirement'] and path.read_bytes()==b'replacement'
                                else:
                                    assert loaded['digest']==fresh['retirement'];q.call('retire');assert q.completion()['outcome']=='durable';assert not path.exists()
                                q.call('ack',serial=fresh['serial']);assert q.call('ack',serial=fresh['serial'])=={'error':'frontend.retirement_scope'}
                                q.drop();q.call('reload');assert q.ready(fresh['serial'])['retirement'] is None
                if not q.closed:q.close()
                report['cases'].append(dict(case=case,outcome='pass',seconds=time.monotonic()-begin));save()
            finally:q.finish()
        report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:report['finished_at']=datetime.now(timezone.utc).isoformat();report['seconds']=time.monotonic()-started;save();print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
