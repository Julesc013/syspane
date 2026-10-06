"""Native controller/shell lifetime oracle with private original operational pixels."""
from fractions import Fraction
import json
import os
from pathlib import Path
import select
import signal
import sys
import time
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib
from gnome_live_network import RECT, FIELDS, now, templates, decode
from gnome_composition import FIXTURE, bind_icon_window, masks, settings
from gnome_shell_recovery import process_identity
from native_x11_host import rgb_record
from x11_recovery import ResourceOwner, manager_identity
from record_gnome_host import rgb
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/protocol'))
from native_network import linux_rows
from native_consumer_continuity import verify_source

BACKGROUND_RECT = (0, 400, 128, 96)  # Outside both the operational tile and icon fixture.


def lines(path, maximum):
    raw = path.read_bytes() if path.exists() else b''
    if len(raw) > maximum:
        raise ValueError('controller evidence capacity')
    return [json.loads(row) for row in raw.split(b'\n')[:-1]]


def controller_rows(workspace):
    return lines(workspace/'controller.log', 1024**2)


def identity(pid):
    row = process_identity(pid)
    row['parent'] = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[1])
    return row


def expected(snapshot):
    observations = {r['field']: r for r in snapshot['observations'] if r['entity_id']=='network:interface:1'}
    values, stamps = [], []
    for name in FIELDS:
        observation = observations[name]
        if observation['acquisition']!='success' or observation['freshness']!='current':
            raise ValueError('successful original source required')
        value = observation['value']; stamps.append(int(observation['measured_at']['nanoseconds']))
        if value['kind']=='uint64':
            values.append(value['data'])
        else:
            rational = Fraction(value['data'])*1000
            integer, remainder = divmod(rational.numerator, rational.denominator)
            integer += int(2*remainder >= rational.denominator)
            text = str(integer).rjust(4, '0'); values.append(text[:-3]+'.'+text[-3:])
    if len(set(stamps))!=1:
        raise ValueError('original acquisition timestamp differs')
    return values, stamps[0]


def visible(samples, calibration, deliveries, connection):
    table = templates(calibration['pixels']); candidates = []
    for row in deliveries:
        message = json.loads(row['payload'])
        if message['type']=='snapshot' and message['connection_id']==connection:
            values, stamp = expected(message['body']['snapshot'])
            candidates.append((int(message['body']['snapshot']['generation']), int(row['now_ns']), values, stamp))
    if len(samples)<35:
        raise ValueError('operational capture coverage missing')
    if samples[-1]['end_ns']-samples[0]['begin_ns']<2_000_000_000:
        raise ValueError('operational capture interval too short')
    last = None; generations = []; ages = []
    for row in samples:
        begin, end = row['begin_ns'], row['end_ns']
        if not begin<=end<=begin+50_000_000 or last is not None and not last<=begin<=last+150_000_000:
            raise ValueError('operational capture gap/deadline')
        last = end
        try:
            actual, age, stale, expired = decode(row['pixels'], table)
        except ValueError:
            return False
        settled = [r[0] for r in candidates if r[1]<=begin-200_000_000]
        floor = max(settled, default=0)
        matches = [r for r in candidates if r[0]>=floor and r[1]<=end+1_000_000 and actual==r[2]
                   and max(0, (begin-r[3])//1_000_000-200)<=age<=(end-r[3])//1_000_000]
        if stale or expired or not matches:
            return False
        generation = max(r[0] for r in matches)
        if generations and generation<generations[-1]:
            raise ValueError('displayed generation regressed')
        generations.append(generation); ages.append(age)
    return len(set(generations))>=2 and max(ages)-min(ages)>=400


def judge(raw, composition):
    mode = raw['mode']
    if mode not in ('live','no-reattach','revoke'):
        raise ValueError('controller recovery mode')
    controller, source, old = (raw['identities'][k] for k in ('controller','source','old_shell'))
    if controller['pid']!=controller['session'] or controller['pid']!=controller['process_group']:
        raise ValueError('controller is not session owner')
    for row in (source, old):
        if row['parent']!=controller['pid'] or row['session']!=controller['pid'] or row['process_group']!=controller['pid']:
            raise ValueError('native child session ownership')
    if not all(raw['held_live'][name] for name in ('controller','source','old_shell','old_icon')):
        raise ValueError('original held native lifetime missing')
    if not raw['old_shell_exit']['pidfd_exit'] or raw['old_shell_exit']['pid']!=old['pid']:
        raise ValueError('held old shell exit missing')
    if raw['fault']['pid']!=old['pid'] or raw['fault']['begin_ns']>raw['fault']['end_ns']:
        raise ValueError('wrong held fault target or clock')
    if not raw['fault']['end_ns']<=raw['old_shell_exit']['observed_ns']<=raw['fault']['end_ns']+2_000_000_000:
        raise ValueError('shell exit deadline')
    if not raw['final_live']['controller'] or not raw['final_live']['source']:
        raise ValueError('independent owner/source died')
    verify_source(raw['source'], raw['bracket']['before'], raw['after'], raw['bracket']['lower_ns'], raw['upper_ns'])
    originals = {json.loads(r['payload'])['body']['snapshot']['generation']:json.loads(r['payload'])['body'] for r in raw['source']}
    events = raw['controller']; started = [e for e in events if e['event']=='source_spawned']
    launches = [e for e in events if e['event']=='consumer_spawned']; failures = [e for e in events if e['event']=='consumer_fault']
    if len(started)!=1 or started[0]['pid']!=source['pid'] or len(failures)!=1 or failures[0]['pid']!=old['pid']:
        raise ValueError('source or fault lifetime differs')
    if launches[0]['pid']!=old['pid'] or any(row['source_pid']!=source['pid'] for row in launches):
        raise ValueError('consumer/source launch binding differs')
    epoch = started[0]['epoch']
    if any(body['snapshot']['producer_epoch']!=epoch for body in originals.values()):
        raise ValueError('collector epoch changed')
    for row in raw['delivery']:
        message = json.loads(row['payload'])
        if message['producer_epoch']!=epoch:
            raise ValueError('delivery epoch differs')
        if message['type']=='snapshot' and message['body']!=originals.get(message['body']['snapshot']['generation']):
            raise ValueError('original snapshot or measurement changed')
    if not visible(raw['baseline'],raw['calibration'],raw['delivery'],launches[0]['connection']):
        raise ValueError('pre-fault original operational pixels missing')
    last = raw['fault']['begin_ns']
    for row in raw['outage']:
        if not last<=row['begin_ns']<=last+150_000_000 or not row['begin_ns']<=row['end_ns']<=row['begin_ns']+50_000_000:
            raise ValueError('outage capture coverage')
        last = row['end_ns']
    if not raw['outage'] or last-raw['fault']['begin_ns']>10_000_000_000:
        raise ValueError('outage observation bound')
    if any(c['method'] in ('Calibrate','Start') and c['begin_ns']>=raw['fault']['begin_ns'] for c in raw['calls']):
        raise ValueError('observer drove replacement attachment')
    if any(c['begin_ns']>=raw['baseline'][0]['begin_ns'] for c in raw['calls']):
        raise ValueError('implementation query during independent capture')
    if raw['settings_after']!=composition['background_settings_before']:
        raise ValueError('native background settings changed')
    failure = failures[0]
    during = [r for r in raw['source'] if r['observed_ms']>=failure['observed_ms']]
    if len(during)<2:
        raise ValueError('no continued acquisition after failure')
    if mode=='revoke':
        grants = [e for e in events if e['event']=='consumer_policy']
        if len(launches)!=1 or len(grants)!=1 or grants[0]['revision']!=8 or grants[0]['permitted']:
            raise ValueError('revoked consumer admitted')
        if any(r['observed_ms']>=grants[0]['observed_ms'] for r in raw['delivery']):
            raise ValueError('operational delivery after revocation')
        return {'outcome':'pass','collection':'pass','policy':'pass','native_replacement':'not_authorized','pixels':'not_authorized'}
    if len(launches)!=2 or launches[1]['observed_ms']-failure['observed_ms']<1000:
        raise ValueError('bounded automatic replacement missing')
    stopped = [e for e in events if e['event']=='stopped' and e['pid']==old['pid']]
    if len(stopped)!=1 or not stopped[0]['os_confirmed'] or stopped[0]['observed_ms']>launches[1]['observed_ms']:
        raise ValueError('replacement before confirmed old exit')
    if not any(stopped[0]['observed_ms']<=r['observed_ms']<=launches[1]['observed_ms'] for r in raw['source']):
        raise ValueError('collection paused with consumer outage')
    new = raw['identities']['new_shell']; icon = raw['identities']['new_icon']
    if new['pid']!=launches[1]['pid'] or new['pid']==old['pid'] or new['start_ticks']<=old['start_ticks']:
        raise ValueError('replacement shell lifetime differs')
    if new['parent']!=controller['pid']:
        raise ValueError('replacement shell has different native parent')
    if new['arguments']!=old['arguments'] or new['executable']!=old['executable']:
        raise ValueError('replacement program differs')
    if not raw['old_icon_exited'] or icon['pid']==raw['identities']['old_icon']['pid']:
        raise ValueError('old icon manager substituted for replacement')
    for row in (new, icon):
        if row['session']!=controller['pid'] or row['process_group']!=controller['pid']:
            raise ValueError('replacement escaped persistent session')
    if not all(raw['final_live'][name] for name in ('new_shell','new_icon')):
        raise ValueError('replacement native lifetime ended')
    ready = raw['native_ready']
    if raw['old_icon_exit']['pid']!=raw['identities']['old_icon']['pid'] or not raw['old_icon_exit']['pidfd_exit'] or raw['old_icon_exit']['observed_ns']>ready['observed_ns']:
        raise ValueError('old icon exit ordering')
    if ready['manager']['pid']!=[new['pid']] or ready['bus_pid']!=new['pid']:
        raise ValueError('native replacement readiness missing')
    manager=ready['manager']
    if manager['self']!=[manager['window']] or manager['pid_origin']!='XResQueryClientIds' or manager['window'] & ~manager['resource_mask'] != manager['resource_base']:
        raise ValueError('replacement native resource binding')
    if ready['observed_ns']-raw['fault']['end_ns']>7_000_000_000:
        raise ValueError('replacement readiness deadline')
    baseline = rgb(composition['calibrations'][2]['frames'][0]['pixels'],180*220*3)
    calibrations = [rgb(stage['frames'][0]['pixels'],180*220*3) for stage in composition['calibrations'][:2]]
    anchors, _ = masks(baseline,calibrations)
    for row in raw['post']:
        data = rgb(row['icons'],len(baseline))
        if any(data[n*3:n*3+3]!=baseline[n*3:n*3+3] for group in anchors for n in group):
            raise ValueError('original icon anchors changed')
        if rgb(row['background'],128*96*3)!=bytes(FIXTURE['background_rgb'])*128*96:
            raise ValueError('original background pixels changed')
    pixels = visible(raw['post'],raw['calibration'],raw['delivery'],launches[1]['connection'])
    return {'outcome':'pass' if pixels else 'fail','collection':'pass','policy':'pass','native_replacement':'pass','pixels':'pass' if pixels else 'fail'}


def observe(display, environment, shell_pid, workspace, composition):
    from native_gnome_bootstrap import mapped_files
    controller = int(environment['SYSPANE_GNOME_CONTROLLER_PID']); mode = environment['SYSPANE_GNOME_CONTROLLER_CONTROL']
    raw = {'version':'0.1.0','mode':mode,'calls':[],'baseline':[],'outage':[],'post':[],'identities':{},'held_live':{},'final_live':{}}
    path = workspace/'network-controller-recovery.private.json'; descriptors = {}; pollers = {}
    connection = Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
    def hold(name,pid):
        fd = os.pidfd_open(pid); poller = select.poll(); poller.register(fd,select.POLLIN)
        descriptors[name]=fd;pollers[name]=poller;raw['identities'][name]=identity(pid);raw['held_live'][name]=not bool(poller.poll(0))
        if not raw['held_live'][name]:raise ValueError('held native process already exited')
    def call(method):
        begin=now();reply=connection.call_sync('org.gnome.Shell','/org/syspane/NetworkLive','org.syspane.NetworkLive',method,None,None,Gio.DBusCallFlags.NO_AUTO_START,1000,None).unpack()[0]
        raw['calls'].append({'method':method,'begin_ns':begin,'end_ns':now(),'reply':reply});return reply
    def capture(extra=False):
        begin=now();row={'begin_ns':begin,'pixels':rgb_record(display.capture(*RECT))}
        if extra:row.update(icons=rgb_record(display.capture(*FIXTURE['overlap'])),background=rgb_record(display.capture(*BACKGROUND_RECT)))
        row['end_ns']=now();return row
    try:
        hold('controller',controller);hold('old_shell',shell_pid);hold('old_icon',composition['icon_manager']['pid'])
        spawned=[r for r in controller_rows(workspace) if r['event']=='source_spawned'];assert len(spawned)==1
        hold('source',spawned[0]['pid'])
        raw['old_icon_mapped_files']=mapped_files(composition['icon_manager']['pid'])
        raw['bracket']=json.loads((workspace/'network-controller-bracket.private.json').read_text())
        assert call('Calibrate')=='calibrated';time.sleep(.2);raw['calibration']=capture();templates(raw['calibration']['pixels'])
        assert call('Start')=='starting'
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            state=json.loads(call('GetState'))
            if state['session'] and state['session']['phase']=='live':break
            time.sleep(.02)
        else:raise TimeoutError('first operational attachment')
        raw['old_shell_mapped_files']=mapped_files(shell_pid)
        time.sleep(.25);until=now()+2_200_000_000
        while now()<until:raw['baseline'].append(capture());time.sleep(.05)
        raw['fault']={'begin_ns':now(),'pid':shell_pid};signal.pidfd_send_signal(descriptors['old_shell'],signal.SIGKILL);raw['fault']['end_ns']=now()
        post_begin=None;new_pid=None;ready=None;end=raw['fault']['begin_ns']+10_000_000_000
        while now()<end:
            row=capture(extra=post_begin is not None);raw['outage'].append(row)
            if post_begin is not None:raw['post'].append(row)
            if 'old_shell_exit' not in raw and pollers['old_shell'].poll(0):
                raw['old_shell_exit']={'pid':shell_pid,'pidfd_exit':True,'observed_ns':now()}
            if 'old_icon_exit' not in raw and pollers['old_icon'].poll(0):
                raw['old_icon_exit']={'pid':raw['identities']['old_icon']['pid'],'pidfd_exit':True,'observed_ns':now()}
            events=controller_rows(workspace);launches=[r for r in events if r['event']=='consumer_spawned']
            if mode=='revoke':
                if 'old_shell_exit' in raw and now()-raw['old_shell_exit']['observed_ns']>=2_500_000_000:break
            else:
                if len(launches)>1 and new_pid is None:
                    new_pid=launches[1]['pid'];hold('new_shell',new_pid)
                if new_pid and ready is None:
                    manager=manager_identity(display,ResourceOwner(display))
                    if manager and manager['pid']==[new_pid] and pollers['old_icon'].poll(0):
                        try:icon=bind_icon_window(display,new_pid,workspace,controller)
                        except ValueError as error:
                            if str(error)!='ambiguous icon-manager window':raise
                            icon=None
                        if icon:
                            bus_pid=connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetConnectionUnixProcessID',GLib.Variant('(s)',('org.gnome.Shell',)),None,Gio.DBusCallFlags.NO_AUTO_START,100,None).unpack()[0]
                            if bus_pid==new_pid:
                                hold('new_icon',icon['pid']);ready={'manager':manager,'icon':icon,'bus_pid':bus_pid,'observed_ns':now()};raw['native_ready']=ready
                                key=display.x.XKeysymToKeycode(display.handle,display.x.XStringToKeysym(b'Escape'))
                                raw['overview_dismissal']={'begin_ns':now()}
                                for pressed in (True,False):
                                    if not display.xtest.XTestFakeKeyEvent(display.handle,key,pressed,0):raise ValueError('native overview dismissal')
                                display.x.XFlush(display.handle);raw['overview_dismissal']['end_ns']=now()
                if ready and post_begin is None and now()>=raw['overview_dismissal']['end_ns']+250_000_000:post_begin=now()
                if post_begin and now()-post_begin>=2_200_000_000:break
            time.sleep(.045)
        else:raise TimeoutError('native recovery interval')
        raw['old_icon_exited']=bool(pollers['old_icon'].poll(0))
        if mode!='revoke':raw['new_shell_mapped_files']=mapped_files(new_pid)
        raw['controller']=controller_rows(workspace)
        raw['source']=lines(Path(environment['SYSPANE_GNOME_CONTROLLER_SOURCE']),4*1024**2)
        raw['delivery']=lines(Path(environment['SYSPANE_GNOME_CONTROLLER_DELIVERY']),4*1024**2)
        raw['after']=linux_rows();raw['upper_ns']=now();raw['settings_after']=settings(environment)
        for name,poller in pollers.items():raw['final_live'][name]=not bool(poller.poll(0))
        raw['evaluation']=judge(raw,composition)
        return {'outcome':raw['evaluation']['outcome'],'evaluation':raw['evaluation'],'journal':str(path),
                'old_shell_mapped_files':raw['old_shell_mapped_files'],'old_icon_mapped_files':raw['old_icon_mapped_files']}
    except Exception as error:
        raw['error']=type(error).__name__+': '+str(error)
        raise
    finally:
        data=json.dumps(raw,indent=2)+'\n'
        if len(data.encode())>16*1024**2:raise ValueError('private controller pixel capacity')
        with path.open('x') as stream:path.chmod(0o600);stream.write(data)
        for fd in descriptors.values():os.close(fd)
