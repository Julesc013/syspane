from pathlib import Path
import json,hashlib,zipfile
r=Path.cwd();p=r/'build-support/components.json';d=json.loads(p.read_bytes());assert not any(x['id']=='editor-refresh-probe' for x in d['components'])
d['components'].append(dict(id='editor-refresh-probe',target='syspane_editor_refresh_probe',type='MODULE_LIBRARY',source_owner='tests/editor/',public_interfaces=[],private_interfaces=[],sources=['tests/editor/refresh_probe_linux.cpp'],allowed_dependencies=['PkgConfig::GTK3','dl'],target_requirements=['cxx17'],roles=['development_test'],installed_files=[],profiles=['linux-x64-gcc13']))
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
names=['tests/editor/refresh-cases.json','tests/editor/native_refresh.py','tests/editor/refresh_probe_linux.cpp'];out=r/'out/campaign/focus-idle';archive=out/'fixed-regression.zip';record=out/'fixed-regression.json';assert not archive.exists() and not record.exists()
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for n in names:z.write(r/n,n)
record.write_text(json.dumps(dict(inputs={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in names},archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8',newline='\n')
