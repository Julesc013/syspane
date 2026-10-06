from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
r=Path('/mnt/d/Projects/SysPane/syspane');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
paths=['/usr/bin/gi-compile-repository','/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0','/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0']
xp=r/'build-support/x11-input-runtime.json';x=json.loads(xp.read_text());oldx=json.loads(xp.read_text())
packages=['libglib2.0-dev','libglib2.0-0t64','libc6','libc6-dev',*x['packages']]
versions=dict(line.split('\t') for line in subprocess.check_output(['dpkg-query','-W',*packages],text=True).splitlines())
files={p:sha(p) for p in paths+list(x['files'])}
log=[l for l in Path('/var/log/dpkg.log').read_text().splitlines() if ' upgrade ' in l and '2026-10-07 06:3' in l]
record={'observed_at':datetime.now(timezone.utc).isoformat(),'versions':versions,'files':files,'package_log_upgrades':log,'previous_input_runtime':oldx,'scope':'Observed external package update. No installation or privilege change by this campaign.'}
write(r/'out/campaign/bindings-runtime-revision.json',record)
p=r/'build-support/check_diagnostic_dependencies.py';s=p.read_text();assert "'libglib2.0-dev': '2.80.0-6ubuntu3.8'" in s
s=s.replace("'libglib2.0-dev': '2.80.0-6ubuntu3.8'","'libglib2.0-dev': '2.80.0-6ubuntu3.9'");p.write_text(s,encoding='utf-8',newline='\n')
p=r/'build-support/check_gjs_clock_dependencies.py';s=p.read_text()
old=['2400af6ecb249f0a75367550e3e4de0ebb396bd25805a216b4c84101bfdff6b9','99bf0727e0ca4faf12ab09b753b3d03294562c29c559b970c4dad435f9ec2bc6','42467d0dbcc0a6c9e0a31f05a5944095504ce98f093c3fe0825f0a1533fa8207']
for path,digest in zip(paths,old):assert digest in s;s=s.replace(digest,files[path])
p.write_text(s,encoding='utf-8',newline='\n')
for k in x['packages']:
 actual=versions[k]
 if actual!=x['packages'][k]:assert k in ('gir1.2-glib-2.0:amd64','libglib2.0-bin') and actual=='2.80.0-6ubuntu3.9';x['packages'][k]=actual
for k in x['files']:x['files'][k]=files[k]
write(xp,x)
p=r/'build-support/targets/linux-x64-gcc13.json';v=json.loads(p.read_text());v['abi']['runtime_version']=v['abi']['runtime_version'].replace('glibc 2.39-0ubuntu8.8','glibc 2.39-0ubuntu8.9')
for d in v['dependencies']:
 if d['id']=='gi-compile-repository':d['sha256']=files[paths[0]];d['version']='2.80.0-6ubuntu3.9'
write(p,v)
p=r/'build-support/targets/README.md';s=p.read_text().replace('2.80.0-6ubuntu3.8','2.80.0-6ubuntu3.9');p.write_text(s,encoding='utf-8',newline='\n')
print('Recorded external runtime identities and revised GLib pins:', versions)
