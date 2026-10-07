from pathlib import Path
r=Path.cwd()
def change(path,old,new):
 p=r/path;s=p.read_text();assert old in s,(path,old[:50]);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
change('tests/editor/editor_window.cpp','if(behavior=="retain-content"){','if(behavior=="retain-binding"){canary=gtk_label_new("Retained binding canary Private filter");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}\n        if(behavior=="retain-content"){')
change('tests/editor/editor_window.cpp','if(behavior=="wrong-content"){','if(behavior=="wrong-binding"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][2]["bindings"][0]["field"]="network.receive_bytes";body=changed.dump();}\n            if(behavior=="wrong-content"){')
change('CMakeLists.txt','        add_test(NAME native.EDITOR-CONTENT-PROPERTIES', '        add_test(NAME native.EDITOR-BINDING-AUTHORING COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_binding_authoring.py"\n            "$<TARGET_FILE:syspane_editor_window>" "$<TARGET_FILE:syspane_editor_exit_probe>" "${CMAKE_BINARY_DIR}/native-evidence")\n        set_tests_properties(native.EDITOR-BINDING-AUTHORING PROPERTIES TIMEOUT 600)\n        add_test(NAME native.EDITOR-CONTENT-PROPERTIES')
for path in ['out/campaign/binding_step.py','out/campaign/binding_flow.py']:
 change(path,"'properties','test'","'bindings','properties','test'") if path.endswith('step.py') else None
 change(path,"'snap','properties')","'snap','properties','bindings')")
 if path.endswith('step.py'):
  change(path,"command={'properties':", "command={'bindings':['ctest','--preset',profile,'-R','^native[.]EDITOR-BINDING-AUTHORING$','--output-on-failure'],'properties':")
  change(path,"artifact_name={'properties':", "artifact_name={'bindings':'syspane_editor_window','properties':")
# Share the existing, independently exercised combo interaction mechanics.
s=(r/'tests/editor/native_content_properties.py').read_text();start=s.index('def value(');end=s.index('def opened(')
helpers=s[start:end].replace("'content.'","'binding.'")
(r/'out/campaign/binding_native_helpers.txt').write_text(helpers)
