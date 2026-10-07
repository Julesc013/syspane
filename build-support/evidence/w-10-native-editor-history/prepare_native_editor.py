from pathlib import Path
import copy,hashlib,json,zipfile
r=Path.cwd();p=r/'tests/editor/native-cases.json';assert not p.exists()
resource=json.loads((r/'tests/configuration/settings-content-fixture.json').read_text());v=copy.deepcopy(resource['authored']);s=v['scene'];first=copy.deepcopy(s['widgets'][0]);second=copy.deepcopy(first);img=copy.deepcopy(s['widgets'][-1])
first.update(title='Editable pane',content={'body':'Editable pane\nMove me'});first['layout']['base'].update(x=40,y=40,width=180,height=80)
second.update(id='widget:second',title='Second pane',content={'body':'Second pane'});second['layout']['base'].update(x=280,y=40,width=180,height=80)
img['layout']['base'].update(x=40,y=180,width=160,height=100)
s['roots']=[first['id'],second['id'],img['id']];s['widgets']=[first,second,img]
v['settings']['display']['theme_id']='theme:native'
expected=copy.deepcopy(s);expected['widgets'][0]['layout']['base'].update(x=70,y=60)
properties=copy.deepcopy(s);properties['widgets'][0].update(title='Renamed pane',content={'body':'Updated body'});properties['widgets'][0]['layout']['base'].update(x=125,y=135,width=210,height=90)
data=dict(authored=v,drag=dict(dx=30,dy=20,expected=expected),properties=properties,resize=dict(width=200,height=90),multi_dx=10,revision='40',committed_revision='41',erase_ms=200,recovery_ms=1500,
 modes=['drag','keyboard','resize','properties','multi','structure','cancel','conflict','deny','revoke','restart','topology','frozen-preview','wrong-commit','retain'],recovery_modes=['key-frozen','button-frozen','drag-frozen','owner-loss','conflict'])
p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
d=r/'out/campaign/native-editor-original';d.mkdir(exist_ok=True)
paths=['spec/delivery/packages/w-10-native-editor.md','tests/editor/native-cases.json','tests/configuration/settings-content-fixture.json','out/campaign/prepare_native_editor.py']
hashes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(d/'original.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'original.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Fixed native scene and expected outputs preserved.')
