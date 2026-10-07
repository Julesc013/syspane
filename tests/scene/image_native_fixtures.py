"""Generate public synthetic codec inputs; expectations do not call production."""
from pathlib import Path
import json,struct,zlib
r=Path(__file__).with_name('image-cases');r.mkdir(exist_ok=True);cases=[]
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
def png(w,h,raw,kind=6,bits=8,extra=b''):
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,bits,kind,0,0,0))+extra+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
def add(name,media,data,expected=None,error=None,size=None):
    (r/name).write_bytes(data);v=dict(name=name,media=media)
    if error:v['error']=error
    else:v.update(size=size,rgba=expected)
    cases.append(v)
raw=bytes([0,255,0,0,255,0,255,0,128,0,0,0,255,0,255,255,255,255])
# Two filter-0 RGBA rows: red, half-green / transparent blue, white.
base=png(2,2,raw);rgba=[255,0,0,255,0,128,0,128,0,0,0,0,255,255,255,255]
add('rgba.png','image/png',base,rgba,size=[2,2])
add('gray.png','image/png',png(2,1,bytes([0,0,137]),0),[0,0,0,255,137,137,137,255],size=[2,1])
add('palette.png','image/png',png(2,1,bytes([0,0,1]),3,extra=chunk(b'PLTE',bytes([255,0,0,0,255,0]))+chunk(b'tRNS',bytes([255,128]))),rgba[:8],size=[2,1])
add('rgb.png','image/png',png(2,1,bytes([0,255,0,0,0,255,0]),2),[255,0,0,255,0,255,0,255],size=[2,1])
add('gray-alpha.png','image/png',png(2,1,bytes([0,255,128,0,0]),4),[128,128,128,128,0,0,0,0],size=[2,1])
add('gray16.png','image/png',png(2,1,bytes([0,0,0,255,255]),0,16),[0,0,0,255,255,255,255,255],size=[2,1])
add('metadata.png','image/png',png(2,2,raw,extra=chunk(b'zTXt',b'bomb\0\0'+zlib.compress(b'x'*4194304))),rgba,size=[2,2])
add('animated.png','image/png',png(2,2,raw,extra=chunk(b'acTL',struct.pack('>II',2,0))),error='image.animation')
add('oversize.png','image/png',png(4097,1,bytes([0])),error='image.capacity')
add('over-area.png','image/png',png(4096,1025,bytes([0])),error='image.capacity')
(r/'maximum.png').write_bytes(png(2048,2048,bytes(2048*(2048*4+1))))
cases.append(dict(name='maximum.png',media='image/png',size=[2048,2048],solid=[0,0,0,0]))
add('truncated.png','image/png',base[:-1],error='image.format')
bad=bytearray(base);bad[-1]^=1;add('crc.png','image/png',bytes(bad),error='image.format')
add('trailing.png','image/png',base+b'x',error='image.format')
add('wrong-media.png','image/jpeg',base,error='image.format')
prefix='<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2">'
suffix='</svg>'
solid='<rect width="2" height="2" fill="red"/>'
red=[255,0,0,255]*4
add('red.svg','image/svg+xml',(prefix+solid+suffix).encode(),red,size=[2,2])
add('style.svg','image/svg+xml',(prefix+'<style>.hot { fill: red; }</style><rect class="hot" width="2" height="2"/>'+suffix).encode(),red,size=[2,2])
add('fragment.svg','image/svg+xml',(prefix+'<defs><rect id="r" width="2" height="2" fill="red"/></defs><use href="#r"/>'+suffix).encode(),red,size=[2,2])
add('local-css.svg','image/svg+xml',(prefix+'<defs><linearGradient id="g"><stop offset="0" stop-color="red"/><stop offset="1" stop-color="red"/></linearGradient></defs><rect width="2" height="2" style="fill:u\\72l(\\23 g)"/>'+suffix).encode(),red,size=[2,2])
for name,body,error in [
 ('external','<image href="file:///etc/passwd"/>','image.reference'),
 ('network','<image href="https://example.invalid/image.png"/>','image.reference'),
 ('embedded','<image href="data:image/png;base64,AA=="/>','image.reference'),
 ('entity','<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>','image.svg'),
 ('animation','<animate attributeName="x" dur="1s"/>','image.animation'),
 ('script','<script>ignored()</script>','image.svg'),
 ('event','<rect onclick="ignored()"/>','image.svg'),
 ('missing','<use href="#missing"/>','image.reference'),
 ('css','<style>.x {fill:u\\72l("https://example.invalid/x");}</style>','image.reference'),
 ('css-import','<style>@\\69mport "https://example.invalid/x";</style>','image.reference'),
 ('css-comment','<style>.x{fill:u/**/rl(file:///etc/passwd)}</style>','image.reference'),
 ('base','<g xml:base="file:///etc/"/>','image.reference'),
 ('include','<xi:include xmlns:xi="http://www.w3.org/2001/XInclude" href="file:///etc/passwd"/>','image.svg'),
 ('depth','<g>'*65+'</g>'*65,'image.capacity'),
 ('duplicate','<g id="same"/><g id="same"/>','image.reference')]:
    data=(body+prefix+solid+suffix if name=='entity' else prefix+body+suffix).encode();add(name+'.svg','image/svg+xml',data,error=error)
add('oversize.svg','image/svg+xml',prefix.replace('width="2"','width="4097"').encode()+suffix.encode(),error='image.capacity')
add('truncated.svg','image/svg+xml',(prefix+solid).encode(),error='image.svg')
add('two-roots.svg','image/svg+xml',((prefix+solid+suffix)*2).encode(),error='image.svg')
gray=(r/'gray.jpg').read_bytes();add('gray.jpg','image/jpeg',gray,[137,137,137,255]*128,size=[16,8])
pattern=(r/'pattern.jpg').read_bytes();progressive=(r/'progressive.jpg').read_bytes()
matrix=[[(v,v,v,255) for v in (32+(x//8)*48+(y//8)*16 for x in range(32))] for y in range(16)]
for name,data in [('pattern.jpg',pattern),('progressive.jpg',progressive)]:add(name,'image/jpeg',data,[v for row in matrix for pixel in row for v in pixel],size=[32,16])
for n in range(1,9):
    tiff=b'II*\0'+struct.pack('<I',8)+struct.pack('<H',1)+struct.pack('<HHIHH',274,3,1,n,0)+b'\0'*4
    app=b'Exif\0\0'+tiff;data=pattern[:2]+b'\xff\xe1'+struct.pack('>H',len(app)+2)+app+pattern[2:]
    rows=matrix
    if n==2:rows=[list(reversed(row)) for row in matrix]
    if n==3:rows=[list(reversed(row)) for row in reversed(matrix)]
    if n==4:rows=list(reversed(matrix))
    if n==5:rows=list(zip(*matrix))
    if n==6:rows=list(zip(*reversed(matrix)))
    if n==7:rows=list(reversed(list(zip(*reversed(matrix)))))
    if n==8:rows=list(reversed(list(zip(*matrix))))
    add('orientation-'+str(n)+'.jpg','image/jpeg',data,[v for row in rows for pixel in row for v in pixel],size=[len(rows[0]),len(rows)])
bad=tiff[:18]+struct.pack('<H',9)+tiff[20:];app=b'Exif\0\0'+bad
add('bad-orientation.jpg','image/jpeg',pattern[:2]+b'\xff\xe1'+struct.pack('>H',len(app)+2)+app+pattern[2:],error='image.format')
app=b'Exif\0\0'+tiff;segment=b'\xff\xe1'+struct.pack('>H',len(app)+2)+app
add('duplicate-exif.jpg','image/jpeg',pattern[:2]+segment*2+pattern[2:],error='image.format')
add('truncated.jpg','image/jpeg',pattern[:-1],error='image.format')
(r/'native.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8',newline='\n')
print(len(cases),'fixed native cases')
