"""Independent render-watch experiment; operational originals/crops stay private."""
import json
import os
from pathlib import Path
import select
import signal
import time
from gnome_live_network import (RECT, now, templates, decode, originals, linux_rows,
                                route_sockets, rgb_record, rgb, FIXTURE, Gio)
from gnome_shell_recovery import process_identity
from gnome_composition import bind_icon_window
from oracle import evaluate

MODES = ('live', 'render-stall', 'false-progress', 'hidden', 'revoke',
         'watch-exit', 'watch-hang', 'shell-freeze')
mono = lambda: time.monotonic_ns() // 1_000_000
BLANK = bytes(FIXTURE['background_rgb']) * RECT[2] * RECT[3]


def timeline(rows, start=None):
    previous = start
    for row in rows:
        begin, end = row['begin_ns'], row['end_ns']
        if not begin <= end <= begin + 50_000_000:
            raise ValueError('capture duration')
        if previous is not None and not previous <= begin <= previous + 150_000_000:
            raise ValueError('capture coverage')
        if not 0 <= row['mono_end_ms'] - row['mono_begin_ms'] <= 51:
            raise ValueError('monotonic capture duration')
        # The two clocks may have a suspend offset; their elapsed durations agree.
        if abs((end-begin)//1_000_000 - (row['mono_end_ms']-row['mono_begin_ms'])) > 2:
            raise ValueError('capture clocks disagree')
        previous = end
    if not rows:
        raise ValueError('capture interval missing')


def judge(raw):
    mode = raw['mode']
    if mode not in MODES:
        raise ValueError('render mode')
    table = templates(raw['calibration']['pixels'])
    expected, stamp = originals(raw)
    baseline, samples = raw['baseline'], raw['samples']
    timeline(baseline); timeline(samples)
    captures = [raw['calibration'], *baseline, *samples, *raw['erasure']['samples'], raw['post_clear']]
    offset = captures[0]['begin_ns']//1_000_000-captures[0]['mono_begin_ms']
    if any(abs(r['begin_ns']//1_000_000-r['mono_begin_ms']-offset)>2 for r in captures):
        raise ValueError('native capture clock relationship changed')
    checks = dict(values=True, age=True, freshness=True, lease=True, erasure=True)

    def measured(rows):
        ages = []
        for row in rows:
            begin, end = row['begin_ns'], row['end_ns']
            values, age, stale, expired = decode(row['pixels'], table)
            checks['values'] &= values == expected
            checks['age'] &= max(0, (begin-stamp)//1_000_000-200) <= age <= (end-stamp)//1_000_000
            if end < stamp+3_000_000_000:
                checks['freshness'] &= not stale
            if begin >= stamp+3_200_000_000:
                checks['freshness'] &= stale
            checks['lease'] &= not expired
            ages.append(age)
        checks['age'] &= all(a <= b for a, b in zip(ages, ages[1:]))
        return ages

    ages = measured(baseline)
    if len(ages) < 22 or baseline[-1]['end_ns']-baseline[0]['begin_ns'] < 1_300_000_000 or ages[-1]-ages[0] < 1000:
        raise ValueError('advancing baseline missing')
    if not all(checks.values()):
        raise ValueError('baseline source/pixels differ')
    if not all(all(r['alive'].values()) for r in baseline):
        raise ValueError('baseline native lifetime missing')
    stimulus = raw['stimulus']
    journal = raw['watch_journal']
    if not journal or journal[0]['event'] != 'ready':
        raise ValueError('watcher original start missing')
    trace = raw['final']['renderTrace']; previous = 0
    for item in trace:
        if item['event'] not in ('challenge','draw','paint','false-progress','fault') or item['monotonic_us'] < previous:
            raise ValueError('render trace order/type')
        previous = item['monotonic_us']
    pending = None; completed = 0; faults = []; issued = {}; progress = []; previous = 0
    for row in journal:
        when = row['observed_ms']
        if when < previous:
            raise ValueError('original watcher clock order')
        previous = when
        event = row['event']
        if faults:
            raise ValueError('watcher events after latched fault')
        if event == 'challenge':
            generation = row['generation']
            if pending is not None or generation != len(issued)+1 or not 0 <= when-row['issued_ms'] <= 100:
                raise ValueError('challenge overlap/identity/time')
            pending = generation; issued[generation] = row['issued_ms']
        elif event == 'progress':
            generation = row['generation']; completed += 1
            if generation != pending or row['completed'] != completed or not 0 <= when-issued[generation] < 3000:
                raise ValueError('unexpected or late native completion')
            related = [t for t in trace if t['generation'] == str(generation)]
            names = [t['event'] for t in related]
            if names == ['challenge','false-progress'] and mode == 'false-progress':
                if related[0]['monotonic_us']//1000 < stimulus['mono_end_ms']:
                    raise ValueError('false progress before injection')
            elif len(names) < 3 or names[0] != 'challenge' or names[-1] != 'paint' or any(n != 'draw' for n in names[1:-1]):
                raise ValueError('completion lacks operational draw/paint')
            if not issued[generation] <= related[0]['monotonic_us']//1000 <= related[-1]['monotonic_us']//1000 <= when:
                raise ValueError('completion causality')
            progress.append(row); pending = None
        elif event == 'fault':
            if row['pending'] != pending or row['completed'] != completed:
                raise ValueError('latched fault state differs')
            received = [r for r in journal if r['event']=='heartbeat' and r['direction']=='received' and r['observed_ms']<=when]
            if not received or abs(when-received[-1]['observed_ms']-row['since_heartbeat_ms'])>2:
                raise ValueError('fault heartbeat age differs from original receipt')
            if pending is None or abs(when-issued[pending]-row['since_challenge_ms'])>2:
                raise ValueError('fault challenge age differs from original issue')
            if row['reason']=='health.expired' and (row['health_alive'] or not 3000<=row['since_heartbeat_ms']<=3200):
                raise ValueError('independent health deadline')
            faults.append(row)
        elif event not in ('ready','authenticated','heartbeat','complete'):
            raise ValueError('watcher event type')
    if len([r for r in progress if r['observed_ms'] <= stimulus['mono_begin_ms']]) < 2:
        raise ValueError('two baseline paint completions required')
    expected_fault = mode in ('render-stall','hidden','shell-freeze')
    if len(faults) != int(expected_fault):
        raise ValueError('independent native fault coverage')
    if mode in ('render-stall','hidden'):
        fault = faults[0]
        if fault['reason'] != 'render.stalled' or pending is None or not 3000 <= fault['since_challenge_ms'] <= 3200:
            raise ValueError('independent render deadline')
        if not fault['health_alive'] or not 0 <= fault['since_heartbeat_ms'] < 1200:
            raise ValueError('render stall confused with process health')
        waiting = [r for r in samples if r['mono_end_ms'] < fault['observed_ms']]
        if not waiting or not all(all(r['alive'].values()) for r in waiting):
            raise ValueError('render fault lacks living native processes')
    if mode in ('render-stall','false-progress','shell-freeze'):
        limit = faults[0]['observed_ms'] if faults else samples[-1]['mono_end_ms']
        frozen = [r for r in samples if r['mono_begin_ms'] >= stimulus['mono_end_ms']+200 and r['mono_end_ms'] < limit]
        if len(frozen) < 25 or frozen[-1]['mono_end_ms']-frozen[0]['mono_begin_ms'] < 1500:
            raise ValueError('frozen pixel interval missing')
        ages = [decode(r['pixels'], table)[1] for r in frozen]
        if len(set(ages)) != 1:
            raise ValueError('injected drawing stop did not freeze pixels')
        if mode == 'false-progress':
            measured(frozen)
            if len([r for r in progress if r['observed_ms'] > stimulus['mono_end_ms']]) < 3 or checks['age']:
                raise ValueError('false progress failed to expose stale pixels')
    if mode == 'hidden':
        hidden = [r for r in samples if r['mono_begin_ms'] >= stimulus['mono_end_ms']+200]
        if len(hidden) < 25 or any(rgb(r['pixels'],len(BLANK)) != BLANK for r in hidden):
            raise ValueError('hidden drawing remained visible')
    if mode == 'live':
        measured(samples)
        if samples[-1]['end_ns']-samples[0]['begin_ns'] < 1_800_000_000:
            raise ValueError('live coverage')
    interval = raw['erasure']; origin = interval['mono_begin_ms']; rows = interval['samples']
    timeline(rows)
    if not origin <= rows[0]['mono_begin_ms'] <= origin+150 or not origin+400 <= rows[-1]['mono_end_ms'] <= origin+550:
        raise ValueError('erasure deadline coverage')
    settled = [r for r in rows if r['mono_begin_ms'] >= origin+200]
    if len(settled) < 3:
        raise ValueError('settled erasure missing')
    checks['erasure'] = all(rgb(r['pixels'],len(BLANK)) == BLANK for r in settled)
    if rgb(raw['post_clear']['pixels'],len(BLANK)) != BLANK:
        raise ValueError('final pixels retained')
    if mode in ('render-stall','hidden') and origin != faults[0]['observed_ms']:
        raise ValueError('fault erasure clock rebased')
    if mode == 'shell-freeze':
        resume = raw['signals'][-1]
        if resume['signal'] != 'SIGCONT' or origin != resume['mono_end_ms'] or not stimulus['mono_end_ms'] <= faults[0]['observed_ms'] <= resume['mono_begin_ms']:
            raise ValueError('shell resumed before independent fault')
        if faults[0]['reason'] not in ('render.stalled','health.expired'):
            raise ValueError('shell freeze fault missing')
    if mode == 'watch-hang':
        receipts = raw['final']['watch']['receipts']
        heartbeat = [int(r['observed_ms']) for r in receipts if r['kind'] == 'heartbeat']
        if not heartbeat or origin != max(heartbeat)+3000:
            raise ValueError('silent watcher deadline rebased')
    final = raw['final']
    if final['labels'] or final['paintSignal'] or final['pending'] is not None or final['staged'] is not None:
        raise ValueError('render lifetime survived closure')
    for key in ('session','watch'):
        state = final[key]
        if state['view'] or state['connection'] or state['queuedBytes'] or not state['exited'] or state['phase'] not in ('closed','failed'):
            raise ValueError('native owner resources survived')
        if state['forced'] != (key == 'watch' and mode == 'watch-hang'):
            raise ValueError('unexpected force exit')
    source = final['session']
    if mode == 'shell-freeze' and source['exitStatus'] == 1:
        failures = [r for r in source['events'] if r['event']=='error']
        if len(failures)!=1 or failures[0]['code'] not in ('health.eof','collector.data_eof','collector.child_exited','clock.peer_exited') or source['phase']!='failed' or source['error'] not in ('clock.peer_exited','session.peer_exited','session.peer_failed','session.eof'):
            raise ValueError('concurrent consumer expiry lacks original failure')
    elif source['exitStatus'] != 0 or source['error'] is not None:
        raise ValueError('collector did not shut down normally')
    expected_exit = -signal.SIGKILL if mode in ('watch-exit','watch-hang') else 1 if expected_fault else 0
    if final['watch']['exitStatus'] != expected_exit or bool(final['watch']['error']) != (expected_fault or mode in ('watch-exit','watch-hang')):
        raise ValueError('watcher native outcome differs')
    if final['watch']['phase'] != ('failed' if final['watch']['error'] else 'closed'):
        raise ValueError('watcher failure relabeled closed')
    if mode == 'watch-hang' and final['watch']['error'] != 'health.peer_expired':
        raise ValueError('native silent watcher expiry missing')
    if set(raw['exits']) != {'supervisor','worker','watcher'} or not all(r['pidfd_exit'] for r in raw['exits'].values()):
        raise ValueError('held native exit proof missing')
    if not raw['watch_registered'] or not raw['same_time_namespace'] or raw['shell_before'] != raw['shell_after']:
        raise ValueError('native source/clock/shell lifetime changed')
    if evaluate(raw['post']['trace']) != raw['post']['evaluation'] or raw['post']['evaluation']['outcome'] != 'pass':
        raise ValueError('post-clear marker failed')
    for rows in (baseline,samples):
        if any(rows[0]['begin_ns'] <= c['begin_ns'] <= rows[-1]['end_ns'] for c in raw['calls']):
            raise ValueError('diagnostic call drove observed pixels')
    # Stale/fresh indicators also freeze in the lying control; the decisive failure is age.
    return {'outcome':'pass' if all(checks.values()) else 'fail',
            **{key:'pass' if value else 'fail' for key,value in checks.items()},
            'completions':completed,'faults':len(faults),'baseline_samples':len(baseline),
            'samples':len(samples),'erasure_samples':len(interval['samples'])}


def observe(display, environment, shell_pid, workspace, composition, trace_function):
    mode = environment['SYSPANE_GNOME_RENDER_WATCH']
    raw = dict(version='0.1.0',mode=mode,baseline=[],samples=[],calls=[],signals=[],peers={},exits={})
    path = workspace/'network-render-watch.private.json'
    producer_path = Path(environment['SYSPANE_GNOME_NETWORK_JOURNAL'])
    watch_path = Path(environment['SYSPANE_GNOME_WATCH_JOURNAL'])
    descriptors = {}; stopped = set()
    connection = Gio.DBusConnection.new_for_address_sync(environment['DBUS_SESSION_BUS_ADDRESS'],
        Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)

    def save():
        content = (json.dumps(raw,indent=2)+'\n').encode()
        if len(content) > 16*1024**2: raise ValueError('private evidence capacity')
        with path.open('wb') as stream: path.chmod(0o600); stream.write(content)

    def journal(source, maximum):
        data = source.read_bytes() if source.exists() else b''
        if len(data) > maximum: raise ValueError('original journal capacity')
        return [json.loads(line) for line in data.splitlines(keepends=True) if line.endswith(b'\n')]

    def watch(): return journal(watch_path,64*1024)

    def call(method):
        start, clock = now(), mono()
        reply = connection.call_sync('org.gnome.Shell','/org/syspane/NetworkLive','org.syspane.NetworkLive',
            method,None,None,Gio.DBusCallFlags.NO_AUTO_START,1000,None).unpack()[0]
        raw['calls'].append(dict(method=method,begin_ns=start,end_ns=now(),mono_begin_ms=clock,mono_end_ms=mono(),reply=reply))
        return reply

    def state(): return json.loads(call('GetState'))

    def until(predicate):
        deadline = time.monotonic()+2
        while time.monotonic() < deadline:
            value = state()
            if predicate(value): return value
            time.sleep(.02)
        raise AssertionError('native render lifecycle deadline')

    def alive(role): return not bool(select.select([descriptors[role]],[],[],0)[0])

    def capture():
        start, clock = now(), mono(); pixels = rgb_record(display.capture(*RECT))
        return dict(begin_ns=start,end_ns=now(),mono_begin_ms=clock,mono_end_ms=mono(),pixels=pixels,
                    alive={role:alive(role) for role in ('supervisor','worker','watcher') if role in descriptors})

    def collect(destination, duration):
        deadline = mono()+duration
        while mono() < deadline: destination.append(capture()); time.sleep(.05)

    def send(role, sig):
        assert alive(role), 'held process already exited'
        start, clock = now(), mono()
        signal.pidfd_send_signal(descriptors[role],sig)
        if sig == signal.SIGSTOP: stopped.add(role)
        elif sig == signal.SIGCONT: stopped.discard(role)
        deadline = time.monotonic()+.5
        while time.monotonic() < deadline:
            if sig == signal.SIGKILL:
                if not alive(role): break
            else:
                state_code = Path('/proc/'+str(raw['peers'][role]['pid'] if role!='shell' else shell_pid)+'/stat').read_text().rsplit(')',1)[1].split()[0]
                if (state_code in ('T','t')) == (sig == signal.SIGSTOP): break
            time.sleep(.002)
        else: raise AssertionError('held process signal observation deadline')
        record = dict(role=role,pid=raw['peers'][role]['pid'] if role!='shell' else shell_pid,signal=sig.name,
                      begin_ns=start,end_ns=now(),mono_begin_ms=clock,mono_end_ms=mono(),confirmed=True)
        raw['signals'].append(record); return record

    try:
        assert composition['outcome'] == 'pass'
        raw['shell_before'] = process_identity(shell_pid); descriptors['shell'] = os.pidfd_open(shell_pid)
        assert call('Calibrate') == 'calibrated'; time.sleep(.2)
        raw['calibration'] = capture(); templates(raw['calibration']['pixels'])
        raw.update(before=linux_rows(),lower_ns=now())
        assert call('Start') == 'starting'
        started = until(lambda s:s['watch'] and s['watch']['phase']=='live')
        supervisor = started['session']['pid']; worker = next(r['pid'] for r in started['session']['events'] if r['event']=='spawned')
        for role,pid in [('supervisor',supervisor),('worker',worker),('watcher',started['watch']['pid'])]:
            descriptors[role] = os.pidfd_open(pid); raw['peers'][role] = process_identity(pid)
            assert alive(role), 'native descendant already exited'
            assert raw['peers'][role]['session'] == raw['peers'][role]['process_group'] == shell_pid, 'owned shell session'
        namespace = lambda pid:(os.stat(f'/proc/{pid}/ns/time').st_dev,os.stat(f'/proc/{pid}/ns/time').st_ino)
        raw['same_time_namespace'] = len({namespace(os.getpid()),namespace(shell_pid),*(namespace(r['pid']) for r in raw['peers'].values())}) == 1
        raw['watch_registered'] = bool(route_sockets(worker))
        time.sleep(.2); collect(raw['baseline'],1400)
        if mode in ('render-stall','hidden','false-progress'):
            assert call('Fault') == 'faulted'; raw['stimulus'] = raw['calls'][-1]
        elif mode in ('watch-exit','watch-hang','shell-freeze'):
            raw['stimulus'] = send('shell' if mode=='shell-freeze' else 'watcher',signal.SIGKILL if mode=='watch-exit' else signal.SIGSTOP)
        elif mode == 'revoke':
            assert call('Revoke') == 'cleared'; raw['stimulus'] = raw['calls'][-1]
        else:
            raw['stimulus'] = dict(begin_ns=now(),end_ns=now(),mono_begin_ms=mono(),mono_end_ms=mono(),method='Observe')

        origin = None
        if mode in ('render-stall','hidden','shell-freeze'):
            deadline = mono()+5000
            while mono() < deadline:
                raw['samples'].append(capture())
                faults = [r for r in watch() if r['event']=='fault']
                if faults:
                    origin = faults[0]['observed_ms']; break
                time.sleep(.05)
            else: raise AssertionError('independent native fault deadline')
            if mode == 'shell-freeze': origin = send('shell',signal.SIGCONT)['mono_end_ms']
        elif mode == 'watch-hang':
            collect(raw['samples'],4500)
            final = until(lambda s:s['watch']['phase']=='failed')
            origin = max(int(r['observed_ms']) for r in final['watch']['receipts'] if r['kind']=='heartbeat')+3000
        elif mode in ('watch-exit','revoke'):
            origin = raw['stimulus']['mono_end_ms']
        else:
            collect(raw['samples'],3600 if mode=='false-progress' else 2000)
            assert call('Stop') == 'stopping'; origin = raw['calls'][-1]['mono_end_ms']
        tail = []
        while mono() < origin+450: tail.append(capture()); time.sleep(.05)
        if mode in ('watch-exit','revoke'): raw['samples'] = tail.copy()
        erasure = [r for r in raw['samples']+tail if origin <= r['mono_begin_ms'] < origin+450]
        # A killed/revoked peer has only one capture stream, not a duplicated interval.
        if mode in ('watch-exit','revoke'): erasure = tail
        raw['erasure'] = dict(mono_begin_ms=origin,samples=erasure)
        for role in ('supervisor','worker','watcher'):
            assert select.select([descriptors[role]],[],[],2)[0], 'native descendant exit deadline'
            raw['exits'][role] = dict(pid=raw['peers'][role]['pid'],pidfd_exit=True,observed_ns=now())
        until(lambda s:s['watch']['phase'] in ('closed','failed') and s['session']['phase'] in ('closed','failed'))
        assert call('Cleanup') == 'cleared'; time.sleep(.2)
        raw['post_clear'] = capture(); raw['final'] = state()
        assert call('Start') == 'closed'
        raw.update(after=linux_rows(),upper_ns=now(),producer=journal(producer_path,4*1024**2),watch_journal=watch())
        raw['shell_after'] = process_identity(shell_pid)
        raw['post'] = trace_function(display,environment,dismiss=False)
        assert bind_icon_window(display,shell_pid,workspace) == composition['icon_manager'], 'icon manager changed'
        raw['evaluation'] = judge(raw); save()
        return dict(control=mode,evaluation=raw['evaluation'],peers=raw['peers'],journal=str(path),
                    disclosure='Operational source/pixel evidence remains private; native health journal contains lifecycle only.')
    except Exception as error:
        raw['error'] = type(error).__name__+': '+str(error); save(); raise
    finally:
        for role in stopped:
            if alive(role): signal.pidfd_send_signal(descriptors[role],signal.SIGCONT)
        for fd in descriptors.values(): os.close(fd)
        connection.close_sync(None)
