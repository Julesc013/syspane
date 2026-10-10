"""Independent authored live-table inputs and exact semantic oracle."""
import re
import inspector_authored_inputs as authored

FIELDS=['network.receive_bytes','network.transmit_bytes','entity.id','entity.kind','entity.display_name']
LABELS=['Rx','Tx','Identity','Kind','Name']

def count(mode):return 65 if mode=='TRUNCATION' else 64
def columns(mode):return 1 if mode=='MAX-ROWS' else 5 if mode=='OVER-CELLS' else 4

def generation(root,mode):
    bindings=[dict(kind='selector',scope=dict(kind='local_host'),entity_type='network.interface',field=f,
                   predicates=[],mode='collection',sort=[],limit=64) for f in FIELDS[:columns(mode)]]
    widget=dict(id='table',kind='table',title='Live table',display=dict(role='primary'),
                layout=dict(base=dict(kind='fixed',x=0,y=0,width=1600,height=2048)),bindings=bindings,
                priority='essential',content=dict(columns=[dict(label=l) for l in LABELS[:columns(mode)]]))
    scene=dict(schema_version='0.3.0',revision='0',scene_id='scene:live-table',theme_id='theme:native',roots=['table'],widgets=[widget])
    return authored.generation(root,mode,scene,9)[0]

def verify(rows,mode,round):
    n=columns(mode);assert mode!='OVER-CELLS'
    entities=sorted('network:interface:'+str(i) for i in range(1,count(mode)+1))[:64]
    assert len(rows)==1+64*(n+1),(len(rows),1+64*(n+1))
    assert rows[0]==['Live table',f'Showing 64 of {count(mode)} rows'],rows[0]
    owners=set()
    for row,entity in enumerate(entities):
        at=1+row*(n+1);item,info=rows[at];assert item==entity,(item,entity)
        owner=re.fullmatch(r'Producer producer:network \| Epoch (\S+) \| Generation (\d+)',info);assert owner,info
        owners.add(owner.groups());i=int(entity.rsplit(':',1)[1])
        for column,field in enumerate(FIELDS[:n]):
            item,info=rows[at+column+1];assert item==LABELS[column]+' ['+field+']',item
            if column<2:
                expected=f'{(1000 if column==0 else 2000)*round+i} byte\nCurrent\n'
                assert info.startswith(expected),(entity,field,info,expected)
                assert re.fullmatch(re.escape(expected)+r'support=supported; acquisition=success; presence=present; freshness=current; origin=observed; lease=active; age=\d+ ns',info),info
            else:
                text=entity if field=='entity.id' else 'network.interface' if field=='entity.kind' else 'Network interface '+str(i)
                expected=text+'\nConfigured\nsupport=supported; acquisition=success; presence=present; freshness=current; origin=configured; lease=active; age=unknown'
                assert info==expected,(info,expected)
    assert len(owners)==1,owners
    return next(iter(owners))
