"""External native glyph and erasure observations; raw values/pixels stay private."""
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import struct
import sys
import time
from types import SimpleNamespace

import gi
gi.require_version('Gio','2.0')
from gi.repository import Gio, GLib
from native_oracle import ROOT
from native_x11_host import rgb_record
from gnome_shell_recovery import process_identity
from gnome_composition import FIXTURE, bind_icon_window
sys.path.insert(0,str(ROOT/'tests/protocol'))
from native_collector import verify_documents, verify_presentation
from record_gnome_host import rgb

CONTROLS=['live','ignore-clear','wrong-value','owner-loss']
CALIBRATION={'producer':'fixture:calibration','epoch':'fixture:1','entity':'network:interface:1','generation':'1',
             'values':['1234567890',None,'1234567890.000',None]}
RECT=(300,310,448,150)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def cell(data,row,column):
    return b''.join(data[((30+row*30+y)*448+column*14)*3:((30+row*30+y)*448+column*14+14)*3] for y in range(26))
def templates(calibration):
    data=rgb(calibration,448*150*3);result={}
    for row,value in enumerate(CALIBRATION['values']):
        for column,char in enumerate(value or '-'):
            pixels=cell(data,row,column)
            if char in result and result[char]!=pixels:raise ValueError('glyph calibration position differs')
            result[char]=pixels
    if set(result)!=set('0123456789.-') or len(set(result.values()))!=12 or any(p==bytes((20,30,40))*14*26 for p in result.values()):raise ValueError('distinct native glyph calibration required')
    return result
def decode(image,table):
    data=rgb(image,448*150*3);inverse={v:k for k,v in table.items()};blank=bytes((20,30,40))*14*26;result=[]
    for row in range(4):
        text='';ended=False
        for column in range(32):
            pixels=cell(data,row,column)
            if pixels==blank:ended=True;continue
            if ended or pixels not in inverse:raise ValueError('unrecognized native glyph or gap')
            text+=inverse[pixels]
        result.append(None if text=='-' else text)
    return result
def judge(raw):
    if raw['control'] not in CONTROLS:raise ValueError('native cache mode')
    table=templates(raw['calibration']['pixels']);values_ok=True;erase_ok=True
    for row in raw['displayed']:
        if row['capture_end_ns']-row['capture_start_ns']>50_000_000:raise ValueError('native value capture duration')
        values_ok &= decode(row['pixels'],table)==row['frame']['values']
    blank=bytes(FIXTURE['background_rgb'])*448*150
    for interval in raw['erasure']:
        samples=interval['samples'];start=interval['start_ns'];last=start;settled=0
        for row in samples:
            begin,end=row['start_ns'],row['end_ns']
            if not last<=begin<=end or begin-last>150_000_000 or end-begin>50_000_000:raise ValueError('erasure capture coverage/order')
            if begin>=start+200_000_000:
                settled+=1;erase_ok &= rgb(row['pixels'],len(blank))==blank
            last=end
        if settled<3 or last<start+400_000_000 or last>start+550_000_000:raise ValueError('erasure settled interval')
    if len(raw['displayed'])!=(1 if raw['control']=='owner-loss' else 2) or len(raw['erasure'])!=(1 if raw['control']=='owner-loss' else 3):raise ValueError('fixed native cache phases')
    if rgb(raw['post_clear'],len(blank))!=blank:raise ValueError('cache survived disable/closure')
    return {'outcome':'pass' if values_ok and erase_ok else 'fail','values':'pass' if values_ok else 'fail',
        'erasure':'pass' if erase_ok else 'fail','fields_compared':len(raw['displayed'])*4}

def observe(display,environment,shell_pid,workspace,composition,trace_function):
    pid=int(environment['SYSPANE_GNOME_NETWORK_PID']);mode=environment['SYSPANE_GNOME_NETWORK_CACHE']
    raw={'version':'0.1.0','control':mode,'relay':process_identity(pid),'calls':[],'displayed':[],'erasure':[],'collectors':[]}
    path=workspace/'network-cache.private.json';descriptor=os.pidfd_open(pid);poller=select.poll();poller.register(descriptor,select.POLLIN)
    connection=Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
    def save():
        data=json.dumps(raw,indent=2)+'\n'
        if len(data.encode())>16*1024**2:raise ValueError('private cache evidence capacity')
        path.write_text(data);path.chmod(0o600)
    def direct(method,args,signature):
        return connection.call_sync('org.gnome.Shell','/org/syspane/NetworkCache','org.syspane.NetworkCache',method,
            GLib.Variant(signature,args),None,Gio.DBusCallFlags.NO_AUTO_START,1000,None).unpack()[0]
    def call(method,args):
        begin=time.monotonic_ns()
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
            client.settimeout(7 if method=='Collect' else 2);client.connect('\0syspane-network-'+workspace.name.rsplit('-',1)[1])
            peer=struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            if peer[0]!=pid or peer[1]!=os.geteuid():raise ValueError('retained relay peer mismatch')
            client.sendall((json.dumps({'method':method,'args':args})+'\n').encode());data=bytearray()
            while not data.endswith(b'\n'):
                part=client.recv(8193-len(data))
                if not part or len(data)+len(part)>8192:raise ValueError('relay response bounds')
                data.extend(part)
        native=json.loads(data);row={'method':method,'args':args,'started_ns':begin,'finished_ns':time.monotonic_ns(),'native':native,'peer_pid':peer[0]}
        raw['calls'].append(row);save();return native['reply']
    beat=0
    def heartbeat():
        nonlocal beat
        assert call('Heartbeat',[beat])=='accepted';beat+=1
    def capture(frame):
        time.sleep(.2);begin=time.monotonic_ns();pixels=rgb_record(display.capture(*RECT));end=time.monotonic_ns()
        raw['displayed'].append({'frame':frame,'capture_start_ns':begin,'capture_end_ns':end,'pixels':pixels});save()
    def erasure(start):
        interval={'start_ns':start,'samples':[]};raw['erasure'].append(interval)
        while time.monotonic_ns()-start<450_000_000:
            begin=time.monotonic_ns();pixels=rgb_record(display.capture(*RECT));end=time.monotonic_ns()
            interval['samples'].append({'start_ns':begin,'end_ns':end,'pixels':pixels});save();time.sleep(.05)
    def collect():
        heartbeat();result=call('Collect',[]);p=Path(result['private_path'])
        if p.parent!=workspace or p.name not in ['network-collector-1.private.json','network-collector-2.private.json']:raise ValueError('private collector evidence path')
        record=json.loads(p.read_text());process=SimpleNamespace(lines=record['events'])
        compared=verify_documents(process,record['before'],record['after'],record['lower'],record['upper'],'live')
        fields=verify_presentation(process,record['lower'],record['upper'])
        latest=[r for r in record['events'] if r['event']=='presentation'][-1]
        expected={'producer':'producer:network','epoch':latest['epoch'],'entity':latest['entity'],'generation':latest['generation'],'values':[f['value'] for f in latest['fields']]}
        if result['frame']!=expected:raise ValueError('relay changed C++ frame')
        raw['collectors'].append({'path':str(p),'sha256':digest(p),'rows_compared':compared,'fields_compared':fields,'artifact_sha256':record['artifact_sha256']})
        heartbeat();return result['frame']
    try:
        if composition['outcome']!='pass':raise ValueError('composition prerequisite')
        raw['unauthorized']=[direct('Attach',[],'()'),direct('Policy',['7',True],'(sb)'),direct('Frame',['7','1','{}'],'(sss)')]
        assert raw['unauthorized']==['unauthorized']*3
        assert call('Attach',[])=='accepted';heartbeat()
        assert call('Frame',['0','1',CALIBRATION])=='restricted'
        assert call('Policy',['7',True])=='cleared'
        assert call('Frame',['7','1',CALIBRATION])=='accepted';time.sleep(.2)
        begin=time.monotonic_ns();raw['calibration']={'pixels':rgb_record(display.capture(*RECT)),'started_ns':begin,'finished_ns':time.monotonic_ns()};templates(raw['calibration']['pixels']);save()
        assert call('Policy',['7',True])=='duplicate'
        assert call('Policy',['6',False])=='invalid'
        invalid=dict(CALIBRATION,generation='00');assert call('Frame',['7','2',invalid])=='invalid'
        invalid=dict(CALIBRATION,extra='forbidden');assert call('Frame',['7','2',invalid])=='invalid'
        assert call('Frame',['7','0',CALIBRATION])=='invalid'
        oversized=dict(CALIBRATION,values=['1234567890',None,'1'*33+'.000',None])
        assert call('Frame',['7','2',oversized])=='capacity'
        raw['capacity_state']=json.loads(direct('GetState',[],'()'))
        assert raw['capacity_state']['entries']==raw['capacity_state']['labels']==0
        frame=collect();assert call('Frame',['7','2',frame])=='accepted';capture(frame)
        if mode=='owner-loss':
            assert call('Exit',[73])=='exiting'
            if not poller.poll(1000):raise ValueError('relay exit not observed')
            raw['exit']={'pid':pid,'observer':'pidfd','observed_ns':time.monotonic_ns()};erasure(raw['exit']['observed_ns'])
            raw['closed_state']=json.loads(direct('GetState',[],'()'));assert raw['closed_state']['closed']
        else:
            assert call('Policy',['8',False])=='cleared';erasure(raw['calls'][-1]['finished_ns'])
            assert call('Frame',['7','3',frame])=='restricted';assert call('Policy',['8',True])=='invalid'
            assert call('Policy',['9',True])=='cleared';erasure(raw['calls'][-1]['finished_ns'])
            fresh=collect();assert fresh['epoch']!=frame['epoch'];assert call('Frame',['9','1',fresh])=='accepted';capture(fresh)
            assert call('Frame',['9','1',fresh])=='invalid'
            assert call('Policy',['10',False])=='cleared';erasure(raw['calls'][-1]['finished_ns'])
            assert call('Disable',[])=='cleared'
        raw['post']=trace_function(display,environment,dismiss=False)
        raw['post_clear']=rgb_record(display.capture(*RECT));raw['evaluation']=judge(raw)
        if raw['post']['evaluation']['outcome']!='pass' or bind_icon_window(display,shell_pid,workspace)!=composition['icon_manager']:raise ValueError('native post/composition identity')
        save()
        return {'version':'0.1.0','control':mode,'evaluation':raw['evaluation'],'relay':raw['relay'],
            'private':{'path':str(path),'sha256':digest(path),'bytes':path.stat().st_size},
            'collectors':raw['collectors'],'disclosure':'Operational digits, source documents and pixel crops remain in owned private evidence only.'}
    except Exception as error:
        raw['error']=type(error).__name__;save();raise RuntimeError('native network cache failed; inspect owned private evidence') from None
    finally:
        connection.close_sync(None);os.close(descriptor)
