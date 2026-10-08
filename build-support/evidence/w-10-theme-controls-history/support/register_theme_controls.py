from pathlib import Path
import json
r=Path.cwd();p=r/'CMakeLists.txt';s=p.read_text();assert 'syspane_theme_controls_tests' not in s
s=s.replace('source/interfaces/editor_visibility_form_linux.cpp)', 'source/interfaces/editor_visibility_form_linux.cpp source/interfaces/editor_theme_form_linux.cpp)')
anchor='    add_executable(syspane_theme_history_tests'
s=s.replace(anchor,'''    add_executable(syspane_theme_controls_tests tests/editor/theme_controls_tests.cpp)
    target_link_libraries(syspane_theme_controls_tests PRIVATE syspane_editor_draft)
    foreach(case INPUT ROLE-MAP HISTORY POLICY)
        add_test(NAME "editor.THEME-CONTROLS-${case}" COMMAND syspane_theme_controls_tests "${case}" "${CMAKE_SOURCE_DIR}")
    endforeach()
'''+anchor)
anchor='        add_executable(syspane_theme_history_probe'
s=s.replace(anchor,'''        add_test(NAME native.EDITOR-FONTS COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_theme_controls.py"
            "$<TARGET_FILE:syspane_editor_window>" "$<TARGET_FILE:syspane_editor_exit_probe>" "$<TARGET_FILE:syspane_text_probe>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.EDITOR-FONTS PROPERTIES TIMEOUT 1000)
'''+anchor)
s=s.replace('list(APPEND component_targets syspane_theme_history_tests','list(APPEND component_targets syspane_theme_controls_tests syspane_theme_history_tests');p.write_text(s,encoding='utf-8',newline='\n')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());items=v['components'];form=next(x for x in items if x['target']=='syspane_editor_form');form['sources'].append('source/interfaces/editor_theme_form_linux.cpp');form['private_interfaces'].append('source/interfaces/editor_theme_form.hpp')
item=json.loads(json.dumps(next(x for x in items if x['target']=='syspane_theme_history_tests')));item['id']='theme-controls-tests';item['target']='syspane_theme_controls_tests';item['sources']=['tests/editor/theme_controls_tests.cpp'];items.append(item);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'tests/editor/editor_window.cpp';s=p.read_text();s=s.replace('#include "async_commands.hpp"','#include "async_commands.hpp"\n#include "authored_theme.hpp"')
s=s.replace('visibility_mode=false;', 'visibility_mode=false,theme_mode=false;')
s=s.replace('return visibility_mode?std::set', 'return theme_mode?std::set<std::string>{"scene.content","scene.edit-locks","scene.visibility","configuration.edit-locks","configuration.visibility","theme.typography","configuration.theme-overrides"}:visibility_mode?std::set')
s=s.replace('        auto fault_catalog=', '        if(theme_mode){base.after_prepare=[this]{prepare(original);};return base;}\n        auto fault_catalog=')
s=s.replace('content=true;visibility_mode=', 'content=true;theme_mode=mode.substr(0,6)=="fonts-";visibility_mode=')
s=s.replace('large=visibility_mode||', 'large=theme_mode||visibility_mode||')
s=s.replace('behavior=visibility_mode?', 'behavior=theme_mode?mode.substr(6):visibility_mode?')
s=s.replace('root+(visibility_mode?', 'root+(theme_mode?"/tests/editor/theme-controls-cases.json":visibility_mode?')
s=s.replace('(properties||visibility_mode)', '(properties||visibility_mode||theme_mode)')
s=s.replace('if(properties||visibility_mode){', 'if(properties||visibility_mode||theme_mode){')
s=s.replace('        if(behavior=="retain-visibility")', '        if(behavior=="retain-font"){canary=gtk_label_new("Retained font canary Private font family");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}\n        if(behavior=="retain-visibility")')
anchor='            if(behavior=="wrong-visibility")'
s=s.replace(anchor,'''            if(behavior=="wrong-font"){auto changed=c::parse_command(body);changed["theme_edit"]["font"]["weight"]=900;auto source=store->load().resources;auto proposed=source->theme();proposed["schema_version"]="0.2.0";proposed["font"]=changed["theme_edit"]["font"];
                if(changed["theme_edit"]["font_roles"].is_null())proposed.erase("font_roles");else proposed["font_roles"]=changed["theme_edit"]["font_roles"];
                auto artifact=c::author_theme(*source,proposed,current,capabilities());need(artifact.has_value(),"wrong font witness");changed["content"]["theme_override"]={{"package",artifact->package_pin},{"theme",artifact->theme_pin}};changed["operations"][0]["scene"]["theme_id"]=artifact->theme["theme_id"];body=changed.dump();}
'''+anchor)
anchor='        else if(value=="topology")'
s=s.replace(anchor,'''        else if(value=="disconnect"){form->disconnected();}
        else if(value=="policy"){current=policy(current.revision+1);owner->policy(current);form->policy(current);}
        else if(value=="deny-font"||value=="capability-loss"){current=policy(current.revision+1);current.denied_capabilities.insert(value=="deny-font"?"theme.edit":"theme.typography");owner->policy(current);form->policy(current);}
'''+anchor)
p.write_text(s,encoding='utf-8',newline='\n')
# Reuse established snapshot, budget and execution harnesses with this package identity.
for old,new in [('theme_history_step.py','theme_controls_step.py'),('theme_history_flow.py','theme_controls_flow.py')]:
 s=(r/'out/campaign'/old).read_text().replace('theme_history','theme_controls').replace('theme-history','theme-controls')
 if new.endswith('step.py'):
  s=s.replace("THEME-HISTORY|THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM", "EDITOR-FONTS|EDITOR-VISIBILITY|EDITOR-CONTENT-PROPERTIES|THEME-HISTORY|THEME-COMMANDS|ROLE-COMPOSITION|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM")
  s=s.replace("artifact_name='syspane_theme_controls_tests.exe'", "artifact_name='syspane_theme_controls_tests.exe'")
 (r/'out/campaign'/new).write_text(s,encoding='utf-8',newline='\n')
print('Registered native font controls and four portable families.')
