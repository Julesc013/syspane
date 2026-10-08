"""First-start bytes and native process cuts, independent of the compiled default builder."""
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
import copy, hashlib, json, os, select, signal, stat, subprocess, sys, time, uuid

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/'tests/configuration/profile-startup-cases.json'
COMMAND=ROOT/'tests/configuration/profile-startup-command-case.json'
CASES=json.loads(FIXTURE.read_bytes());TRACE=json.loads(COMMAND.read_bytes())
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
sha=lambda b:hashlib.sha256(b).hexdigest()

def write(p,b):p.write_bytes(b);p.chmod(0o600)
def line(q):
    assert select.select([q.stdout],[],[],8)[0],'startup observation timeout'
    raw=q.stdout.readline();assert raw,'startup EOF';return json.loads(raw)
def stopped(q):
    deadline=time.monotonic()+3
    while time.monotonic()<deadline:
        event=os.waitid(os.P_PID,q.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
        if event:
            assert event.si_code==os.CLD_STOPPED and event.si_status==signal.SIGSTOP
            return
        time.sleep(.01)
    raise AssertionError('owned process did not stop')

def main():
    exe,config_exe,owner_exe,evidence=[Path(v).resolve() for v in sys.argv[1:5]]
    assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('profile-startup-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='PROFILE-STARTUP',outcome='fail',uid=os.geteuid(),filesystem='ext4',kernel=list(os.uname()),
                started_at=datetime.now(timezone.utc).isoformat(),artifacts={p.name:sha(p.read_bytes()) for p in (exe,config_exe,owner_exe)},
                oracle_sha256=sha(Path(__file__).read_bytes()),fixture_sha256=sha(FIXTURE.read_bytes()),command_sha256=sha(COMMAND.read_bytes()),cases=[])
    packages={sha(p['manifest'].encode()):p for p in CASES['packages']}
    body=encoded(TRACE['command']).decode()
    def passed(name,**facts):report['cases'].append(dict(case=name,outcome='pass',**facts));write(folder/'result.json',encoded(report))
    def selection(name,**fields):return dict(profile='profile:default',root=str(folder/name),**fields)
    def args(v,op='open',phase='-',fault='-'):
        p=folder/('input-'+uuid.uuid4().hex[:10]+'.json');write(p,encoded(v));return [str(exe),str(p),op,phase,fault]
    def call(v,op='open',phase='-',fault='-',good=True):
        q=subprocess.run(args(v,op,phase,fault),capture_output=True,timeout=8);out=json.loads(q.stdout)
        assert (q.returncode==0)==good,(v,op,out,q.stderr);return out
    def config_root(v):return Path(v['root'])/'syspane/configuration'/sha(v['profile'].encode())
    def store_root(v):return config_root(v)/'generations'
    def document_expectations(revision='0',forced=None):
        s=copy.deepcopy(CASES['documents']['settings']);scene=copy.deepcopy(CASES['documents']['scene']);s['revision']=scene['revision']=revision
        if revision=='1':s['sampling']['resources_ms']=TRACE['expected_resources_ms']
        for name,value in (forced or {}).items():a,b=name.split('.');s[a][b]=value
        return s,scene
    def check_reply(out,revision='0',forced=None,fallback=False):
        settings,scene=document_expectations(revision,forced)
        assert out['settings']==settings and out['scene']==scene
        assert out['packages']==packages and out['selection']==CASES['selection'] and out['theme_pin']==CASES['theme_pin']
        assert out['recovered_previous']==fallback
        if fallback:assert out['generation'] is None
        else:assert len(out['generation'])==64
        if revision=='0':assert out['identity'] is None and out['receipts']==0
        else:assert out['identity']==dict(epoch='E1',request='R',body=body) and out['receipts']==1
    def inspect(v,revision='0',forced=None):
        root=store_root(v);selector=json.loads((root/'current.json').read_bytes());generation=root/selector['generation']
        manifest_bytes=(generation/'manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
        assert sha(manifest_bytes)==selector['manifest']
        settings,scene=document_expectations(revision,forced)
        for name,value in [('settings',settings),('scene',scene)]:
            raw=(generation/(name+'.json')).read_bytes();assert raw==encoded(value) and sha(raw)==manifest[name]
        assert manifest['revision']==revision
        if revision=='0':assert manifest['version']==CASES['initial_manifest'] and manifest['identity'] is None and not (generation/'request.json').exists()
        else:assert manifest['version']=='0.3.0' and (generation/'request.json').read_bytes()==body.encode()
        index_bytes=(generation/'resources.json').read_bytes();assert sha(index_bytes)==manifest['resources'];index=json.loads(index_bytes)
        assert index==dict(version='0.1.0',selection=CASES['selection'],theme=CASES['theme_pin'],packages=sorted(packages))
        expected=set()
        for key,p in packages.items():
            name='m-'+key+'.json';expected.add(name);assert (generation/'resources'/name).read_bytes()==p['manifest'].encode()
            for asset in p['assets'].values():
                name='a-'+sha(asset.encode())+'.bin';expected.add(name);assert (generation/'resources'/name).read_bytes()==asset.encode()
        assert {p.name for p in (generation/'resources').iterdir()}==expected
        for p in generation.rglob('*'):
            info=p.lstat();assert info.st_uid==os.geteuid()
            assert (stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode)==0o700) or (stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode)==0o600 and info.st_nlink==1)
        return generation
    @contextmanager
    def held(v,phase='-',fault='-',op='session'):
        q=subprocess.Popen(args(v,op,phase,fault),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        try:yield q,line(q)
        finally:
            if q.poll() is None:q.kill();q.wait(timeout=3)
            write(folder/('stderr-'+str(q.pid)),q.stderr.read());q.stdin.close();q.stdout.close();q.stderr.close()
    def send(q,op,**fields):q.stdin.write(encoded(dict(op=op,**fields))+b'\n');q.stdin.flush();return line(q)
    def commit(q):return send(q,'commit',body=body)
    try:
        v=selection('cold');out=call(v);check_reply(out);inspect(v)
        before={p:p.stat().st_ino for p in Path(v['root']).rglob('*')}
        check_reply(call(dict(v,create=False)));assert before=={p:p.stat().st_ino for p in before};inspect(v)
        raw=subprocess.run([str(config_exe),str(store_root(v)),'read'],capture_output=True,timeout=8)
        assert raw.returncode==0 and json.loads(raw.stdout)['settings']==CASES['documents']['settings'];passed('cold-start-exact-reopen-reader')
        with held(v) as (q,out):
            check_reply(out);assert call(v,good=False)['error']=='profile.busy'
            assert send(q,'thread')['error']=='profile_store.thread';check_reply(send(q,'read'))
            result=commit(q);assert result['result']['outcome']=='accepted';check_reply(result['snapshot'],'1')
        check_reply(call(v),'1');inspect(v,'1')
        with held(v) as (q,_):
            result=send(q,'reconcile',epoch='E2',original_epoch='E1',request='R');assert result['result']['outcome']=='accepted' and result['result']['revision']=='1'
        assert len(list(store_root(v).glob('g-*')))==2;passed('normal-edit-restart-reconcile')
        for phase in CASES['cut_phases']:
            v=selection('initial-cut-'+phase.replace(':','_'))
            with held(v,'configuration.initial.'+phase,'stop','open') as (q,event):
                assert event==dict(event='phase',phase='configuration.initial.'+phase,pid=q.pid);stopped(q);q.kill();assert q.wait(timeout=3)==-signal.SIGKILL
            assert not config_root(v).exists()
            stages=list(config_root(v).parent.glob('.*.pending-*'));assert len(stages)==1
            original={p:sha(p.read_bytes()) for p in stages[0].rglob('*') if p.is_file()}
            check_reply(call(v));inspect(v);assert original=={p:sha(p.read_bytes()) for p in original}
            passed('initial-cut-'+phase,cut=event,exit=q.returncode)
        for phase in ('configuration.publish_ready','configuration.published','content.published','state.published'):
            v=selection('profile-cut-'+phase)
            with held(v,phase,'stop','open') as (q,event):stopped(q);q.kill();assert q.wait(timeout=3)==-signal.SIGKILL
            if phase=='configuration.publish_ready':assert not config_root(v).exists()
            else:inspect(v)
            check_reply(call(v));inspect(v);assert len(list(store_root(v).glob('g-*')))==1
            passed('profile-cut-'+phase,cut=event,exit=q.returncode)
        for phase in ('created','resource_index','selector_ready','authorized','selected','durable'):
            v=selection('commit-cut-'+phase);call(v)
            with held(v,'store.'+phase,'stop') as (q,out):
                check_reply(out);event=commit(q);assert event['event']=='phase';stopped(q);q.kill();assert q.wait(timeout=3)==-signal.SIGKILL
            revision='1' if phase in ('selected','durable') else '0';check_reply(call(v),revision);inspect(v,revision)
            passed('commit-cut-'+phase,cut=event,exit=q.returncode)
        for phase in ('configuration.initial.created','configuration.initial.selector_ready','configuration.publish_ready'):
            for fault in ('deny','change'):
                v=selection('initial-'+fault+'-'+phase)
                assert call(v,phase=phase,fault=fault,good=False)['error'].startswith(('profile.','storage.'))
                assert not config_root(v).exists();check_reply(call(v));inspect(v);passed('initial-'+fault+'-'+phase)
        for op in ('deny','revision','forced','disclosure','capability','throw','source-reentry'):
            v=selection('policy-'+op);call(v);before={p:sha(p.read_bytes()) for p in store_root(v).rglob('*') if p.is_file()}
            with held(v) as (q,_):
                assert send(q,op)['error'].startswith('profile')
                assert send(q,'regrant')['error']=='profile_store.invalidated'
            assert before=={p:sha(p.read_bytes()) for p in before};check_reply(call(v));passed('policy-'+op)
        for phase in ('store.selector_ready','store.authorized'):
            v=selection('commit-deny-'+phase);call(v)
            with held(v,phase,'deny') as (q,_):
                result=commit(q)
                # At authorized the native selection permit has already linearized.
                expected='accepted' if phase=='store.authorized' else 'invalid'
                assert result['result']['outcome']==expected,(phase,result)
            revision='1' if phase=='store.authorized' else '0';check_reply(call(v),revision);inspect(v,revision);passed('commit-deny-'+phase)
        for fields in ({'available':False},{'denied':['profile.open']},{'denied':['profile.create']},{'denied':['settings.commit']},{'capabilities':[]},{'forced':{'display.theme_id':'theme:absent'}}):
            v=selection('denied-'+uuid.uuid4().hex[:8],**fields);assert call(v,good=False)['error'];assert not config_root(v).exists();passed('new-refusal-'+str(fields))
        v=selection('forced',forced={'sampling.resources_ms':1500,'display.enabled':False});check_reply(call(v),forced=v['forced']);inspect(v,forced=v['forced'])
        # A new policy does not rewrite already requested saved settings.
        check_reply(call(dict(v,forced={'sampling.resources_ms':2000})),forced=v['forced']);inspect(v,forced=v['forced']);passed('forced-initial-and-preserved-authored-values')
        v=selection('create-denied-existing');call(v);check_reply(call(dict(v,denied=['profile.create'])));passed('create-denial-allows-existing-open')
        v=selection('empty-existing');request=folder/'owner-empty.json';write(request,encoded(dict(profile=v['profile'],portable_root=v['root'])))
        q=subprocess.run([str(owner_exe),str(request),'open','-','-'],capture_output=True,timeout=8);assert q.returncode==0
        assert call(v,good=False)['error']=='storage.unavailable' and not list(store_root(v).glob('g-*'));passed('marked-empty-not-reseeded')
        for mutation in ('settings','scene'):
            v=selection('staged-'+mutation)
            with held(v,'configuration.publish_ready','block','open') as (q,_):
                stage=next(config_root(v).parent.glob('.*.pending-*'));root=stage/'generations';selector=json.loads((root/'current.json').read_bytes());g=root/selector['generation']
                value=json.loads((g/(mutation+'.json')).read_bytes())
                if mutation=='settings':value['sampling']['resources_ms']=2000
                else:value['widgets'][0]['title']='Changed'
                write(g/(mutation+'.json'),encoded(value));m=json.loads((g/'manifest.json').read_bytes());m[mutation]=sha(encoded(value));write(g/'manifest.json',encoded(m));selector['manifest']=sha(encoded(m));write(root/'current.json',encoded(selector))
                q.stdin.write(b'resume\n');q.stdin.flush();assert line(q)['error']=='profile.initial_changed' and q.wait(timeout=3)==1
                assert not config_root(v).exists()
            passed('staged-'+mutation)
        for mutation in ('downgrade','revision','resource'):
            v=selection('corrupt-'+mutation);call(v);g=inspect(v);root=store_root(v);selector=json.loads((root/'current.json').read_bytes());m=json.loads((g/'manifest.json').read_bytes())
            if mutation=='downgrade':m['version']='0.2.0'
            elif mutation=='revision':
                m['revision']='1'
                for name in ('settings','scene'):
                    x=json.loads((g/(name+'.json')).read_bytes());x['revision']='1';write(g/(name+'.json'),encoded(x));m[name]=sha(encoded(x))
            else:
                resource=next((g/'resources').glob('a-*'));write(resource,b'corrupt')
            write(g/'manifest.json',encoded(m));selector['manifest']=sha(encoded(m));write(root/'current.json',encoded(selector))
            before={p:sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()};assert call(v,good=False)['error']=='storage.unrecoverable'
            assert before=={p:sha(p.read_bytes()) for p in before};passed('corrupt-'+mutation)
        v=selection('previous-recovery');call(v)
        with held(v) as (q,_):assert commit(q)['result']['outcome']=='accepted'
        write(store_root(v)/'current.json',b'{}')
        with held(v) as (q,out):
            check_reply(out,fallback=True);assert commit(q)['result']['outcome']=='invalid'
        assert (store_root(v)/'current.json').read_bytes()==b'{}';passed('previous-recovery-read-only')
        v=selection('native-source',create=False);policy=call(v,'native-policy');assert call(v,'native-open',good=False)['error'];assert not Path(v['root']).exists()
        passed('native-fixed-policy-source',observed_policy_available=policy['available'],positive_native_provenance_qualified=False)
        v=selection('wrong-byte-control');out=call(v);out['settings']['sampling']['resources_ms']=999;detected=False
        try:check_reply(out)
        except AssertionError:detected=True
        assert detected;passed('wrong-byte-oracle-control',fault_detected=True)
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        report['files']={p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if stat.S_ISREG(p.lstat().st_mode) and p.name!='result.json'}
        write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'],len(report['cases']))

if __name__=='__main__':main()
