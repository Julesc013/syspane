"""Independent native Windows topology/PDH oracle, exact intervals and DLL evidence."""
import copy
import ctypes as c
from ctypes import wintypes as w
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid

assert c.sizeof(c.c_void_p)==8 and os.name=='nt'
kernel=c.WinDLL('kernel32',use_last_error=True)
kernel.GetLogicalProcessorInformationEx.argtypes=[w.DWORD,c.c_void_p,c.POINTER(w.DWORD)]
kernel.GetLogicalProcessorInformationEx.restype=w.BOOL
kernel.GetSystemDirectoryW.argtypes=[w.LPWSTR,w.UINT]
buffer=c.create_unicode_buffer(32768);length=kernel.GetSystemDirectoryW(buffer,len(buffer));assert 0<length<len(buffer)
PDH_PATH=Path(buffer.value)/'pdh.dll'
pdh=c.WinDLL(str(PDH_PATH),winmode=0x800)
kernel.GetModuleFileNameW.argtypes=[w.HMODULE,w.LPWSTR,w.DWORD]
module_name=c.create_unicode_buffer(32768)
module_size=kernel.GetModuleFileNameW(pdh._handle,module_name,len(module_name))
assert 0<module_size<len(module_name) and Path(module_name.value).resolve()==PDH_PATH.resolve()
H=c.c_void_p
for name,args in [('PdhOpenQueryW',[w.LPCWSTR,c.c_size_t,c.POINTER(H)]),('PdhCloseQuery',[H]),('PdhAddEnglishCounterW',[H,w.LPCWSTR,c.c_size_t,c.POINTER(H)]),('PdhCollectQueryData',[H]),('PdhGetRawCounterValue',[H,c.POINTER(w.DWORD),c.c_void_p]),('PdhCalculateCounterFromRawValue',[H,w.DWORD,c.c_void_p,c.c_void_p,c.c_void_p])]:
    function=getattr(pdh,name);function.argtypes=args;function.restype=w.LONG

class Affinity(c.Structure):_fields_=[('mask',c.c_ulonglong),('group',w.WORD),('reserved',w.WORD*3)]
class GroupInfo(c.Structure):_fields_=[('maximum',w.BYTE),('active',w.BYTE),('reserved',w.BYTE*38),('mask',c.c_ulonglong)]
class GroupHeader(c.Structure):_fields_=[('maximum',w.WORD),('active',w.WORD),('reserved',w.BYTE*20)]
class RelationHeader(c.Structure):_fields_=[('flags',w.BYTE),('efficiency',w.BYTE),('reserved',w.BYTE*20),('groups',w.WORD)]
class Header(c.Structure):_fields_=[('kind',w.DWORD),('size',w.DWORD)]
class Raw(c.Structure):_fields_=[('status',w.DWORD),('timestamp',w.FILETIME),('first',c.c_longlong),('second',c.c_longlong),('multi',w.DWORD)]
class Formatted(c.Structure):_fields_=[('status',w.DWORD),('value',c.c_double)]

def native_records(kind):
    size=w.DWORD();assert not kernel.GetLogicalProcessorInformationEx(kind,None,c.byref(size)) and c.get_last_error()==122
    assert 0<size.value<=8388608
    buffer=c.create_string_buffer(size.value);assert kernel.GetLogicalProcessorInformationEx(kind,buffer,c.byref(size))
    raw=buffer.raw[:size.value];records=[];offset=0
    while offset<len(raw):
        header=Header.from_buffer_copy(raw,offset);assert header.kind==kind and 8<header.size<=len(raw)-offset
        records.append(raw[offset+8:offset+header.size]);offset+=header.size
    assert offset==len(raw);return records

def topology():
    groups=native_records(4);assert len(groups)==1
    header=GroupHeader.from_buffer_copy(groups[0]);data=groups[0][c.sizeof(GroupHeader):]
    assert len(data)==header.active*c.sizeof(GroupInfo)
    result=dict(maximum_groups=header.maximum,groups=[],cores=[],packages=[])
    for number in range(header.active):
        group=GroupInfo.from_buffer_copy(data,number*c.sizeof(GroupInfo))
        assert group.mask.bit_count()==group.active and 0<group.active<=group.maximum<=64
        result['groups'].append(dict(number=number,active=group.active,maximum=group.maximum,mask=str(group.mask)))
    for name,kind in [('cores',0),('packages',3)]:
        for raw in native_records(kind):
            header=RelationHeader.from_buffer_copy(raw);data=raw[c.sizeof(RelationHeader):]
            assert len(data)==header.groups*c.sizeof(Affinity)
            masks=[]
            for n in range(header.groups):
                mask=Affinity.from_buffer_copy(data,n*c.sizeof(Affinity));masks.append(dict(group=mask.group,mask=str(mask.mask)))
            masks.sort(key=lambda v:(v['group'],int(v['mask'])))
            result[name].append(dict(flags=header.flags,efficiency=header.efficiency,masks=masks))
        result[name].sort(key=lambda v:[(m['group'],int(m['mask'])) for m in v['masks']])
    return result

def keys(value):return [(g['number'],bit) for g in value['groups'] for bit in range(64) if int(g['mask'])&(1<<bit)]
def raw_struct(row):
    value=Raw();value.status=row['counter_status'];value.first=int(row['first']);value.second=int(row['second']);value.multi=row['multi'];stamp=int(row['timestamp']);value.timestamp.dwLowDateTime=stamp&0xffffffff;value.timestamp.dwHighDateTime=stamp>>32;return value

class Query:
    def __init__(self,cpus):
        self.handle=H();self.counters={};assert pdh.PdhOpenQueryW(None,0,c.byref(self.handle))==0
        try:
            for group,number in cpus:
                for part,name in enumerate(('User Time','Privileged Time','Idle Time')):
                    counter=H();assert pdh.PdhAddEnglishCounterW(self.handle,f'\\Processor Information({group},{number})\\% {name}',0,c.byref(counter))==0
                    self.counters[(group,number,part)]=counter
        except BaseException:self.close();raise
    def close(self):
        if self.handle:
            assert pdh.PdhCloseQuery(self.handle)==0;self.handle=H()
    def read(self):
        assert pdh.PdhCollectQueryData(self.handle)==0
        result={}
        for key,counter in self.counters.items():
            value=Raw();kind=w.DWORD();assert pdh.PdhGetRawCounterValue(counter,c.byref(kind),c.byref(value))==0
            assert value.status in (0,1) and kind.value==0x20510500 and value.multi==1
            result.setdefault(f'{key[0]},{key[1]}',[]).append(dict(first=value.first,second=value.second,timestamp=(value.timestamp.dwHighDateTime<<32)|value.timestamp.dwLowDateTime))
        return result
    def calculate(self,key,current,old):
        a,b=raw_struct(current),raw_struct(old);result=Formatted()
        assert pdh.PdhCalculateCounterFromRawValue(self.counters[key],0x200|0x1000|0x8000,c.byref(a),c.byref(b),c.byref(result))==0
        assert result.status in (0,1) and math.isfinite(result.value)
        return result.value

def verify(before,probe,after,query):
    assert probe['definition']=='windows:pdh-accounted-time-v1' and probe['cancelled'] and probe['timed_out']
    first,second=probe['first'],probe['second']
    assert before['topology']==first['topology']==second['topology']==after['topology']
    assert int(first['start'])<=int(first['end'])<int(second['start'])<=int(second['end'])
    cpus=keys(before['topology']);expected={};groups={}
    assert [(v['group'],v['number']) for v in first['rows']]==cpus==[(v['group'],v['number']) for v in second['rows']]
    for a,b in zip(first['rows'],second['rows']):
        key=(a['group'],a['number']);name=f'{key[0]},{key[1]}'
        deltas=[]
        assert len(a['accounting'])==len(b['accounting'])==3
        for index,(old,current) in enumerate(zip(a['accounting'],b['accounting'])):
            for sample in (old,current):
                assert sample['api_status']==0 and sample['counter_status'] in (0,1) and sample['type']==0x20510500 and sample['multi']==1
                for field in ('first','second'):assert before['counters'][name][index][field]<=int(sample[field])<=after['counters'][name][index][field]
            delta=int(current['first'])-int(old['first']);base=int(current['second'])-int(old['second']);assert delta>=0 and base>0
            formatted=query.calculate(key+(index,),current,old)
            assert math.isclose(formatted,float(Fraction(100*delta,base)),rel_tol=4e-14,abs_tol=1e-10)
            deltas.append(delta)
        total=sum(deltas);busy=sum(deltas[:2]);assert total>0
        identifier=f'windows:cpu:{key[0]}:{key[1]}';expected[identifier]=(busy,total)
        groups.setdefault(f'windows:group:{key[0]}',[]).append((busy,total))
    assert probe['commit']==0 and probe['pending']==0 and len(probe['ratios'])==len(cpus)
    interval=int(second['start'])-int(first['start'])
    def ratio(value,wanted):
        busy,total=wanted
        assert int(value['busy'])==busy and int(value['total'])==total and int(value['interval_ns'])==interval
        assert math.isclose(value['percent'],float(Fraction(100*busy,total)),rel_tol=4e-14,abs_tol=1e-10)
    for row in probe['ratios']:ratio(row['ratio'],expected[row['id']])
    assert set(probe['domains'])==set(groups)
    for name,values in groups.items():ratio(probe['domains'][name],(sum(v[0] for v in values),sum(v[1] for v in values)))
    ratio(probe['aggregate'],(sum(v[0] for v in expected.values()),sum(v[1] for v in expected.values())))
    if len(before['topology']['groups'])==1:
        for sample in (first,second):
            raw_total=sum(int(part['first']) for row in sample['rows'] for part in row['accounting'])
            raw_idle=sum(int(row['accounting'][2]['first']) for row in sample['rows'])
            assert before['system_times']['total']<=raw_total<=after['system_times']['total']
            assert before['system_times']['idle']<=raw_idle<=after['system_times']['idle']

def system_times():
    idle,kernel_time,user=w.FILETIME(),w.FILETIME(),w.FILETIME()
    kernel.GetSystemTimes.argtypes=[c.POINTER(w.FILETIME)]*3;kernel.GetSystemTimes.restype=w.BOOL
    assert kernel.GetSystemTimes(c.byref(idle),c.byref(kernel_time),c.byref(user))
    value=lambda t:(t.dwHighDateTime<<32)|t.dwLowDateTime
    return dict(idle=value(idle),total=value(kernel_time)+value(user))

def main():
    executable,evidence=map(lambda v:Path(v).resolve(),sys.argv[1:]);build=executable.parent
    assert evidence==build/'native-evidence' and json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='windows-x64-gcc15'
    folder=evidence/('windows-processor-'+uuid.uuid4().hex[:10]);folder.mkdir(parents=True)
    result=dict(outcome='fail',environment=dict(windows=platform.win32_ver(),machine=platform.machine(),python=sys.version),executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),system_pdh=dict(path=str(PDH_PATH),loaded_module_path=module_name.value,sha256=hashlib.sha256(PDH_PATH.read_bytes()).hexdigest()))
    query=None
    try:
        before_topology=topology();query=Query(keys(before_topology));result['before']=dict(topology=before_topology,system_times=system_times(),counters=query.read())
        run=subprocess.run([str(executable)],capture_output=True,timeout=20)
        (folder/'stdout.json').write_bytes(run.stdout);(folder/'stderr.txt').write_bytes(run.stderr);result['exit']=run.returncode
        result['after']=dict(counters=query.read(),system_times=system_times(),topology=topology());result['probe']=json.loads(run.stdout)
        assert run.returncode==0,run.stderr.decode(errors='replace')
        verify(result['before'],result['probe'],result['after'],query)
        wrong=copy.deepcopy(result['probe']);wrong['aggregate']['total']=str(int(wrong['aggregate']['total'])+1)
        try:verify(result['before'],wrong,result['after'],query)
        except AssertionError:result['wrong_denominator_rejected']=True
        else:raise AssertionError('wrong denominator accepted')
        wrong=copy.deepcopy(result['probe']);wrong['second']['rows'].pop()
        try:verify(result['before'],wrong,result['after'],query)
        except AssertionError:result['missing_cpu_rejected']=True
        else:raise AssertionError('missing CPU accepted')
        result['outcome']='pass'
        print(f"Complete {len(keys(before_topology))}-CPU / {len(before_topology['groups'])}-group topology, raw PDH brackets and exact intervals: pass; {folder}")
    except BaseException as error:result['error']=repr(error);raise
    finally:
        if query:query.close()
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')

if __name__=='__main__':main()
