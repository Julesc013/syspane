"""Installed production inspector with CPU bindings, native values and actual stop."""
from pathlib import Path
from fractions import Fraction
import json
import math
import os
import re
import select
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/configuration'))
import native_installed_editor as h
import inspector_authored_inputs as inputs

CASES_PATH='tests/configuration/installed-processor-cases.json'
h.CASES=json.loads((ROOT/CASES_PATH).read_bytes())
original_xvfb=h.launch_xvfb
h.launch_xvfb=lambda workspace:original_xvfb(workspace,tuple(h.CASES['screen']))
FIELDS=['linux.cpu.execution_percent','linux.cpu.interval_busy_ticks','linux.cpu.interval_total_ticks']

def scene():
    value=json.loads((ROOT/'tests/configuration/profile-startup-cases.json').read_bytes())['documents']['scene']
    table=value['widgets'][1]
    table['id']='widget:cpu';table['title']='Online CPU execution'
    table['layout']['base'].update(x=24,y=24,width=1520,height=1120)
    table['bindings']=[dict(kind='selector',scope=dict(kind='local_host'),entity_type='processor.logical',field=field,predicates=[],mode='collection',sort=[],limit=64) for field in FIELDS]
    table['content']['columns']=[{'label':title} for title in ('Execution','Busy ticks','Total ticks')]
    value['scene_id']='scene:cpu';value['roots']=['widget:cpu'];value['widgets']=[table]
    return value

def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value=(e[k] for k in ('wait','click','find','value'))
    (folder/'network').write_text('allow');(folder/'processor-record').write_text('yes')
    e['launch']();e['settings_ready']();e['quit']()
    fixture,_=inputs.generation(ROOT,'PROCESSOR',authored=scene());inputs.install(e['generations'],fixture)
    report['scene_sha256']=h.sha(fixture[2]['scene.json'])
    report['screen']=h.CASES['screen']
    e['launch']();e['settings_ready']()
    online=[]
    for token in Path('/sys/devices/system/cpu/online').read_text().strip().split(','):
        limits=list(map(int,token.split('-')));online.extend(range(limits[0],limits[-1]+1))
    assert 0<len(online)<=64,'this UI profile requires complete visible CPU coverage within the existing table bound'
    def children():
        pids=set();parent=e['process']().pid
        for task in Path('/proc',str(parent),'task').iterdir():
            try:pids.update(map(int,(task/'children').read_text().split()))
            except FileNotFoundError:pass
        result=[]
        for pid in pids:
            try:
                args=Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')[:-1]
                if args==[b'syspane-network-host',b'--network',str(parent).encode()]:result.append(pid)
            except FileNotFoundError:pass
        assert len(result)<=1;return result
    def rows():
        tree=find('syspane.scene.inspector')
        if not tree:return []
        table=tree.get_table_iface();assert table and table.get_n_columns()==2
        return [[e['text'](table.get_accessible_at(r,c)) for c in range(2)] for r in range(table.get_n_rows())]
    def live():
        actual=rows();fields=[(k,v) for k,v in actual if '[linux.cpu.' in k]
        if len(fields)!=3*len(online) or not all('acquisition=success' in v and 'lease=active' in v for _,v in fields):return False
        epochs={re.search(r' \| Epoch (\S+) \| Generation (\d+)$',v).group(1) for k,v in actual if k.startswith('processor:logical:')}
        if len(epochs)!=1:return False
        parsed={};entity=None
        for key,text in actual:
            if key.startswith('processor:logical:'):entity=key;continue
            if '[linux.cpu.' not in key:continue
            field=next(name for name in FIELDS if key.endswith('['+name+']'))
            number=re.search(r'(?:^|\n)([0-9]+(?:\.[0-9]+)?) (percent|USER_HZ tick)(?:\n|$)',text)
            if not number:return False
            if entity is None:return False
            parsed.setdefault(entity,{})[field]=float(number[1]) if field==FIELDS[0] else int(number[1])
        if len(parsed)!=len(online) or any(set(v)!=set(FIELDS) for v in parsed.values()):return False
        for values in parsed.values():
            busy,total=values[FIELDS[1]],values[FIELDS[2]]
            if not 0<=busy<=total or not total:return False
            if not math.isclose(values[FIELDS[0]],float(Fraction(100*busy,total)),abs_tol=.051):return False
        return actual
    click('frontend.inspector');current=wait(live,12);pid=wait(lambda:children() and children()[0]);fd=e['helper_pidfds'][pid]
    report['observations'].append(dict(rows=current,online_processors=len(online),pid=pid))
    if mode=='NAVIGATION':
        click('frontend.settings');e['settings_ready']();wait(lambda:bool(select.select([fd],[],[],0)[0]),3)
        assert not children();click('frontend.inspector');wait(live,12);replacement=wait(lambda:children() and children()[0]);assert replacement!=pid
    elif mode=='POLICY':
        (folder/'policy').write_text('deny');wait(lambda:bool(select.select([fd],[],[],0)[0]),4)
        start=time.monotonic();wait(lambda:not any(k.startswith('processor:logical:') for k,_ in rows()) and value('syspane.scene.requested-summary')=='',.2)
        report['erasure_ms']=(time.monotonic()-start)*1000
    elif mode=='CLOSE-HELD':
        (folder/'processor-mode').write_text('hold');wait(lambda:(folder/'processor-held').is_file(),3)
        assert int((folder/'processor-held').read_text())==pid
    else:assert mode=='LIVE'
    e['quit']()

if __name__=='__main__':h.main(exercise,Path(__file__).resolve(),CASES_PATH,prefix='installed-processor-')
