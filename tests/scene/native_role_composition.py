"""Independent literal-font and pixel oracle; never derives expected roles from output."""
from datetime import datetime, timezone
from pathlib import Path
import copy, hashlib, json, subprocess, sys, uuid
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'source/build'))
from check_text_runtime import verify
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    probe, text_probe, evidence = map(Path, sys.argv[1:4])
    folder = evidence / ('roles-' + uuid.uuid4().hex[:12]); folder.mkdir(parents=True)
    fixed_path = ROOT / 'tests/scene/role-composition-cases.json'
    fixed = json.loads(fixed_path.read_bytes())
    record = dict(family='ROLE-COMPOSITION', started_at=datetime.now(timezone.utc).isoformat(),
                  executable_sha256=sha(probe), text_executable_sha256=sha(text_probe),
                  oracle_sha256=sha(Path(__file__)), fixed_inputs_sha256=sha(fixed_path), cases=[], outcome='fail')
    count = 0
    def execute(exe, args, wire=None):
        nonlocal count
        count += 1; stem = folder / str(count)
        p = subprocess.run([str(exe), *map(str,args)], input=wire, capture_output=True, timeout=20)
        stem.with_suffix('.stdout').write_bytes(p.stdout); stem.with_suffix('.stderr').write_bytes(p.stderr)
        if wire: stem.with_suffix('.input.json').write_bytes(wire)
        assert p.returncode == 0, (args, p.returncode, p.stderr)
        return json.loads(p.stdout)
    def text(block, scale, contrast, all_body=False):
        theme = copy.deepcopy(fixed['theme']); theme.pop('font_roles')
        theme['font'] = fixed['expected_fonts']['body' if all_body else block['role']]
        theme['tokens']['background'] = '#00000000'
        if contrast != 'authored': theme['tokens']['foreground'] = '#000000ff' if contrast=='light' else '#ffffffff'
        path = folder / ('text-' + str(count+1) + '.rgba')
        result = execute(text_probe, [path], json.dumps(dict(text=block['text'],theme=theme,numerator=scale[0],denominator=scale[1])).encode())
        assert 'error' not in result and result['missing_glyphs']==0
        return result['width'], result['height'], path.read_bytes()
    def bg(contrast):
        if contrast != 'authored': return bytes([255,255,255,255] if contrast=='light' else [0,0,0,255])
        c=bytes.fromhex(fixed['theme']['tokens']['background'][1:]); return bytes([(x*c[3]+127)//255 for x in c[:3]]+[c[3]])
    def over(dst, width, part, x, y):
        w,h,src=part
        for row in range(h):
            for col in range(w):
                a=(row*w+col)*4; b=((y+row)*width+x+col)*4; inv=255-src[a+3]
                for channel in range(4): dst[b+channel]=src[a+channel]+(dst[b+channel]*inv+127)//255
    def stack(blocks, scale, contrast, all_body=False, background=True):
        parts=[text(b,scale,contrast,all_body) for b in blocks]
        gap=(4*scale[0]+scale[1]-1)//scale[1]
        width=max(p[0] for p in parts); height=sum(p[1] for p in parts)+gap*(len(parts)-1)
        data=bytearray((bg(contrast) if background else bytes(4))*width*height); y=0
        for p in parts: over(data,width,p,0,y); y+=p[1]+gap
        return width,height,data
    def crop(frame,pixels,x,y,w,h):
        return b''.join(pixels[((y+r)*frame['width']+x)*4:((y+r)*frame['width']+x+w)*4] for r in range(h))
    def check(case,scale=(1,1),contrast='authored'):
        path=folder/('scene-'+str(count+1)+'.rgba')
        result=execute(probe,[ROOT/'spec/fixtures/valid',fixed_path,case,path,scale[0],scale[1],contrast])
        data=path.read_bytes(); assert len(data)==result['width']*result['height']*4
        if case=='empty':
            assert not any(data) and result['blocks']==[] and not result['presented']; return
        if case=='table':
            f=fixed['table']; assert result['cells']==f['cells']
            title=text(f['title'],scale,contrast); summary=text(f['summary'],scale,contrast)
            headers=[text(b,scale,contrast) for b in f['headers']]
            cells=[[stack(c,scale,contrast,background=False) for c in row] for row in f['cells']]
            widths=[max(headers[c][0],*(row[c][0] for row in cells)) for c in range(len(headers))]
            gap=(4*scale[0]+scale[1]-1)//scale[1]; horizontal=(8*scale[0]+scale[1]-1)//scale[1]
            y=title[1]+gap; placements=[(title,0,0),(summary,0,y)];y+=summary[1]+gap
            x=0
            for col,h in enumerate(headers): placements.append((h,x,y));x+=widths[col]+horizontal
            y+=max(h[1] for h in headers); rectangles=[]
            for row in cells:
                y+=gap;x=0;rect=[]
                for col,c in enumerate(row): placements.append((c,x,y));rect.append([x,y,c[0],c[1]]);x+=widths[col]+horizontal
                rectangles.append(rect);y+=max(c[1] for c in row)
            width=max(title[0],summary[0],sum(widths)+horizontal*(len(widths)-1))
            expected=bytearray(bg(contrast)*width*y)
            for part,x,y0 in placements: over(expected,width,part,x,y0)
            assert result['rectangles']==rectangles
            assert crop(result,data,0,0,width,y)==expected
        else:
            blocks=fixed['cases'][case]; assert result['blocks']==blocks,(case,result['blocks'],blocks)
            expected=stack(blocks,scale,contrast)
            assert crop(result,data,0,0,expected[0],expected[1])==expected[2],case
            if case in ('chart','chartgap'):
                assert result['plot_y']==expected[1]+(4*scale[0]+scale[1]-1)//scale[1]
            if case in ('value','failed','newline','hidden','hiddenstale'):
                wrong=stack(blocks,scale,contrast,all_body=True)
                assert wrong!=expected,('all-body fault not detected',case)
        record['cases'].append(dict(case=case,scale=scale,contrast=contrast,outcome='pass'))
    try:
        verify();record['runtime_identity_sha256']=sha(ROOT/'source/build/text-runtime.json')
        for case in fixed['cases']: check(case)
        check('table')
        for contrast in ('light','dark'): check('value',contrast=contrast);check('table',contrast=contrast)
        check('value',(3,2));check('table',(3,2))
        result=execute(probe,[ROOT/'spec/fixtures/valid',fixed_path,'contracts',folder/'unused.rgba',1,1,'authored'])
        assert result=={'admission':True,'erasure':True,'limits':True,'replacement':True,'group':True}
        record['cases'].append(dict(case='admission-erasure-limits-replacement-group',outcome='pass'));record['outcome']='pass'
    except BaseException as e: record['error']=repr(e);raise
    finally:
        record['finished_at']=datetime.now(timezone.utc).isoformat();record['files']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        (folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(folder/'result.json',record['outcome'],flush=True)
if __name__=='__main__':main()
