"""Independent owned-X11 pixels and AT-SPI observations; public synthetic input only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import select
import signal
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/desktop'),str(ROOT/'tests/fault'),str(ROOT/'tests/scene'),str(ROOT/'build-support')]
from native_diagnostic import launch_xvfb
from native_oracle import Display
from check_text_runtime import verify
from check_surface_runtime import verify as verify_surface
from native_text import THEME

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def observe(exe,text_probe,folder,mode,table=False):
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi,GLib
    Atspi.set_timeout(500,1000)
    verify();verify_surface();folder.mkdir()
    report=dict(mode=mode,outcome='fail',observations=[],executable_sha256=sha(exe),text_probe_sha256=sha(text_probe),
                oracle_sha256=sha(Path(__file__)),runtime_identity_sha256=sha(ROOT/'build-support/text-runtime.json'))
    report['surface_runtime_sha256']=sha(ROOT/'build-support/surface-runtime.json')
    err=(folder/'stderr').open('wb')
    proc=subprocess.Popen([str(exe),str(ROOT/'spec/fixtures/valid'),'WINDOW',('table-' if table else '')+mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
    display=None;sequence=0;last_ack=None
    def read():
        assert select.select([proc.stdout],[],[],5)[0], 'native reply timeout'
        line=proc.stdout.readline();assert line, 'native exited before reply'
        return json.loads(line)
    def command(cmd):
        nonlocal last_ack
        proc.stdin.write((cmd+'\n').encode());proc.stdin.flush();assert read()=={'ack':cmd}
        last_ack=time.monotonic()
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def find_accessible():
        desktop=Atspi.get_desktop(0)
        if desktop is None:return None
        pending=[]
        desktop.clear_cache()
        for index in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(index)
            if app.get_process_id()==proc.pid:pending.append((app,0))
        for _ in range(64):
            if not pending:return None
            item,depth=pending.pop();item.clear_cache()
            if item.get_description()=='syspane.scene.surface':
                assert item.get_process_id()==proc.pid
                return item
            if depth<8:
                for i in range(item.get_child_count()):pending.append((item.get_child_at_index(i),depth+1))
        raise AssertionError('accessibility traversal bound')
    def raster(text):
        target=folder/('expected-'+hashlib.sha256(text.encode()).hexdigest()[:12]+'.rgba')
        theme=dict(THEME,theme_id='theme:native')
        p=subprocess.run([str(text_probe),str(target)],input=json.dumps(dict(text=text,theme=theme)).encode(),capture_output=True,timeout=5)
        assert p.returncode==0,p.stderr
        m=json.loads(p.stdout);assert 'error' not in m,m
        return m,target.read_bytes()
    def expected(text):
        m,raw=raster(text);image=bytearray(800*600*3)
        for y in range(m['height']):
            for x in range(m['width']):
                a=(y*m['width']+x)*4;b=(y*800+x)*3;image[b:b+3]=raw[a:a+3]
        return bytes(image)
    def view(number=None,retained=False):
        status='Retained' if retained else 'Current'
        if not table:
            text='Receive\nWaiting' if number is None else f'Receive\n{number} byte\n{status}'
            return expected(text),text+('' if number is None else '\nsupport=supported;')
        title='Interfaces';summary='Waiting' if number is None else 'Showing 2 of 2 rows'
        labels=['network.receive_bytes','network.transmit_bytes'];values=[[number,7],[124,8]]
        title_r,summary_r=raster(title),raster(summary);parts=[(0,0,title_r),(0,title_r[0]['height']+4,summary_r)]
        name=title+'\n'+summary
        if number is not None:
            headers=[raster(s) for s in labels];cells=[[raster(f'{v} byte\n{status}') for v in row] for row in values]
            widths=[max(headers[c][0]['width'],*(row[c][0]['width'] for row in cells)) for c in range(2)]
            y=title_r[0]['height']+4+summary_r[0]['height']+4
            for c,h in enumerate(headers):parts.append((0 if c==0 else widths[0]+8,y,h))
            y+=max(h[0]['height'] for h in headers)+4
            for row,entries in enumerate(cells):
                name+=f'\nRow P1/E1/network:interface:{row+1}'
                for c,cell in enumerate(entries):
                    parts.append((0 if c==0 else widths[0]+8,y,cell))
                    name+=f'\n{labels[c]}: {values[row][c]} byte\n{status}\nsupport=supported; acquisition=success; presence=present; freshness=current; origin=observed; lease={"retained" if retained else "active"}; age=dynamic ns'
                y+=max(cell[0]['height'] for cell in entries)+4
        image=bytearray(800*600*3)
        for x,y,(m,raw) in parts:
            assert x+m['width']<=800 and y+m['height']<=600
            for dy in range(m['height']):
                for dx in range(m['width']):
                    a=(dy*m['width']+dx)*4;b=((y+dy)*800+x+dx)*3;image[b:b+3]=raw[a:a+3]
        return bytes(image),name
    def check(name,pixels,prefix,timeout=.2,negative=None):
        nonlocal sequence
        started=last_ack if last_ack is not None else time.monotonic();last=None;observed_at=None
        while True:
            pump();actual=display.capture(0,0,800,600);accessible.clear_cache();label=accessible.get_name() or ''
            observed_at=time.monotonic()
            matches=(re.sub(r'age=[0-9]+ ns','age=dynamic ns',label)==prefix if table else label.startswith(prefix)) if prefix else label==''
            last=dict(pixels=actual==pixels,accessible=matches)
            sequence+=1;path=folder/(str(sequence)+'.rgb');path.write_bytes(actual)
            report['observations'].append(dict(case=name,elapsed=observed_at-started,pixels_sha256=sha(path),name=label,**last))
            if all(last.values()) or time.monotonic()-started>=timeout:break
            time.sleep(.015)
        if negative:
            assert not last[negative],(name,'negative control escaped',last)
            assert last['accessible' if negative=='pixels' else 'pixels'],(name,last)
        else:assert all(last.values()) and observed_at-started<=timeout,(name,last,observed_at-started)
    try:
        assert read()=={'ready':True};report['pid']=proc.pid;display=Display()
        deadline=time.monotonic()+5;accessible=None
        while accessible is None and time.monotonic()<deadline:
            pump();accessible=find_accessible()
            if accessible is None:time.sleep(.025)
        assert accessible is not None,'owned AT-SPI surface absent'
        references={(n,retained):view(n,retained) for n,retained in ((123,False),(987,False),(None,False),(456,False),(456,True))}
        check('INITIAL',*references[(123,False)],timeout=2)
        if mode=='normal':
            command('replace');check('REPLACE',*references[(987,False)])
        command('revoke');blank=bytes(800*600*3)
        check('REVOKE',blank,'',negative={'ignore-pixels':'pixels','ignore-accessible':'accessible'}.get(mode))
        if mode=='normal':
            command('stale');check('STALE',blank,'')
            command('regrant');check('REGRANT',*references[(None,False)])
            command('fresh');check('FRESH',*references[(456,False)])
            command('disconnect');check('DISCONNECT',*references[(456,True)])
        command('close');assert proc.wait(timeout=5)==0
        report['outcome']='pass';report['negative_control']=mode!='normal'
    except Exception as exc:
        report['error']=repr(exc);raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        err.close()
        if display:display.close()
        report['files']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')

def main():
    if sys.argv[1]=='--observe':
        observe(Path(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]),sys.argv[5],len(sys.argv)>6);return
    exe,text_probe,evidence=map(Path,sys.argv[1:4]);folder=evidence/('surface-'+uuid.uuid4().hex[:12]);folder.mkdir()
    table=len(sys.argv)>4;report=dict(family='TABLE-ERASURE' if table else 'SCENE-ERASURE',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),cases=[],executable_sha256=sha(exe),oracle_sha256=sha(Path(__file__)))
    server=None
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in ('normal','ignore-pixels','ignore-accessible'):
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)), '--observe',str(exe),str(text_probe),str(folder/mode),mode]+(['TABLE'] if table else []),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=35)
            except subprocess.TimeoutExpired:
                timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
            assert not timed_out and child.returncode==0,(mode,'observer deadline' if timed_out else stderr.decode(errors='replace'))
            case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass'
            report['cases'].append(dict(case=mode,outcome='pass',record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server is not None:
            server.terminate();server.communicate(timeout=5)
        # Do not preserve the ephemeral X authorization cookie.
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'}
        (folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print(folder/'result.json',report['outcome'])

if __name__=='__main__':main()
