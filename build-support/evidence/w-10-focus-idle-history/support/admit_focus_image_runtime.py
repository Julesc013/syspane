from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,subprocess,sys
r=Path('/mnt/d/Projects/SysPane/syspane');out=r/'out/campaign/focus-idle';sys.path.insert(0,str(r/'build-support'))
from check_image_runtime import identify
p=r/'build-support/image-runtime.json';before=p.read_bytes();candidate=json.loads(before);actual=identify();assert actual==json.loads((out/'image-runtime-actual.json').read_bytes())
candidate['packages']=candidate['packages'].replace('librsvg2-2:amd64\t2.58.0+dfsg-1build1\n','librsvg2-2:amd64\t2.58.0+dfsg-1ubuntu0.1\n').replace('librsvg2-common:amd64\t2.58.0+dfsg-1build1\n','librsvg2-common:amd64\t2.58.0+dfsg-1ubuntu0.1\n')
changes={'/lib/x86_64-linux-gnu/libfreetype.so.6':'992dac80abe3a3854f3eb2668da4207c029664ceca5f122ddb46e2a8169e9499','/lib/x86_64-linux-gnu/librsvg-2.so.2':'81b5db4db32c47697c7b6d7432e541544342c97bc88173df9f18bb0679279c51','/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.so':'2e0ec411b0891ed7a7848bc52ad939fb4be9552eaf76ec427790f092a57990b3'}
candidate['files'].update(changes);assert candidate==actual
check=subprocess.run(['dpkg','-V','librsvg2-2','librsvg2-common'],capture_output=True,text=True);assert check.returncode==0 and not check.stdout and not check.stderr
changelog=Path('/usr/share/doc/librsvg2-2/changelog.Debian.gz').read_bytes();assert '2.58.0+dfsg-1ubuntu0.1' in gzip.decompress(changelog).decode().splitlines()[0]
assert not (out/'image-runtime-before.json').exists();(out/'image-runtime-before.json').write_bytes(before);(out/'librsvg-changelog.Debian.gz').write_bytes(changelog)
p.write_text(json.dumps(actual,indent=2)+'\n',encoding='utf-8',newline='\n')
(out/'image-runtime-admission.json').write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),outcome='admitted_for_verification',before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),changed_files=changes,dpkg_verify=dict(exit=check.returncode,stdout=check.stdout,stderr=check.stderr),changelog_sha256=hashlib.sha256(changelog).hexdigest(),notice='https://ubuntu.com/security/notices/USN-8891-1',decision='Record the already installed vendor librsvg security revision and transitive FreeType identity. No packages were installed or altered. Kernel, headers, other image dependencies and all acceptance fixtures remain unchanged. Revalidate native decode/containment and rendering before qualification.'),indent=2)+'\n')
print('Recorded exact installed image dependency revisions; acceptance unchanged.')
