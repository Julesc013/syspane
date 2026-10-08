from pathlib import Path
import json,copy
r=Path.cwd()
def edit(name,old,new):
 p=r/name;s=p.read_text();assert old in s,(name,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('build-support/generate_authored_schemas.py',"'theme-v0.2')","'theme-v0.2','resource-selection-v0.2')")
edit('source/configuration/authored.cpp','theme_schema,theme_v0_2_schema}','theme_schema,theme_v0_2_schema,resource_selection_v0_2_schema}')
edit('source/configuration/authored.cpp','kind=="preset"||kind=="theme","content.kind"','kind=="preset"||kind=="theme"||kind=="resource-selection","content.kind"')
edit('source/configuration/authored.cpp','std::string(typography?"0.2.0/":"0.1.0/")','std::string((typography||kind=="resource-selection")?"0.2.0/":"0.1.0/")')
edit('source/configuration/authored.cpp','kind=="content-catalog"?16384:','kind=="resource-selection"?4096:kind=="content-catalog"?16384:')
edit('CMakeLists.txt','preset theme theme-v0.2)','preset theme theme-v0.2 resource-selection-v0.2)')
edit('CMakeLists.txt','source/configuration/authored_theme.cpp','source/configuration/authored_theme.cpp source/configuration/theme_resources.cpp')
edit('CMakeLists.txt','    add_executable(syspane_theme_authoring_tests','    add_executable(syspane_theme_override_tests tests/configuration/theme_override_tests.cpp)\n    target_link_libraries(syspane_theme_override_tests PRIVATE syspane_settings_draft)\n    foreach(case RESOLVE REPLACE INVALID CAPACITY)\n        add_test(NAME "configuration.THEME-OVERRIDE-${case}" COMMAND syspane_theme_override_tests "${case}" "${CMAKE_SOURCE_DIR}")\n    endforeach()\n    add_executable(syspane_theme_authoring_tests')
edit('CMakeLists.txt','syspane_theme_authoring_tests)','syspane_theme_authoring_tests syspane_theme_override_tests)')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());c=next(x for x in v['components'] if x['target']=='syspane_authored');c['sources'].append('source/configuration/theme_resources.cpp');c['public_interfaces'].append('source/configuration/theme_resources.hpp')
c=copy.deepcopy(next(x for x in v['components'] if x['target']=='syspane_theme_authoring_tests'));c.update(id='theme-override-tests',target='syspane_theme_override_tests',source_owner='tests/configuration/',sources=['tests/configuration/theme_override_tests.cpp'],allowed_dependencies=['syspane_settings_draft']);v['components'].append(c);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for old,new in [('theme_authoring_step.py','theme_overrides_step.py'),('theme_authoring_flow.py','theme_overrides_flow.py'),('archive_theme_authoring.py','archive_theme_overrides.py')]:
 s=(r/'out/campaign'/old).read_text().replace('w-10-theme-authoring','w-10-theme-overrides').replace('theme_authoring_step','theme_overrides_step').replace('theme-authoring-execution','theme-overrides-execution')
 if new=='theme_overrides_step.py':
  s=s.replace("'native':['ctest','--preset',profile,'-R','^native[.](ROLE-COMPOSITION|THEME-TYPOGRAPHY)$'","'native':['ctest','--preset',profile,'-R','^native[.](RESOURCE-GENERATIONS|CONTENT-COMMANDS)$'")
  s=s.replace("'test':'syspane_theme_authoring_tests'","'test':'syspane_theme_override_tests'").replace("artifact_name='syspane_editor_tests.exe'","artifact_name='syspane_theme_override_tests.exe'").replace("'native':'SysPane.TextProbe'","'native':'SysPane.CommandProbe'")
 (r/'out/campaign'/new).write_text(s,encoding='utf-8',newline='\n')
for old,new in [('prune_theme_authoring_duplicates.py','prune_theme_overrides_duplicates.py'),('prune_theme_authoring_attempt_duplicates.ps1','prune_theme_overrides_attempt_duplicates.ps1')]:
 s=(r/'out/campaign'/old).read_text().replace('w-09-role-composition','w-10-theme-authoring').replace('theme-authoring-pruned-duplicates','theme-overrides-pruned-duplicates').replace('theme-authoring-attempt-pruned-duplicates','theme-overrides-attempt-pruned-duplicates');(r/'out/campaign'/new).write_text(s,encoding='utf-8',newline='\n')
