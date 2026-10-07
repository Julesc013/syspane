from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, zipfile
r=Path(__file__).resolve().parents[2]
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
old=json.loads((r/'tests/editor/native-cases.json').read_text())
a=copy.deepcopy(old['authored']);s=a['scene'];s['widgets']=s['widgets'][:2]+[copy.deepcopy(s['widgets'][1])]
s['roots']=['widget:text','widget:second','widget:third']
for w,ident,title,body,rect in zip(s['widgets'],s['roots'],['Editable pane','Second pane','Third pane'],['Move me','Second','Third'],[(40,40,120,80),(200,170,96,64),(370,300,80,48)]):
 w.update(id=ident,title=title,content={'body':body});w['layout']['base'].update(dict(zip(('x','y','width','height'),rect)))
# Expected coordinates are independently calculated literals, not an implementation call.
expected={'left':('x',[40,40,40]),'hcenter':('x',[185,197,205]),'right':('x',[330,354,370]),'top':('y',[40,40,40]),'vcenter':('y',[154,162,170]),'bottom':('y',[268,284,300]),'horizontal':('x',[40,217,370]),'vertical':('y',[40,178,300])}
cases=[]
for action,(axis,positions) in expected.items():
 scene=copy.deepcopy(s)
 for w,n in zip(scene['widgets'],positions):w['layout']['base'][axis]=n
 cases.append({'action':action,'ids':['widget:third','widget:text','widget:second'],'expected':scene})
# Fractional cases specify only the affected axis; the orthogonal axis is preserved.
fractional=[
 {'action':'hcenter','positions':[-40,-6.984375,30.015625],'extents':[32,33,32],'expected':[-5,-5.5,-5]},
 {'action':'hcenter','positions':[0,50,100.015625],'extents':[32,33,32],'expected':[50.015625,49.515625,50.015625]},
 {'action':'horizontal','positions':[0,100,200.015625],'extents':[32,33,32],'expected':[0,99.515625,200.015625]},
 {'action':'horizontal','positions':[0,100,200.0078125],'extents':[32,33,32],'expected':[0,99.515625,200.0078125]},
 {'action':'horizontal','positions':[0,32,65],'extents':[32,33,32],'expected':[0,32,65]},
 {'action':'right','positions':[-0.0078125,40.0078125,100.0078125],'extents':[32.0001,33.0001,32],'expected':[100,99,100.015625]},
]
v={'authored':a,'cases':cases,'fractional':fractional,'erase_ms':200,'native_modes':[*(c['action'] for c in cases),'cancel','deny','revoke','restart','wrong-commit','frozen-preview']}
write(r/'tests/editor/arrange-cases.json',v)
print('Prepared independent literals; freeze together with the package before implementation.')
