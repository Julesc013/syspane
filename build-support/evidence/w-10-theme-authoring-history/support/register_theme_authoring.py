from pathlib import Path
import json,copy
r=Path.cwd()
def edit(name,old,new):
 p=r/name;s=p.read_text();assert old in s,(name,old);p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
edit('tests/editor/theme_authoring_tests.cpp','#include <iostream>','#include <algorithm>\n#include <iostream>')
edit('CMakeLists.txt','source/configuration/theme_font.cpp','source/configuration/theme_font.cpp source/configuration/authored_theme.cpp')
edit('CMakeLists.txt','source/interfaces/editor_content.cpp','source/interfaces/editor_content.cpp source/interfaces/editor_theme.cpp')
edit('CMakeLists.txt','    add_executable(syspane_typography_tests','    add_executable(syspane_theme_authoring_tests tests/editor/theme_authoring_tests.cpp)\n    target_link_libraries(syspane_theme_authoring_tests PRIVATE syspane_editor_draft)\n    foreach(case INPUT NOOP INVALID ARTIFACT)\n        add_test(NAME "editor.THEME-${case}" COMMAND syspane_theme_authoring_tests "${case}" "${CMAKE_SOURCE_DIR}")\n    endforeach()\n    add_executable(syspane_typography_tests')
edit('CMakeLists.txt','syspane_typography_tests syspane_role_composition_probe)','syspane_typography_tests syspane_role_composition_probe syspane_theme_authoring_tests)')
p=r/'build-support/components.json';v=json.loads(p.read_bytes())
for target,source,header in [('syspane_authored','source/configuration/authored_theme.cpp','source/configuration/authored_theme.hpp'),('syspane_editor_draft','source/interfaces/editor_theme.cpp','source/interfaces/editor_theme.hpp')]:
 c=next(x for x in v['components'] if x['target']==target);c['sources'].append(source);c['public_interfaces'].append(header)
c=copy.deepcopy(next(x for x in v['components'] if x['target']=='syspane_typography_tests'));c.update(id='theme-authoring-tests',target='syspane_theme_authoring_tests',source_owner='tests/editor/',sources=['tests/editor/theme_authoring_tests.cpp'],allowed_dependencies=['syspane_editor_draft']);v['components'].append(c);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
for old,new in [('roles_step.py','theme_authoring_step.py'),('roles_flow.py','theme_authoring_flow.py'),('archive_roles.py','archive_theme_authoring.py')]:
 s=(r/'out/campaign'/old).read_text().replace('w-09-role-composition','w-10-theme-authoring').replace('roles_step','theme_authoring_step').replace('roles-execution','theme-authoring-execution')
 if new=='theme_authoring_step.py':s=s.replace('ROLE-COMPOSITION|THEME-TYPOGRAPHY|TEXT-RASTER|SCENE-SURFACE|SCENE-VISIBILITY|VISIBILITY-PIXELS','ROLE-COMPOSITION|THEME-TYPOGRAPHY');s=s.replace("'test':'syspane_editor_tests'","'test':'syspane_theme_authoring_tests'")
 (r/'out/campaign'/new).write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_roles_duplicates.py').read_text().replace("('w-09-typography',)","('w-09-role-composition',)").replace('roles-pruned-duplicates.json','theme-authoring-pruned-duplicates.json');(r/'out/campaign/prune_theme_authoring_duplicates.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/prune_roles_attempt_duplicates.ps1').read_text().replace('w-09-typography','w-09-role-composition').replace('roles-attempt-pruned-duplicates.json','theme-authoring-attempt-pruned-duplicates.json');(r/'out/campaign/prune_theme_authoring_attempt_duplicates.ps1').write_text(s,encoding='utf-8',newline='\n')
print(json.loads((r/'tests/editor/theme-authoring-cases.json').read_bytes())['source']['font'])
