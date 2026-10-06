"""Independent public glyph/BOOTTIME oracle for the owned shell clock experiment."""
import json
import os
from pathlib import Path
import select
import time

import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib
from native_x11_host import rgb_record
from gnome_shell_recovery import process_identity
from gnome_composition import FIXTURE, bind_icon_window
from record_gnome_host import rgb

MODES = ('live', 'freeze-age', 'ignore-expiry', 'peer-exit', 'pending-disable', 'wrong-peer')
RECT = (300, 310, 448, 60)
FRESH, STALE = bytes((40, 200, 80)), bytes((240, 160, 40))
now = lambda: time.clock_gettime_ns(time.CLOCK_BOOTTIME)

def cell(data, column):
    return b''.join(data[((30+y)*448+column*14)*3:((30+y)*448+column*14+14)*3] for y in range(26))

def templates(pixels):
    data = rgb(pixels, 448*60*3)
    result = {digit: cell(data, i) for i, digit in enumerate('1234567890')}
    if len(set(result.values())) != 10 or bytes((20,30,40))*14*26 in result.values():
        raise ValueError('distinct public digit calibration required')
    return result

def decode(pixels, table):
    data = rgb(pixels, 448*60*3); inverse = {v:k for k,v in table.items()}
    text = ''; ended = False
    for column in range(16):
        value = cell(data, column)
        if value == bytes((20,30,40))*14*26:
            ended = True; continue
        if ended or value not in inverse:
            raise ValueError('unknown age glyph or gap')
        text += inverse[value]
    if not text or text != str(int(text)):
        raise ValueError('noncanonical age glyphs')
    indicator = b''.join(data[((30+y)*448+224)*3:((30+y)*448+244)*3] for y in range(26))
    if indicator not in (FRESH*20*26, STALE*20*26):
        raise ValueError('unknown native freshness indicator')
    return int(text), indicator == STALE*20*26

def judge(raw):
    mode = raw['mode']; table = templates(raw['calibration']['pixels'])
    if mode not in MODES:
        raise ValueError('clock mode')
    age_ok = status_ok = True
    ages = []; fresh = stale = 0; previous = None
    if mode not in ('pending-disable', 'wrong-peer'):
        stamp = int(raw['ready']['sample'])
        if not int(raw['ready']['before']) <= stamp <= int(raw['ready']['after']):
            raise ValueError('native peer bracket')
        for row in raw['samples']:
            begin, end = row['begin_ns'], row['end_ns']
            if not stamp <= begin <= end or end-begin > 50_000_000 or (previous is not None and not previous <= begin <= previous+150_000_000):
                raise ValueError('clock capture coverage')
            age, is_stale = decode(row['pixels'], table); ages.append(age)
            age_ok &= max(0, (begin-stamp)//1_000_000-200) <= age <= (end-stamp)//1_000_000
            if end < stamp+3_000_000_000:
                status_ok &= not is_stale; fresh += 1
            if begin >= stamp+3_200_000_000:
                status_ok &= is_stale; stale += 1
            previous = end
        minimum = 300 if mode == 'peer-exit' else 3000
        age_ok &= len(ages) >= (6 if mode == 'peer-exit' else 55) and all(a<=b for a,b in zip(ages,ages[1:])) and ages[-1]-ages[0] >= minimum
        if fresh < 3 or (mode != 'peer-exit' and stale < 3):
            raise ValueError('fresh/stale temporal witnesses missing')
    elif raw['samples'] or raw['final']['sample'] is not None:
        raise ValueError('sample published after failed/pending admission')
    blank = bytes(FIXTURE['background_rgb'])*448*60
    interval = raw['erasure']; previous = interval['begin_ns']; settled = 0
    for row in interval['samples']:
        begin, end = row['begin_ns'], row['end_ns']
        if not previous <= begin <= end <= begin+50_000_000 or begin-previous > 150_000_000:
            raise ValueError('clock erasure coverage')
        if begin >= interval['begin_ns']+200_000_000:
            settled += 1
            if rgb(row['pixels'], len(blank)) != blank:
                raise ValueError('clock tile survived closure')
        previous = end
    required = 800_000_000 if mode == 'pending-disable' else 400_000_000
    if settled < 3 or previous < interval['begin_ns']+required:
        raise ValueError('clock late-callback observation missing')
    final = raw['final']
    if not raw['exit']['pidfd_exit'] or final['pid'] != raw['exit']['pid'] or not final['exited'] or final['clock'] or final['connection'] or final['labels']:
        raise ValueError('native clock/child resources survived closure')
    expected_error = 'peer.process' if mode == 'wrong-peer' else 'clock.peer_exited' if mode == 'peer-exit' else None
    if final['error'] != expected_error or final['phase'] != ('failed' if expected_error else 'closed'):
        raise ValueError('clock final state differs')
    return {'outcome':'pass' if age_ok and status_ok else 'fail', 'age':'pass' if age_ok else 'fail',
        'expiry':'pass' if status_ok else 'fail', 'samples':len(ages), 'fresh_witnesses':fresh, 'stale_witnesses':stale}

def observe(display, environment, shell_pid, workspace, composition, trace_function):
    mode = environment['SYSPANE_GNOME_CLOCK_AGE']
    raw = {'version':'0.1.0', 'mode':mode, 'samples':[], 'calls':[]}
    path = workspace/'clock-age.json'; descriptor = None
    connection = Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],
        Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
    def save():
        data = json.dumps(raw, indent=2)+'\n'
        if len(data.encode()) > 8*1024**2: raise ValueError('clock evidence capacity')
        path.write_text(data)
    def call(method):
        begin = now()
        reply = connection.call_sync('org.gnome.Shell', '/org/syspane/ClockExperiment', 'org.syspane.ClockExperiment',
            method, None, None, Gio.DBusCallFlags.NO_AUTO_START, 1000, None).unpack()[0]
        raw['calls'].append({'method':method, 'begin_ns':begin, 'end_ns':now(), 'reply':reply})
        return reply
    def state(): return json.loads(call('GetState'))
    def until(predicate):
        deadline = time.monotonic()+2
        while time.monotonic()<deadline:
            value=state()
            if predicate(value):return value
            time.sleep(.02)
        raise AssertionError('clock state deadline: '+json.dumps(value))
    def capture():
        begin=now();pixels=rgb_record(display.capture(*RECT));return {'begin_ns':begin,'end_ns':now(),'pixels':pixels}
    try:
        assert composition['outcome']=='pass'
        raw['calibration']=capture();templates(raw['calibration']['pixels'])
        assert call('Start')=='starting'
        started=until(lambda s:s['pid'] is not None)
        pid=started['pid'];descriptor=os.pidfd_open(pid)
        raw['peer']=process_identity(pid)
        assert raw['peer']['session']==shell_pid and raw['peer']['process_group']==shell_pid
        assert raw['peer']['arguments']==['/usr/bin/python3',environment['SYSPANE_GNOME_CLOCK_HELPER'],environment['SYSPANE_GNOME_CLOCK_SOCKET'],'slow-ready' if mode=='pending-disable' else 'normal']
        if mode=='pending-disable':
            journal=workspace/'clock-peer.jsonl';deadline=time.monotonic()+.5
            while time.monotonic()<deadline and not journal.exists():time.sleep(.01)
            assert journal.exists() and started['sample'] is None
            assert call('Disable')=='closed';origin=raw['calls'][-1]['end_ns']
        elif mode=='wrong-peer':
            failed=until(lambda s:s['phase']=='failed')
            assert failed['error']=='peer.process' and failed['sample'] is None
            origin=now()
        else:
            raw['ready']=until(lambda s:s['phase']=='ready')
            deadline=now()+(650_000_000 if mode=='peer-exit' else 3_600_000_000)
            time.sleep(.12)
            while now()<deadline:
                raw['samples'].append(capture());time.sleep(.05)
            if mode=='peer-exit':
                assert call('StopPeer')=='requested'
                assert select.select([descriptor],[],[],1)[0]
                origin=now()
            else:
                assert call('Disable')=='closed';origin=raw['calls'][-1]['end_ns']
        assert select.select([descriptor],[],[],1)[0]
        raw['exit']={'pid':pid,'pidfd_exit':True,'observed_ns':now()}
        raw['erasure']={'begin_ns':origin,'samples':[]}
        duration=850_000_000 if mode=='pending-disable' else 450_000_000
        while now()<origin+duration:
            raw['erasure']['samples'].append(capture());time.sleep(.05)
        raw['final']=until(lambda s:s['exited'])
        assert raw['final']['exitStatus']==0, 'clock peer did not exit normally'
        assert call('Start')=='closed' and call('Disable')=='closed'
        raw['post']=trace_function(display,environment,dismiss=False)
        assert raw['post']['evaluation']['outcome']=='pass'
        assert bind_icon_window(display,shell_pid,workspace)==composition['icon_manager']
        raw['peer_journal']=[json.loads(line) for line in (workspace/'clock-peer.jsonl').read_text().splitlines()]
        samples=[r for r in raw['peer_journal'] if r['event']=='sample']
        assert len(samples)==(0 if mode in ('pending-disable','wrong-peer') else 1)
        if samples:assert samples[0]['sample_ns']==raw['ready']['sample']
        assert all(r['pid']==pid and r['parent']==shell_pid and r['session']==shell_pid for r in raw['peer_journal'])
        raw['evaluation']=judge(raw);save()
        return {'control':mode,'evaluation':raw['evaluation'],'peer':raw['peer'],'journal':str(path)}
    except Exception as error:
        raw['error']=type(error).__name__+': '+str(error);save();raise
    finally:
        if descriptor is not None:os.close(descriptor)
        connection.close_sync(None)
