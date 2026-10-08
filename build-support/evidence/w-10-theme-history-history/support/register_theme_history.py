from pathlib import Path
import json
r=Path.cwd();out=r/'out/campaign'
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
p=r/'CMakeLists.txt';s=p.read_text();needle='    add_executable(syspane_theme_command_tests'
start=s.index(needle);s=s[:start]+'''    add_executable(syspane_theme_history_tests tests/editor/theme_history_tests.cpp)
    target_link_libraries(syspane_theme_history_tests PRIVATE syspane_editor_draft)
    foreach(case SHARING HISTORY COMMANDS RESULTS POLICY LIMITS)
        add_test(NAME "editor.THEME-HISTORY-${case}" COMMAND syspane_theme_history_tests "${case}" "${CMAKE_SOURCE_DIR}")
    endforeach()
'''+s[start:]
needle='    if(TARGET syspane_configuration_probe)\n        add_test(NAME native.THEME-COMMANDS';s=s.replace(needle,'''    if(TARGET syspane_configuration_probe)
        add_executable(syspane_theme_history_probe tests/editor/native_theme_history_probe.cpp)
        target_link_libraries(syspane_theme_history_probe PRIVATE syspane_editor_draft syspane_generation_store)
        add_test(NAME native.THEME-HISTORY COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_theme_history.py"
            "$<TARGET_FILE:syspane_theme_history_probe>" "$<TARGET_FILE:syspane_configuration_probe>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.THEME-HISTORY PROPERTIES TIMEOUT 90)
        add_test(NAME native.THEME-COMMANDS''')
s=s.replace('list(APPEND component_targets syspane_large_command_tests','list(APPEND component_targets syspane_theme_history_tests syspane_theme_history_probe syspane_large_command_tests');write(p,s)
p=r/'build-support/components.json';v=json.loads(p.read_bytes());rows=v['components']
for name,sources,deps,profiles in [('theme-history-tests',['tests/editor/theme_history_tests.cpp'],['syspane_editor_draft'],['windows-x64-gcc15','linux-x64-gcc13','windows-x86-v141-xp']),('theme-history-probe',['tests/editor/native_theme_history_probe.cpp'],['syspane_editor_draft','syspane_generation_store'],['linux-x64-gcc13'])]:
 rows.append(dict(id=name,target='syspane_'+name.replace('-','_'),type='EXECUTABLE',source_owner='tests/editor/',public_interfaces=[],private_interfaces=['tests/editor/theme_history_fixture.hpp'],sources=sources,allowed_dependencies=deps,target_requirements=['cxx17'],roles=['development_test'],installed_files=[],profiles=profiles))
write(p,json.dumps(v,indent=2)+'\n')
for name in ('step','flow'):
 s=(out/('theme_commands_'+name+'.py')).read_text().replace('w-08-theme-commands','w-10-theme-history').replace('theme_commands','theme_history').replace('theme-commands','theme-history').replace('syspane_theme_command_tests','syspane_theme_history_tests')
 if name=='step':s=s.replace('THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC|VISIBILITY-ADMISSION','THEME-HISTORY|THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM')
 write(out/('theme_history_'+name+'.py'),s)
for name in ('archive','prune'):
 file='archive_theme_commands.py' if name=='archive' else 'prune_theme_commands_duplicates.py'
 s=(out/file).read_text().replace('w-08-theme-commands','w-10-theme-history').replace('theme-commands','theme-history')
 if name=='archive':s=s.replace("('THEME-COMMANDS',","('THEME-HISTORY','THEME-COMMANDS',")
 else:s=s.replace("('w-10-theme-overrides',)","('w-08-theme-commands',)")
 write(out/('archive_theme_history.py' if name=='archive' else 'prune_theme_history_duplicates.py'),s)
s=(out/'prune_theme_commands_attempt_duplicates.ps1').read_text().replace('w-10-theme-overrides','w-08-theme-commands').replace('theme-commands-attempt-pruned','theme-history-attempt-pruned');write(out/'prune_theme_history_attempt_duplicates.ps1',s)
print('Registered theme history portable and native tests, bounded execution/evidence helpers.')
