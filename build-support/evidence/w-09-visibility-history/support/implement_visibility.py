from pathlib import Path
import json
r=Path.cwd()
def edit(n,old,new):
 p=r/n;s=p.read_text();assert old in s,n;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
p=r/'source/scene/bindings.cpp';s=p.read_text();start=s.index('struct Number ');end=s.index('struct Datum ',start);block=s[start:end]
for signature in ('Number number(', 'int compare_unsigned_real(', 'int compare('):block=block.replace(signature,'inline '+signature)
(r/'source/scene/value_compare.hpp').write_text('#pragma once\n#include "authored.hpp"\n#include "state.hpp"\n#include <cmath>\n\n// Shared exact numeric comparison; callers validate finite values first.\nnamespace syspane::scene::detail {\nusing configuration::Json;\n'+block+'}\n',encoding='utf-8',newline='\n')
s=s[:start]+'using detail::number;\nusing detail::compare;\n'+s[end:];s=s.replace('#include "bindings.hpp"','#include "bindings.hpp"\n#include "value_compare.hpp"');p.write_text(s,encoding='utf-8',newline='\n')
edit('source/configuration/authored.hpp','void validate_binding_document(const Json& value);','void validate_binding_document(const Json& value);\nvoid validate_visibility_document(const Json& value);')
edit('source/configuration/authored.cpp','layout_schema,binding_schema,','layout_schema,binding_schema,visibility_schema,')
edit('source/configuration/authored.cpp','void validate_binding_document(const Json& value){structural(value,"0.1.0/binding",262144);}','void validate_binding_document(const Json& value){structural(value,"0.1.0/binding",262144);}\nvoid validate_visibility_document(const Json& value){structural(value,"0.1.0/visibility",65536);}')
edit('CMakeLists.txt','scene-v0.4 layout binding command-v0.2','scene-v0.4 layout binding visibility command-v0.2')
edit('CMakeLists.txt','source/scene/bindings.cpp source/scene/chart_history.cpp','source/scene/bindings.cpp source/scene/visibility.cpp source/scene/chart_history.cpp')
edit('CMakeLists.txt','tests/scene/binding_tests.cpp tests/scene/chart_history_tests.cpp','tests/scene/binding_tests.cpp tests/scene/visibility_tests.cpp tests/scene/chart_history_tests.cpp')
edit('CMakeLists.txt','foreach(case PLOT-NUMERIC','foreach(case VISIBILITY-COMPARE VISIBILITY-STATES VISIBILITY-LIFECYCLE VISIBILITY-LIMITS VISIBILITY-GRAMMAR PLOT-NUMERIC')
edit('tests/scene/layout_tests.cpp','int binding_test(const std::string& name);','int binding_test(const std::string& name);\nint visibility_test(const std::string& name,const std::string& root);')
edit('tests/scene/layout_tests.cpp','if(name.rfind("BIND-",0)==0)return binding_test(name);','if(name.rfind("BIND-",0)==0)return binding_test(name);\n    if(name.rfind("VISIBILITY-",0)==0)return visibility_test(name,root);')
p=r/'build-support/components.json';v=json.loads(p.read_bytes())
for item in v['components']:
 if item['target']=='syspane_scene':
  item['sources'].append('source/scene/visibility.cpp');item['public_interfaces'].append('source/scene/visibility.hpp');item['private_interfaces'].append('source/scene/value_compare.hpp')
 if item['target']=='syspane_scene_tests':item['sources'].append('tests/scene/visibility_tests.cpp')
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
step=(r/'out/campaign/runtime_observation_step.py').read_text().replace('w-09-runtime-observation','w-09-visibility')
step=step.replace("'^(scene[.]IMAGE-|composition[.])'","'^(scene[.](VISIBILITY-|BIND-)|composition[.])'")
step=step.replace("artifact_name='syspane_editor_tests' if profile.startswith('linux') else 'syspane_editor_tests.exe'","artifact_name='syspane_scene_tests' if profile.startswith('linux') else 'syspane_scene_tests.exe'")
step=step.replace("'rendering':'syspane_scene_surface_tests'","'test':'syspane_scene_tests','rendering':'syspane_scene_surface_tests'")
step=step.replace("r/'spec/delivery/packages/w-09-visibility.md',r/'spec/delivery/packages/w-09-visibility.md'","r/'spec/delivery/packages/w-09-visibility.md'")
(r/'out/campaign/visibility_step.py').write_text(step,encoding='utf-8',newline='\n')
flow=(r/'out/campaign/runtime_observation_flow.py').read_text().replace('runtime-observation','visibility').replace('runtime_observation','visibility')
flow='\n'.join(line.rstrip() for line in flow.splitlines())+'\n'
(r/'out/campaign/visibility_flow.py').write_text(flow,encoding='utf-8',newline='\n')
print('Implemented bounded visibility projection through the existing scene/binding owners.')
