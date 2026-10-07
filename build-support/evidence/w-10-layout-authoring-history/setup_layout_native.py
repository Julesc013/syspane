from pathlib import Path
r=Path(__file__).resolve().parents[2]
p=r/'tests/editor/editor_window.cpp';s=p.read_text().replace('properties=false;Json alternate_selection','properties=false,layout_mode=false;Json alternate_selection')
s=s.replace('content=true;large=', 'content=true;layout_mode=mode.substr(0,7)=="layout-";large=')
s=s.replace('behavior=large?mode.substr(6):','behavior=layout_mode?mode.substr(7):large?mode.substr(6):')
s=s.replace('root+(large?"/tests/configuration/large-command-cases.json"','root+(layout_mode?"/tests/editor/layout-authoring-cases.json":large?"/tests/configuration/large-command-cases.json"')
s=s.replace('        if(behavior=="retain-create")', '        if(behavior=="retain-layout"){canary=gtk_label_new("Retained layout canary Private layout role");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}\n        if(behavior=="retain-create")')
s=s.replace('            if(behavior=="wrong-group")', '            if(behavior=="wrong-layout"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"][0]["layout"]["base"]["x"]=71;body=changed.dump();}\n            if(behavior=="wrong-group")')
s=s.replace('        else if(value=="topology")', '        else if(value=="layout-narrow"||value=="layout-wide"){need(layout_mode,"layout laboratory control");auto t=topology();t.displays[0].bounds.width=t.displays[0].work.width=(value=="layout-narrow"?399:500)*64;form->topology(t,"D1");}\n        else if(value=="topology")')
p.write_text(s,encoding='utf-8',newline='\n')
p=r/'tests/editor/native_editor.py';s=p.read_text().replace('snap=False,properties=False):','snap=False,properties=False,layout=False):').replace('sum((large,arrange,group,snap,properties))','sum((large,arrange,group,snap,properties,layout))').replace('self.large=large;','self.layout=layout;self.large=large;').replace("ROOT/('tests/configuration/large-command-cases.json' if large", "ROOT/('tests/editor/layout-authoring-cases.json' if layout else 'tests/configuration/large-command-cases.json' if large").replace('("large-" if self.large', '("layout-" if self.layout else "large-" if self.large');p.write_text(s,encoding='utf-8',newline='\n')
p=r/'CMakeLists.txt';s=p.read_text().replace('        add_test(NAME native.EDITOR-OBSERVATION', '''        add_test(NAME native.EDITOR-LAYOUT COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_layout_authoring.py"
            "$<TARGET_FILE:syspane_editor_window>" "$<TARGET_FILE:syspane_editor_exit_probe>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.EDITOR-LAYOUT PROPERTIES TIMEOUT 600)
        add_test(NAME native.EDITOR-OBSERVATION''');p.write_text(s,encoding='utf-8',newline='\n')
