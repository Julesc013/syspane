"""Observe owned Xvfb root pixels independently of an isolated native marker painter."""
import ctypes as C
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import select
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/fault'))
from native_diagnostic import launch_xvfb
from oracle import evaluate, pack_frame, decode

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class XImage(C.Structure):
    _fields_=[('width',C.c_int),('height',C.c_int),('xoffset',C.c_int),('format',C.c_int),('data',C.c_void_p),
              ('byte_order',C.c_int),('bitmap_unit',C.c_int),('bitmap_bit_order',C.c_int),('bitmap_pad',C.c_int),
              ('depth',C.c_int),('bytes_per_line',C.c_int),('bits_per_pixel',C.c_int),
              ('red_mask',C.c_ulong),('green_mask',C.c_ulong),('blue_mask',C.c_ulong)]
class ClientData(C.Union):
    _fields_=[('b',C.c_char*20),('s',C.c_short*10),('l',C.c_long*5)]
class ClientMessage(C.Structure):
    _fields_=[('type',C.c_int),('serial',C.c_ulong),('send_event',C.c_int),('display',C.c_void_p),
              ('window',C.c_ulong),('message_type',C.c_ulong),('format',C.c_int),('data',ClientData)]
class Event(C.Union):
    _fields_=[('client',ClientMessage),('padding',C.c_long*24)]
class ClassHint(C.Structure):
    _fields_=[('name',C.c_void_p),('kind',C.c_void_p)]

class Display:
    def __init__(self):
        x=self.x=C.CDLL('libX11.so.6');p=C.c_void_p;w=C.c_ulong;i=C.c_int
        signatures={
            'XOpenDisplay':([C.c_char_p],p),'XCloseDisplay':([p],i),'XDefaultRootWindow':([p],w),
            'XInternAtom':([p,C.c_char_p,i],w),'XSync':([p,i],i),'XFlush':([p],i),'XFree':([p],i),
            'XGetImage':([p,w,i,i,C.c_uint,C.c_uint,w,i],C.POINTER(XImage)),
            'XDestroyImage':([C.POINTER(XImage)],i),'XSendEvent':([p,w,i,C.c_long,p],i),
            'XGetWindowProperty':([p,w,w,C.c_long,C.c_long,i,w,C.POINTER(w),C.POINTER(i),C.POINTER(w),C.POINTER(w),C.POINTER(p)],i),
            'XFetchName':([p,w,C.POINTER(p)],i),'XGetClassHint':([p,w,C.POINTER(ClassHint)],i),
            'XCreateSimpleWindow':([p,w,i,i,C.c_uint,C.c_uint,C.c_uint,w,w],w),
            'XMapRaised':([p,w],i),'XDestroyWindow':([p,w],i),
        }
        for name,(arguments,result) in signatures.items():
            getattr(x,name).argtypes=arguments;getattr(x,name).restype=result
        self.handle=x.XOpenDisplay(None)
        if not self.handle:raise RuntimeError('owned display unavailable')
        self.root=x.XDefaultRootWindow(self.handle)
    def close(self):
        if self.handle:self.x.XCloseDisplay(self.handle);self.handle=None
    def atom(self,name):return self.x.XInternAtom(self.handle,name.encode('ascii'),False)
    def property_snapshot(self,window,name):
        kind,form,length,remaining,data=C.c_ulong(),C.c_int(),C.c_ulong(),C.c_ulong(),C.c_void_p()
        status=self.x.XGetWindowProperty(self.handle,window,self.atom(name),0,8,False,0,C.byref(kind),C.byref(form),C.byref(length),C.byref(remaining),C.byref(data))
        try:
            if status or length.value>8 or remaining.value or (form.value!=32 and not (form.value==0 and length.value==0 and kind.value==0)):raise ValueError('native property shape')
            return {'type':kind.value,'format':form.value,'values':[C.cast(data,C.POINTER(C.c_ulong))[n] for n in range(length.value)]}
        finally:
            if data:self.x.XFree(data)
    def property(self,window,name):return self.property_snapshot(window,name)['values']
    def root_configuration(self):
        return {name:self.property_snapshot(self.root,name) for name in ('_XROOTPMAP_ID','ESETROOT_PMAP_ID','_XSETROOT_ID','_NET_SUPPORTING_WM_CHECK','_NET_CURRENT_DESKTOP','_NET_SHOWING_DESKTOP')}
    def verify(self,window,pid):
        if self.property(window,'_NET_WM_PID') != [pid]:raise ValueError('candidate PID mismatch')
        name=C.c_void_p();hint=ClassHint()
        if not self.x.XFetchName(self.handle,window,C.byref(name)):raise ValueError('candidate name absent')
        try:
            if C.string_at(name)!=b'SysPane Oracle Probe':raise ValueError('candidate name mismatch')
        finally:self.x.XFree(name)
        if not self.x.XGetClassHint(self.handle,window,C.byref(hint)):raise ValueError('candidate class absent')
        try:
            if C.string_at(hint.name)!=b'syspane-oracle-probe' or C.string_at(hint.kind)!=b'SysPaneOracleProbe':raise ValueError('candidate class mismatch')
        finally:
            self.x.XFree(hint.name);self.x.XFree(hint.kind)
    def send(self,window,generation=None):
        event=Event();event.client.type=33;event.client.display=self.handle;event.client.window=window;event.client.format=32
        event.client.message_type=self.atom('_SYSPANE_ORACLE_GENERATION' if generation is not None else 'WM_PROTOCOLS')
        event.client.data.l[0]=generation>>32 if generation is not None else self.atom('WM_DELETE_WINDOW')
        event.client.data.l[1]=generation&0xffffffff if generation is not None else 0
        if not self.x.XSendEvent(self.handle,window,False,0,C.byref(event)):raise RuntimeError('native stimulus send failed')
        self.x.XFlush(self.handle)
    def capture(self,x=32,y=32,width=128,height=96):
        if not (0<width<=800 and 0<height<=600):raise ValueError('capture bounds')
        image=self.x.XGetImage(self.handle,self.root,x,y,width,height,0xffffffff,2)
        if not image:raise RuntimeError('root capture unavailable')
        try:
            value=image.contents
            if (value.width,value.height,value.xoffset,value.format,value.byte_order,value.depth,value.bits_per_pixel,value.red_mask,value.green_mask,value.blue_mask)!=(width,height,0,2,0,24,32,0xff0000,0xff00,0xff):raise RuntimeError('unqualified native image format')
            if not width*4<=value.bytes_per_line<=width*4+16:raise RuntimeError('native row stride')
            raw=C.string_at(value.data,value.bytes_per_line*height)
            rgb=bytearray(width*height*3)
            for row in range(height):
                rowbytes=raw[row*value.bytes_per_line:row*value.bytes_per_line+width*4]
                at=row*width*3
                rgb[at:at+width*3:3]=rowbytes[2::4]
                rgb[at+1:at+width*3:3]=rowbytes[1::4]
                rgb[at+2:at+width*3:3]=rowbytes[0::4]
            return bytes(rgb)
        finally:self.x.XDestroyImage(image)

def observer(environment,channel):
    os.environ.update(environment)
    display=journal=None
    try:
        display=Display()
        baseline=hashlib.sha256(display.capture(0,0,800,600)).hexdigest()
        configuration=display.root_configuration()
        channel.send({'ready':True,'root_before_sha256':baseline,'root_configuration_before':configuration})
        command=channel.recv();window,pid,case=command['window'],command['pid'],command['case']
        journal=Path(command['journal']).open('x',encoding='utf-8',newline='\n')
        def preserve(kind,value):
            journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        display.verify(window,pid)
        display.send(window,1)
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            if decode(display.capture())==1:break
            time.sleep(.02)
        else:raise AssertionError('baseline generation did not become visible')
        start=time.monotonic_ns();now=lambda:(time.monotonic_ns()-start)//1000
        trace={'version':'0.1.0','start_us':0,'end_us':2100000,'stimuli':[{'at_us':0,'generation':1}],'frames':[]}
        preserve('interval',{'start_us':0,'end_us':2100000});preserve('stimulus',trace['stimuli'][0])
        sent=1;cover=0;covered=False;gap_done=False;next_capture=0;acks=[]
        while now()<2100000:
            elapsed=now()
            if sent==1 and elapsed>=500000:
                issued=now();display.send(window,2);trace['stimuli'].append({'at_us':issued,'generation':2});sent=2
                preserve('stimulus',trace['stimuli'][-1])
            if sent==2 and elapsed>=1200000:
                issued=now();display.send(window,3);trace['stimuli'].append({'at_us':issued,'generation':3});sent=3
                preserve('stimulus',trace['stimuli'][-1])
            if case=='OCCLUDE' and elapsed>=750000 and not covered:
                cover=display.x.XCreateSimpleWindow(display.handle,display.root,32,32,128,96,0,0,0)
                display.x.XMapRaised(display.handle,cover);display.x.XSync(display.handle,False);covered=True
            if cover and elapsed>=1000000:
                display.x.XDestroyWindow(display.handle,cover);display.x.XSync(display.handle,False);cover=0
            if case=='GAP' and elapsed>=750000 and not gap_done:
                time.sleep(.35);gap_done=True;continue
            if elapsed<next_capture:
                time.sleep(min((next_capture-elapsed)/1000000,.01));continue
            begin=now();pixels=display.capture();finish=now()
            if finish>2100000:break
            trace['frames'].append(pack_frame(pixels,begin,finish))
            preserve('frame',trace['frames'][-1])
            words=display.property(window,'_SYSPANE_ORACLE_ACCEPTED')
            acks.append({'at_us':now(),'generation':str((words[0]<<32)|words[1]) if len(words)==2 else None})
            next_capture=finish+50000
        if cover:display.x.XDestroyWindow(display.handle,cover)
        result=evaluate(trace)
        channel.send({'trace':trace,'observation':result,'acknowledgements':acks,'candidate_identity_verified':True})
        display.send(window)
        if channel.recv()!={'candidate_exited':True}:raise RuntimeError('candidate exit not confirmed')
        display.x.XSync(display.handle,False)
        after=hashlib.sha256(display.capture(0,0,800,600)).hexdigest()
        after_configuration=display.root_configuration()
        channel.send({'root_after_sha256':after,'root_configuration_after':after_configuration,'root_restored':after==baseline and configuration==after_configuration})
    except Exception as error:
        channel.send({'error':type(error).__name__+': '+str(error)})
    finally:
        if journal:journal.close()
        if display:display.close()
        channel.close()

def receive(channel,timeout=6):
    if not channel.poll(timeout):raise TimeoutError('external observer exceeded bound')
    result=channel.recv()
    if 'error' in result:raise AssertionError(result['error'])
    return result

def run_case(executable,workspace,name):
    server=child=worker=None;parent=None
    row={'case':'ORACLE-01.'+name,'outcome':'fail'}
    journal=workspace/(name+'.frames.jsonl')
    try:
        server,environment=launch_xvfb(workspace)
        context=mp.get_context('spawn');parent,remote=context.Pipe()
        worker=context.Process(target=observer,args=({key:environment[key] for key in ('DISPLAY','XAUTHORITY')},remote))
        worker.start();remote.close()
        row.update(receive(parent))
        mode={'DISAPPEAR':'hide','FREEZE':'freeze'}.get(name,'live')
        child=subprocess.Popen([str(executable),mode],cwd=workspace,env=environment,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if not select.select([child.stdout],[],[],5)[0]:raise TimeoutError('native probe bootstrap timeout')
        bootstrap=b''
        while not bootstrap.endswith(b'\n') and len(bootstrap)<256:
            if not select.select([child.stdout],[],[],1)[0]:raise TimeoutError('native probe incomplete bootstrap')
            byte=os.read(child.stdout.fileno(),1)
            if not byte:raise AssertionError('native probe closed before bootstrap')
            bootstrap+=byte
        info=json.loads(bootstrap)
        if set(info)!={'window','pid','claims_visible'} or info['pid']!=child.pid:raise AssertionError('native bootstrap identity')
        row['candidate_claims_visible']=info['claims_visible']
        parent.send({'window':info['window'],'pid':child.pid,'case':name,'journal':str(journal)})
        row.update(receive(parent,8))
        stdout,stderr=child.communicate(timeout=5)
        row.update(candidate_exit=child.returncode,candidate_stderr=stderr.decode('utf-8',errors='replace'))
        if child.returncode!=0 or stdout:raise AssertionError('native probe shutdown failed')
        parent.send({'candidate_exited':True});row.update(receive(parent))
        expected={'LIVE':'pass','DISAPPEAR':'fail','FREEZE':'fail','OCCLUDE':'fail','GAP':'inconclusive'}[name]
        if row['observation']['outcome']!=expected:raise AssertionError('fixed temporal outcome differs: '+str(row['observation']))
        if not row['root_restored']:raise AssertionError('private root pixels changed after candidate exit')
        if name=='FREEZE' and not {'2','3'}<=set(r['generation'] for r in row['acknowledgements']):raise AssertionError('freeze did not preserve native event-loop progress')
        row['outcome']='pass';row['expected_observation']=expected
    except Exception as error:row['error']=type(error).__name__+': '+str(error)
    finally:
        cleanup=[]
        if child and child.poll() is None:
            child.kill()
            try:child.communicate(timeout=5)
            except subprocess.TimeoutExpired:cleanup.append('candidate exit unconfirmed')
        if parent:parent.close()
        if worker:
            worker.join(1)
            if worker.is_alive():worker.terminate();worker.join(2)
            if worker.is_alive():worker.kill();worker.join(2)
            row['observer_exit']=worker.exitcode
            if worker.exitcode!=0:cleanup.append('observer did not exit normally')
        if server:
            server.terminate()
            try:server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                try:server.communicate(timeout=5)
                except subprocess.TimeoutExpired:cleanup.append('Xvfb exit unconfirmed')
            row['server_exit']=server.poll()
            if row['server_exit'] is None:cleanup.append('Xvfb exit unconfirmed')
        auth=workspace/'xauthority'
        if auth.exists() and not auth.is_symlink():auth.unlink()
        if journal.exists():row['capture_journal']={'path':str(journal.relative_to(executable.parent)),'sha256':sha(journal),'bytes':journal.stat().st_size}
        if cleanup:row['outcome']='fail';row['cleanup_errors']=cleanup
    return row

def main():
    executable,output=Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()
    if output.parent!=executable.parent or output.name!='native-evidence':raise ValueError('owned output required')
    output.mkdir(exist_ok=True);token=uuid.uuid4().hex
    workspace=executable.parent/('oracle-case-'+token);workspace.mkdir(mode=0o700)
    inputs=[Path(__file__),ROOT/'tests/desktop/oracle.py',ROOT/'tests/fault/native_diagnostic.py',ROOT/'source/diagnostics/oracle_probe_x11.cpp',ROOT/'spec/delivery/packages/w-02-desktop-oracle.md']
    report={'family':'ORACLE-01','outcome':'fail','profile':'linux-x64-gcc13','executed_at':datetime.now(timezone.utc).isoformat(),
            'executable_sha256':sha(executable),'source_inputs':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
            'environment':{'display':'owned authenticated Xvfb, abstract local only','xvfb_sha256':sha(Path('/usr/bin/Xvfb'))},
            'qualification':'Native synthetic observer calibration only; no shell, icons, reveal action, compositor output, user-desktop capture or wall qualification.', 'cases':[]}
    try:
        for name in ['LIVE','DISAPPEAR','FREEZE','OCCLUDE','GAP']:
            print('Oracle calibration: '+name,flush=True)
            row=run_case(executable,workspace,name);report['cases'].append(row)
            if row['outcome']!='pass':break
        if len(report['cases'])==5 and all(row['outcome']=='pass' for row in report['cases']):report['outcome']='pass'
    finally:
        path=output/('ORACLE-01-'+token+'.json')
        with path.open('x',encoding='utf-8',newline='\n') as file:json.dump(report,file,indent=2);file.write('\n')
        if not any(workspace.iterdir()):workspace.rmdir()
        print('Native evidence: '+str(path),flush=True)
    return 0 if report['outcome']=='pass' else 1

if __name__=='__main__':sys.exit(main())
