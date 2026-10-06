"""Independent pinned-resource durability and process-interruption oracle on ext4."""
from pathlib import Path
import copy,hashlib,json,os,select,signal,subprocess,sys,time,uuid,warnings
import jsonschema
exe,repo,evidence=map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(evidence).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('scene-content-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
assert subprocess.check_output(['findmnt','--target',str(root),'--noheadings','--output','FSTYPE'],text=True).strip()=='ext4'
sha=lambda b:hashlib.sha256(b).hexdigest();encoded=lambda v:json.dumps(v,separators=(',',':')).encode()
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
record={'family':'SCENE-CONTENT','outcome':'running','filesystem':'ext4','uid':os.geteuid(),'executable_sha256':sha(exe.read_bytes()),
 'oracle_sha256':sha(Path(__file__).read_bytes()),'cases':[],
 'qualification':'Owned ext4 process-interruption and exact resource recovery only; media decoding, installed ownership, visible activation, power cuts and other platforms remain open.'}
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def save():write(root/'result.json',encoded(record))
def valid(v,name):
 s=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',DeprecationWarning);jsonschema.Draft202012Validator(s,resolver=jsonschema.RefResolver.from_schema(s,store=schemas)).validate(v)
def run(store,*args,success=True):
 p=subprocess.run([str(exe),str(store),*map(str,args)],capture_output=True,text=True,timeout=8)
 if not success:assert p.returncode!=0;return p.stderr.strip()
 assert p.returncode==0,(args,p.returncode,p.stderr);v=json.loads(p.stdout)
 if 'result' in v:valid(v['result'],'command-result')
 return v
def fixture(name):
 d=root/name;d.mkdir(mode=0o700);store=d/'store';store.mkdir(mode=0o700);imports=d/'imports';imports.mkdir(mode=0o700)
 settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text())
 settings['revision']=scene['revision']='40';scene['widgets'][1]['layout']={'base':{'kind':'fixed','x':10,'y':20,'width':240,'height':80}}
 write(d/'settings.json',encoded(settings));write(d/'scene.json',encoded(scene));run(store,'init',d/'settings.json',d/'scene.json')
 paths=[];pins=[];docs=[];files={};theme=json.loads((repo/'spec/fixtures/valid/theme.json').read_text());theme['theme_id']='theme:custom'
 def package(kind,doc,deps,extras=None):
  p=imports/kind;p.mkdir(mode=0o700);assets={kind+'.json':encoded(doc)+b'\n',**(extras or {})};rows=[]
  for path,raw in assets.items():
   target=p/path
   if target.parent!=p:target.parent.mkdir(mode=0o700)
   write(target,raw);rows.append({'path':path,'media_type':'application/json' if path.endswith('.json') else 'image/png','sha256':sha(raw),'bytes':len(raw)})
   files['a-'+sha(raw)+'.bin']=raw
  m={'schema_version':'0.1.0','package_id':'package:'+kind,'version':'0.1.0','kind':kind,'license':'MIT','dependencies':deps,'assets':rows,
    'total_unpacked_bytes':sum(map(len,assets.values())),'required_capabilities':[],'optional_capabilities':[]}
  valid(m,'content-package');valid(doc,('scene-v0.3' if doc['schema_version']=='0.3.0' else 'scene-v0.2') if kind=='scene' else kind);mb=encoded(m)+b'\n';write(p/'manifest.json',mb);files['m-'+sha(mb)+'.json']=mb
  pins.append({'id':m['package_id'],'version':'0.1.0','sha256':sha(mb)});docs.append({'id':doc[kind+'_id'],'version':'0.1.0','sha256':sha(assets[kind+'.json'])});paths.append(p)
 package('theme',theme,[],{'images/pixel.png':b'opaque media bytes\x00unchanged'})
 authored=json.loads((repo/'spec/fixtures/valid/scene-content.json').read_text());authored['revision']='3';authored['widgets'][6]['content']['asset']={'package':pins[0],'path':'images/pixel.png','sha256':sha(b'opaque media bytes\x00unchanged')};package('scene',authored,[])
 preset={'schema_version':'0.1.0','preset_id':'preset:custom','version':'0.1.0','parent':None,'scene':docs[1],'theme':docs[0],
  'settings':[{'path':'display.theme_id','value':'theme:custom'}],'required_capabilities':['scene.selector'],'optional_capabilities':[]}
 package('preset',preset,copy.deepcopy(pins));candidate=copy.deepcopy(authored);candidate['revision']='40';candidate['theme_id']='theme:custom'
 selection={'package':pins[2],'preset':docs[2]}
 q={'schema_version':'0.4.0','request_id':'R','expected_revision':'40','policy_generation':'7','intent':'commit','content':selection,
  'operations':[{'op':'scene.replace','scene':candidate},{'op':'settings.set','path':'display.theme_id','value':'theme:custom'}]}
 valid(q,'command-v0.4');write(d/'command.json',encoded(q))
 return {'directory':d,'store':store,'paths':paths,'files':files,'pins':pins,'theme':theme,'theme_pin':docs[0],'selection':selection,'command':q,'settings':settings,'scene':scene,'candidate':candidate}
def commit(f,phase='-'):return run(f['store'],'content-commit',f['directory']/'command.json',phase,*f['paths'])['result']
def inspect(f,revision,fallback=False):
 value=run(f['store'],'read');settings=copy.deepcopy(f['settings']);scene=copy.deepcopy(f['candidate'] if revision>40 else f['scene']);settings['revision']=scene['revision']=str(revision)
 expected={'settings':settings,'scene':scene,'recovered_previous':fallback}
 if revision>40:
  settings['display']['theme_id']='theme:custom';expected['resources']={'selection':f['selection'],'theme':f['theme'],'theme_pin':f['theme_pin'],'packages':sorted(p['sha256'] for p in f['pins'])}
 assert value==expected,(value,expected)
 pointer=json.loads((f['store']/('previous.json' if fallback else 'current.json')).read_bytes());generation=f['store']/pointer['generation'];manifest=json.loads((generation/'manifest.json').read_bytes())
 assert sha((generation/'manifest.json').read_bytes())==pointer['manifest'] and sha((generation/'settings.json').read_bytes())==manifest['settings'] and sha((generation/'scene.json').read_bytes())==manifest['scene']
 if revision>40:
  assert manifest['version']=='0.2.0';index=json.loads((generation/'resources.json').read_bytes());assert sha((generation/'resources.json').read_bytes())==manifest['resources']
  assert index=={'version':'0.1.0','selection':f['selection'],'theme':f['theme_pin'],'packages':expected['resources']['packages']}
  assert {p.name:p.read_bytes() for p in (generation/'resources').iterdir()}==f['files']
  assert json.loads(manifest['identity']['body'])['content']==f['selection']
 return generation
def passed(name,**facts):record['cases'].append({'case':name,'outcome':'pass',**facts});save()
def second(f):
 assert commit(f)['revision']=='41';q=f['command'];q['request_id']='S';q['expected_revision']=q['operations'][0]['scene']['revision']='41';write(f['directory']/'command.json',encoded(q));assert commit(f)['revision']=='42';return inspect(f,42)
try:
 phases=['created','settings','scene','resources_created',*[f'resource_manifest:{i}' for i in range(3)],*[f'resource_asset:{i}' for i in range(4)],
  'resource_index','resources_flushed','manifest','generation','previous','selector_ready','authorized','selected','durable']
 for phase in phases:
  f=fixture('cut-'+phase.replace(':','-'));p=subprocess.Popen([str(exe),str(f['store']),'content-commit',str(f['directory']/'command.json'),phase,*map(str,f['paths'])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   assert select.select([p.stdout],[],[],5)[0],phase;assert json.loads(p.stdout.readline())=={'transition':phase}
   end=time.monotonic()+3;stopped=None
   while time.monotonic()<end:
    stopped=os.waitid(os.P_PID,p.pid,os.WSTOPPED|os.WNOHANG|os.WNOWAIT)
    if stopped:break
    time.sleep(.01)
   assert stopped and stopped.si_code==os.CLD_STOPPED and stopped.si_status==signal.SIGSTOP;p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
  finally:
   if p.poll() is None:p.kill();p.wait(timeout=3)
   p.stdout.close();p.stderr.close()
  revision=41 if phase in ('selected','durable') else 40;inspect(f,revision);reply=run(f['store'],'reconcile','E1','R')['result']
  assert reply['outcome']==('accepted' if revision==41 else 'unknown')
  if revision==41:assert reply['activation'][0]['state']=='pending' and reply['visible'] is False
  passed('CUT-'+phase,recovered_revision=revision,held_stop_observed=True)
 f=fixture('source-gone');accepted=commit(f);assert accepted['revision']=='41';inspect(f,41);(f['directory']/'imports').rename(f['directory']/'preserved-imports')
 before=(f['store']/'current.json').read_bytes();assert commit(f)==accepted and (f['store']/'current.json').read_bytes()==before;inspect(f,41)
 q=f['command'];q['request_id']='next';q['expected_revision']=q['operations'][0]['scene']['revision']='41';write(f['directory']/'command.json',encoded(q))
 assert commit(f)['outcome']=='invalid';assert (f['store']/'current.json').read_bytes()==before;passed('SOURCE-GONE-REPLAY',recovered_revision=41)
 f=fixture('policy');assert commit(f,'deny')['outcome']=='denied';inspect(f,40);assert commit(f,'revoke')['error']['code']=='policy.changed';inspect(f,40);passed('POLICY-BEFORE-REPLACE')
 f=fixture('content-policy');assert commit(f,'deny-content')['outcome']=='denied';inspect(f,40);passed('CONTENT-CAPABILITY-DENIED')
 for fault in ('CORRUPT','MISSING','EXTRA','HARDLINK','SYMLINK','INDEX-BINDING','IDENTITY','GENERATION-EXTRA','FORMAT-DROP'):
  f=fixture(fault);generation=second(f);asset=next((generation/'resources').glob('a-*.bin'))
  if fault=='CORRUPT':asset.write_bytes(b'corrupt')
  elif fault=='MISSING':asset.unlink()
  elif fault=='EXTRA':write(generation/'resources'/'extra',b'undeclared')
  elif fault=='HARDLINK':os.link(asset,f['directory']/'alias')
  elif fault=='SYMLINK':
   target=f['directory']/'outside';asset.rename(target);asset.symlink_to(target)
  elif fault=='GENERATION-EXTRA':write(generation/'extra',b'undeclared')
  else:
   pointer=json.loads((f['store']/'current.json').read_bytes());manifest=json.loads((generation/'manifest.json').read_bytes())
   if fault=='INDEX-BINDING':
    index=json.loads((generation/'resources.json').read_bytes());index['theme']['sha256']='0'*64;raw=encoded(index);write(generation/'resources.json',raw);manifest['resources']=sha(raw)
   elif fault=='FORMAT-DROP':
    manifest['version']='0.1.0';manifest.pop('resources');q=json.loads(manifest['identity']['body']);q['schema_version']='0.2.0';q.pop('content');q['operations']=q['operations'][1:];manifest['identity']['body']=encoded(q).decode()
   else:
    q=json.loads(manifest['identity']['body']);q['content']['package']['sha256']='0'*64;manifest['identity']['body']=encoded(q).decode()
   raw=encoded(manifest);write(generation/'manifest.json',raw);pointer['manifest']=sha(raw);write(f['store']/'current.json',encoded(pointer))
  damaged=(f['store']/'current.json').read_bytes();inspect(f,41,True);assert (f['store']/'current.json').read_bytes()==damaged
  assert run(f['store'],'reconcile','E1','R')['result']['revision']=='41';assert run(f['store'],'reconcile','E1','S')['result']['outcome']=='unknown'
  q=f['command'];q['request_id']='new';write(f['directory']/'command.json',encoded(q));assert commit(f)['error']['code']=='storage.recovery_required';passed(fault+'-FALLBACK',recovered_revision=41)
 f=fixture('legacy');assert commit(f)['revision']=='41';q=f['command'];q['schema_version']='0.2.0';q.pop('content');q['operations']=q['operations'][1:];q['request_id']='legacy';q['expected_revision']='41';write(f['directory']/'command.json',encoded(q))
 assert run(f['store'],'commit',f['directory']/'command.json')['result']['error']['code']=='resource.contract';inspect(f,41);passed('LEGACY-CANNOT-DROP-CLOSURE')
 f=fixture('bootstrap-content');bare=f['directory']/'bare';bare.mkdir(mode=0o700);write(f['directory']/'scene.json',encoded(f['command']['operations'][0]['scene']))
 assert run(bare,'init',f['directory']/'settings.json',f['directory']/'scene.json',success=False)=='storage.resource_required';assert not (bare/'current.json').exists();passed('CONTENT-REQUIRES-CLOSURE')
 record['outcome']='pass';save();print('SCENE-CONTENT pass:',len(record['cases']),'cases;',root/'result.json')
except BaseException as e:
 record['outcome']='fail';record['error']=repr(e);save();raise
