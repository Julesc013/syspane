from pathlib import Path
import copy,hashlib,json,zipfile
r=Path.cwd();p=r/'tests/editor/cases.json';p.parent.mkdir(exist_ok=True)
base=json.loads((r/'tests/configuration/settings-content-fixture.json').read_text())['authored']['scene']
rows=[]
def case(name,ops,modify):
 value=copy.deepcopy(base);modify(value);rows.append(dict(name=name,operations=ops,expected=value))
def widget(s,id):return next(w for w in s['widgets'] if w['id']==id)
case('TITLE',[dict(op='property',id='widget:text',property='title',value='Edited title')],lambda s:widget(s,'widget:text').update(title='Edited title'))
case('MOVE',[dict(op='move',ids=['widget:text','widget:value'],dx=12.5,dy=-3)],lambda s:[widget(s,id)['layout']['base'].update(x=x,y=y) for id,x,y in [('widget:text',12.5,-3),('widget:value',32.5,17)]])
case('RESIZE',[dict(op='resize',id='widget:text',width=320,height=96)],lambda s:widget(s,'widget:text')['layout']['base'].update(width=320,height=96))
case('DISPLAY',[dict(op='property',id='widget:text',property='display',value={'local_id':'missing-monitor'})],lambda s:widget(s,'widget:text').update(display={'local_id':'missing-monitor'}))
case('CONTENT',[dict(op='content',id='widget:text',bindings=[],content={'body':'New body\nsecond line'})],lambda s:widget(s,'widget:text').update(content={'body':'New body\nsecond line'}))
case('THEME',[dict(op='theme',theme='theme:contrast')],lambda s:s.update(theme_id='theme:contrast'))
added=copy.deepcopy(base['widgets'][0]);added['id']='widget:added';added['title']='Added';added['content']['body']='Added body'
def insert(s):s['widgets'].append(copy.deepcopy(added));s['roots'].insert(1,'widget:added')
case('INSERT',[dict(op='insert',widget=added,parent=None,index=1)],insert)
def group(s):
 s['roots'].remove('widget:text');s['roots'].remove('widget:value');widget(s,'widget:group')['children']=['widget:value','widget:text']
case('REPARENT',[dict(op='reparent',ids=['widget:value','widget:text'],parent='widget:group',index=0)],group)
def remove(s):s['roots'].remove('widget:text');s['widgets']=[w for w in s['widgets'] if w['id']!='widget:text']
case('REMOVE',[dict(op='remove',ids=['widget:text'])],remove)
newgroup=copy.deepcopy(widget(base,'widget:group'));newgroup['id']='widget:newgroup';newgroup['title']='New group'
def grouping(s):
 s['widgets'].append(copy.deepcopy(newgroup));s['roots'].insert(1,'widget:newgroup');s['roots'].remove('widget:text');s['roots'].remove('widget:value');widget(s,'widget:newgroup')['children']=['widget:text','widget:value']
case('GROUP',[dict(op='insert',widget=newgroup,parent=None,index=1),dict(op='reparent',ids=['widget:text','widget:value'],parent='widget:newgroup',index=0)],grouping)
def duplicate(s):
 group(s)
 for old,new in [('widget:text','widget:text-copy'),('widget:value','widget:value-copy'),('widget:group','widget:group-copy')]:
  w=copy.deepcopy(widget(s,old));w['id']=new
  if 'children'in w:w['children']=['widget:value-copy','widget:text-copy']
  s['widgets'].append(w)
 s['roots'].insert(s['roots'].index('widget:group')+1,'widget:group-copy')
case('DUPLICATE',[dict(op='reparent',ids=['widget:value','widget:text'],parent='widget:group',index=0),dict(op='duplicate',ids=['widget:group'],mapping={'widget:group':'widget:group-copy','widget:text':'widget:text-copy','widget:value':'widget:value-copy'})],duplicate)
def cascade(s):group(s);s['roots'].remove('widget:group');s['widgets']=[w for w in s['widgets'] if w['id']not in ['widget:text','widget:value','widget:group']]
case('CASCADE',[dict(op='reparent',ids=['widget:value','widget:text'],parent='widget:group',index=0),dict(op='remove',ids=['widget:group'])],cascade)
data=dict(base_revision='40',accepted_revision='41',history_entries=64,history_bytes=8388608,cases=rows)
assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
d=r/'out/campaign/editor-original';d.mkdir(exist_ok=True)
paths=['spec/delivery/packages/w-10-editor-draft.md','tests/editor/cases.json','tests/configuration/settings-content-fixture.json','out/campaign/prepare_editor_inputs.py']
hashes={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in paths}
with zipfile.ZipFile(d/'original.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
(d/'original.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved independent literal inputs and',len(rows),'complete expected scenes.')
