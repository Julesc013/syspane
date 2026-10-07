from pathlib import Path
from datetime import datetime,timezone
import copy,json,hashlib,zipfile
r=Path(__file__).resolve().parents[2]
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
a=json.loads((r/'tests/editor/arrange-cases.json').read_text())['authored'];base=a['scene']
def container(ident,children,rect):return dict(id=ident,kind='group',title='Group',display={'local_id':'D1'},layout={'base':dict(zip(('kind','x','y','width','height'),('fixed',*rect)))},bindings=[],priority='normal',content={},children=children)
# Complete expected scenes assembled from literal independently calculated boxes.
group=copy.deepcopy(base);group['roots']=['widget:new1']
for w,x,y in zip(group['widgets'],[0,160,330],[0,130,260]):w['layout']['base'].update(x=x,y=y)
group['widgets'].append(container('widget:new1',base['roots'],[40,40,410,308]))
moved=copy.deepcopy(group);moved['widgets'][3]['layout']['base'].update(x=70,y=60)
ungrouped=copy.deepcopy(base)
for w,x,y in zip(ungrouped['widgets'],[70,230,400],[60,190,320]):w['layout']['base'].update(x=x,y=y)
partial=copy.deepcopy(base);partial['roots']=['widget:new1','widget:third']
for w,x,y in zip(partial['widgets'][:2],[0,160],[0,130]):w['layout']['base'].update(x=x,y=y)
partial['widgets'].append(container('widget:new1',base['roots'][:2],[40,40,256,194]))
nested=copy.deepcopy(partial);nested['roots']=['widget:new2'];nested['widgets'][2]['layout']['base'].update(x=330,y=260);nested['widgets'][3]['layout']['base'].update(x=0,y=0)
nested['widgets'].append(container('widget:new2',['widget:new1','widget:third'],[40,40,410,308]))
nonadjacent=copy.deepcopy(base);nonadjacent['roots']=['widget:new1','widget:second'];nonadjacent['widgets'][0]['layout']['base'].update(x=0,y=0);nonadjacent['widgets'][2]['layout']['base'].update(x=330,y=260)
nonadjacent['widgets'].append(container('widget:new1',['widget:text','widget:third'],[40,40,410,308]))
overlap=copy.deepcopy(nonadjacent);overlap['widgets'][1]['layout']['base'].update(x=400,y=320)
fractional=copy.deepcopy(base);fractional['widgets'][0]['layout']['base'].update(x=-0.0078125,y=-0.0078125)
fraction_group=copy.deepcopy(fractional);fraction_group['roots']=['widget:new1']
for w,x,y in zip(fraction_group['widgets'],[0,200.015625,370.015625],[0,170.015625,300.015625]):w['layout']['base'].update(x=x,y=y)
fraction_group['widgets'].append(container('widget:new1',base['roots'],[-0.015625,-0.015625,450.015625,348.015625]))
responsive=copy.deepcopy(base);responsive['widgets'][0]['layout']['breakpoints']=[dict(min_width_dip=800,layout=dict(kind='fixed',x=-20,y=10,width=160,height=96))]
responsive_group=copy.deepcopy(responsive);responsive_group['roots']=['widget:new1']
for w,x,y in zip(responsive_group['widgets'],[60,220,390],[30,160,290]):w['layout']['base'].update(x=x,y=y)
responsive_group['widgets'][0]['layout']['breakpoints'][0]['layout'].update(x=0,y=0)
responsive_group['widgets'].append(container('widget:new1',base['roots'],[-20,10,470,338]))
v=dict(authored=a,grouped=group,moved=moved,ungrouped=ungrouped,partial=partial,nested=nested,nonadjacent=nonadjacent,overlap=overlap,
 fractional=fractional,fractional_grouped=fraction_group,responsive=responsive,responsive_grouped=responsive_group,erase_ms=200,
 native_modes=['group','move','ungroup','nested','overlap','cancel','deny','revoke','restart','wrong-group','frozen-preview'])
write(r/'tests/editor/group-cases.json',v)
d=r/'out/campaign/w-10-group';d.mkdir();names=['tests/editor/group-cases.json','spec/delivery/packages/w-10-group.md'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(d/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(r/n,n)
write(d/'fixed-inputs.json',dict(frozen_at=datetime.now(timezone.utc).isoformat(),inputs={n:sha(r/n) for n in names},archive_sha256=sha(d/'fixed-inputs.zip')))
print('Frozen independent complete scenes and grouping contract before production changes.')
