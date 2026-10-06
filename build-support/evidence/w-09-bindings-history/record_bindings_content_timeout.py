from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,zipfile
r=Path('/mnt/d/Projects/SysPane/syspane');native=Path('/home/ir4runner/.cache/syspane/campaign-229a498/linux-x64-gcc13/native-evidence/content-commands-814898fc96ea')
assert os.geteuid()==1000 and native.resolve()==native and json.loads((native/'result.json').read_text())['outcome']=='fail'
files=sorted(p for p in native.rglob('*') if p.is_file());assert not any(p.is_symlink() for p in native.rglob('*'));assert sum(p.stat().st_size for p in files)<4*1024*1024
zpath=r/'out/campaign/bindings-content-timeout.zip'
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(native).as_posix())
store=native/'PREPARE-HANG/store';pointer=json.loads((store/'current.json').read_text());selected=json.loads((store/pointer['generation']/'scene.json').read_text())['revision']
v={'recorded_at':datetime.now(timezone.utc).isoformat(),'native_report':str(native/'result.json'),'archive_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),
 'files':{p.relative_to(native).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'selected_revision_after_oracle_cleanup':selected,
 'facts':['PREPARE-HANG original worker hit the existing 5000 ms transaction deadline and was reaped before replacement.',
 'The replacement accepted a new command and the supervisor recorded armed; the oracle socket timed out at its unchanged 1 second receive limit.',
 'Oracle cleanup killed the supervisor, and held pidfds confirmed child exits. The selected generation remained revision 40 with a separate prepared candidate.',
 'The earlier full run passed this oracle using the same command/store executable identities. This failed run does not establish a product deadline overrun or a cause.'],
 'decision':'Preserve the complete synthetic failure tree and retry the unchanged oracle in isolation. No deadline, assertion, product implementation or acceptance condition changed.'}
(r/'out/campaign/bindings-content-timeout-review.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Preserved',len(files),'failure-tree files; selected revision',selected)
