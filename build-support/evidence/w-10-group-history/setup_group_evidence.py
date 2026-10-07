from pathlib import Path
r=Path(__file__).resolve().parents[2];d=r/'out/campaign'
base='bd964bd465265a274dffe34b666994835cd3e643'
def write(name,s):(d/name).write_text(s,encoding='utf-8',newline='\n')
for name in ('archive','finish_arrange_checks'):
    old='archive_arrange.py' if name=='archive' else name+'.py'
    s=(d/old).read_text().replace('w-10-arrange','w-10-group').replace('62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1',base)
    if name=='archive':s=s.replace("('EDITOR-ARRANGE','LARGE", "('EDITOR-GROUP','EDITOR-ARRANGE','LARGE")
    write(old.replace('arrange','group'),s)
s=(d/'preserve_arrange.py').read_text().replace('w-10-arrange','w-10-group').replace('62ca793c31fc7a1ac70a7b2f2f93b837bedc8cd1',base)
start=s.index('helpers=');end=s.index('\nfor p in ',start)
s=s[:start]+"helpers=['prepare_group.py','group_step.py','group_flow.py','document_group.py','archive_group.py','preserve_group.py','finish_group_checks.py','setup_group_evidence.py','finish_group.py','stage_group.py']"+s[end:]
s=s.replace('arrange-execution-', 'group-execution-').replace("('fixed-inputs.json','fixed-inputs.zip')", "('fixed-inputs.json','fixed-inputs.zip','overlap-input.json','overlap-input.zip')")
s=s.replace("latest('linux-x64-gcc13','arrange')", "latest('linux-x64-gcc13','group')")
s=s.replace("(n=='tests/editor/native_arrange.py' and v['action']!='arrange')", "(n=='tests/editor/native_group.py' and v['action']!='group')")
s=s.replace("for action in ('arrange','native','large'):","for action in ('group','arrange','native','large'):")
s=s.replace("families={'EDITOR-ARRANGE'", "families={'EDITOR-GROUP':('syspane_editor_window','tests/editor/native_group.py',11),'EDITOR-ARRANGE'")
s=s.replace("    if family=='EDITOR-ARRANGE':", "    if family=='EDITOR-GROUP':\n        assert v['fixture_sha256']==sha(r/'tests/editor/group-cases.json') and v['harness_sha256']==sha(r/'tests/editor/native_editor.py') and v['overlap_fixture_sha256']==sha(r/'tests/editor/group-overlap-cases.json')\n    if family=='EDITOR-ARRANGE':")
s=s.replace('==94','==101').replace('94 affected','101 affected').replace('independent native arrange, editor','independent native group, arrange, editor')
s=s.replace("archive=ref(history/'fixed-inputs.zip'))", "archive=ref(history/'fixed-inputs.zip'),overlap_record=ref(history/'overlap-input.json'),overlap_archive=ref(history/'overlap-input.zip'))")
write('preserve_group.py',s)
s=(d/'stage_arrange.py').read_text().replace('w-10-arrange','w-10-group').replace('arrange-handoff.json','group-handoff.json').replace('arrange-staging-paths','group-staging-paths')
s=s.replace("(n=='tests/editor/native_arrange.py' and action!='arrange')", "(n=='tests/editor/native_group.py' and action!='group')")
s=s.replace("('EDITOR-ARRANGE','LARGE-COMMANDS','EDITOR-FORM')", "('EDITOR-GROUP','EDITOR-ARRANGE','LARGE-COMMANDS','EDITOR-FORM')")
s=s.replace("else 'tests/editor/arrange-cases.json'", "else 'tests/editor/group-cases.json' if family=='EDITOR-GROUP' else 'tests/editor/arrange-cases.json'")
s=s.replace("check('tests/editor/native_arrange.py'", "check('tests/editor/native_group.py' if family=='EDITOR-GROUP' else 'tests/editor/native_arrange.py'")
s=s.replace("if family=='EDITOR-ARRANGE':check", "if family in ('EDITOR-GROUP','EDITOR-ARRANGE'):check")
s=s.replace("'frozen-preview','wrong-commit'", "'frozen-preview','wrong-group','wrong-commit'")
s=s.replace("native=json.loads(content(index['native_index']['path']));refs(native)", """overlap=json.loads(content(original['overlap_record']['path']))
with zipfile.ZipFile(io.BytesIO(content(original['overlap_archive']['path']))) as z:
    for n,digest in overlap['inputs'].items():assert hashlib.sha256(z.read(n)).hexdigest()==digest;check(n,digest)
native=json.loads(content(index['native_index']['path']));refs(native)""")
s=s.replace("                assert detail['executable_sha256']", "                if family=='EDITOR-GROUP':check('tests/editor/group-overlap-cases.json',detail['overlap_fixture_sha256'])\n                assert detail['executable_sha256']")
s=s.replace('native arrangement, exact', 'native grouping, exact')
write('stage_group.py',s)
print('Prepared archive and staged-identity helpers.')
