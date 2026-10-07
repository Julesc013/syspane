from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=(r/'out/campaign/archive_native_editor.py').read_text().replace('w-10-native-editor','w-08-large-commands')
s=s.replace("'EDITOR-FORM','SETTINGS-FORM'","'LARGE-COMMANDS','EDITOR-FORM','SETTINGS-FORM'")
s=s.replace("names=sorted(v['files']) if 'files' in v else sorted(q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if q.is_file() or q.is_symlink())", "names=sorted(q.relative_to(p.parent).as_posix() for q in p.parent.rglob('*') if (q.is_file() or q.is_symlink()) and q.name!='xauthority')")
(r/'out/campaign/archive_large_commands.py').write_text(s,encoding='utf-8',newline='\n')
s=(r/'out/campaign/finish_native_editor_checks.py').read_text().replace('w-10-native-editor','w-08-large-commands').replace('c225a32823682b904e624d295b694d233accb773','c7c2f32489caec1c1cba143ec3c48cef707a86e5')
(r/'out/campaign/finish_large_checks.py').write_text(s,encoding='utf-8',newline='\n')
