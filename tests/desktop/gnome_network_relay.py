"""Finite owned native bus relay; operational inputs remain in private evidence."""
import hashlib
import json
import os
from pathlib import Path
import queue
import pwd
import signal
import socket
import struct
import stat
import sys
import time
import uuid

import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/protocol'),str(ROOT/'tests/fault')]
from native_ipc import Process, Harness, events
from native_network import linux_rows
from native_recovery import ObservedChild

workspace=Path(os.environ['HOME']).parent.resolve(strict=True)
if not workspace.name.startswith('GNOME-NETWORK-CACHE-01-'):raise ValueError('owned native cache workspace required')
connection=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],
    Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
connection.set_exit_on_close(False)
journal=(workspace/'network-relay.private.jsonl').open('x',encoding='utf-8');os.chmod(journal.name,0o600)
server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
server.bind('\0syspane-network-'+workspace.name.rsplit('-',1)[1]);server.listen(1);server.settimeout(.2)
stopping=False
def stop(*_):
    global stopping
    stopping=True
signal.signal(signal.SIGTERM,stop)
def record(row):
    raw=json.dumps(row,separators=(',',':'))+'\n'
    if journal.tell()+len(raw.encode())>1024**2:raise ValueError('private relay capacity')
    journal.write(raw);journal.flush()
record({'event':'ready','pid':os.getpid(),'owner':connection.get_unique_name(),'at_ns':time.monotonic_ns()})
collect_count=0

def collect():
    global collect_count
    collect_count+=1
    if collect_count>2:raise ValueError('collection count')
    executable=workspace.parent/'SysPane.CollectorProbe'
    build_record=ROOT/'build-support/evidence/w-25-consumer-continuity-linux-x64-gcc13.json'
    expected=json.loads(build_record.read_text())
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if digest(executable)!=expected['artifacts']['SysPane.CollectorProbe']['sha256']:raise ValueError('tested collector identity differs')
    for name,sha in expected['source_inputs'].items():
        if name.startswith('source/') and Path(name).suffix in ('.hpp','.cpp') and digest(ROOT/name)!=sha:
            raise ValueError('tested collector source differs')
    # The isolated GNOME HOME is too long for sockaddr_un. Reuse the already
    # admitted native IPC root, resolved from this real unprivileged account.
    ipc=Path(pwd.getpwuid(os.geteuid()).pw_dir)/'.cache/syspane/ipc-w24'
    info=ipc.lstat()
    if ipc.resolve()!=ipc or not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o700:
        raise ValueError('owned native IPC root required')
    owned=ipc/('case-'+uuid.uuid4().hex[:12]);owned.mkdir(mode=0o700)
    for suffix in ('h','d'):(owned/suffix).mkdir(mode=0o700)
    process=None;observers={};raw={'before':linux_rows(),'lower':time.clock_gettime_ns(time.CLOCK_BOOTTIME),
        'artifact_sha256':digest(executable),'build_record_sha256':digest(build_record)}
    path=workspace/('network-collector-'+str(collect_count)+'.private.json')
    try:
        process=Process([str(executable),'supervisor',str(owned),'live'])
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            try:event=process.events.get(timeout=.05)
            except queue.Empty:
                if process.process.poll() is not None and not process.reader.is_alive():break
                continue
            if event['event']=='spawned':observers[event['pid']]=ObservedChild(event['pid'])
            if event['event']=='error':raise ValueError('collector failure')
        if process.finish(1)!=0 or len(observers)!=1 or not all(o.exited(0) for o in observers.values()):raise ValueError('collector exit proof')
        raw.update(after=linux_rows(),upper=time.clock_gettime_ns(time.CLOCK_BOOTTIME),events=process.lines,
            children=[{'pid':pid,'observed_alive':True,'observed_exited':o.exited(0),'observer':'pidfd'} for pid,o in observers.items()])
        frames=events(process,'presentation')
        if len(frames)!=2 or frames[-1]['code']!=0:raise ValueError('complete projected fields required')
        frame=frames[-1]
        value={'producer':'producer:network','epoch':frame['epoch'],'entity':frame['entity'],
               'generation':frame['generation'],'values':[field['value'] for field in frame['fields']]}
        return {'frame':value,'private_path':str(path),'artifact_sha256':raw['artifact_sha256']}
    finally:
        if process:process.stop();raw['events']=process.lines
        path.write_text(json.dumps(raw,indent=2)+'\n');path.chmod(0o600)
        for observer in observers.values():observer.close()
        for suffix in ('h','d'):
            folder=owned/suffix
            if not list(folder.iterdir()):folder.rmdir()
        if not list(owned.iterdir()):owned.rmdir()

try:
    started=time.monotonic();count=0
    while not stopping and time.monotonic()-started<40:
        try:client,_=server.accept()
        except socket.timeout:continue
        with client:
            client.settimeout(2)
            if struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[1]!=os.geteuid():raise ValueError('foreign control identity')
            data=bytearray()
            while not data.endswith(b'\n'):
                part=client.recv(8193-len(data))
                if not part or len(data)+len(part)>8192:raise ValueError('bounded control required')
                data.extend(part)
            request=json.loads(data);count+=1
            if set(request)!={'method','args'} or count>40:raise ValueError('control shape/count')
            method,args=request['method'],request['args']
            row={'event':'call','request':request,'owner':connection.get_unique_name(),'started_ns':time.monotonic_ns()}
            if method=='Collect' and args==[]:reply=collect()
            elif method=='Exit' and args==[73]:
                row.update(reply='exiting',finished_ns=time.monotonic_ns());record(row)
                client.sendall((json.dumps(row)+'\n').encode());os._exit(73)
            else:
                signatures={'Attach':'()','Policy':'(sb)','Frame':'(sss)','Heartbeat':'(u)','Disable':'()'}
                if method not in signatures:raise ValueError('unknown relay method')
                values=list(args)
                if method=='Frame':values[2]=json.dumps(values[2],separators=(',',':'))
                response=connection.call_sync('org.gnome.Shell','/org/syspane/NetworkCache','org.syspane.NetworkCache',
                    method,GLib.Variant(signatures[method],values),GLib.VariantType.new('(s)'),Gio.DBusCallFlags.NO_AUTO_START,1000,None)
                reply=response.unpack()[0]
            row.update(reply=reply,finished_ns=time.monotonic_ns());record(row)
            client.sendall((json.dumps(row)+'\n').encode())
finally:
    server.close();connection.close_sync(None);journal.close()
