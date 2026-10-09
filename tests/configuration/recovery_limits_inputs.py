"""Deterministic maximum-input recipe; never derives expectations from the product."""
from pathlib import Path
import copy,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
encoded=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()
sha=lambda value:hashlib.sha256(value).hexdigest()


def scene(maximum=False):
    value=copy.deepcopy(json.loads((ROOT/'tests/configuration/profile-startup-cases.json').read_bytes())['documents']['scene'])
    for index in range(254):
        name='widget:limit:'+format(index,'03d')
        value['roots'].append(name)
        value['widgets'].append(dict(id=name,kind='text',title='Limit text '+format(index,'03d'),bindings=[],content=dict(body='L'),
            display=dict(role='primary'),layout=dict(base=dict(kind='fixed',x=(index%16)*40,y=(index//16)*30,width=40,height=30)),priority='normal'))
    assert len(value['widgets'])==256
    if maximum:
        remaining=262144-len(encoded(value));assert remaining>0
        for widget in value['widgets'][2:]:
            count=min(remaining,1023);widget['content']['body']+='L'*count;remaining-=count
        assert remaining==0 and len(encoded(value))==262144
    return value


def command(value,maximum=False):
    result=json.loads((ROOT/'tests/configuration/frontend-recovery-command.json').read_bytes())
    result['operations'][0]['scene']=copy.deepcopy(value)
    if maximum:
        result['extensions']={'experiment.padding':''}
        result['extensions']['experiment.padding']='P'*(327680-len(encoded(result)))
        assert len(encoded(result))==327680
    return result


def record(value,generation,maximum=False,command_maximum=False):
    raw=encoded(dict(format='syspane.editor-recovery',schema_version='0.1.0',identity=dict(profile='profile:default',generation=generation),command=encoded(command(value,command_maximum)).decode()))
    if maximum:
        raw+=b' '*(786432-len(raw));assert len(raw)==786432
    return raw


def identities():
    return {name:dict(widgets=len(value['widgets']),scene_bytes=len(encoded(value)),scene_sha256=sha(encoded(value)),command_bytes=len(encoded(command(value))),record_bytes=len(record(value,'0'*64))) for name,value in [('MAX-WIDGETS',scene()),('MAX-SCENE',scene(True))]}
