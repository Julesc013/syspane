"""Independent OS counter brackets; do not publish raw interface keys/counters."""
from datetime import datetime, timezone
import ctypes as c
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def windows_rows():
    u8,u16,u32,u64=c.c_uint8,c.c_uint16,c.c_uint32,c.c_uint64
    class Guid(c.Structure):
        _fields_=[('a',u32),('b',u16),('c',u16),('d',u8*8)]
    class Row(c.Structure):
        _fields_=[('luid',u64),('index',u32),('guid',Guid),('alias',u16*257),('description',u16*257),
            ('address_length',u32),('address',u8*32),('permanent_address',u8*32),('mtu',u32),('type',u32),
            ('tunnel',u32),('media',u32),('physical',u32),('access',u32),('direction',u32),('flags',u8),
            ('oper',u32),('admin',u32),('media_state',u32),('network',Guid),('connection',u32)]+[
            (name,u64) for name in ('tx_speed','rx_speed','rx','rx_unicast','rx_nonunicast','rx_discards','rx_errors',
            'rx_unknown','rx_unicast_bytes','rx_multicast_bytes','rx_broadcast_bytes','tx','tx_unicast','tx_nonunicast',
            'tx_discards','tx_errors','tx_unicast_bytes','tx_multicast_bytes','tx_broadcast_bytes','out_queue')]
    class Table(c.Structure):
        _fields_=[('count',u32),('rows',Row*1)]
    api=c.WinDLL('iphlpapi.dll')
    api.GetIfTable2.argtypes=[c.POINTER(c.POINTER(Table))]; api.GetIfTable2.restype=u32
    api.FreeMibTable.argtypes=[c.c_void_p]; api.FreeMibTable.restype=None
    pointer=c.POINTER(Table)()
    code=api.GetIfTable2(c.byref(pointer))
    if code: raise RuntimeError('independent Windows table query failed')
    try:
        count=pointer.contents.count
        if count>8192: raise RuntimeError('independent table over capacity')
        rows=c.cast(c.addressof(pointer.contents)+Table.rows.offset,c.POINTER(Row*count)).contents
        return {str(row.luid):{'index':row.index,'native_type':row.type,'receive':row.rx,'transmit':row.tx} for row in rows}
    finally: api.FreeMibTable(pointer)

def linux_rows():
    result={}
    for path in Path('/sys/class/net').iterdir():
        index=int((path/'ifindex').read_text())
        result[str(index)]={'index':index,'native_type':int((path/'type').read_text()),
            'receive':int((path/'statistics/rx_bytes').read_text()),'transmit':int((path/'statistics/tx_bytes').read_text())}
        if len(result)>8192: raise RuntimeError('independent table over capacity')
    return result

def main():
    executable,output=(Path(value).resolve() for value in sys.argv[1:3])
    assert output.parent==executable.parent and output.name=='native-evidence'
    output.mkdir(exist_ok=True)
    identity=uuid.uuid4().hex[:12]
    report={'family':'NATIVE-NETWORK','outcome':'fail','executed_at':datetime.now(timezone.utc).isoformat(),
        'executable_sha256':sha(executable),'host':{'system':platform.system(),'release':platform.release(),'machine':platform.machine()},
        'cases':[],'source_inputs':{p.relative_to(ROOT).as_posix():sha(p) for directory in ('source','tests/protocol')
            for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts},
        'qualification':'Raw real native acquisition only; no model identity, topology continuity, rate, supervised collector or desktop qualification.',
        'disclosure':'Committed results exclude all native keys, interface names and counter values. Failed raw exchanges remain local ignored evidence only.'}
    package='spec/delivery/packages/w-25-network-acquisition.md'
    report['source_inputs'][package]=sha(ROOT/package)
    exchanges=[]
    try:
        read=windows_rows if platform.system()=='Windows' else linux_rows
        for mode in ('read','cancel','deadline','capacity'):
            case={'case':'NATIVE-NETWORK.NETWORK-'+mode.upper(),'outcome':'fail'}; report['cases'].append(case)
            before=read() if mode in ('read','capacity') else {}
            result=subprocess.run([str(executable),mode],capture_output=True,timeout=5)
            exchanges.append({'mode':mode,'returncode':result.returncode,'stdout':result.stdout.decode('utf-8',errors='replace'),
                'stderr':result.stderr.decode('utf-8',errors='replace'),'before':before})
            assert result.returncode==0 and not result.stderr and len(result.stdout)<=2*1024*1024,'probe process/output bound'
            value=json.loads(result.stdout)
            assert set(value)=={'status','native_error','rows'} and value['native_error']==0,'result shape/native error'
            if mode=='read':
                after=read(); exchanges[-1]['after']=after
                rows=value['rows']; assert value['status']=='success' and before and len(rows)==len(before),'complete acquisition'
                assert set(before)==set(after)=={row['key'] for row in rows},'native key set changed/missing'
                assert [int(row['key']) for row in rows]==sorted(int(row['key']) for row in rows),'native ordering'
                for row in rows:
                    assert set(row)=={'key','index','native_type','receive','transmit'},'raw row shape'
                    low,high=before[row['key']],after[row['key']]
                    assert row['index']==low['index']==high['index'] and row['native_type']==low['native_type']==high['native_type'],'native type/index'
                    for field in ('receive','transmit'):
                        assert isinstance(row[field],str) and row[field]==str(int(row[field])),'counter representation'
                        assert 0<=low[field]<=int(row[field])<=high[field]<=2**64-1,'native counter bracket/reset'
                case['rows_compared']=len(rows)
                case['oracle']='independent ctypes GetIfTable2 decoding' if platform.system()=='Windows' else 'independent sysfs index/type/counter reads'
            else:
                if mode=='capacity': assert before,'capacity fixture requires a native interface'
                assert value['status']=={'cancel':'cancelled','deadline':'timed_out','capacity':'capacity'}[mode] and value['rows']==[],'terminal result is empty'
            case['outcome']='pass'; print(case['case']+': pass',flush=True)
        report['outcome']='pass'
    except Exception as error:
        # Fixed assertions exclude row values; no repr of native exceptions/rows.
        report['failure_type']=type(error).__name__
        private=output/('NATIVE-NETWORK-'+identity+'.private.json')
        private.write_text(json.dumps(exchanges,indent=2)+'\n',encoding='utf-8',newline='\n')
        report['private_failure']={'filename':private.name,'sha256':sha(private),'scope':'owned ignored output; do not copy into public evidence'}
        raise
    finally:
        path=output/('NATIVE-NETWORK-'+identity+'.json')
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print('Native evidence: '+str(path),flush=True)
if __name__=='__main__': main()
