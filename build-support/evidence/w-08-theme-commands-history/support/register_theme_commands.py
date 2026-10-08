from pathlib import Path
import json,copy
r=Path.cwd();out=r/'out/campaign'
def edit(n,a,b):
 p=r/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
edit('CMakeLists.txt','    add_executable(syspane_theme_override_tests','    add_executable(syspane_theme_command_tests tests/configuration/theme_command_tests.cpp)\n    target_link_libraries(syspane_theme_command_tests PRIVATE syspane_async_commands syspane_settings_draft)\n    foreach(case SCHEMA TRANSACTION GUARDS ASYNC NEGOTIATE)\n        add_test(NAME "configuration.THEME-COMMAND-${case}" COMMAND syspane_theme_command_tests "${case}" "${CMAKE_SOURCE_DIR}")\n    endforeach()\n    add_executable(syspane_theme_override_tests')
edit('CMakeLists.txt','    if(TARGET syspane_configuration_probe)','    if(TARGET syspane_configuration_probe)\n        add_test(NAME native.THEME-COMMANDS COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/configuration/native_theme_commands.py"\n            "$<TARGET_FILE:syspane_command_probe>" "$<TARGET_FILE:syspane_configuration_probe>" "${CMAKE_BINARY_DIR}/native-evidence")\n        set_tests_properties(native.THEME-COMMANDS PROPERTIES TIMEOUT 180)')
edit('CMakeLists.txt','syspane_theme_override_tests)','syspane_theme_override_tests syspane_theme_command_tests)')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());c=copy.deepcopy(next(x for x in v['components'] if x['target']=='syspane_theme_override_tests'));c.update(id='theme-command-tests',target='syspane_theme_command_tests',sources=['tests/configuration/theme_command_tests.cpp'],allowed_dependencies=['syspane_async_commands','syspane_settings_draft']);v['components'].append(c);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for old,new in [('theme_overrides_step.py','theme_commands_step.py'),('theme_overrides_flow.py','theme_commands_flow.py'),('archive_theme_overrides.py','archive_theme_commands.py')]:
 s=(out/old).read_text().replace('w-10-theme-overrides','w-08-theme-commands').replace('theme_overrides_step','theme_commands_step').replace('theme-overrides-execution','theme-commands-execution')
 if new=='theme_commands_step.py':
  s=s.replace('^native[.](RESOURCE-GENERATIONS|CONTENT-COMMANDS)$','^native[.](THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC|VISIBILITY-ADMISSION)$').replace('syspane_theme_override_tests','syspane_theme_command_tests')
 if new=='archive_theme_commands.py':s=s.replace("('ROLE-COMPOSITION'","('THEME-COMMANDS','ROLE-COMPOSITION'")
 (out/new).write_text(s,encoding='utf-8',newline='\n')
for old,new in [('prune_theme_overrides_duplicates.py','prune_theme_commands_duplicates.py'),('prune_theme_overrides_attempt_duplicates.ps1','prune_theme_commands_attempt_duplicates.ps1')]:
 s=(out/old).read_text().replace('w-10-theme-authoring','w-10-theme-overrides').replace('theme-overrides-pruned-duplicates','theme-commands-pruned-duplicates').replace('theme-overrides-attempt-pruned-duplicates','theme-commands-attempt-pruned-duplicates');(out/new).write_text(s,encoding='utf-8',newline='\n')
print('Registered shared command and independent native tests.')
