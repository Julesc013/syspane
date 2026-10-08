from pathlib import Path
import json
r=Path.cwd()
def edit(n,old,new):
 p=r/n;s=p.read_text(encoding='utf-8');assert old in s,(n,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('CMakeLists.txt','    add_executable(syspane_authored_tests', '''    add_executable(syspane_typography_tests tests/scene/typography_tests.cpp)
    target_link_libraries(syspane_typography_tests PRIVATE syspane_authored)
    foreach(case RESOLUTION INVALID RESOURCES)
        add_test(NAME "configuration.TYPOGRAPHY-${case}" COMMAND syspane_typography_tests "${case}" "${CMAKE_SOURCE_DIR}/tests/scene/typography-cases.json" "${CMAKE_SOURCE_DIR}/spec/fixtures/valid")
    endforeach()
    add_executable(syspane_authored_tests''')
edit('CMakeLists.txt','        set_tests_properties(native.TEXT-RASTER PROPERTIES TIMEOUT 90)','''        set_tests_properties(native.TEXT-RASTER PROPERTIES TIMEOUT 90)
        add_test(NAME native.THEME-TYPOGRAPHY COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/scene/native_typography.py"
            "$<TARGET_FILE:syspane_text_probe>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.THEME-TYPOGRAPHY PROPERTIES TIMEOUT 90)''')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());template=next(x for x in v['components'] if x['target']=='syspane_authored_tests').copy();template.update(id='typography-tests',target='syspane_typography_tests',source_owner='tests/scene/',sources=['tests/scene/typography_tests.cpp'],allowed_dependencies=['syspane_authored']);v['components'].append(template);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
edit('tests/scene/surface_tests.cpp','    test("VISIBILITY-GATE",','''    test("TYPOGRAPHY-GATE",[&]{Owner f(root);f.attach();f.receive();f.paint();auto theme=read(root,"theme-typography.json");theme["theme_id"]=f.cfg.resources->theme()["theme_id"];
        auto cfg=config(root,theme);cfg.capabilities.insert("theme.typography");f.surface->replace(cfg,3);check_empty(*f.surface,v::SurfaceCode::alternative,4);
        need(f.surface->status().reason=="surface.typography_unavailable","role composition must be admitted before new theme rendering");
        f.surface->policy(policy(8,false),5);check_empty(*f.surface,v::SurfaceCode::restricted,6);f.surface->policy(policy(9),7);check_empty(*f.surface,v::SurfaceCode::alternative,8);
        f.surface->replace(f.cfg,9);need(f.paint(10).widgets[0].text=="Receive\\nWaiting","legacy resume has no old payload");});
    test("VISIBILITY-GATE",''')
# Exact helper clones keep ordinary profile commands and evidence identities.
s=(r/'out/campaign/visibility_controls_step.py').read_text();s=s.replace('w-10-visibility-controls','w-09-typography');s=s.replace("'^native[.]EDITOR-VISIBILITY$'","'^native[.](THEME-TYPOGRAPHY|TEXT-RASTER|SCENE-SURFACE)$'");s=s.replace("'native':'syspane_editor_window'","'native':'SysPane.TextProbe'")
(r/'out/campaign/typography_step.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/visibility_controls_flow.py').read_text().replace('visibility-controls','typography').replace('visibility_controls_step','typography_step')
(r/'out/campaign/typography_flow.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_visibility_controls_duplicates.py').read_text().replace("('w-09-native-visibility',)","('w-10-visibility-controls',)").replace('visibility-controls-pruned-duplicates.json','typography-pruned-duplicates.json')
(r/'out/campaign/prune_typography_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_visibility_controls_attempt_duplicates.ps1').read_text().replace('w-09-native-visibility','w-10-visibility-controls').replace('visibility-controls-attempt-pruned-duplicates.json','typography-attempt-pruned-duplicates.json')
(r/'out/campaign/prune_typography_attempt_duplicates.ps1').write_text(s,encoding='utf-8',newline='\n')
(r/'out/campaign/typography-freeze-clarification.json').write_text(json.dumps({'scope':'Freeze sequence clarification','original_freeze':'w-09-typography/fixed-inputs.json','revised_freeze':'w-09-typography/fixed-inputs-v2.json','facts':['Original package/schema/literal cases froze before all production additions.','The standalone theme_font.hpp/.cpp files were written in the patch that added the refinement helper, before that helper executed.','The revision moves only C1 rejection from byte-based regex to Unicode semantic validation; fixed invalid-font expectations did not change.','The refinement preceded changes to existing production source, builds and test execution.']},indent=2)+'\n',encoding='utf-8')
print('Registered typography acceptance and prepared bounded profile/evidence runners.')
