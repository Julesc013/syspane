"""Independent Windows pipe admission, complete timing and cancellation checks."""
import copy
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import uuid
from native_ipc import Process

assert os.name=='nt'
kernel=c.WinDLL('kernel32',use_last_error=True)
kernel.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE];kernel.CreateFileW.restype=w.HANDLE
kernel.WriteFile.argtypes=[w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD),c.c_void_p];kernel.WriteFile.restype=w.BOOL
kernel.ReadFile.argtypes=kernel.WriteFile.argtypes;kernel.ReadFile.restype=w.BOOL
kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL
kernel.GetNamedPipeServerProcessId.argtypes=[w.HANDLE,c.POINTER(w.ULONG)];kernel.GetNamedPipeServerProcessId.restype=w.BOOL
kernel.PeekNamedPipe.argtypes=[w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD),c.POINTER(w.DWORD),c.POINTER(w.DWORD)];kernel.PeekNamedPipe.restype=w.BOOL
kernel.WaitNamedPipeW.argtypes=[w.LPCWSTR,w.DWORD];kernel.WaitNamedPipeW.restype=w.BOOL

class Peer:
    def __init__(self,endpoint,pid):
        deadline=time.monotonic()+5
        while True:
            self.handle=kernel.CreateFileW(endpoint,0x0012019b,0,None,3,0x00110000,None)
            if self.handle not in (None,c.c_void_p(-1).value):break
            error=c.get_last_error();remaining=int((deadline-time.monotonic())*1000)
            assert error==231 and remaining>0,error
            assert kernel.WaitNamedPipeW(endpoint,remaining),c.get_last_error()
        actual=w.ULONG();assert kernel.GetNamedPipeServerProcessId(self.handle,c.byref(actual)) and actual.value==pid
    def write(self,value=b'x'):
        count=w.DWORD();assert kernel.WriteFile(self.handle,value,len(value),c.byref(count),None) and count.value==len(value)
    def receive(self):
        end=time.monotonic()+3
        while time.monotonic()<end:
            available=w.DWORD();assert kernel.PeekNamedPipe(self.handle,None,0,None,c.byref(available),None)
            if available.value:
                byte=c.create_string_buffer(1);count=w.DWORD();assert kernel.ReadFile(self.handle,byte,1,c.byref(count),None) and count.value==1;return byte.raw
            time.sleep(.002)
        raise AssertionError('retained stream byte timeout')
    def close(self):
        if self.handle:assert kernel.CloseHandle(self.handle);self.handle=None

def verify(record,expected_pid,admitted,minimum_ticks):
    complete=record['complete'];samples=complete['samples']
    assert record['ready']['access_controls_verified'] and record['ready']['unprivileged_context']
    assert samples and len(samples)==complete['call_count']<=20000
    assert [v['ordinal'] for v in samples]==list(range(1,len(samples)+1))
    started=int(record['ready']['started_ms']);previous=started
    for sample in samples:
        start,end=int(sample['start_ms']),int(sample['end_ms']);assert previous<=start<=end
        assert end-start<=(1250 if sample['error']=='io.timeout' else 100)
        assert sample['result'] in ('empty','accepted','error') and bool(sample['error'])==(sample['result']=='error')
        previous=end
    ticks=[started]+[int(t) for t in complete['ticks']];assert len(ticks)-1>=minimum_ticks
    for first,last in zip(ticks,ticks[1:]):
        assert first<last
        if last-first>250:
            assert any(s['error']=='io.timeout' and first<=int(s['start_ms'])<=int(s['end_ms'])<=last and int(s['end_ms'])-int(s['start_ms'])<=1250 for s in samples)
    assert complete['admitted']==admitted and int(complete['destroy_ms'])<=1250
    if admitted:
        auth=record['authenticated'];assert auth['peer_pid']==expected_pid and auth['first_read_bytes']==1 and auth['first_value']==120
        assert auth['second_read_bytes']==0 and auth['second_timeout'] and auth['busy_rejected'] and int(auth['listener_destroy_ms'])<=1250
        accepted=[s for s in samples if s['result']=='accepted'];assert len(accepted)==1
        assert started<=int(auth['connected_ms'])<=int(auth['first_observed_ms'])<=int(accepted[0]['end_ms'])
    else:assert not any(s['result']=='accepted' for s in samples)
    assert record['process']['exit_code']==0

def main():
    executable,evidence=map(lambda v:Path(v).resolve(),sys.argv[1:]);build=executable.parent
    assert evidence==build/'native-evidence' and json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='windows-x64-gcc15'
    folder=evidence/('windows-poll-'+uuid.uuid4().hex[:10]);folder.mkdir(parents=True)
    result=dict(outcome='fail',executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),environment=dict(windows=platform.win32_ver(),machine=platform.machine(),python=sys.version),cases=[])
    def save():(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    def run(mode,ticks,admitted,endpoint=None):
        endpoint=endpoint or '\\\\.\\pipe\\SysPane.Dev.'+uuid.uuid4().hex
        process=Process([str(executable),'poll',endpoint,mode,str(os.getpid())]);peer=None;intruder=None
        case=dict(case=mode,endpoint=endpoint,outcome='fail');result['cases'].append(case);save()
        try:
            case['ready']=process.event('ready')
            if mode not in ('idle','close-connect'):
                if mode=='retry':
                    intruder=Process([str(executable),'client',endpoint,'partial-eof',str(process.process.pid)])
                    assert process.event('admission_error')['code']=='peer.process';assert intruder.finish()==0
                peer=Peer(endpoint,process.process.pid)
                if mode=='delayed':time.sleep(.7)
                if mode=='timeout':
                    begin=time.monotonic();failure=process.event('admission_error',7);assert failure['code']=='io.timeout' and 4.7<=time.monotonic()-begin<=6.4
                    peer.close();peer=Peer(endpoint,process.process.pid)
                if mode!='close-read':peer.write()
                if mode=='keep-stream':assert process.event('retained_stream');assert peer.receive()==b'y';peer.write(b'z')
                if admitted:case['authenticated']=process.event('authenticated')
            case['complete']=process.event('complete',8);assert process.finish()==0;case['process']=process.record()
            verify(case,os.getpid(),admitted,ticks)
            if mode=='delayed':assert int(case['authenticated']['first_observed_ms'])-int(case['authenticated']['connected_ms'])>=550
            if mode=='keep-stream':assert case['authenticated']['stream_survived_listener']
            if mode=='retry':assert case['complete']['errors']==1
            if mode=='timeout':assert case['complete']['errors']==1
            case['outcome']='pass';save()
            return endpoint
        finally:
            if peer:peer.close()
            if intruder:intruder.stop()
            process.stop();case['process']=process.record();save()
    try:
        run('idle',5,False)
        run('delayed',5,True)
        run('preconnected',1,True)
        run('retry',0,True)
        run('timeout',40,True)
        old=run('close-connect',2,False);run('preconnected',1,True,old)
        old=run('close-read',6,False);run('preconnected',1,True,old)
        run('keep-stream',0,True)
        example=next(v for v in result['cases'] if v['case']=='delayed')
        for label,mutate in [('missing_sample',lambda d:d['complete']['samples'].pop()),('slow_call',lambda d:d['complete']['samples'][0].update(end_ms=str(int(d['complete']['samples'][0]['start_ms'])+101))),('false_byte',lambda d:d['authenticated'].update(first_value=121)),('false_pid',lambda d:d['authenticated'].update(peer_pid=os.getpid()+1))]:
            wrong=copy.deepcopy(example);mutate(wrong)
            try:verify(wrong,os.getpid(),True,5)
            except AssertionError:result[label+'_rejected']=True
            else:raise AssertionError(label+' oracle mutation accepted')
        result['outcome']='pass';save();print(f'Windows polling admission, complete timings and cancellation: pass; {folder}')
    finally:save()

if __name__=='__main__':main()
