"""Independent literal recovery, real generation identity, Apply and lost-result checks."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,os,select,signal,subprocess,sys,uuid
from native_theme_history import HistoryStore,inspect as inspect_theme,encoded,generation,sha,write,FIXTURE
from native_settings import check_resources
ROOT=Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'tests/editor/recovery-draft-cases.json').read_bytes())
NATIVE=json.loads((ROOT/'tests/editor/recovery-apply-cases.json').read_bytes())

def inspect(store,body,theme):
    if theme:return inspect_theme(store,body,'first',41)
    scene=copy.deepcopy(CASES['scene']);scene['revision']='41'
    settings=copy.deepcopy(CASES['authored']['settings']);settings['revision']='41'
    g,m=generation(store.path);assert m['version']=='0.3.0' and m['revision']=='41'
    assert (g/'request.json').read_bytes()==body and sha(g/'request.json')==m['identity']['body_sha256']
    for name,want in [('scene',scene),('settings',settings)]:
        assert json.loads((g/(name+'.json')).read_bytes())==want and sha(g/(name+'.json'))==m[name]
    check_resources(store.path,manifest_version='0.3.0')
    read=store.call('read');assert read['scene']==scene and read['settings']==settings and not read['recovered_previous']
    return scene,read['resources']['theme'],CASES['selection']

def main():
    exe,probe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:4]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('recovery-apply-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='RECOVERY-APPLY',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),executable_sha256=sha(exe),store_executable_sha256=sha(probe),fixture_sha256=sha(ROOT/'tests/editor/recovery-draft-cases.json'),native_fixture_sha256=sha(ROOT/'tests/editor/recovery-apply-cases.json'),cases=[])
    def one(path,mode):
        p=subprocess.run([str(exe),str(ROOT),str(path),mode],capture_output=True,timeout=8)
        assert p.returncode==0,(mode,p.returncode,p.stderr);return json.loads(p.stdout)
    try:
        for mode in NATIVE['cases']:
            f=HistoryStore(probe,folder/mode);token=sha(f.path/'current.json');initial_dirs=sorted(p.name for p in f.path.glob('g-*'))
            theme=mode.startswith('theme');q=copy.deepcopy(CASES['theme_commands']['first'] if theme else CASES['command'])
            envelope=copy.deepcopy(CASES['envelope']);envelope.update(identity=dict(profile=NATIVE['profile'],generation=token),command=encoded(q).decode());record=encoded(envelope).decode()
            capture=one(f.path,'capture-theme' if theme else 'capture');assert capture==dict(event='captured',token=token,record=record)
            assert sha(f.path/'current.json')==token
            write(f.folder/'capture.json',encoded(capture))
            if mode=='wrong-generation':envelope['identity']['generation']='0'*64;record=encoded(envelope).decode()
            p=subprocess.Popen([str(exe),str(ROOT),str(f.path),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0);events=[]
            def receive():
                assert select.select([p.stdout],[],[],8)[0],'recovery observation timeout'
                line=p.stdout.readline();assert line,'recovery EOF';v=json.loads(line);events.append(v);return v
            try:
                p.stdin.write(encoded(record)+b'\n');p.stdin.flush()
                v=receive()
                if mode in ('revoked','wrong-generation'):
                    assert v==dict(event='refused',scene=CASES['authored']['scene'],token=token)
                    assert p.wait(timeout=5)==0 and sha(f.path/'current.json')==token
                    assert sorted(x.name for x in f.path.glob('g-*'))==initial_dirs
                    report['cases'].append(dict(case=mode,outcome='pass',events=events));continue
                restored=CASES['theme_scenes']['first'] if theme else CASES['scene']
                selection=CASES['theme_selections']['first'] if theme else CASES['selection']
                expected_theme=CASES['theme_artifacts']['first']['theme'] if theme else f.call('read')['resources']['theme']
                assert v==dict(event='restored',scene=restored,theme=expected_theme,selection=selection,token=token)
                assert sha(f.path/'current.json')==token
                v=receive();assert v['event']=='request';body=v['body'].encode()
                q.update(intent='commit',request_id=NATIVE['request_id']);assert body==encoded(q)
                write(f.folder/'editor-request.json',body)
                operation='theme-commit' if theme else 'content-commit'
                imports=[] if theme else f.imports
                if 'lost' in mode:
                    args=[str(probe),str(f.path),operation,str(f.folder/'editor-request.json'),NATIVE['interrupt_after'],*map(str,imports)]
                    cut=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    try:
                        assert select.select([cut.stdout],[],[],8)[0],'commit cut timeout'
                        event=json.loads(cut.stdout.readline());assert event==dict(transition=NATIVE['interrupt_after'])
                        cut.kill();assert cut.wait(timeout=3)==-signal.SIGKILL
                        write(f.folder/'cut.json',encoded(dict(event=event,exit=cut.returncode,stderr=cut.stderr.read().decode())))
                    finally:
                        if cut.poll() is None:cut.kill();cut.wait(timeout=3)
                    result=dict(schema_version='0.1.0',query_id='Q',original_producer_epoch='E1',request_id=q['request_id'],result=f.call('reconcile','E1',q['request_id'])['result'])
                    assert result['result']['outcome']=='accepted' and result['result']['revision']=='41'
                else:
                    result=f.call(operation,f.folder/'editor-request.json','-',*imports)['result'];write(f.folder/'commit-result.json',encoded(result));assert result['outcome']=='accepted' and result['revision']=='41'
                scene,expected_theme,selection=inspect(f,body,theme)
                p.stdin.write(encoded(result)+b'\n');p.stdin.flush();v=receive()
                assert v['event']=='accepted' and v['theme']==expected_theme and v['selection']==selection
                detected=mode=='wrong-report'
                if detected:assert v['scene']!=scene
                else:assert v['scene']==scene
                new_token=sha(f.path/'current.json');assert new_token!=token
                assert receive()==dict(event='reloaded',old_record_rejected=True,scene=scene,theme=expected_theme,selection=selection,token=new_token)
                assert p.wait(timeout=5)==0
                assert len(list(f.path.glob('g-*')))==len(initial_dirs)+1
                assert one(f.path,'token-read')==dict(event='token',token=new_token,scene=scene)
                report['cases'].append(dict(case=mode,outcome='pass',fault_detected=detected,events=events))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=3)
                write(f.folder/'draft.stderr',p.stderr.read());write(f.folder/'draft.events.json',encoded(events))
        for mode in NATIVE['token_refusal_cases']:
            if mode=='empty':
                path=folder/'empty';path.mkdir(mode=0o700);before=None
            else:
                f=HistoryStore(probe,folder/('token-'+mode));path=f.path;before=sha(path/'current.json')
                if mode in ('fallback','damaged'):write(path/('current.json' if mode=='fallback' else 'previous.json'),b'corrupt')
            v=one(path,'token-'+mode);assert v==dict(event='token-unavailable',readable=mode in ('fallback','damaged'),fallback=mode=='fallback')
            if mode=='poisoned':
                after=sha(path/'current.json');assert after!=before
                assert one(path,'token-read')==dict(event='token',token=after,scene=CASES['authored']['scene'])
                assert f.call('read')['scene']==CASES['authored']['scene']
            report['cases'].append(dict(case='token-'+mode,outcome='pass',observation=v))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and not p.is_symlink()};write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
