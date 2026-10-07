from pathlib import Path
import json
r=Path.cwd()
p=r/'build-support/components.json';v=json.loads(p.read_text());rows=v['components'] if 'components'in v else v['implementation']['components']
# Follow the existing manifest container without inventing another registry.
for id,target,source,header,dependency in [('editor-draft','syspane_editor_draft','source/interfaces/editor_draft.cpp','source/interfaces/editor_draft.hpp','syspane_settings_draft'),('editor-tests','syspane_editor_tests','tests/editor/editor_draft_tests.cpp',None,'syspane_editor_draft')]:
 template=next(x for x in rows if x['id']==('settings-draft' if header else 'settings-tests'));item=json.loads(json.dumps(template))
 item.update(id=id,target=target,source_owner='source/interfaces/' if header else 'tests/editor/',public_interfaces=[header] if header else [],private_interfaces=[],sources=[source],allowed_dependencies=[dependency]);rows.append(item)
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_text());rows=v['work_units']
w=next(x for x in rows if x['id']=='W-10');w.update(status='in_progress',execution_grant='user:foundation-native-campaign-2026-10-05',package='delivery/packages/w-10-editor-draft.md',notes='The complete release instruction admits W-10 against the implemented authored/resource/scene boundaries. Implement typed local operations and bounded reversible history through the existing transaction owner; native interactive surface, escape attachment, larger-scene envelope, remaining authoring contracts and full installed editor qualification remain required.');w['specs'].append('SP-W10-EDITOR-DRAFT')
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'out/campaign/resource_settings_step.py';s=p.read_text().replace('w-11-settings-resources','w-10-editor-draft').replace("'^(settings[.]|composition[.])'","'^(editor[.]|settings[.]|composition[.])'").replace("'^(settings[.]|configuration[.]","'^(editor[.]|settings[.]|configuration[.]").replace("artifact_name='syspane_settings_tests'","artifact_name='syspane_editor_tests'").replace("else 'syspane_settings_tests.exe'","else 'syspane_editor_tests.exe'")
(r/'out/campaign/editor_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/resource_settings_flow.py').read_text().replace('resource-settings-execution','editor-execution').replace('resource_settings_step','editor_step')
(r/'out/campaign/editor_flow.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/reclaim_resource_settings_prior.ps1').read_text().replace('resource-settings-prior-reclamation','editor-prior-reclamation')
(r/'out/campaign/reclaim_editor_prior.ps1').write_text(s,encoding='utf-8',newline='\n')
