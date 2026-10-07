from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,zipfile
r=Path(__file__).resolve().parents[2]
encode=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda n:json.loads((r/'spec/fixtures/valid'/n).read_bytes())
settings,scene,theme=read('settings.json'),read('scene-content.json'),read('theme.json');settings['revision']=scene['revision']='40';scene['theme_id']=None
packages=[]
def pack(id,kind,doc,deps=(),extras=None):
    assets={kind+'.json':encode(doc),**(extras or {})}
    manifest=dict(schema_version='0.1.0',package_id='package:'+id,version='0.1.0',kind=kind,license='MIT',dependencies=list(deps),assets=[dict(path=n,media_type='image/png' if n.endswith('.png') else 'application/json',sha256=sha(b),bytes=len(b)) for n,b in sorted(assets.items())],total_unpacked_bytes=sum(map(len,assets.values())),required_capabilities=[],optional_capabilities=[])
    raw=encode(manifest);packages.append(dict(manifest=raw.decode(),assets_hex={n:b.hex() for n,b in assets.items()}));return dict(id=manifest['package_id'],version='0.1.0',sha256=sha(raw)),dict(id=doc[kind+'_id'],version='0.1.0',sha256=sha(assets[kind+'.json']))
rgb=(r/'tests/scene/image-cases/rgb.png').read_bytes();gray=(r/'tests/scene/image-cases/gray.png').read_bytes()
native,nt=pack('properties-native','theme',theme,extras={'images/a-rgb.png':rgb,'images/b-gray.png':gray})
contrast=copy.deepcopy(theme);contrast['theme_id']='theme:contrast';contrast['name']='Content contrast';contrast['tokens']['foreground']='#00ffffff';contrast['tokens']['background']='#000000ff';other,ot=pack('properties-contrast','theme',contrast)
selected=[]
for index,rect,title in [(0,[20,20,120,50],'Text'),(4,[20,90,460,90],'Table'),(5,[20,195,300,180],'Chart'),(6,[355,230,120,100],'Image')]:
    w=copy.deepcopy(scene['widgets'][index]);w['title']=title;w['layout']['base'].update(zip(('x','y','width','height'),rect));selected.append(w)
scene['widgets']=selected;scene['roots']=[w['id'] for w in selected]
scene['widgets'][0]['content']['body']='Move me'
table=scene['widgets'][1];table['bindings'].append(copy.deepcopy(table['bindings'][0]));table['bindings'][1]['field']='network.transmit_bytes';table['content']['columns'].append(dict(label='Sent'))
image=scene['widgets'][3];image['content']['asset']=dict(package=native,path='images/a-rgb.png',sha256=sha(rgb));image['content'].update(width_dip=120,height_dip=100,alt='Initial color image')
sc,sp=pack('properties-scene','scene',scene)
preset=dict(schema_version='0.1.0',preset_id='preset:properties',version='0.1.0',parent=None,scene=sp,theme=None,settings=[],required_capabilities=[],optional_capabilities=[])
pr,pp=pack('properties','preset',preset,[native,other,sc]);selection=dict(package=pr,preset=pp)
fixture=dict(authored=dict(settings=settings,scene=scene),packages=packages,selection=selection,alternate_selection=selection,themes={'theme:native':nt,'theme:contrast':ot})
(r/'tests/editor/content-properties-fixture.json').write_bytes(encode(fixture))
expected={}
def scene_case(name,index,content=None,bindings=None,theme='unchanged'):
    value=copy.deepcopy(scene)
    if content is not None:value['widgets'][index]['content']=content
    if bindings is not None:value['widgets'][index]['bindings']=bindings
    if theme!='unchanged':value['theme_id']=theme
    expected[name]=value;return value
cols=[dict(label='Received\nbytes'),dict(label='Sent bytes')]
scene_case('table',1,dict(columns=cols))
scene_case('order',1,dict(columns=list(reversed(cols))),list(reversed(table['bindings'])))
scene_case('chart',2,dict(window_ms=2000,max_points=32,interpolation='step',axis=dict(mode='fixed',minimum=-5.5,maximum=100)))
scene_case('chart-auto',2,dict(window_ms=1000,max_points=2,interpolation='linear',axis=dict(mode='auto',include_zero=False)))
im=copy.deepcopy(image['content']);im.update(alt='Gray replacement',width_dip=96,height_dip=80,fit='stretch',asset=dict(package=native,path='images/b-gray.png',sha256=sha(gray)));scene_case('image',3,im)
scene_case('theme',0,theme='theme:contrast');scene_case('inherit',0,theme=None)
value=dict(authored=fixture['authored'],expected=expected,gray_asset=im['asset'],erase_ms=200,native_modes=['table','order','chart','chart-auto','image','theme','inherit','invalid','cancel-buffer','cancel','revoke','restart','wrong-content','frozen-preview','retain-content'])
(r/'tests/editor/content-properties-cases.json').write_bytes(encode(value))
d=r/'out/campaign/w-10-content-properties';d.mkdir();names=['spec/delivery/packages/w-10-content-properties.md','tests/editor/content-properties-fixture.json','tests/editor/content-properties-cases.json']
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
    for n in names:z.write(r/n,n)
(d/'fixed-inputs.json').write_bytes(encode(dict(frozen_at=datetime.now(timezone.utc).isoformat(),inputs={n:sha((r/n).read_bytes()) for n in names},archive_sha256=sha((d/'fixed-inputs.zip').read_bytes()))))
print('Frozen native content contract, exact resource closure and expected scenes.')
