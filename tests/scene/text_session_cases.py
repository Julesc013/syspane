"""Fixed requests for isolated versus composition-scoped native text rendering."""
from pathlib import Path
import copy
import json

ROOT=Path(__file__).resolve().parents[2]


def cases():
    theme=dict(schema_version='0.1.0',theme_id='test',name='Text session oracle',
               tokens=dict(foreground='#ffffffff',background='#00000000',warning='#ff8000ff',error='#ff0000ff',muted='#808080ff'),
               font=dict(family='Noto Sans',size_dip=24),motion='none')
    typography=json.loads((ROOT/'tests/scene/typography-cases.json').read_bytes())['theme']
    rows=[]
    def add(name,text='SysPane',**options):
        rows.append(dict(id=name,request=dict(text=text,theme=copy.deepcopy(theme),**options)))
    add('plain','SysPane 0123456789')
    add('empty','')
    add('combining','cafe\u0301')
    add('arabic','مرحبا بالعالم',language='ar')
    add('bidi','SysPane مرحبا 123',language='ar',wrap_units=240*64)
    add('wrap','network throughput sample label',wrap_units=100*64)
    add('multiline','first\nsecond')
    add('scale','Scale مرحبا',numerator=3,denominator=2)
    add('missing-glyph','\U0010ffff')
    add('fallback');rows[-1]['request']['theme']['font']['family']='SysPane Missing Family 72'
    for role in ('body','label','value','diagnostic'):
        add('role-'+role,'Throughput مرحبا',role=role);rows[-1]['request']['theme']=copy.deepcopy(typography)
    for contrast in ('light','dark'):
        add('contrast-'+contrast,contrast=contrast,token='warning')
    add('alpha');rows[-1]['request']['theme']['tokens']['foreground']='#ff000080'
    add('background','');rows[-1]['request']['theme']['tokens']['background']='#204080ff'
    add('fractional');rows[-1]['request']['theme']['font']['size_dip']=17.25
    add('bad-role',role='unknown')
    add('bad-wrap',wrap_units=0)
    add('bad-scale',numerator=0)
    add('bad-language',language='1bad')
    add('bad-token',token='unknown')
    add('bad-pixels',pixel_budget=0)
    add('bad-control','x\u0000y')
    add('bad-utf8',text_hex='c0af')
    add('too-long','x'*1025)
    add('capacity','W'*1024)
    add('after-rejections','SysPane 0123456789')
    assert len(rows)<=64
    return rows
