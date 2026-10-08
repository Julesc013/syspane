"""Independent store bytes for commands emitted by the actual shared EditorDraft."""
from pathlib import Path
from datetime import datetime,timezone
import copy,json,os,select,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/configuration'))
from native_large_commands import Store,encoded,generation,sha,write
CASES=json.loads((ROOT/'tests/editor/theme-history-cases.json').read_bytes())
FIXTURE=json.loads((ROOT/'tests/configuration/settings-content-fixture.json').read_bytes())
BASE=json.loads((ROOT/'tests/configuration/theme-command-cases.json').read_bytes())['base_manifests']

class HistoryStore(Store):
    def __init__(self,exe,folder):
        self.exe,self.folder=exe,folder;folder.mkdir(mode=0o700);self.path=folder/'store';self.path.mkdir(mode=0o700)
        self.imports=[];self.catalog=folder/'imports';self.catalog.mkdir(mode=0o700)
        for n,pkg in enumerate(FIXTURE['packages']):
            p=self.catalog/str(n);p.mkdir(mode=0o700);self.imports.append(p);write(p/'manifest.json',pkg['manifest'].encode())
            for name,raw in pkg['assets_hex'].items():
                dest=p/name;dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True);write(dest,bytes.fromhex(raw))
        settings=copy.deepcopy(CASES['base']['settings']);scene=json.loads((ROOT/'spec/fixtures/valid/scene-portable.json').read_bytes())
        settings['revision']=scene['revision']='39';write(folder/'settings.json',encoded(settings));write(folder/'scene.json',encoded(scene))
        self.call('init',folder/'settings.json',folder/'scene.json')
        scene=copy.deepcopy(CASES['base']['scene']);scene['revision']='39'
        command=dict(schema_version='0.5.0',request_id='bootstrap',expected_revision='39',policy_generation='7',intent='commit',content=FIXTURE['selection'],operations=[dict(op='scene.replace',scene=scene)])
        write(folder/'bootstrap.json',encoded(command));result=self.call('content-commit',folder/'bootstrap.json','-',*self.imports)['result']
        assert result['outcome']=='accepted' and result['revision']=='40'
        actual=self.call('read');assert actual['scene']==CASES['base']['scene'] and actual['settings']==CASES['base']['settings'] and not actual['recovered_previous']
def inspect(store,body,key,revision):
    scene=copy.deepcopy(CASES['base']['scene'] if key=='reset' else CASES['scenes'][key]);scene['revision']=str(revision)
    settings=copy.deepcopy(CASES['base']['settings']);settings['revision']=str(revision)
    selected=CASES['base_selection'] if key=='reset' else CASES['selections'][key]
    g,m=generation(store.path);assert m['version']=='0.4.0' and m['revision']==str(revision)
    assert (g/'request.json').read_bytes()==body and sha(g/'request.json')==m['identity']['body_sha256']
    assert json.loads((g/'scene.json').read_bytes())==scene and json.loads((g/'settings.json').read_bytes())==settings
    for name in ('scene','settings','resources'):assert sha(g/(name+'.json'))==m[name]
    index=json.loads((g/'resources.json').read_bytes());assert index['version']=='0.2.0' and index['selection']==selected
    packages=[p for p in FIXTURE['packages'] if __import__('hashlib').sha256(p['manifest'].encode()).hexdigest() in BASE]
    files={}
    for p in packages:
        files['m-'+__import__('hashlib').sha256(p['manifest'].encode()).hexdigest()+'.json']=p['manifest'].encode()
        for value in p['assets_hex'].values():
            raw=bytes.fromhex(value);files['a-'+__import__('hashlib').sha256(raw).hexdigest()+'.bin']=raw
    if key!='reset':
        a=CASES['artifacts'][key];files['m-'+a['package_pin']['sha256']+'.json']=a['manifest'].encode();files['a-'+a['theme_pin']['sha256']+'.bin']=a['asset'].encode()
        assert index['theme']==a['theme_pin'];theme=a['theme']
    else:
        theme=json.loads(next(raw for raw in files.values() if __import__('hashlib').sha256(raw).hexdigest()==FIXTURE['themes']['theme:native']['sha256']))
        assert index['theme']==FIXTURE['themes']['theme:native']
    assert index['packages']==sorted(BASE+([] if key=='reset' else [CASES['artifacts'][key]['package_pin']['sha256']]))
    assert set(p.name for p in (g/'resources').iterdir())==set(files)
    for name,raw in files.items():assert (g/'resources'/name).read_bytes()==raw
    return scene,theme,selected
def main():
    exe,probe,evidence=map(lambda s:Path(s).resolve(),sys.argv[1:4]);assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent)
    folder=evidence/('theme-history-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700,parents=True)
    assert subprocess.check_output(['findmnt','--target',str(folder),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
    report=dict(family='THEME-HISTORY',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),oracle_sha256=sha(Path(__file__)),executable_sha256=sha(exe),store_executable_sha256=sha(probe),fixture_sha256=sha(ROOT/'tests/editor/theme-history-cases.json'),cases=[])
    try:
        for mode in ('normal','lost','wrong-report'):
            f=HistoryStore(probe,folder/mode);p=subprocess.Popen([str(exe),str(ROOT),str(f.path),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0);events=[];detected=False
            def receive():
                assert select.select([p.stdout],[],[],8)[0],'draft observation timeout';line=p.stdout.readline();assert line,'draft EOF';v=json.loads(line);events.append(v);return v
            try:
                for i,key in enumerate(('first',) if mode=='lost' else ('first','second','reset')):
                    v=receive();assert v['event']=='request' and v['step']==key;body=v['body'].encode();q=json.loads(body)
                    expected=copy.deepcopy(CASES['commands'][key] if key!='reset' else CASES['commands']['first']);expected['request_id']='history:'+key;expected['expected_revision']=str(40+i)
                    if key=='reset':expected.update(theme_edit=None,content=CASES['base_selection']);expected['operations'][0]['scene']=copy.deepcopy(CASES['base']['scene'])
                    if key=='second':expected['theme_edit']['source']=CASES['artifacts']['first']['theme_pin']
                    expected['operations'][0]['scene']['revision']=str(40+i);assert q==expected
                    write(f.folder/'editor-request.json',body);result=f.call('theme-commit',f.folder/'editor-request.json','-')['result'];assert result['outcome']=='accepted' and result['revision']==str(41+i)
                    scene,theme,selection=inspect(f,body,key,41+i)
                    if mode=='lost':result=dict(schema_version='0.1.0',query_id='Q',original_producer_epoch='E1',request_id=q['request_id'],result=f.call('reconcile','E1',q['request_id'])['result'])
                    p.stdin.write(encoded(result)+b'\n');p.stdin.flush();v=receive();assert v['event']=='accepted' and v['scene']==scene and v['selection']==selection
                    if mode=='wrong-report':
                        assert v['theme']!=theme;detected=True;break
                    assert v['theme']==theme
                if mode!='wrong-report':
                    v=receive();assert v==dict(event='reloaded',scene=scene,theme=theme,selection=selection);assert p.wait(timeout=5)==0
                else:assert detected
                report['cases'].append(dict(case=mode,outcome='pass',fault_detected=detected,events=events))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=3)
                write(f.folder/'draft.stderr',p.stderr.read())
                write(f.folder/'draft.events.json',encoded(events))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and not p.is_symlink()};write(folder/'result.json',encoded(report));print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
