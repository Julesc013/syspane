from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,subprocess,sys
r=Path('/mnt/d/Projects/SysPane/syspane');out=r/'out/campaign/focus-idle';sys.path.insert(0,str(r/'build-support'))
from check_text_runtime import identify
p=r/'build-support/text-runtime.json';before=p.read_bytes();old=json.loads(before);actual=identify();delta=json.loads((out/'text-runtime-difference.json').read_bytes());assert actual==delta['actual']
candidate=json.loads(before);candidate['packages']=candidate['packages'].replace('libfreetype6:amd64\t2.13.2+dfsg-1ubuntu0.1\n','libfreetype6:amd64\t2.13.2+dfsg-1ubuntu0.2\n')
candidate['files']['/usr/lib/x86_64-linux-gnu/libfreetype.so.6']='992dac80abe3a3854f3eb2668da4207c029664ceca5f122ddb46e2a8169e9499';assert candidate==actual
check=subprocess.run(['dpkg','-V','libfreetype6'],capture_output=True,text=True);assert check.returncode==0 and not check.stdout and not check.stderr
changelog=Path('/usr/share/doc/libfreetype6/changelog.Debian.gz').read_bytes();assert '2.13.2+dfsg-1ubuntu0.2' in gzip.decompress(changelog).decode().splitlines()[0]
assert not (out/'text-runtime-before.json').exists();(out/'text-runtime-before.json').write_bytes(before);(out/'freetype-changelog.Debian.gz').write_bytes(changelog)
p.write_text(json.dumps(actual,indent=2)+'\n',encoding='utf-8',newline='\n')
(out/'text-runtime-admission.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),outcome='admitted_for_verification',before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dpkg_verify=dict(exit=check.returncode,stdout=check.stdout,stderr=check.stderr),changelog_sha256=hashlib.sha256(changelog).hexdigest(),vendor='https://packages.ubuntu.com/noble/libfreetype6',notice='https://ubuntu.com/security/notices/USN-8881-1',decision='Record the already installed vendor security revision in the development profile. No packages were installed or altered. Fonts, fontconfig and all other recorded package/library identities are unchanged. Rendering and text acceptance fixtures remain fixed; revalidate them before qualification.'),indent=2)+'\n')
print('Recorded the exact installed FreeType security revision; acceptance unchanged.')
