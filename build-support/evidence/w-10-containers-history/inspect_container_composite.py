from pathlib import Path
from collections import Counter
import hashlib,json,struct,zlib
p=Path(r'\\wsl.localhost\Ubuntu-24.04\home\ir4runner\.cache\syspane\campaign-229a498\linux-x64-gcc13\native-evidence\containers-a1ccf6e67130\unwrap')
def png(path):
 raw=path.read_bytes();offset=8;data=b''
 while offset<len(raw):
  n=struct.unpack('!I',raw[offset:offset+4])[0];kind=raw[offset+4:offset+8]
  if kind==b'IDAT':data+=raw[offset+8:offset+8+n]
  offset+=n+12
 pixels=zlib.decompress(data);assert all(pixels[y*2401]==0 for y in range(600));return b''.join(pixels[y*2401+1:(y+1)*2401] for y in range(600))
def crop(raw,x,y,w,h):return b''.join(raw[(yy*800+x)*3:(yy*800+x+w)*3] for yy in range(y,y+h))
a=png(p/'initial.png');f=png(p/'failure.png');first=crop(a,24,62,160,28);second=crop(a,24,142,160,28);actual=crop(f,4,42,160,28)
print('Reference hashes',hashlib.sha256(first).hexdigest(),hashlib.sha256(second).hexdigest());print('Report hashes',json.loads((p/'result.json').read_text())['baseline_pixel_sha256'])
print('Common pixels',Counter(tuple(second[i:i+3]) for i in range(0,len(second),3)).most_common(12));print('White pixels',sum(second[i:i+3]==b'\xff\xff\xff' for i in range(0,len(second),3)))
print('Lower matches',actual[160*20*3:]==first[160*20*3:]);print('Old position clear',set(crop(f,24,142,160,28))=={0})
multiply=lambda a,b:(a*b+127)//255
lookup={(0,0,0):{0}};bg=(16,41,72)
for coverage in range(256):
 rgb=tuple(coverage+multiply(c,255-coverage) for c in bg)
 lookup.setdefault(rgb,set()).add(coverage+multiply(204,255-coverage))
unknown=set();ambiguous=set();expected=bytearray()
for i in range(0,len(second),3):
 rgb=tuple(second[i:i+3]);alphas=lookup.get(rgb,set())
 if not alphas:unknown.add(rgb);continue
 if len(alphas)!=1:ambiguous.add(rgb);continue
 alpha=next(iter(alphas));expected.extend(rgb[c]+multiply(first[i+c],255-alpha) for c in range(3))
print('Unknown colors',len(unknown),'ambiguous alpha',len(ambiguous),'exact composite match',bytes(expected)==actual)
assert not unknown and not ambiguous and bytes(expected)==actual
record=dict(input_images={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (p/'initial.png',p/'failure.png')},original_oracle_sha256=hashlib.sha256(Path('tests/editor/native_containers.py').read_bytes()).hexdigest(),analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),pixels=160*28,bytes_compared=len(actual),unknown_colors=len(unknown),ambiguous_alpha=len(ambiguous),expected_sha256=hashlib.sha256(expected).hexdigest(),actual_sha256=hashlib.sha256(actual).hexdigest(),match=bytes(expected)==actual,correction='Replace the attempted sparse-opaque check (whose arbitrary count exceeded available opaque glyph samples) with a full exact premultiplied source-over composite derived from the two isolated baseline captions and pinned translucent theme. Every observed foreground color must resolve to one alpha; unavailable or ambiguous calibration fails. Require the old location to be black. No production, fixture, geometry, scene, timing or storage expectation changes.')
dest=Path('out/campaign/w-10-containers/composite-calibration.json');assert not dest.exists();dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
