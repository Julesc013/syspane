"""Independent file/hash/preview oracle for the private Linux content reader."""
from pathlib import Path
import copy,hashlib,json,os,select,subprocess,sys,uuid,warnings
import jsonschema

exe,repo,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:4])
assert os.geteuid()!=0 and evidence.is_relative_to(exe.parent) and str(evidence).startswith('/home/ir4runner/.cache/syspane/')
root=evidence/('content-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700,parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
encoded=lambda v:(json.dumps(v,separators=(',',':'))+'\n').encode()
schemas={v['$id']:v for p in (repo/'spec/contracts').glob('*.schema.json') for v in [json.loads(p.read_text())]}
record={'family':'CONTENT-READER','outcome':'running','uid':os.geteuid(),'executable_sha256':sha(exe.read_bytes()),
 'oracle_sha256':sha(Path(__file__).read_bytes()),'cases':[],
 'qualification':'Explicit private Linux uncompressed directories and previews only; no durable resource closure, media decoding, installation or activation.'}
def save():(root/'result.json').write_text(json.dumps(record,indent=2)+'\n')
def validate(v,name):
 s=json.loads((repo/'spec/contracts'/(name+'.schema.json')).read_text())
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',DeprecationWarning);jsonschema.Draft202012Validator(s,resolver=jsonschema.RefResolver.from_schema(s,store=schemas)).validate(v)
def write(p,b):p.write_bytes(b);p.chmod(0o600)
def fixture(name):
 d=root/name;d.mkdir(mode=0o700);packages=[];pins=[];docs=[];manifests=[]
 def package(kind,value,deps):
  p=d/str(len(packages));p.mkdir(mode=0o700);raw=encoded(value)
  m={'schema_version':'0.1.0','package_id':'package:'+str(len(packages)),'version':'0.1.0','kind':kind,'license':'MIT',
   'dependencies':deps,'assets':[{'path':kind+'.json','media_type':'application/json','sha256':sha(raw),'bytes':len(raw)}],
   'total_unpacked_bytes':len(raw),'required_capabilities':[],'optional_capabilities':[]}
  validate(m,'content-package');validate(value,{'scene':'scene-v0.2'}.get(kind,kind))
  mb=encoded(m);write(p/'manifest.json',mb);write(p/(kind+'.json'),raw);packages.append(p);manifests.append(m)
  pins.append({'id':m['package_id'],'version':'0.1.0','sha256':sha(mb)})
  docs.append({'id':value[kind+'_id'],'version':'0.1.0','sha256':sha(raw)})
 settings=json.loads((repo/'spec/fixtures/valid/settings.json').read_text());settings['revision']='40'
 scene=json.loads((repo/'spec/fixtures/valid/scene-portable.json').read_text());scene['revision']='3'
 theme=json.loads((repo/'spec/fixtures/valid/theme.json').read_text());package('theme',theme,[]);package('scene',scene,[])
 parent={'schema_version':'0.1.0','preset_id':'preset:parent','version':'0.1.0','parent':None,'scene':docs[1],'theme':docs[0],
  'settings':[{'path':'display.enabled','value':False},{'path':'sampling.resources_ms','value':1000}],
  'required_capabilities':['scene.selector'],'optional_capabilities':['optional.z','optional.a']}
 package('preset',parent,copy.deepcopy(pins));leaf=copy.deepcopy(parent);leaf.update(preset_id='preset:leaf',parent=docs[2],theme=None,settings=[{'path':'sampling.resources_ms','value':1500}]);package('preset',leaf,[pins[2]])
 scene['revision']='40';query={'settings':settings,'scene':scene,'package':pins[3],'preset':docs[3]}
 expected_settings=copy.deepcopy(settings);expected_settings['display']['enabled']=False;expected_settings['sampling']['resources_ms']=1500
 operations=[{'op':'settings.set','path':'display.enabled','value':False},{'op':'settings.set','path':'sampling.resources_ms','value':1500},{'op':'scene.replace','scene':scene}]
 expected={'command':{'schema_version':'0.2.0','request_id':'P','expected_revision':'40','policy_generation':'7','intent':'preview','operations':operations},
  'settings':expected_settings,'scene':scene,'theme':theme,'packages':pins,'presets':docs[2:4],
  'origins':{'display.enabled':docs[2],'sampling.resources_ms':docs[3]},'missing_optional':['optional.a','optional.z']}
 return packages,query,expected,manifests
def invoke(paths,query,mode='preview'):
 p=subprocess.run([str(exe),mode,*map(str,paths)],input=json.dumps(query)+'\n',text=True,capture_output=True,timeout=5)
 assert not p.stderr,p.stderr
 return p.returncode,json.loads(p.stdout)
def compare(value,expected):
 assert value==expected,(value,expected)
 for name,key in [('settings','settings'),('scene-v0.2','scene'),('command-v0.2','command'),('theme','theme')]:validate(value[key],name)
try:
 for name in ('COMPOSE','SNAPSHOT','ROOT-LINK','ASSET-LINK','HARDLINK','EXECUTABLE','PUBLIC','FIFO','EXTRA','MISSING','DIGEST','TRUNCATED','PIN','POLICY','MANIFEST-OVERSIZE','MANIFEST-LINK','DIRECTORY-LINK'):
  paths,query,expected,manifests=fixture(name);mode='preview';target=paths[0]/'theme.json';error=None
  if name=='ROOT-LINK':
   link=root/name/'link';link.symlink_to(paths[0],target_is_directory=True);paths[0]=link;error='content.root'
  elif name=='ASSET-LINK':
   other=root/name/'outside';target.rename(other);target.symlink_to(other);error='content.open'
  elif name=='HARDLINK':os.link(target,root/name/'alias');error='content.file'
  elif name=='EXECUTABLE':target.chmod(0o700);error='content.file'
  elif name=='PUBLIC':target.chmod(0o644);error='content.permissions'
  elif name=='FIFO':target.unlink();os.mkfifo(target,0o600);error='content.file'
  elif name=='EXTRA':write(paths[0]/'undeclared',b'x');error='content.undeclared'
  elif name=='MISSING':target.unlink();error='content.assets'
  elif name=='DIGEST':target.write_bytes(target.read_bytes().replace(b'theme:native',b'theme:broken'));error='content.digest'
  elif name=='TRUNCATED':target.write_bytes(b'{}');error='content.digest'
  elif name=='PIN':query['package']['sha256']='0'*64;error='content.reference'
  elif name=='POLICY':mode='denied';error='policy.denied'
  elif name=='MANIFEST-OVERSIZE':write(paths[0]/'manifest.json',b' '*65537);error='content.file'
  elif name=='MANIFEST-LINK':
   m=paths[0]/'manifest.json';other=root/name/'outside';m.rename(other);m.symlink_to(other);error='content.open'
  elif name=='DIRECTORY-LINK':
   # A declared nested payload must not follow an intermediate directory link.
   outside=root/name/'outside';outside.mkdir(mode=0o700);write(outside/'a.json',b'{}');(paths[0]/'nested').symlink_to(outside,target_is_directory=True)
   m=manifests[0];m['assets'].append({'path':'nested/a.json','media_type':'application/json','bytes':2,'sha256':sha(b'{}')});m['total_unpacked_bytes']+=2
   write(paths[0]/'manifest.json',encoded(m));error='content.open'
  if name=='SNAPSHOT':
   process=subprocess.Popen([str(exe),'snapshot',*map(str,paths)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
   try:
    assert select.select([process.stdout],[],[],5)[0],'snapshot did not become ready';assert json.loads(process.stdout.readline())=={'ready':True}
    before=target.read_bytes();target.write_bytes(before.replace(b'theme:native',b'theme:broken'))
    stdout,stderr=process.communicate(json.dumps(query)+'\n',timeout=5);assert process.returncode==0 and not stderr;compare(json.loads(stdout),expected)
    code,value=invoke(paths,query);assert code==2 and value=={'error':'content.digest'}
   finally:
    if process.poll() is None:process.kill();process.wait()
   observation={'prepared_snapshot':'unchanged','fresh_read':'content.digest'}
  else:
   code,value=invoke(paths,query,mode)
   if error:assert code==2 and value=={'error':error},(name,code,value,error)
   else:assert code==0;compare(value,expected)
   observation=value
  record['cases'].append({'case':name,'outcome':'pass','observation':observation});save()
 record['outcome']='pass';save();print('CONTENT-READER pass: '+str(len(record['cases']))+' native cases; '+str(root/'result.json'))
except BaseException as e:
 record['outcome']='fail';record['failure']=repr(e);save();raise
