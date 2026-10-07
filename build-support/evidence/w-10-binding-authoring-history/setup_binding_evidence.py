from pathlib import Path
import json,hashlib,subprocess
r=Path.cwd();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();old='ce7731133431029d72d6d39f149d59f4663e66af'
def read(n):return (r/'out/campaign'/n).read_text()
def write(n,s):(r/'out/campaign'/n).write_text(s,encoding='utf-8',newline='\n')
def common(s):return s.replace('w-10-content-properties-','w-10-binding-authoring-').replace('out/campaign/w-10-content-properties','out/campaign/w-10-binding-authoring').replace(old,base).replace('111','118')
s=common(read('archive_properties.py'));s=s.replace("('EDITOR-CONTENT-PROPERTIES'","('EDITOR-BINDING-AUTHORING','EDITOR-CONTENT-PROPERTIES'");write('archive_bindings.py',s)
s=common(read('preserve_properties.py'));start=s.index('helpers=');end=s.index('for p in [',start)
helpers=['prepare_binding_authoring.py','prepare_binding_text.py','setup_binding_authoring.py','setup_binding_native.py','binding_step.py','binding_flow.py','document_bindings.py','archive_bindings.py','preserve_bindings.py','finish_bindings_checks.py','setup_binding_evidence.py','finish_bindings.py','stage_bindings.py','prune_bindings_duplicates.py','bindings-pruned-duplicates.json','prune_bindings_older_duplicates.py','bindings-pruned-older-duplicates.json']
s=s[:start]+'helpers='+repr(helpers)+'\n'+s[end:];s=s.replace("'properties-execution-*.json'","'binding-execution-*.json'").replace("('fixed-inputs.json','fixed-inputs.zip')","('fixed-inputs.json','fixed-inputs.zip','fixed-text-inputs.json','fixed-text-inputs.zip')").replace("latest('linux-x64-gcc13','properties')","latest('linux-x64-gcc13','bindings')").replace("('properties','snap','group','arrange','native','large')","('bindings','properties','snap','group','arrange','native','large','oracle')")
s=s.replace("families={'EDITOR-CONTENT-PROPERTIES'", "families={'EDITOR-BINDING-AUTHORING':('syspane_editor_window','tests/editor/native_binding_authoring.py',15),'SETTINGS-FORM':('syspane_settings_window','tests/configuration/native_settings.py',18),'EDITOR-CONTENT-PROPERTIES'")
s=s.replace("    if family=='EDITOR-CONTENT-PROPERTIES':", "    if family=='EDITOR-BINDING-AUTHORING':\n        assert v['fixture_sha256']==sha(r/'tests/editor/binding-authoring-cases.json') and v['text_fixture_sha256']==sha(r/'tests/editor/binding-text-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py') and v['content_harness_sha256']==sha(r/'tests/editor/native_content_properties.py')\n    if family=='EDITOR-CONTENT-PROPERTIES':")
s=s.replace("scope='118 affected checks on each development profile and independent native content properties, snap, group, arrange, editor and large-command/store/IPC cases.","scope='118 affected checks on each development profile and independent native binding, content, snap, group, arrange, editor, settings and large-command/store/IPC cases.")
s=s.replace("originals=dict(record=", "text_originals=dict(record=ref(history/'fixed-text-inputs.json'),archive=ref(history/'fixed-text-inputs.zip')),originals=dict(record=")
write('preserve_bindings.py',s)
s=common(read('finish_properties_checks.py'));write('finish_bindings_checks.py',s)
s=common(read('stage_properties.py')).replace('content-properties-handoff.json','binding-authoring-handoff.json').replace('properties-staging-paths.txt','bindings-staging-paths.txt')
s=s.replace("original=index['originals'];fixed=", "original=index['text_originals'];fixed=json.loads(content(original['record']['path']))\nwith zipfile.ZipFile(io.BytesIO(content(original['archive']['path']))) as z:\n    for n,digest in fixed['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)\noriginal=index['originals'];fixed=")
s=s.replace("('EDITOR-CONTENT-PROPERTIES'","('EDITOR-BINDING-AUTHORING','EDITOR-CONTENT-PROPERTIES'")
s=s.replace("check('tests/configuration/large-command-cases.json'", "check('tests/editor/binding-authoring-cases.json' if family=='EDITOR-BINDING-AUTHORING' else 'tests/configuration/large-command-cases.json'")
s=s.replace("check('tests/editor/native_content_properties.py'", "check('tests/editor/native_binding_authoring.py' if family=='EDITOR-BINDING-AUTHORING' else 'tests/editor/native_content_properties.py'")
s=s.replace("'wrong-content','retain-content')","'wrong-content','retain-content','wrong-binding','retain-binding')")
s=s.replace("    report=json.loads(content(row['path']));assert report['outcome']=='pass'","    report=json.loads(content(row['path']));assert report['outcome']=='pass'\n    if family=='EDITOR-BINDING-AUTHORING':\n        check('tests/editor/binding-text-cases.json',report['text_fixture_sha256']);check('tests/editor/native_content_properties.py',report['content_harness_sha256'])")
s=s.replace('Staged shared and native content properties,','Staged shared and native binding authoring,');write('stage_bindings.py',s)
for stem in ('fixed-inputs','fixed-text-inputs'):
 p=r/'out/campaign/w-10-binding-authoring'/(stem+'.json');v=json.loads(p.read_text());v['archive_sha256']=hashlib.sha256(p.with_suffix('.zip').read_bytes()).hexdigest();p.write_text(json.dumps(v,indent=2)+'\n')
print('Prepared evidence helpers.')
