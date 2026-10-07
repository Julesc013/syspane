from pathlib import Path
import json
r=Path.cwd();p=r/'CMakeLists.txt';s=p.read_text()
anchor='    add_library(syspane_native_image STATIC'
i=s.index(anchor)
s=s[:i]+'''    add_library(syspane_scene_inspector STATIC source/interfaces/scene_inspector_model.cpp source/interfaces/scene_inspector_linux.cpp)
    target_include_directories(syspane_scene_inspector PUBLIC "${CMAKE_SOURCE_DIR}/source/interfaces")
    target_link_libraries(syspane_scene_inspector PUBLIC syspane_scene_surface PRIVATE PkgConfig::GTK3)
'''+s[i:]
anchor='        add_executable(syspane_scene_surface_tests';i=s.index(anchor)
s=s[:i]+'''        add_executable(syspane_scene_inspector_tests tests/scene/inspector_tests.cpp)
        target_link_libraries(syspane_scene_inspector_tests PRIVATE syspane_scene_inspector syspane_network_publication PkgConfig::GTK3)
        add_test(NAME native.SCENE-INSPECTOR-MODEL COMMAND syspane_scene_inspector_tests "${CMAKE_SOURCE_DIR}/spec/fixtures/valid")
        set_tests_properties(native.SCENE-INSPECTOR-MODEL PROPERTIES TIMEOUT 60)
        add_test(NAME native.SCENE-INSPECTOR COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/scene/native_inspector.py"
            "$<TARGET_FILE:syspane_scene_inspector_tests>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.SCENE-INSPECTOR PROPERTIES TIMEOUT 180)
'''+s[i:];p.write_text(s,encoding='utf-8',newline='\n')
p=r/'build-support/components.json';v=json.loads(p.read_text());base=next(x for x in v['components'] if x['id']=='scene-surface');row=dict(base)
row.update(id='scene-inspector',target='syspane_scene_inspector',source_owner='source/interfaces/',public_interfaces=['source/interfaces/scene_inspector.hpp'],private_interfaces=['source/interfaces/scene_inspector_model.hpp'],sources=['source/interfaces/scene_inspector_model.cpp','source/interfaces/scene_inspector_linux.cpp'],allowed_dependencies=['syspane_scene_surface','PkgConfig::GTK3']);v['components'].append(row)
base=next(x for x in v['components'] if x['target']=='syspane_scene_surface_tests');row=dict(base)
row.update(id='scene-inspector-tests',target='syspane_scene_inspector_tests',sources=['tests/scene/inspector_tests.cpp'],allowed_dependencies=['syspane_scene_inspector','syspane_network_publication','PkgConfig::GTK3']);v['components'].append(row)
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'out/campaign/scene_images_step.py';s=p.read_text().replace('w-09-scene-images','w-11-scene-inspector').replace('native[.](SCENE-IMAGE|IMAGE-JOB)$','native[.]SCENE-INSPECTOR-MODEL$').replace('^native[.]IMAGE-ERASURE$','^native[.]SCENE-INSPECTOR$')
(r/'out/campaign/inspector_step.py').write_text(s,encoding='utf-8',newline='\n')
p=r/'out/campaign/scene_images_flow.py';s=p.read_text().replace('scene-images-execution-','scene-inspector-execution-').replace('scene_images_step.py','inspector_step.py')
(r/'out/campaign/inspector_flow.py').write_text(s,encoding='utf-8',newline='\n')
print('Declared native inspector component, tests and bounded execution helpers.')
