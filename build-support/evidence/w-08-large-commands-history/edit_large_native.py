from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
def edit(name,pairs):
    p=r/name;s=p.read_text(encoding='utf-8')
    for old,new in pairs:assert old in s,(name,old);s=s.replace(old,new)
    p.write_text(s,encoding='utf-8',newline='\n')
edit('source/configuration/session.cpp',[(
    'if (!c.selection.features.count("settings.preview")&&!c.selection.features.count("configuration.transactions")) throw Error("feature.unsupported");',
    'if (!c.selection.features.count("settings.preview")&&!c.selection.features.count("configuration.transactions")&&message.body.value("schema_version",Json())!="0.5.0") throw Error("feature.unsupported");')])
edit('tests/editor/editor_window.cpp',[
    ('bool content=false;','bool content=false,large=false;'),
    ('content=true;behavior=mode;','content=true;large=mode.substr(0,6)=="large-";behavior=large?mode.substr(6):mode;'),
    ('read(root+"/tests/editor/native-cases.json")','read(root+(large?"/tests/configuration/large-command-cases.json":"/tests/editor/native-cases.json"))'),
    ('{"schema_version","0.4.0"}','{"schema_version",large?"0.5.0":"0.4.0"}'),
    ('image_worker(),std::move(actions));','image_worker(),std::move(actions),large);'),
    ('p::parse(body)','c::parse_command(body)')])
edit('tests/configuration/native_settings.py',[
    ('def resource_index(directory):','def resource_index(directory,manifest_version="0.2.0"):'),
    ("manifest['version']=='0.2.0'","manifest['version']==manifest_version"),
    ("def check_resources(directory,theme='theme:native'):","def check_resources(directory,theme='theme:native',manifest_version='0.2.0'):"),
    ('generation,index=resource_index(directory)','generation,index=resource_index(directory,manifest_version)')])
edit('tests/editor/native_editor.py',[
    ('def __init__(self,exe,exit_exe,folder,mode):','def __init__(self,exe,exit_exe,folder,mode,large=False):'),
    ('        self.exe,self.exit_exe,self.folder,self.mode=exe,exit_exe,folder,mode',
     "        self.large=large;self.case_path=ROOT/('tests/configuration/large-command-cases.json' if large else 'tests/editor/native-cases.json')\n        self.cases=json.loads(self.case_path.read_text())\n        if large:self.cases['drag']['expected']=self.cases['moved_scene']\n        self.exe,self.exit_exe,self.folder,self.mode=exe,exit_exe,folder,mode"),
    ("fixture_sha256=sha(ROOT/'tests/editor/native-cases.json')","fixture_sha256=sha(self.case_path)"),
    ('mode or self.mode]','("large-" if self.large else "")+(mode or self.mode)]'),
    ("value=copy.deepcopy(CASES['authored'])","value=copy.deepcopy(self.cases['authored'])"),
    ('check_resources(self.directory)','check_resources(self.directory,manifest_version="0.3.0" if self.large else "0.2.0")'),
    ('    mode=h.mode;h.launch()','    CASES=h.cases\n    mode=h.mode;h.launch()'),
    ('    mode=h.mode[9:];','    CASES=h.cases\n    mode=h.mode[9:];'),
    ('def observe(exe,exit_exe,folder,mode):','def observe(exe,exit_exe,folder,mode,large=False):'),
    ('h=Harness(exe,exit_exe,folder,mode)','h=Harness(exe,exit_exe,folder,mode,large)')])
# Register the concrete test component in the existing graph.
p=r/'build-support/components.json';v=json.loads(p.read_bytes());v['components'].append({
    'id':'large-command-tests','target':'syspane_large_command_tests','type':'EXECUTABLE','source_owner':'tests/configuration/',
    'public_interfaces':[],'private_interfaces':[],'sources':['tests/configuration/large_command_tests.cpp'],
    'allowed_dependencies':['syspane_editor_draft','syspane_async_commands'],'target_requirements':['cxx17'],
    'roles':['development_test'],'installed_files':[],'profiles':['windows-x64-gcc15','linux-x64-gcc13','windows-x86-v141-xp']})
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
edit('CMakeLists.txt',[('list(APPEND component_targets syspane_editor_draft','list(APPEND component_targets syspane_large_command_tests syspane_editor_draft')])
