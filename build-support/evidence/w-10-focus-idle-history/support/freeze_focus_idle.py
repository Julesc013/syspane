from pathlib import Path
import hashlib,json,subprocess,zipfile
r=Path.cwd();out=r/'out/campaign/focus-idle';record=out/'fixed-inputs.json';archive=out/'fixed-inputs.zip';assert not record.exists() and not archive.exists()
names=['spec/delivery/packages/w-10-focus-idle.md','source/interfaces/editor_form_linux.cpp','tests/editor/native_editor.py','tests/editor/native_observation.py','tests/configuration/native_large_commands.py','tests/configuration/large-command-cases.json','out/campaign/editor_idle_probe.c','out/campaign/run_editor_idle_probe.py']
inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in names}
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(r/n,n)
record.write_text(json.dumps(dict(source_ref=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs=inputs,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n')
