from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
def change(path,old,new):
 p=r/path;s=p.read_text(encoding='utf-8');assert old in s,(path,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
change('source/interfaces/editor_content.cpp','for(const char* k:{"window_ms","max_points"})out.fields[k]=c.at(k).dump();out.fields["interpolation"]','for(const char* k:{"window_ms","max_points"})out.fields[k]=c.at(k).dump();\n        out.fields["interpolation"]')
change('tests/editor/content_properties_tests.cpp','const auto q=draft.begin("commit","properties:"+mode);','ui::EditorDraft submitted(authority,policy(),f.authored,"E1",f.resources());submitted.execute(edits);const auto q=submitted.begin("commit","properties:"+mode);')
change('tests/editor/content_properties_tests.cpp','rejects([&]{draft.execute(edits);});draft.reload(f.authored,"E1",f.resources());','rejects([&]{submitted.execute(edits);});draft.discard();')
change('CMakeLists.txt','source/interfaces/editor_snap.cpp)','source/interfaces/editor_snap.cpp source/interfaces/editor_content.cpp)')
change('CMakeLists.txt','source/interfaces/editor_form_linux.cpp)','source/interfaces/editor_form_linux.cpp source/interfaces/editor_content_form_linux.cpp)')
change('CMakeLists.txt','tests/editor/snap_tests.cpp)','tests/editor/snap_tests.cpp tests/editor/content_properties_tests.cpp)')
change('CMakeLists.txt','SNAP-HISTORY)','SNAP-HISTORY CONTENT-MAPPING CONTENT-HISTORY CONTENT-NUMBERS CONTENT-ATOMIC CONTENT-CHOICES CONTENT-POLICY)')
change('CMakeLists.txt','PRIVATE syspane_editor_form syspane_async_commands','PRIVATE syspane_editor_form syspane_network_publication syspane_async_commands')
change('CMakeLists.txt','        add_test(NAME native.EDITOR-SNAP','        add_test(NAME native.EDITOR-CONTENT-PROPERTIES COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_content_properties.py"\n            "$<TARGET_FILE:syspane_editor_window>" "$<TARGET_FILE:syspane_editor_exit_probe>" "${CMAKE_BINARY_DIR}/native-evidence")\n        set_tests_properties(native.EDITOR-CONTENT-PROPERTIES PROPERTIES TIMEOUT 600)\n        add_test(NAME native.EDITOR-SNAP')
change('tests/editor/editor_draft_tests.cpp','void run_snap(','void run_content_properties(const std::string&,const std::string&);\nvoid run_snap(')
change('tests/editor/editor_draft_tests.cpp','    Fixture f(root);const auto cases=','    if(name.substr(0,8)=="CONTENT-"){run_content_properties(name.substr(8),root);return;}\n    Fixture f(root);const auto cases=')
p=r/'build-support/components.json';d=json.loads(p.read_text());rows=next(v for v in d.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'target' in v[0])
for row in rows:
 if row['target']=='syspane_editor_draft':row['sources'].append('source/interfaces/editor_content.cpp');row['public_interfaces'].append('source/interfaces/editor_content.hpp')
 if row['target']=='syspane_editor_form':row['sources'].append('source/interfaces/editor_content_form_linux.cpp');row['private_interfaces'].append('source/interfaces/editor_content_form.hpp')
 if row['target']=='syspane_editor_tests':row['sources'].append('tests/editor/content_properties_tests.cpp')
 if row['target']=='syspane_editor_window':row['allowed_dependencies'].append('syspane_network_publication')
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
for file in ('step','flow'):
 s=(r/f'out/campaign/snap_{file}.py').read_text().replace('w-10-snap','w-10-content-properties').replace('snap_step.py','properties_step.py').replace('snap-execution','properties-execution')
 s=s.replace("'snap','test'","'snap','properties','test'").replace("'group','snap')","'group','snap','properties')")
 if file=='step':
  s=s.replace("command={'snap':","command={'properties':['ctest','--preset',profile,'-R','^native[.]EDITOR-CONTENT-PROPERTIES$','--output-on-failure'],'snap':")
  s=s.replace("'snap':'syspane_editor_window'","'properties':'syspane_editor_window','snap':'syspane_editor_window'").replace('^editor[.]SNAP-','^editor[.]CONTENT-')
 (r/f'out/campaign/properties_{file}.py').write_text(s,encoding='utf-8',newline='\n')
