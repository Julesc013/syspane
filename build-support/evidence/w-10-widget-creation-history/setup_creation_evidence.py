from pathlib import Path
r=Path.cwd();base='8ecf403ebef7622c967f10b90d337d6c3d7037de'
def write(n,s):(r/'out/campaign'/n).write_text(s,encoding='utf-8',newline='\n')
def read(n):return (r/'out/campaign'/n).read_text()
s=read('archive_bindings.py').replace('w-10-binding-authoring','w-10-widget-creation').replace("('EDITOR-BINDING-AUTHORING',","('EDITOR-WIDGET-CREATION','EDITOR-BINDING-AUTHORING',");write('archive_creation.py',s)
s=read('preserve_bindings.py').replace('w-10-binding-authoring','w-10-widget-creation').replace('e1c96162bd7f755c182d050e1611a1aabd9a3c8e',base)
a=s.index('helpers=');b=s.index('for p in [',a)
s=s[:a]+"helpers=['prepare_widget_creation.py','setup_widget_creation.py','setup_creation_native.py','creation_step.py','creation_flow.py','document_creation.py','archive_creation.py','preserve_creation.py','setup_creation_evidence.py','finish_creation_checks.py','finish_creation.py','stage_creation.py']\n"+s[b:]
s=s.replace("glob('binding-execution-*.json')","glob('creation-execution-*.json')").replace("('fixed-inputs.json','fixed-inputs.zip','fixed-text-inputs.json','fixed-text-inputs.zip')","('fixed-inputs.json','fixed-inputs.zip')")
a=s.index('def compatible(');b=s.index('final={}',a)
s=s[:a]+'''def compatible(v):
    assert set(v['source_inputs'])==set(current)
    assert v['source_inputs']==current

'''+s[b:]
s=s.replace('==118','==124').replace("('bindings','properties','snap','group','arrange','native','large','oracle')","('creation','bindings','properties','snap','group','arrange','native','large')")
s=s.replace("families={'EDITOR-BINDING-AUTHORING'", "families={'EDITOR-WIDGET-CREATION':('syspane_editor_window','tests/editor/native_widget_creation.py',17),'EDITOR-BINDING-AUTHORING'")
s=s.replace("'SETTINGS-FORM':('syspane_settings_window','tests/configuration/native_settings.py',18),",'')
s=s.replace("    if family=='EDITOR-BINDING-AUTHORING':", "    if family=='EDITOR-WIDGET-CREATION':\n        assert v['fixture_sha256']==sha(r/'tests/editor/widget-creation-cases.json') and v['resources_sha256']==sha(r/'tests/editor/content-properties-fixture.json') and v['content_harness_sha256']==sha(r/'tests/editor/native_content_properties.py') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py')\n    if family=='EDITOR-BINDING-AUTHORING':")
s=s.replace("text_originals=dict(record=ref(history/'fixed-text-inputs.json'),archive=ref(history/'fixed-text-inputs.zip')),",'').replace('118 affected checks','124 affected checks').replace('binding, content, snap, group, arrange, editor, settings and','creation, binding, content, snap, group, arrange, editor and')
write('preserve_creation.py',s)
s=read('finish_bindings_checks.py').replace('w-10-binding-authoring','w-10-widget-creation').replace('e1c96162bd7f755c182d050e1611a1aabd9a3c8e',base);write('finish_creation_checks.py',s)
s=read('finish_bindings.py').replace('w-10-binding-authoring','w-10-widget-creation').replace('binding-authoring-handoff.json','widget-creation-handoff.json').replace('==118','==124').replace('==130','==129').replace('118 affected','124 affected').replace('130 native','129 native')
a=s.index("h.update(source_ref=");b=s.index('jsonschema.validate(h',a)
s=s[:a]+'''h.update(source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),objective='Add native creation of all seven primitives through existing atomic draft, resource, policy and persistence owners',changed_files=sorted(set(files)|{hp,prefix+'staging.json'}),
 decisions=['Freeze exact default objects, full expected scenes and resource inputs before implementation.', 'Keep parent-local geometry and root/group display intent explicit; images require an admitted choice.', 'Use separate private buffers, atomic insertion/selection history and separate durable Apply.', 'Preserve original compile/test/native failures with exact source identities.', 'Keep the 7 GiB workspace limit and all five release tracks.'],
 checks=[{'name':'124 affected checks on each of three toolchains','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'}, {'name':'129 native cases across eight matrices','outcome':'not_run' if pending else 'pass','evidence':prefix+'attempts.json'}, {'name':'Schema, fixture, tooling and integrity checks','outcome':'not_run' if pending else 'pass','evidence':prefix+'verification.json'}, {'name':'Staged source/oracle/artifact/evidence identities','outcome':'not_run','evidence':prefix+'staging.json'}, {'name':'Complete native editions and historical/release qualification','outcome':'not_run','evidence':None}],
 next_step='Close responsive/flow transforms and remaining properties, then installed controller/catalog/policy ownership, scene-aligned entry/restoration and independent escape. Continue all five release tracks.',
 limitations=['Owned Linux ext4/Xvfb/DBus evidence does not qualify installed editing or physical power-loss durability.', 'Provider discovery, responsive/flow transforms, lock/visibility/typography, clipboard authority and recovery drafts remain required.', 'Full accessibility/performance, other adapters, historical laboratories and every complete-edition gate remain open.', 'Windows builds run on contemporary Windows; two existing symlink tooling assertions remain skipped.'])
'''+s[b:];write('finish_creation.py',s)
s=read('stage_bindings.py').replace('w-10-binding-authoring','w-10-widget-creation').replace('binding-authoring-handoff.json','widget-creation-handoff.json').replace('bindings-staging-paths','creation-staging-paths')
a=s.index('    delta={n:dict(');b=s.index("    if action!='build'",a);s=s[:a]+"    assert v['source_inputs']==index['current_inputs']\n"+s[b:]
a=s.index("original=index['text_originals']");b=s.index("original=index['originals']",a);s=s[:a]+s[b:]
s=s.replace("    if family=='EDITOR-BINDING-AUTHORING':", "    if family=='EDITOR-WIDGET-CREATION':\n        check('tests/editor/widget-creation-cases.json',report['fixture_sha256']);check('tests/editor/content-properties-fixture.json',report['resources_sha256']);check('tests/editor/native_content_properties.py',report['content_harness_sha256'])\n    if family=='EDITOR-BINDING-AUTHORING':")
s=s.replace("('EDITOR-BINDING-AUTHORING',","('EDITOR-WIDGET-CREATION','EDITOR-BINDING-AUTHORING',")
s=s.replace("check('tests/editor/binding-authoring-cases.json' if family", "check('tests/editor/widget-creation-cases.json' if family=='EDITOR-WIDGET-CREATION' else 'tests/editor/binding-authoring-cases.json' if family")
s=s.replace("check('tests/editor/native_binding_authoring.py' if family", "check('tests/editor/native_widget_creation.py' if family=='EDITOR-WIDGET-CREATION' else 'tests/editor/native_binding_authoring.py' if family")
s=s.replace("('frozen-preview','wrong-group'","('wrong-insert','retain-create','frozen-preview','wrong-group'").replace('native binding authoring','native widget creation')
write('stage_creation.py',s)
