from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess,zipfile
r=Path.cwd();d=r/'out/campaign/visibility';d.mkdir(exist_ok=True)
def write(n,v):
 p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
binding={'kind':'direct','producer_id':'P1','producer_epoch':'E1','entity_id':'a','field':'test.value'}
rule={'schema_version':'0.1.0','binding':binding,'op':'eq','value':3,'unit':'byte'}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://schemas.example.invalid/syspane/0.1.0/visibility.schema.json','title':'SysPane visibility comparison experimental 0.1.0','type':'object','properties':{
 'schema_version':{'const':'0.1.0'},'binding':{'$ref':'https://schemas.example.invalid/syspane/0.1.0/binding.schema.json','if':{'properties':{'kind':{'const':'selector'}}},'then':{'properties':{'mode':{'const':'singleton'},'limit':{'const':1}}}},
 'op':{'enum':['eq','ne','lt','le','gt','ge']},'value':{'type':['number','boolean','string'],'maxLength':512},'unit':{'type':'string','minLength':1,'maxLength':64,'pattern':'^[A-Za-z0-9_./%:*^-]+$'}},
 'required':['schema_version','binding','op','value','unit'],'additionalProperties':False,
 'if':{'properties':{'value':{'type':['string','boolean']}}},'then':{'properties':{'op':{'enum':['eq','ne']},'unit':{'const':'1'}}}}
write('spec/contracts/visibility.schema.json',schema)
fixtures=[('valid/visibility-counter.json',rule,'valid','Exact singleton comparison.'),
 ('invalid/visibility-collection.json',{**rule,'binding':{'kind':'selector','scope':{'kind':'local_host'},'entity_type':'fixture.entity','mode':'collection','predicates':[],'sort':[],'limit':1,'field':'test.value'}},'invalid','A one-row collection is still not a singleton condition.'),
 ('invalid/visibility-string-order.json',{**rule,'value':'3','unit':'1','op':'lt'},'invalid','Text ordering is not admitted.'),
 ('invalid/visibility-coercion.json',{**rule,'value':True},'invalid','Boolean literals require dimensionless unit 1.'),
 ('invalid/visibility-extension.json',{**rule,'script':'return true'},'invalid','No executable or unknown property.')]
catalog=json.loads((r/'spec/fixtures/catalog.json').read_bytes())
for name,value,outcome,reason in fixtures:
 path='spec/fixtures/'+name;write(path,value)
 catalog['fixtures'].append(dict(path='fixtures/'+name,schema='visibility',expected=outcome,semantic=False,reason=reason))
write('spec/fixtures/catalog.json',catalog)
cases=[]
def case(name,kind,observed,op,literal,result,unit='1',literal_unit=None):
 cases.append(dict(id=name,kind=kind,observed=observed,unit=unit,op=op,literal=literal,literal_unit=unit if literal_unit is None else literal_unit,expected=result))
for op,result in [('eq','shown'),('ne','hidden'),('lt','hidden'),('le','shown'),('gt','hidden'),('ge','shown')]:case('equal-'+op,'uint64','3',op,3,result,'byte')
for op,result in [('eq','hidden'),('ne','shown'),('lt','shown'),('le','shown'),('gt','hidden'),('ge','hidden')]:case('below-'+op,'uint64','3',op,4,result,'byte')
case('above-2p53','uint64','9007199254740993','gt',9007199254740992.0,'shown')
case('no-rounded-equality','uint64','9007199254740993','eq',9007199254740992.0,'hidden')
case('uint64-max-exact','uint64','18446744073709551615','eq',18446744073709551615,'shown')
case('uint64-max-below-double-2p64','uint64','18446744073709551615','lt',18446744073709551616.0,'shown')
case('uint64-above-negative','uint64','0','gt',-9223372036854775808,'shown')
case('double-below-uint64-max','number',18446744073709549568.0,'lt',18446744073709551615,'shown')
case('double-2p64-above-max','number',18446744073709551616.0,'gt',18446744073709551615,'shown')
case('negative-signed-min','number',-9223372036854775808.0,'eq',-9223372036854775808,'shown')
case('negative-rounded-int','number',-9007199254740992.0,'gt',-9007199254740993,'shown')
case('fraction','number',3.5,'gt',3,'shown')
case('negative-fraction','number',-3.5,'lt',-3,'shown')
case('negative-zero','number',-0.0,'eq',0,'shown')
case('minimum-positive-double','number',5e-324,'gt',0,'shown')
case('maximum-double','number',1.7976931348623157e308,'gt',18446744073709551615,'shown')
case('boolean-true','boolean',True,'eq',True,'shown')
case('boolean-false','boolean',False,'ne',True,'shown')
case('no-bool-number-coercion','boolean',True,'ne',1,'type_mismatch')
case('no-string-number-coercion','string','3','ne',3,'type_mismatch')
case('no-number-string-coercion','uint64','3','ne','3','type_mismatch')
case('no-number-bool-coercion','uint64','1','ne',True,'type_mismatch')
case('unicode','string','漢字\n😀','eq','漢字\n😀','shown')
case('no-normalization','string','é','eq','e\u0301','hidden')
case('no-case-fold','string','Alpha','eq','alpha','hidden')
case('empty-text','string','','eq','','shown')
case('unit-mismatch','uint64','3','eq',3,'unit_mismatch','byte','bit')
case('no-unit-conversion','number',1000.0,'eq',1,'unit_mismatch','byte','kbyte')
write('tests/scene/visibility-cases.json',dict(comparisons=cases,states=[
 dict(id=k,expected=v) for k,v in [('current','shown'),('denied','denied'),('unsupported','unsupported'),('failed-retained','unavailable'),('pending-retained','unavailable'),('disabled','unavailable'),('absent','unavailable'),('support-unknown','unavailable'),('no-value','unavailable'),('stale','stale'),('clock-missing','pending'),('expired','lease_lost'),('disconnected','lease_lost'),('clock-missing-retained','lease_lost'),('missing-field','pending'),('unsupported-field','unsupported'),('missing-entity','empty'),('ambiguous','ambiguous'),('revoked','denied'),('regranted','pending'),('no-snapshot','pending')]]))
# Reclaim only byte-verified committed native duplicates before future builds.
s=(r/'out/campaign/prune_runtime_observation_duplicates.py').read_text()
s=s.replace("('w-10-focus-idle',)","('w-09-runtime-observation',)").replace('runtime-observation-pruned-duplicates.json','visibility-pruned-duplicates.json')
(r/'out/campaign/prune_visibility_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
print('Prepared fixed visibility schema and',len(cases),'comparison examples.')
