"""Real native collector -> asynchronous GJS session; operational evidence stays private."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import signal
import stat
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from native_gjs_clock import ROOT, sha, owned_build, inventory, verify
sys.path[:0] = [str(ROOT/'tests/protocol'), str(ROOT/'tests/fault')]
from native_network import linux_rows
from native_recovery import ObservedChild
from native_collector import route_sockets

SOURCES = ['CMakeLists.txt', 'CMakePresets.json', 'source/build/components.json', 'source/build/targets/linux-x64-gcc13.json',
    'source/build/check_gjs_clock_dependencies.py', 'source/build/prepare_gnome_lab.py', 'source/build/gnome-lab-packages.json',
    'spec/delivery/packages/w-25-live-network-session.md', 'spec/delivery/packages/w-25-gjs-network-view.md',
    'tests/desktop/native_live_network.py', 'tests/desktop/gjs_live_network.js', 'tests/desktop/native_gjs_clock.py',
    'tests/protocol/native_network.py', 'tests/protocol/native_collector.py', 'tests/protocol/native_ipc.py', 'tests/fault/native_recovery.py']
SOURCES += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'source').rglob('*') if p.suffix in ('.cpp', '.hpp', '.gir', '.js'))
FIELDS = ['network.receive_bytes', 'network.transmit_bytes', 'network.receive_bytes_per_second', 'network.transmit_bytes_per_second']

def private_write(path, value):
    raw=json.dumps(value, indent=2)+'\n'; assert len(raw.encode()) <= 4*1024**2, 'private evidence bound'
    with path.open('x', encoding='utf-8') as stream:
        path.chmod(0o600); stream.write(raw)

def validate(rows, original, before, after, lower, upper):
    messages=[json.loads(row['payload']) for row in original]
    docs=[row['body']['snapshot'] for row in messages if row['type']=='snapshot']
    assert len(docs)==2 and [d['generation'] for d in docs]==['1','2'], 'two original real publications'
    by_generation={d['generation']:d for d in docs}
    for number, doc in enumerate(docs):
        assert {e['identity']['native_index'] for e in doc['entities']}==set(before)==set(after), 'native interface coverage'
        for entity in doc['entities']:
            index=entity['identity']['native_index']; current={o['field']:o for o in doc['observations'] if o['entity_id']==entity['id']}
            assert int(entity['identity']['native_type'])==before[index]['native_type']==after[index]['native_type'], 'native interface type'
            for direction, field in [('receive',FIELDS[0]),('transmit',FIELDS[1])]:
                observation=current[field]; value=int(observation['value']['data']); stamp=int(observation['measured_at']['nanoseconds'])
                assert before[index][direction] <= value <= after[index][direction], 'native counter bracket'
                assert lower <= stamp <= upper, 'native measurement bracket'
                rate=current[field+'_per_second']
                if not number: assert rate['value'] is None and rate['measured_at'] is None, 'first rate missing'
                else:
                    previous=next(o for o in docs[0]['observations'] if o['entity_id']==entity['id'] and o['field']==field)
                    interval=stamp-int(previous['measured_at']['nanoseconds']); delta=value-int(previous['value']['data'])
                    assert interval > 0 and delta >= 0 and rate['sample_interval_ns']==str(interval), 'native rate interval'
                    assert math.isclose(rate['value']['data'], float(Fraction(delta*10**9,interval)), rel_tol=4e-15, abs_tol=1e-9), 'native derived rate'
    projections=[r for r in rows if r['event']=='projection'];assert {r['frame']['generation'] for r in projections}=={'1','2'}, 'both projected generations'
    for row in projections:
        frame=row['frame'];doc=by_generation[frame['generation']]
        assert frame['epoch']==doc['producer_epoch'] and frame['entity']=='network:interface:1' and frame['producer']=='producer:network', 'bound projection identity'
        selected={o['field']:o for o in doc['observations'] if o['entity_id']==frame['entity']}
        assert len(frame['fields'])==4,'four projected fields'
        for field, shown in zip(FIELDS,frame['fields']):
            original=selected[field]; value=original['value']; expected=None
            if value is not None:
                if value['kind']=='uint64': expected=value['data']
                else:
                    rational=Fraction(value['data'])*1000; integer,remainder=divmod(rational.numerator,rational.denominator)
                    integer+=int(2*remainder>=rational.denominator); text=str(integer).rjust(4,'0');expected=text[:-3]+'.'+text[-3:]
            assert shown['value']==expected and shown['unit']==original['unit'], 'original counter/rate text'
            measured=original['measured_at']; assert shown['measured_ns']==(measured['nanoseconds'] if measured else None), 'immutable original measurement'
            assert shown['interval_ns']==original['sample_interval_ns'] and shown['acquisition']==(0 if value else 1), 'original status/interval'
            assert shown['support']==shown['presence']==0 and shown['origin']==(0 if field.endswith('_bytes') else 1), 'original status axes'
            assert shown['reported']==(0 if value else 2) and shown['error_code']=='', 'original freshness/error'
            def utc(text):
                return None if text is None else {'seconds':str(int(datetime.fromisoformat(text.replace('Z','+00:00')).timestamp())), 'nanoseconds':0, 'subnanoseconds':''}
            assert shown['observed_at']==utc(original['observed_at']) and shown['attempted_at']==utc(original['attempted_at']), 'original descriptive times'
            if measured:
                age=int(shown['age_ns']); projected=int(measured['nanoseconds'])+age
                assert 0 <= int(row['received_ns'])-projected < 500_000_000, 'native receipt/age bracket'
                assert shown['effective']==(1 if age>=3_000_000_000 else 0), 'shared exact TTL'
            else: assert shown['age_ns'] is None and shown['effective']==2, 'pending unknown age'
    return len(projections)

def run_case(build, executable, env, mode, output):
    identifier=uuid.uuid4().hex[:12];workspace=output/('GJS-LIVE-'+mode+'-'+identifier);workspace.mkdir(mode=0o700)
    root=Path.home()/'.cache/syspane/ipc-w24';info=root.stat()
    assert root.resolve(strict=True)==root and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o700
    endpoint=root/('case-'+identifier);endpoint.mkdir(mode=0o700)
    for name in ('h','d','v'):(endpoint/name).mkdir(mode=0o700)
    journal=workspace/'producer.private.jsonl'; transcript=workspace/'consumer.private.json'
    scenario=mode if mode in ('lease-loss','hang') else 'hold'
    command=[str(executable),'-m',str(ROOT/'tests/desktop/gjs_live_network.js'),str(build/'SysPane.CollectorProbe'),str(endpoint),scenario,str(journal)]
    public={'case':'GJS-LIVE.'+mode.upper(),'outcome':'fail','command':command,'children':[]}
    raw={'before':linux_rows(),'lower_ns':str(time.clock_gettime_ns(time.CLOCK_BOOTTIME)),'rows':[]}
    observers={};process=None;reader=None;inbox=queue.Queue(maxsize=1024);reader_error=[]
    try:
        process=subprocess.Popen(command,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        owner=ObservedChild(process.pid);observers['gjs']=owner
        def collect():
            total=0
            try:
                for line in iter(lambda:process.stdout.readline(65537),''):
                    total+=len(line.encode());assert total<=4*1024**2 and len(line)<=65536,'consumer output bound'
                    row=json.loads(line);row['received_ns']=str(time.clock_gettime_ns(time.CLOCK_BOOTTIME));raw['rows'].append(row);inbox.put_nowait(row)
            except Exception: reader_error.append('consumer output reader failed')
        reader=threading.Thread(target=collect,daemon=True);reader.start()
        def send(text):process.stdin.write(text+'\n');process.stdin.flush()
        deadline=time.monotonic()+12;triggered=False;stopped=None;revoked=None;second=False;expired=False;stale=False
        while time.monotonic()<deadline:
            try:row=inbox.get(timeout=.1)
            except queue.Empty:
                assert not reader_error,'bounded JSON consumer output'
                if process.poll() is not None and not reader.is_alive():break
                continue
            if row['event']=='native':
                native=row['row']
                if native['event']=='ready':observers['supervisor']=ObservedChild(row['supervisor_pid'])
                if native['event']=='spawned':observers['worker']=ObservedChild(native['pid'])
                if native['event']=='error' and mode!='hang':raise AssertionError('unexpected native stream fault: '+native['code'])
            if row['event']=='projection' and row['frame']['generation']=='2':
                second=True;frame=row['frame'];stale|=all(f['effective']==1 for f in frame['fields']);expired|=frame['lease']==3
                if 'watch_registered' not in public:
                    assert route_sockets(observers['worker'].pid),'held native network watch'
                    public['watch_registered']=True
                    namespace=lambda pid:(os.stat(f'/proc/{pid}/ns/time').st_dev,os.stat(f'/proc/{pid}/ns/time').st_ino)
                    identities={namespace(os.getpid()),*(namespace(o.pid) for o in observers.values())}
                    assert len(identities)==1,'shared native time namespace'
                    public['same_time_namespace']=True
                if not triggered:
                    if mode=='parent-loss': process.kill();triggered=True;break
                    if mode=='revoke':send('revoke');triggered=True
                    if mode=='live' and stale:send('stop');triggered=True
                    if mode=='lease-loss' and expired and stale:send('stop');triggered=True
            if row['event']=='revoked':revoked=row;send('stop')
            if mode=='hang' and row['event']=='cleared' and second and not triggered:
                send('stop');triggered=True
            if row['event']=='stopped':stopped=row;break
        assert second and len(observers)==3,'real source/session admission'
        expected=-signal.SIGKILL if mode=='parent-loss' else 0
        assert process.wait(timeout=4)==expected,'GJS native completion'
        reader.join(timeout=2);assert not reader.is_alive() and not reader_error,'observer drained'
        stderr=process.stderr.read();raw['stderr']=stderr;assert not stderr,'GJS diagnostic output'
        for name,observer in observers.items():
            assert observer.exited(2000),'native descendant exit'
            public['children'].append({'role':name,'pid':observer.pid,'observer':'pidfd','observed_alive':True,'observed_exited':True})
        if mode!='parent-loss':
            assert stopped and not stopped['payload'] and not stopped['state']['view'] and not stopped['state']['connection'] and not stopped['state']['queuedBytes'],'owner/sink cleanup'
            assert stopped['state']['exited'] and not stopped['state']['forced'],'native supervisor reaped'
            native=[r['row'] for r in raw['rows'] if r['event']=='native'];finished=[r for r in native if r['event']=='stopped']
            assert len(finished)==1 and finished[0]['os_confirmed'],'native worker proof'
            if mode=='hang':
                assert stopped['state']['exitStatus']==1 and finished[0]['forced'] and finished[0]['signaled'],'worker hang cleanup'
                assert any(r['event']=='error' and r['code']=='collector.producer_expired' for r in native),'independent producer expiry'
            else:assert stopped['state']['exitStatus']==0 and not finished[0]['forced'] and finished[0]['code']==0,'graceful native source exit'
        if mode=='revoke':
            assert revoked and revoked['code']=='cleared' and not revoked['payload'],'synchronous policy erasure'
            position=raw['rows'].index(revoked);assert not any(r['event']=='projection' for r in raw['rows'][position+1:]),'no late payload after revocation'
        if mode=='live':assert stale and not expired,'live lease with stale measurement'
        if mode=='lease-loss':assert stale and expired,'lease loss independent of acquisition'
        raw.update(after=linux_rows(),upper_ns=str(time.clock_gettime_ns(time.CLOCK_BOOTTIME)))
        original=[json.loads(line) for line in journal.read_text().splitlines()]
        public['projected_frames']=validate(raw['rows'],original,raw['before'],raw['after'],int(raw['lower_ns']),int(raw['upper_ns']))
        public['outcome']='pass'
    except Exception as error:
        public['failure']=type(error).__name__+': '+str(error);raise
    finally:
        if process:
            if process.poll() is None:process.kill()
            process.wait(timeout=4)
            if reader:reader.join(timeout=2)
            raw.setdefault('stderr',process.stderr.read())
            public['gjs_exit']=process.returncode
        for observer in observers.values():
            if not observer.exited(2000):signal.pidfd_send_signal(observer.handle,signal.SIGKILL)
            assert observer.exited(2000),'cleanup descendant exit';observer.close()
        private_write(transcript,raw)
        public['private_artifacts']={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in (transcript,journal) if p.exists()}
        for name in ('h','d','v'):
            folder=endpoint/name
            # Parent-loss kills cannot run Listener destructors. Remove only the
            # exact owned endpoint after independent exit of all descendants.
            socket=folder/'s'
            if socket.is_socket():socket.unlink()
            folder.rmdir()
        endpoint.rmdir()
        (workspace/'result.json').write_text(json.dumps(public,indent=2)+'\n')
    return public

def main():
    build=owned_build(Path(sys.argv[1]));output=build/'native-evidence';output.mkdir(exist_ok=True)
    attempt='GJS-LIVE-'+uuid.uuid4().hex;report={'family':'GJS-LIVE','outcome':'fail','executed_at':datetime.now(timezone.utc).isoformat(),
        'source_inputs':{p:sha(ROOT/p) for p in SOURCES},'cases':[],
        'qualification':'Real supervised native collector and asynchronous GJS owner only. No shell pixels, installed policy or complete product qualification.'}
    archive=output/(attempt+'-sources.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as bundle:
        for name in SOURCES:bundle.write(ROOT/name,name)
    report['source_archive_sha256']=sha(archive)
    try:
        report['build_dependencies']=verify();lab=build/'gnome-lab';identity=json.loads((lab/'identity.json').read_text())
        assert identity['lock_sha256']==sha(ROOT/'source/build/gnome-lab-packages.json') and identity['files']==inventory(lab/'sysroot'),'runtime identity'
        executable=lab/'sysroot/usr/bin/gjs';lib=lab/'sysroot/usr/lib/x86_64-linux-gnu'
        report['artifacts']={str(p):sha(p) for p in [build/'libsyspane_gjs_clock.so',build/'SysPaneClock-0.1.typelib',build/'SysPane.CollectorProbe',executable,lab/'identity.json']}
        env={k:v for k,v in os.environ.items() if k not in ('DISPLAY','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','GI_TYPELIB_PATH','LD_LIBRARY_PATH')}
        env.update(LD_LIBRARY_PATH=str(build)+':'+str(lib),GI_TYPELIB_PATH=':'.join(map(str,[build,lib/'gjs/girepository-1.0',lib/'girepository-1.0'])))
        for mode in ('live','lease-loss','hang','revoke','parent-loss'):
            report['cases'].append(run_case(build,executable,env,mode,output))
        report['outcome']='pass'
    except Exception as error:report['failure']=type(error).__name__+': '+str(error);raise
    finally:
        path=output/(attempt+'.json');path.write_text(json.dumps(report,indent=2)+'\n');print('Native evidence:',path,flush=True);print('GJS-LIVE:',report['outcome'],flush=True)

if __name__=='__main__':main()
