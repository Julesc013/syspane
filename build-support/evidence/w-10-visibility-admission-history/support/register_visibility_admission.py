from pathlib import Path
import json
r=Path.cwd()
def edit(n,a,b):
 p=r/n;s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
edit('CMakeLists.txt','tests/editor/edit_lock_tests.cpp)','tests/editor/edit_lock_tests.cpp tests/editor/visibility_admission_tests.cpp)')
edit('CMakeLists.txt','LOCK-DURABLE)','LOCK-DURABLE VIS-SCHEMAS VIS-DRAFT VIS-GUARDS VIS-PRESERVE VIS-ATOMIC VIS-POLICY VIS-NEGOTIATE VIS-DURABLE)')
edit('tests/editor/editor_draft_tests.cpp','void run_edit_lock(const std::string&,const std::string&);','void run_edit_lock(const std::string&,const std::string&);\nvoid run_visibility_admission(const std::string&,const std::string&);')
edit('tests/editor/editor_draft_tests.cpp','if(name.substr(0,5)=="LOCK-")','if(name.substr(0,4)=="VIS-"){run_visibility_admission(name.substr(4),root);return;}\n    if(name.substr(0,5)=="LOCK-")')
p=r/'build-support/components.json';v=json.loads(p.read_bytes());next(x for x in v['components'] if x['target']=='syspane_editor_tests')['sources'].append('tests/editor/visibility_admission_tests.cpp');p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
edit('CMakeLists.txt','add_test(NAME "native.SCENE-CONTENT"','add_test(NAME native.VISIBILITY-ADMISSION COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/configuration/native_visibility_admission.py"\n            "$<TARGET_FILE:SysPane.ConfigProbe>" "${CMAKE_BINARY_DIR}/native-evidence")\n        set_tests_properties(native.VISIBILITY-ADMISSION PROPERTIES TIMEOUT 90)\n        add_test(NAME "native.SCENE-CONTENT"')
# Keep each attempt/source snapshot distinct from the preceding evaluator checkpoint.
for source,dest in [('visibility_step.py','visibility_admission_step.py'),('visibility_flow.py','visibility_admission_flow.py')]:
 s=(r/'out/campaign'/source).read_text().replace('w-09-visibility','w-10-visibility-admission').replace('visibility_step.py','visibility_admission_step.py').replace('visibility-execution-','visibility-admission-execution-')
 s=s.replace('^(scene[.](VISIBILITY-|BIND-)|composition[.])','^(editor[.](VIS-|LOCK-)|configuration[.]|composition[.])').replace('^native[.]EDITOR-LOCKS$','^native[.]VISIBILITY-ADMISSION$')
 s=s.replace('syspane_scene_tests','syspane_editor_tests')
 if dest.endswith('step.py'):s=s.replace("'locks':'syspane_editor_window'","'locks':'SysPane.ConfigProbe'")
 (r/'out/campaign'/dest).write_text(s,encoding='utf-8',newline='\n')
print('Registered portable and native visibility admission checks.')
