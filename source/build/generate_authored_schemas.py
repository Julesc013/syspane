"""Embed the closed authored-document schema set; fail on unsupported schema growth."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
NAMES=('settings','scene-v0.2','scene-v0.3','scene-v0.4','scene-v0.5','layout','binding','visibility','command-v0.2','command-v0.3','command-v0.4','command-v0.5','command-v0.6','command-v0.7','command-v0.8','command-result','content-package','content-catalog','preset','theme','theme-v0.2','resource-selection-v0.2')
KEYS={'$schema','$id','$defs','$ref','$comment','title','description','type','properties','required','additionalProperties',
      'const','enum','oneOf','anyOf','allOf','if','then','else','not','minLength','maxLength','pattern','propertyNames',
      'minItems','maxItems','uniqueItems','items','contains','minimum','maximum','maxProperties'}
def check(s):
    if not isinstance(s,dict) or set(s)-KEYS:raise ValueError('unsupported authored schema keyword')
    if 'additionalProperties' in s and s['additionalProperties'] is not False:raise ValueError('unsupported additional properties')
    for key in ('properties','$defs'):
        for child in s.get(key,{}).values():check(child)
    for key in ('oneOf','anyOf','allOf'):
        for child in s.get(key,[]):check(child)
    for key in ('if','then','else','not','items','contains','propertyNames'):
        if key in s:check(s[key])
def main():
    lines=['// Generated from the canonical authored schemas. Do not edit.','#pragma once','namespace syspane::configuration {']
    for name in NAMES:
        p=ROOT/'spec/contracts'/(name+'.schema.json');v=json.loads(p.read_text());check(v)
        text=json.dumps(v,separators=(',',':'),ensure_ascii=True)
        lines+=['// '+name+' SHA256 '+hashlib.sha256(p.read_bytes()).hexdigest(),
                'inline constexpr const char '+name.replace('-','_').replace('.','_')+'_schema[] =']
        lines += [json.dumps(text[i:i+2048]) for i in range(0,len(text),2048)];lines+=[';']
    lines+=['}'];text='\n'.join(lines)+'\n';p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists() or p.read_text()!=text:p.write_text(text,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
