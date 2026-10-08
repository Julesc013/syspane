from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess,zipfile
r=Path.cwd();out=r/'out/campaign/w-09-typography';out.mkdir(exist_ok=True)
def read(n):return json.loads((r/n).read_bytes())
def write(n,v):(r/n).write_text(json.dumps(v,indent=2,ensure_ascii=True)+'\n',encoding='utf-8',newline='\n')
s=read('spec/contracts/theme.schema.json');s['$id']=s['$id'].replace('/0.1.0/','/0.2.0/');s['title']='SysPane theme typography 0.2';s['properties']['schema_version']['const']='0.2.0'
font={'type':'object','properties':{'family':{'type':'string','minLength':1,'maxLength':128,'pattern':'^[^ \\u0000-\\u001f\\u007f-\\u009f,](?:[^\\u0000-\\u001f\\u007f-\\u009f,]*[^ \\u0000-\\u001f\\u007f-\\u009f,])?$'},'size_dip':{'type':'number','minimum':9,'maximum':72},'weight':{'enum':[100,200,300,400,500,600,700,800,900]},'style':{'enum':['normal','italic','oblique']}},'required':['family','size_dip','weight','style'],'additionalProperties':False}
s['$defs']={'font':font};s['properties']['font']={'$ref':'#/$defs/font'};s['properties']['font_roles']={'type':'object','properties':{n:{'$ref':'#/$defs/font'} for n in ('body','label','value','diagnostic')},'additionalProperties':False}
s['description']='Versioned complete font roles. Family is one literal font-family name; missing roles use the base font. Current-policy resource capability theme.typography is required.'
write('spec/contracts/theme-v0.2.schema.json',s)
legacy={'schema_version':'0.1.0','theme_id':'theme:typography','name':'Typography oracle','tokens':{'foreground':'#ffffffff','background':'#00000000','warning':'#ff8000ff','error':'#ff0000ff','muted':'#808080ff'},'font':{'family':'Noto Sans','size_dip':24},'motion':'none','extensions':{'author.note':{'preserve':['font',1,False]}}}
base={'family':'Noto Sans','size_dip':24,'weight':400,'style':'normal'}
roles={'body':{'family':'Noto Serif','size_dip':17.25,'weight':300,'style':'normal'},'label':{'family':'Noto Sans','size_dip':20,'weight':700,'style':'normal'},'value':{'family':'DejaVu Sans Mono','size_dip':26,'weight':400,'style':'italic'},'diagnostic':{'family':'Noto Sans','size_dip':22,'weight':900,'style':'oblique'}}
theme=copy.deepcopy(legacy);theme.update(schema_version='0.2.0',font=base,font_roles=roles)
cases={'legacy':legacy,'theme':theme,'expected_base':base,'expected_roles':copy.deepcopy(roles),'native_text':'SysPane 128','invalid_roles':['','caption','BODY'],'invalid_fonts':[]}
for key,values in {'family':['',' ',' Noto Sans','Noto Sans ','Noto,Sans','bad\nfont','bad\u0085font','x'*129],'size_dip':[8.999,72.001],'weight':[0,350,1000,'400'],'style':['bold',None]}.items():
 for value in values:
  bad=copy.deepcopy(base);bad[key]=value;cases['invalid_fonts'].append(bad)
for key in base:
 bad=copy.deepcopy(base);del bad[key];cases['invalid_fonts'].append(bad)
bad=copy.deepcopy(base);bad['script']='no';cases['invalid_fonts'].append(bad)
write('tests/scene/typography-cases.json',cases)
fixtures=[('valid/theme-typography',theme)]
for name,change in [('weight',lambda t:t['font'].update(weight=350)),('role',lambda t:t['font_roles'].update(caption=base)),('partial',lambda t:t['font_roles'].update(body={'size_dip':12})),('family',lambda t:t['font'].update(family='Noto,Sans')),('null',lambda t:t.update(font_roles=None)),('old',lambda t:t.update(schema_version='0.1.0'))]:
 bad=copy.deepcopy(theme);change(bad);fixtures.append(('invalid/theme-typography-'+name,bad))
catalog=read('spec/fixtures/catalog.json')
for name,value in fixtures:
 write('spec/fixtures/'+name+'.json',value);catalog['fixtures'].append({'path':'fixtures/'+name+'.json','schema':'theme' if name.endswith('-old') else 'theme-v0.2','expected':name.split('/')[0],'semantic':False,'reason':'Versioned literal typography roles and legacy rejection.'})
write('spec/fixtures/catalog.json',catalog)
paths=['spec/delivery/packages/w-09-typography.md','spec/contracts/theme-v0.2.schema.json','tests/scene/typography-cases.json']+['spec/fixtures/'+n+'.json' for n,_ in fixtures]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(out/'fixed-inputs.zip','x',zipfile.ZIP_DEFLATED) as z:
 for n in paths:z.write(r/n,n)
write('out/campaign/w-09-typography/fixed-inputs.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'source_base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'inputs':{n:sha(r/n) for n in paths},'archive_sha256':sha(out/'fixed-inputs.zip')})
import jsonschema
validator=jsonschema.Draft202012Validator(s)
validator.validate(theme)
for f in cases['invalid_fonts']:
 bad=copy.deepcopy(theme);bad['font']=f;assert list(validator.iter_errors(bad)),f
for name,value in fixtures:
 v=jsonschema.Draft202012Validator(read('spec/contracts/theme.schema.json') if name.endswith('-old') else s)
 assert bool(list(v.iter_errors(value)))==name.startswith('invalid/'),name
write('out/campaign/typography-fixed-validation.json',{'outcome':'pass','schema_sha256':sha(r/'spec/contracts/theme-v0.2.schema.json'),'invalid_fonts':len(cases['invalid_fonts']),'fixtures':len(fixtures),'scope':'Independent JSON Schema validation before production edits; expected role values are literal.'})
print('Frozen typography contract, literal cases and independently validated fixtures.')
