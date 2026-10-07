from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,zipfile
r=Path.cwd();out=r/'out/campaign/w-10-edit-locks';out.mkdir(exist_ok=True)
def read(n):return json.loads((r/n).read_bytes())
def write(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
scene=read('spec/contracts/scene-v0.3.schema.json');scene['$id']=scene['$id'].replace('/0.3.0/','/0.4.0/');scene['title']='SysPane authored edit-lock scene 0.4.0';scene['properties']['schema_version']['const']='0.4.0'
widget=scene['$defs']['widget'] if 'widget' in scene['$defs'] else scene['properties']['widgets']['items']
widget['properties']['edit_locked']={'type':'boolean','description':'Own editing lock; missing/false is unlocked. Group locks apply to descendants. Not an authorization or disclosure rule.'}
write('spec/contracts/scene-v0.4.schema.json',scene)
command=read('spec/contracts/command-v0.5.schema.json');command['$id']=command['$id'].replace('/0.5.0/','/0.6.0/');command['title']='SysPane authored edit-lock command 0.6.0';command['properties']['schema_version']['const']='0.6.0'
op=next(x for x in command['properties']['operations']['items']['oneOf'] if x['properties']['op']['const']=='scene.replace');op['properties']['scene']['oneOf'].append({'$ref':scene['$id']})
version=command['allOf'][0]['if']['properties']['operations']['contains']['properties']['scene']['properties']['schema_version'];version.clear();version['enum']=['0.3.0','0.4.0']
write('spec/contracts/command-v0.6.schema.json',command)
base=read('tests/editor/native-cases.json')['authored'];locked=copy.deepcopy(base['scene']);locked['schema_version']='0.4.0';locked['widgets'][0]['edit_locked']=True
unlocked=copy.deepcopy(locked);del unlocked['widgets'][0]['edit_locked'];moved=copy.deepcopy(unlocked);moved['widgets'][0]['layout']['base']['x']=60
multi=copy.deepcopy(locked);multi['widgets'][1]['edit_locked']=True
grouped=copy.deepcopy(locked);grouped['widgets'][0].pop('edit_locked');grouped['roots']=['widget:group','widget:image'];grouped['widgets'].append({'id':'widget:group','kind':'group','title':'Locked group','display':{'local_id':'D1'},'layout':{'base':{'kind':'fixed','x':0,'y':0,'width':480,'height':140}},'priority':'normal','bindings':[],'content':{},'children':['widget:text','widget:second'],'edit_locked':True})
cases={'authored':base,'locked':locked,'unlocked':unlocked,'moved':moved,'multi':multi,'grouped':grouped,'native_cases':['lock','unlock-move','multi','nested','restart','revoke','wrong-lock'], 'erase_ms':200}
write('tests/editor/edit-lock-cases.json',cases)
selection=read('tests/configuration/settings-content-fixture.json')['selection']
q={'schema_version':'0.6.0','request_id':'lock','expected_revision':'40','policy_generation':'7','intent':'commit','content':selection,'operations':[{'op':'scene.replace','scene':locked}]}
write('spec/fixtures/valid/scene-edit-locks.json',locked);write('spec/fixtures/valid/command-edit-locks.json',q)
bad=copy.deepcopy(locked);bad['widgets'][0]['edit_locked']='true';write('spec/fixtures/invalid/scene-edit-lock-type.json',bad)
old=copy.deepcopy(locked);old['schema_version']='0.3.0';write('spec/fixtures/invalid/scene-old-edit-lock.json',old)
oldcmd=copy.deepcopy(q);oldcmd['schema_version']='0.5.0';write('spec/fixtures/invalid/command-old-edit-lock.json',oldcmd)
paths=['spec/delivery/packages/w-10-edit-locks.md','spec/contracts/scene-v0.4.schema.json','spec/contracts/command-v0.6.schema.json','tests/editor/edit-lock-cases.json','spec/fixtures/valid/scene-edit-locks.json','spec/fixtures/valid/command-edit-locks.json','spec/fixtures/invalid/scene-edit-lock-type.json','spec/fixtures/invalid/scene-old-edit-lock.json','spec/fixtures/invalid/command-old-edit-lock.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(out/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
write('out/campaign/w-10-edit-locks/fixed-inputs.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'inputs':{n:sha(r/n) for n in paths},'archive_sha256':sha(out/'fixed-inputs.zip')})
print('Frozen edit-lock package, schemas and exact expected scenes.')
