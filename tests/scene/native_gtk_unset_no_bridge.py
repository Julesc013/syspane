"""Native-only diagnostic control; never a wire/GUI/accessibility qualification."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,select,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tests/fault'),str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify as surface_runtime
from check_text_runtime import verify as text_runtime
sha=lambda raw:hashlib.sha256(raw).hexdigest()
exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
surface_runtime();text_runtime();folder=evidence/('gtk-unset-no-bridge-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
report=dict(outcome='fail',diagnostic_only=True,wire_qualified=False,performance_qualified=False,started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/gtk_accessible_erase_probe.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.hpp',ROOT/'source/build/surface-runtime.json',ROOT/'source/build/text-runtime.json')},cases=[])
try:
    server,env=launch_xvfb(folder,(1600,2048));env.update(NO_AT_BRIDGE='1',G_DEBUG='fatal-warnings',SYSPANE_GTK_UNSET_PRIME='1')
    for cohort in ('expanded','collapsed'):
        proc=subprocess.Popen([str(exe),'lifetime-unset',cohort],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        begin=time.monotonic();deadline=begin+15;buffer=b'';records=[];stages=[];err=b''
        def reply():
            global buffer
            while b'\n' not in buffer:
                assert time.monotonic()<deadline,'native-only child deadline'
                if select.select([proc.stdout],[],[],.1)[0]:
                    raw=os.read(proc.stdout.fileno(),4096);assert raw,'native-only premature exit';buffer+=raw;assert len(buffer)<=4096
            line,buffer=buffer.split(b'\n',1);assert len(line)<=1024 and len(records)<32;records.append(line);return json.loads(line)
        try:
            assert reply()==dict(ready=True,rows=3172,columns=2,held_cells=6344,native_word_primed=True)
            for command in ('retire','erase','recover','quit'):
                proc.stdin.write((command+'\n').encode());proc.stdin.flush();v=reply();assert v['ack']==command and v['held_cells']==6344;stages.append(v)
                assert v['cache_profiled'] and v['unset_max_depth']<=32 and v['notify_max_depth']<=32
                assert v['cache_calls']<=1000000 and v['unset_calls']<=1000000 and v['notify_calls']<=1000000
                assert max(v['cache_us'],v['unset_us'],v['notify_us'])<=120000000
                if v['local_checked']:assert all(v[k]==0 for k in ('text_leaks','name_leaks','count_leaks','word_leaks'))
                if command=='retire':assert v['retired_checked'] and v['retired_leaks']==v['collapsed_leaks']==0
                expected=(6342 if cohort=='collapsed' else 66) if command=='retire' else 6344;assert v['defunct_count']==expected
            assert proc.wait(timeout=3)==0;err=proc.stderr.read();assert len(err)<=2*1024*1024 and b'WARNING' not in err and b'CRITICAL' not in err
            report['cases'].append(dict(cohort=cohort,outcome='pass',stages=stages,actual_exit=True,native_word_primed=True))
        finally:
            if proc.poll() is None:proc.kill();proc.wait(timeout=3)
            remaining=proc.stderr.read();(folder/(cohort+'.stderr')).write_bytes(err+remaining)
            proc.stdin.close();proc.stdout.close();proc.stderr.close();(folder/(cohort+'.stdout.jsonl')).write_bytes(b'\n'.join(records)+b'\n')
    report['outcome']='pass'
finally:
    if server:server.terminate();server.communicate(timeout=5)
    report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
