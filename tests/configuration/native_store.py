"""Independent coherent-generation/crash oracle on an owned native Linux ext4 root."""
from pathlib import Path
import copy,hashlib,json,os,select,signal,subprocess,sys,time,uuid,warnings,importlib.metadata
import jsonschema

exe=Path(sys.argv[1]).resolve();repo=Path(sys.argv[2]).resolve();evidence=Path(sys.argv[3]).resolve()
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(exe).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('configuration-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
filesystem=subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip()
assert filesystem=='ext4','native experiment requires the admitted ext4 profile'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
def validate(value,name):
    schema=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',DeprecationWarning)
        jsonschema.Draft202012Validator(schema,resolver=jsonschema.RefResolver.from_schema(schema,store=schemas)).validate(value)
def write(p,v):p.write_text(json.dumps(v,separators=(',',':')),encoding='utf-8');p.chmod(0o600)
settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text())
settings['revision']=scene['revision']='40';scene['widgets'][1]['layout']={'base':{'kind':'fixed','x':10,'y':20,'width':240,'height':80}}
write(root/'settings.json',settings);write(root/'scene.json',scene)
candidate=copy.deepcopy(scene);candidate['widgets'][1]['layout']['base']['x']=20
command={'schema_version':'0.2.0','request_id':'R','expected_revision':'40','policy_generation':'7','intent':'commit',
 'operations':[{'op':'scene.replace','scene':candidate},{'op':'settings.set','path':'sampling.resources_ms','value':1500}]}
write(root/'command.json',command);validate(command,'command-v0.2')
expected={40:(settings,scene)};new_settings=copy.deepcopy(settings);new_scene=copy.deepcopy(candidate)
new_settings['revision']=new_scene['revision']='41';new_settings['sampling']['resources_ms']=1500;expected[41]=(new_settings,new_scene)
record={'family':'CONFIG-STORE','outcome':'running','executable_sha256':sha(exe),'oracle_sha256':sha(Path(__file__)),
 'filesystem':filesystem,'uid':os.geteuid(),'cases':[],
 'schema_oracle':{'version':importlib.metadata.version('jsonschema'),'module_sha256':sha(Path(jsonschema.__file__))},
 'qualification':'Owned synthetic documents and process-interruption recovery only; no hardware power-cut, other filesystem, installed policy, native editor or commit IPC qualification.'}
def save():write(root/'result.json',record)
def run(directory,*args,success=True):
    p=subprocess.run([str(exe),str(directory),*map(str,args)],capture_output=True,text=True,timeout=8)
    if success:
        assert p.returncode==0,(args,p.returncode,p.stderr)
        v=json.loads(p.stdout)
        if 'result' in v:validate(v['result'],'command-result')
        return v
    assert p.returncode!=0,(args,p.stdout);return p.stderr.strip()
def initialized(name):
    directory=root/name;directory.mkdir(mode=0o700);run(directory,'init',root/'settings.json',root/'scene.json');return directory
def inspect(directory,revision,fallback=False):
    v=run(directory,'read');assert (v['settings'],v['scene'])==expected[revision] and v['recovered_previous']==fallback
    validate(v['settings'],'settings');validate(v['scene'],'scene-v0.2')
    return v
def passed(name,**facts):record['cases'].append({'case':name,'outcome':'pass',**facts});save()
try:
    for stage in ('created','settings','scene','manifest','generation','previous','selector_ready','authorized','selected','durable'):
        directory=initialized('cut-'+stage)
        p=subprocess.Popen([str(exe),str(directory),'commit',str(root/'command.json'),stage],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            assert select.select([p.stdout],[],[],5)[0],'transition timeout'
            assert json.loads(p.stdout.readline())=={'transition':stage}
            deadline=time.monotonic()+3;stopped=None
            while time.monotonic()<deadline:
                stopped=os.waitid(os.P_PID,p.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
                if stopped:break
                time.sleep(.01)
            assert stopped and stopped.si_code==os.CLD_STOPPED and stopped.si_status==signal.SIGSTOP
            p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
        finally:
            if p.poll() is None:p.kill();p.wait(timeout=3)
            p.stdout.close();p.stderr.close()
        revision=41 if stage in ('selected','durable') else 40;inspect(directory,revision)
        reply=run(directory,'reconcile','E1','R')['result']
        assert reply['outcome']==('accepted' if revision==41 else 'unknown') and reply['visible'] in (False,None)
        if revision==41:assert reply['revision']=='41' and reply['durable'] is True and reply['activation'][0]['state']=='pending'
        passed('CUT-'+stage,held_stop_observed=True,native_exit=-signal.SIGKILL,recovered_revision=revision)
    directory=initialized('replay');result=run(directory,'commit',root/'command.json')['result'];assert result['revision']=='41' and result['durable'] is True
    before=(directory/'current.json').read_bytes();assert run(directory,'commit',root/'command.json')['result']==result
    assert (directory/'current.json').read_bytes()==before;inspect(directory,41)
    assert run(directory,'deny-reconcile','E1','R')['result']['outcome']=='denied'
    selector=json.loads(before);generation=directory/selector['generation'];manifest=json.loads((generation/'manifest.json').read_text())
    assert sha(generation/'manifest.json')==selector['manifest'] and sha(generation/'settings.json')==manifest['settings'] and sha(generation/'scene.json')==manifest['scene']
    assert manifest['identity']=={'principal':'fixture:principal','epoch':'E1','request':'R','body':(root/'command.json').read_text()}
    passed('REPLAY-RECONCILE',recovered_revision=41,independent_digests=True)
    directory=initialized('late-policy');reply=run(directory,'commit',root/'command.json','revoke')['result']
    assert reply['outcome']=='conflict' and reply['error']['code']=='policy.changed' and reply['stored'] is False
    inspect(directory,40);passed('POLICY-BEFORE-REPLACE',recovered_revision=40)
    for phase,outcome,revision in [('generation','invalid',40),('selected','unknown',41)]:
        directory=initialized('failure-'+phase);reply=run(directory,'commit',root/'command.json','fail:'+phase)['result']
        assert reply['outcome']==outcome
        if outcome=='unknown':assert reply['stored'] is None and reply['durable'] is None
        else:assert reply['stored'] is False and reply['durable'] is False
        inspect(directory,revision);passed('FAIL-'+phase,recovered_revision=revision)
    directory=initialized('corrupt');run(directory,'commit',root/'command.json');(directory/'current.json').write_bytes(b'corrupt-selector')
    corruption=sha(directory/'current.json');inspect(directory,40,True);assert sha(directory/'current.json')==corruption
    assert run(directory,'commit',root/'command.json')['result']['error']['code']=='storage.recovery_required'
    (directory/'previous.json').write_bytes(b'corrupt-previous');run(directory,'read',success=False)
    passed('CORRUPT-SELECTORS',fallback_revision=40,corruption_preserved=True)
    directory=initialized('corrupt-previous');run(directory,'commit',root/'command.json');(directory/'previous.json').write_bytes(b'corrupt-previous')
    inspect(directory,41);q=copy.deepcopy(command);q['request_id']='next';q['expected_revision']=q['operations'][0]['scene']['revision']='41';write(root/'next.json',q)
    assert run(directory,'commit',root/'next.json')['result']['error']['code']=='storage.recovery_required'
    assert (directory/'previous.json').read_bytes()==b'corrupt-previous';passed('CORRUPT-PREVIOUS-PRESERVED',current_revision=41)
    directory=initialized('mixed');run(directory,'commit',root/'command.json');selector=json.loads((directory/'current.json').read_text())
    target=directory/selector['generation']/'settings.json';target.write_text(json.dumps(settings));target.chmod(0o600)
    inspect(directory,40,True);passed('MIXED-DOCUMENT-REJECTED',fallback_revision=40)
    directory=initialized('linked');(directory/'current.json').unlink();(directory/'current.json').symlink_to(root/'settings.json')
    run(directory,'read',success=False);assert json.loads((root/'settings.json').read_text())==settings;passed('SYMLINK-REJECTED')
    directory=initialized('lock');p=subprocess.Popen([str(exe),str(directory),'hold'],stdout=subprocess.PIPE,text=True)
    try:
        assert select.select([p.stdout],[],[],5)[0] and json.loads(p.stdout.readline())=={'locked':True}
        assert run(directory,'read',success=False)=='storage.busy'
    finally:
        p.kill();assert p.wait(timeout=3)==-signal.SIGKILL;p.stdout.close()
    inspect(directory,40);passed('EXCLUSIVE-WRITER',held_exit=True)
    directory=initialized('capacity')
    for index in range(31):
        q=copy.deepcopy(command);q['request_id']='C'+str(index);q['expected_revision']=q['operations'][0]['scene']['revision']=str(40+index);write(root/'next.json',q)
        assert run(directory,'commit',root/'next.json')['result']['revision']==str(41+index)
    q['request_id']='overflow';q['expected_revision']=q['operations'][0]['scene']['revision']='71';write(root/'next.json',q)
    before=(directory/'current.json').read_bytes();assert run(directory,'commit',root/'next.json')['result']['error']['code']=='storage.capacity'
    assert (directory/'current.json').read_bytes()==before and len(list(directory.glob('g-*')))==32;passed('BOUNDED-GENERATIONS',retained_generations=32)
    record['outcome']='pass';save();print('CONFIG-STORE pass:',len(record['cases']),'cases; report',root/'result.json')
except BaseException as exc:
    record['outcome']='fail';record['error']=str(exc);save();print('CONFIG-STORE failed; report',root/'result.json',file=sys.stderr);raise
