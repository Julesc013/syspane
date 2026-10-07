from pathlib import Path
import copy,json
r=Path(__file__).resolve().parents[2]
p=r/'build-support/components.json';d=json.loads(p.read_text());rows=d['components'];template=next(x for x in rows if x['id']=='settings-form')
for name,kind,owner,header,sources,deps in [
 ('private-text','STATIC_LIBRARY','source/interfaces/',['source/interfaces/private_text.hpp'],['source/interfaces/private_text_linux.cpp'],['PkgConfig::GTK3']),
 ('editor-form','STATIC_LIBRARY','source/interfaces/',['source/interfaces/editor_form.hpp'],['source/interfaces/editor_form_linux.cpp'],['syspane_editor_draft','syspane_scene_surface','syspane_private_text','PkgConfig::GTK3']),
 ('editor-window','EXECUTABLE','tests/editor/',[],['tests/editor/editor_window.cpp'],['syspane_editor_form','syspane_async_commands','syspane_generation_store','syspane_child','PkgConfig::GTK3','Threads::Threads'])]:
    row=copy.deepcopy(template);row.update(id=name,target='syspane_'+name.replace('-','_'),type=kind,source_owner=owner,public_interfaces=header,sources=sources,allowed_dependencies=deps);rows.append(row)
template['allowed_dependencies'].insert(-1,'syspane_private_text');p.write_text(json.dumps(d,indent=2)+'\n')
p=r/'spec/delivery/work-units.json';d=json.loads(p.read_text());row=next(x for x in d['work_units'] if x['id']=='W-10');row['specs'].append('SP-W10-NATIVE-EDITOR');row['package']='delivery/packages/w-10-native-editor.md';p.write_text(json.dumps(d,indent=2)+'\n')
for name in ('step','flow'):
    p=r/f'out/campaign/editor_{name}.py';s=p.read_text().replace('editor_step.py','native_editor_step.py').replace('w-10-editor-draft','w-10-native-editor').replace('editor-execution-','native-editor-execution-')
    s=s.replace("'image','test'","'image','native','exit','surface','test'").replace("'resources','image')","'resources','image','native','exit','surface')")
    if name=='step':
        s=s.replace("command={'image':", "command={'native':['ctest','--preset',profile,'-R','^native[.]EDITOR-FORM$','--output-on-failure'],'exit':['ctest','--preset',profile,'-R','^native[.]EDITOR-EXIT$','--output-on-failure'],'surface':['ctest','--preset',profile,'-R','^(scene[.]|rendering[.]|native[.](SCENE|TABLE|CHART|CONTENT|IMAGE)-ERASURE$)','--output-on-failure'],'image':")
    (r/f'out/campaign/native_editor_{name}.py').write_text(s)
p=r/'out/campaign/reclaim_editor_prior.ps1';(r/'out/campaign/reclaim_native_prior.ps1').write_text(p.read_text().replace('editor-prior-reclamation.json','native-editor-prior-reclamation.json'))
