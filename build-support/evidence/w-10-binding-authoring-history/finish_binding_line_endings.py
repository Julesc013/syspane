from pathlib import Path
r=Path.cwd();p=r/'out/campaign/preserve_bindings.py';s=p.read_text()
old="    for n in delta:assert n.endswith('.md') or"
new="""    if 'tests/editor/native_binding_authoring.py' in delta:
        archive=next(a['source_archive']['path'] for a in attempts if a['source_archive']['sha256']==v['source_archive_sha256'])
        with zipfile.ZipFile(r/archive) as z:assert z.read('tests/editor/native_binding_authoring.py').replace(b'\\r\\n',b'\\n')==(r/'tests/editor/native_binding_authoring.py').read_bytes()
    for n in delta:assert (n=='tests/editor/native_binding_authoring.py' and v['action']!='bindings') or n.endswith('.md') or"""
assert old in s;s=s.replace(old,new).replace('Only documentation, the settings observer','Only documentation, verified CRLF-to-LF normalization of the binding observer for other checks, the settings observer');s=s.replace("helpers=['correct_binding_metadata.py'","helpers=['finish_binding_line_endings.py','binding-staging-failure.json','correct_binding_metadata.py'");p.write_text(s,encoding='utf-8',newline='\n')
p=r/'out/campaign/stage_bindings.py';s=p.read_text();old="    for n in delta:assert n.endswith('.md') or";new="""    if 'tests/editor/native_binding_authoring.py' in delta:
        with zipfile.ZipFile(io.BytesIO(content(Path(row['path']).with_name('source-inputs.zip').as_posix()))) as z:assert z.read('tests/editor/native_binding_authoring.py').replace(b'\\r\\n',b'\\n')==content('tests/editor/native_binding_authoring.py')
    for n in delta:assert (n=='tests/editor/native_binding_authoring.py' and action!='bindings') or n.endswith('.md') or""";assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8',newline='\n')
p=r/'spec/delivery/binding-authoring-handoff.md';s=p.read_text();needle='## Next admitted boundary';assert needle in s;s=s.replace(needle,'The staged identity check also detected CRLF-to-LF normalization in the new binding\nobserver. Its worktree was normalized and its 15-case native matrix rerun against\nthe final bytes. Original attempts and that staging failure remain recorded.\n\n'+needle);p.write_text(s,encoding='utf-8',newline='\n')
