from pathlib import Path
import struct,zlib,json,hashlib,zipfile
r=Path.cwd();p=r/'tests/scene/image-cases/large-encoded.png';base=(p.parent/'rgba.png').read_bytes();payload=b'public\0'+b'a'*1048576;chunk=b'tEXt'+payload
p.write_bytes(base[:33]+struct.pack('>I',len(payload))+chunk+struct.pack('>I',zlib.crc32(chunk))+base[33:])
d=r/'out/campaign/scene-images-original';v={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()}
with zipfile.ZipFile(d/'large-original.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(p,p.relative_to(r).as_posix())
(d/'large-original.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Public encoded PNG fixture',p.stat().st_size,'bytes; pixels unchanged from rgba.png')
