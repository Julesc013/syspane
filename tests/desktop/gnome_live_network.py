"""Independent original-source and pixel oracle; all operational evidence stays private."""
from fractions import Fraction
import json
import os
from pathlib import Path
import select
import signal
import sys
import time
from types import SimpleNamespace
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio
from native_oracle import ROOT
from native_x11_host import rgb_record
from gnome_shell_recovery import process_identity
from gnome_composition import FIXTURE, bind_icon_window
from record_gnome_host import rgb
from oracle import evaluate
sys.path.insert(0, str(ROOT/'tests/protocol'))
from native_network import linux_rows
from native_collector import verify_documents, route_sockets

MODES = ('live','freeze-age','ignore-expiry','wrong-value','ignore-clear','lease-loss','revoke','peer-exit','hang')
RECT = (300,310,448,210)
FIELDS = ('network.receive_bytes','network.transmit_bytes','network.receive_bytes_per_second','network.transmit_bytes_per_second')
CALIBRATION = ('1234567890','-','1234567890.000','-','1234567890')
BACKGROUND = bytes((20,30,40))
FRESH, STALE = bytes((40,200,80)), bytes((240,160,40))
ACTIVE, EXPIRED = bytes((40,140,240)), bytes((240,60,60))
now = lambda: time.clock_gettime_ns(time.CLOCK_BOOTTIME)

def cell(data, row, column):
    top = 180 if row==4 else 30+row*30
    return b''.join(data[((top+y)*448+column*14)*3:((top+y)*448+column*14+14)*3] for y in range(26))

def templates(pixels):
    data=rgb(pixels,448*210*3);result={}
    for row,text in enumerate(CALIBRATION):
        for column,char in enumerate(text):
            glyph=cell(data,row,column)
            if char in result and result[char]!=glyph:raise ValueError('native calibration position differs')
            result[char]=glyph
    if len(set(result.values()))!=12 or BACKGROUND*14*26 in result.values():raise ValueError('distinct native calibration required')
    return result

def decode(pixels, table):
    data=rgb(pixels,448*210*3);inverse={v:k for k,v in table.items()};texts=[]
    for row in range(5):
        text='';ended=False
        for column in range(16 if row==4 else 32):
            glyph=cell(data,row,column)
            if glyph==BACKGROUND*14*26:ended=True;continue
            if ended or glyph not in inverse:raise ValueError('unrecognized native glyph or gap')
            text+=inverse[glyph]
        texts.append(None if text=='-' else text)
    def indicator(x,first,second):
        pixels=b''.join(data[((180+y)*448+x)*3:((180+y)*448+x+20)*3] for y in range(26))
        if pixels not in (first*20*26,second*20*26):raise ValueError('unknown native indicator')
        return pixels==second*20*26
    if not texts[4] or texts[4]!=str(int(texts[4])):raise ValueError('noncanonical age')
    return texts[:4],int(texts[4]),indicator(224,FRESH,STALE),indicator(360,ACTIVE,EXPIRED)

def originals(raw):
    rows=raw['producer'];events=[];docs=[]
    for row in rows:
        message=json.loads(row['payload'])
        if message['type']=='snapshot':
            assert not row['dropped'],'original snapshot dropped'
            events.append({'event':'imported','body':json.dumps(message['body']),'duplicate':False,'now_ns':row['now_ns']})
            docs.append(message['body']['snapshot'])
    before=raw['before'];after=raw['after']
    verify_documents(SimpleNamespace(lines=events),before,after,int(raw['lower_ns']),int(raw['upper_ns']),'live')
    assert [d['generation'] for d in docs]==['1','2'],'original generation identity'
    selected={o['field']:o for o in docs[1]['observations'] if o['entity_id']=='network:interface:1'}
    values=[];stamps=[]
    for field in FIELDS:
        observation=selected[field];value=observation['value'];stamps.append(int(observation['measured_at']['nanoseconds']))
        assert observation['acquisition']=='success' and observation['freshness']=='current','original successful sample'
        if value['kind']=='uint64':values.append(value['data'])
        else:
            rational=Fraction(value['data'])*1000;integer,remainder=divmod(rational.numerator,rational.denominator)
            integer+=int(2*remainder>=rational.denominator);text=str(integer).rjust(4,'0');values.append(text[:-3]+'.'+text[-3:])
    assert len(set(stamps))==1,'shared native acquisition stamp'
    return values,stamps[0]

def judge(raw):
    mode=raw['mode']
    if mode not in MODES:raise ValueError('network mode')
    table=templates(raw['calibration']['pixels']);expected,stamp=originals(raw)
    checks={key:True for key in ('values','age','freshness','lease','erasure')}
    short=mode in ('peer-exit','hang');ages=[];fresh=stale=active=expired=0;previous=None
    beats=[int(r['now_ns']) for r in raw['producer'] if not r['dropped'] and json.loads(r['payload'])['type']=='heartbeat']
    if not beats:raise ValueError('original accepted heartbeat required')
    expiry=max(beats)+3_000_000_000
    for row in raw['samples']:
        begin,end=row['begin_ns'],row['end_ns']
        if not stamp<=begin<=end<=begin+50_000_000 or previous is not None and not previous<=begin<=previous+150_000_000:raise ValueError('network capture coverage')
        values,age,is_stale,is_expired=decode(row['pixels'],table);ages.append(age)
        checks['values'] &= values==expected
        checks['age'] &= max(0,(begin-stamp)//1_000_000-200)<=age<=(end-stamp)//1_000_000
        if end<stamp+3_000_000_000:checks['freshness'] &= not is_stale;fresh+=1
        if begin>=stamp+3_200_000_000:checks['freshness'] &= is_stale;stale+=1
        if mode!='lease-loss' or end<expiry:checks['lease'] &= not is_expired;active+=1
        elif begin>=expiry+200_000_000:checks['lease'] &= is_expired;expired+=1
        previous=end
    checks['age'] &= len(ages)>=(30 if short else 55) and all(a<=b for a,b in zip(ages,ages[1:])) and ages[-1]-ages[0]>=(1500 if short else 3000)
    if fresh<3 or (not short and stale<3) or active<3 or (mode=='lease-loss' and expired<3):raise ValueError('temporal witnesses missing')
    interval=raw['erasure'];previous=interval['begin_ns'];settled=0;blank=bytes(FIXTURE['background_rgb'])*448*210
    for row in interval['samples']:
        begin,end=row['begin_ns'],row['end_ns']
        if not previous<=begin<=end<=begin+50_000_000 or begin-previous>150_000_000:raise ValueError('erasure capture coverage')
        if begin>=interval['begin_ns']+200_000_000:
            settled+=1;checks['erasure'] &= rgb(row['pixels'],len(blank))==blank
        previous=end
    if settled<3 or not interval['begin_ns']+400_000_000<=previous<=interval['begin_ns']+550_000_000:raise ValueError('settled erasure coverage')
    if rgb(raw['post_clear']['pixels'],len(blank))!=blank:raise ValueError('network pixels survived final cleanup')
    final=raw['final'];session=final['session']
    if final['labels'] or session['view'] or session['connection'] or session['queuedBytes'] or not session['exited'] or session['forced']:raise ValueError('native session resources survived')
    if session['exitStatus']!=(-signal.SIGKILL if mode=='peer-exit' else 1 if mode=='hang' else 0):raise ValueError('native supervisor exit differs')
    if session['phase']!=('failed' if short else 'closed') or bool(session['error'])!=short:raise ValueError('native session outcome differs')
    events=session['events'];stopped=[r for r in events if r['event']=='stopped']
    if mode!='peer-exit':
        if len(stopped)!=1 or not stopped[0]['os_confirmed'] or stopped[0]['forced']!=(mode=='hang'):raise ValueError('native worker exit evidence')
        if mode=='hang' and not any(r['event']=='error' and r['code']=='collector.producer_expired' for r in events):raise ValueError('native health expiry missing')
    if set(raw['exits'])!={'supervisor','worker'} or not all(r['pidfd_exit'] for r in raw['exits'].values()):raise ValueError('independent descendant exit missing')
    if not raw['watch_registered'] or not raw['same_time_namespace']:raise ValueError('native source watch/clock missing')
    if evaluate(raw['post']['trace'])!=raw['post']['evaluation'] or raw['post']['evaluation']['outcome']!='pass':raise ValueError('post-network marker failed')
    if any(raw['samples'][0]['begin_ns']<=c['begin_ns']<=raw['samples'][-1]['end_ns'] for c in raw['calls']):raise ValueError('diagnostic queries drove pixels')
    return {'outcome':'pass' if all(checks.values()) else 'fail',**{k:'pass' if v else 'fail' for k,v in checks.items()},
        'samples':len(ages),'fresh_witnesses':fresh,'stale_witnesses':stale,'active_witnesses':active,'expired_witnesses':expired}

def observe(display, environment, shell_pid, workspace, composition, trace_function):
    mode=environment['SYSPANE_GNOME_NETWORK_LIVE'];raw={'version':'0.1.0','mode':mode,'samples':[],'calls':[],'peers':{},'exits':{}}
    path=workspace/'network-live.private.json';journal=Path(environment['SYSPANE_GNOME_NETWORK_JOURNAL']);descriptors={}
    connection=Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
    def save():
        data=json.dumps(raw,indent=2)+'\n'
        if len(data.encode())>16*1024**2:raise ValueError('private pixel evidence capacity')
        with path.open('w') as stream:path.chmod(0o600);stream.write(data)
    def call(method):
        begin=now();reply=connection.call_sync('org.gnome.Shell','/org/syspane/NetworkLive','org.syspane.NetworkLive',method,None,None,Gio.DBusCallFlags.NO_AUTO_START,1000,None).unpack()[0]
        raw['calls'].append({'method':method,'begin_ns':begin,'end_ns':now(),'reply':reply});return reply
    def state():return json.loads(call('GetState'))
    def until(predicate):
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            value=state()
            if predicate(value):return value
            time.sleep(.02)
        raise AssertionError('network lifecycle deadline')
    def capture():
        begin=now();pixels=rgb_record(display.capture(*RECT));return {'begin_ns':begin,'end_ns':now(),'pixels':pixels}
    def producer():
        data=journal.read_bytes() if journal.exists() else b''
        if len(data)>4*1024**2:raise ValueError('original producer capacity')
        return [json.loads(line) for line in data.splitlines(keepends=True) if line.endswith(b'\n')]
    try:
        assert composition['outcome']=='pass'
        assert call('Calibrate')=='calibrated';time.sleep(.2);raw['calibration']=capture();templates(raw['calibration']['pixels'])
        raw.update(before=linux_rows(),lower_ns=now())
        assert call('Start')=='starting'
        started=until(lambda s:s['session'] and any(e['event']=='spawned' for e in s['session']['events']))
        supervisor=started['session']['pid'];worker=next(e['pid'] for e in started['session']['events'] if e['event']=='spawned')
        for role,pid in [('supervisor',supervisor),('worker',worker)]:
            descriptors[role]=os.pidfd_open(pid);raw['peers'][role]=process_identity(pid)
            assert not select.select([descriptors[role]],[],[],0)[0],'native peer already exited'
            assert raw['peers'][role]['session']==shell_pid and raw['peers'][role]['process_group']==shell_pid,'native shell session'
        namespace=lambda pid:(os.stat(f'/proc/{pid}/ns/time').st_dev,os.stat(f'/proc/{pid}/ns/time').st_ino)
        raw['same_time_namespace']=len({namespace(os.getpid()),namespace(shell_pid),namespace(supervisor),namespace(worker)})==1
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            if sum(json.loads(r['payload'])['type']=='snapshot' for r in producer())==2:break
            time.sleep(.02)
        else:raise AssertionError('second original publication deadline')
        raw['watch_registered']=bool(route_sockets(worker));time.sleep(.2)
        deadline=now()+(2_200_000_000 if mode in ('peer-exit','hang') else 3_600_000_000)
        while now()<deadline:raw['samples'].append(capture());time.sleep(.05)
        if mode=='peer-exit':signal.pidfd_send_signal(descriptors['supervisor'],signal.SIGKILL)
        if mode in ('peer-exit','hang'):
            assert select.select([descriptors['supervisor']],[],[],2)[0],'native supervisor exit deadline'
            origin=now()
        elif mode in ('revoke','ignore-clear'):
            assert call('Revoke')=='cleared';origin=raw['calls'][-1]['end_ns']
        else:
            assert call('Stop')=='stopping';origin=raw['calls'][-1]['end_ns']
        raw['erasure']={'begin_ns':origin,'samples':[]}
        while now()<origin+450_000_000:raw['erasure']['samples'].append(capture());time.sleep(.05)
        for role,descriptor in descriptors.items():
            assert select.select([descriptor],[],[],2)[0],'native descendant exit deadline'
            raw['exits'][role]={'pid':raw['peers'][role]['pid'],'pidfd_exit':True,'observed_ns':now()}
        until(lambda s:s['session']['phase'] in ('closed','failed'))
        assert call('Cleanup')=='cleared';time.sleep(.2);raw['post_clear']=capture();raw['final']=state()
        assert call('Start')=='closed'
        raw.update(after=linux_rows(),upper_ns=now(),producer=producer())
        raw['post']=trace_function(display,environment,dismiss=False)
        assert bind_icon_window(display,shell_pid,workspace)==composition['icon_manager'],'icon manager changed'
        raw['evaluation']=judge(raw);save()
        return {'control':mode,'evaluation':raw['evaluation'],'peers':raw['peers'],'journal':str(path),
            'disclosure':'Operational source JSON and pixels remain private; public report stores identities and outcomes only.'}
    except Exception as error:
        raw['error']=type(error).__name__+': '+str(error);save();raise
    finally:
        for descriptor in descriptors.values():os.close(descriptor)
        connection.close_sync(None)
