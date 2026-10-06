"""Replace only an owned GNOME shell; independently preserve the complete outage."""
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time

from gnome_composition import FIXTURE, masks, settings, judge_samples
from gnome_icon_recovery import safe_icon
from gnome_reveal import issue
from native_x11_host import rgb_record
from oracle import decode, evaluate, pack_frame, unpack_frame
from x11_recovery import ResourceOwner, manager_identity

CONTROLS = ['live', 'no-reattach', 'no-restart']


def process_identity(pid):
    path = Path('/proc') / str(pid)
    fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
    raw = (path / 'cmdline').read_bytes()
    if len(raw) > 16384:
        raise ValueError('shell argument capacity')
    return {'pid': pid, 'start_ticks': int(fields[19]), 'process_group': int(fields[2]),
            'session': int(fields[3]), 'executable': str((path / 'exe').resolve(strict=True)),
            'arguments': [s.decode() for s in raw.rstrip(b'\0').split(b'\0')]}


class Parent:
    def __init__(self, shell, command, launch, channel, control, report):
        self.shell, self.command, self.launch, self.channel = shell, command, launch, channel
        self.control, self.report, self.armed, self.replacement = control, report, False, None
        report['shell_recovery_parent'] = []

    def receive(self, message):
        if 'shell_recovery_request' not in message:
            return False
        request = message['shell_recovery_request']
        row = {'message': message, 'received_ns': time.monotonic_ns()}
        self.report['shell_recovery_parent'].append(row)
        if message != {'shell_recovery_request': request, 'pid': self.shell.pid}:
            raise ValueError('shell recovery parent message shape')
        if request == 'arm' and not self.armed and self.shell.poll() is None:
            self.armed = True
            response = {'armed': self.shell.pid}
        elif request == 'restart' and self.armed and self.replacement is None and self.control != 'no-restart':
            if self.shell.poll() != -signal.SIGKILL:
                raise ValueError('retained original shell exit not confirmed before replacement')
            self.replacement = self.launch('shell-replacement', self.command)
            response = {'replacement_started': self.replacement.pid, 'old_exit': self.shell.returncode}
        else:
            raise ValueError('unexpected shell recovery request/state')
        row.update(response=response, responded_ns=time.monotonic_ns())
        self.channel.send(response)
        return True


def bridge_peer(environment, pid):
    base = ['/usr/bin/gdbus', 'call', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
            '--dest', 'org.freedesktop.DBus', '--object-path', '/org/freedesktop/DBus',
            '--method', 'org.freedesktop.DBus.GetConnectionUnixProcessID', 'org.gnome.Shell']
    peer = subprocess.run(base, env=environment, capture_output=True, text=True, timeout=1)
    if peer.returncode or peer.stdout.strip() != '(uint32 ' + str(pid) + ',)':
        return None
    command = ['/usr/bin/gdbus', 'introspect', '--address', environment['DBUS_SESSION_BUS_ADDRESS'],
               '--dest', 'org.gnome.Shell', '--object-path', '/org/syspane/LabMarker', '--xml']
    result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=1)
    if result.returncode or len(result.stdout) > 16384:
        return None
    if 'name="SetGeneration"' not in result.stdout or 'name="SetSceneEnabled"' not in result.stdout:
        return None
    return {'pid': pid, 'peer_reply': peer.stdout.strip(), 'interface_xml': result.stdout}


def judge(result, composition):
    from record_gnome_host import rgb
    samples = result['samples']; events = result['events']; control = result['control']
    if not 3 <= len(samples) <= 200 or not 0 < result['end_us'] <= 10000000:
        raise ValueError('shell recovery interval bounds')
    event = lambda name: next(e for e in events if e['event'] == name)
    stop, exited = event('stop'), event('shell-exit')
    if not 250000 <= stop['start_us'] <= 300000 or not stop['start_us'] <= stop['end_us'] <= stop['start_us'] + 50000:
        raise ValueError('shell fault schedule')
    if stop['binding'] != result['old_shell'] or not stop['held_live'] or stop['pid'] != result['old_process']['pid']:
        raise ValueError('shell fault ownership')
    if exited['observer'] != 'pidfd' or not exited['readable'] or exited['pid'] != stop['pid'] or not stop['end_us'] <= exited['at_us'] <= stop['end_us'] + 2000000:
        raise ValueError('shell exit proof/deadline')
    if len([s for s in samples if s['end_us'] < stop['start_us']]) < 3:
        raise ValueError('pre-fault capture coverage')
    last = gap = duration = 0
    for row in samples:
        frame = row['marker']
        decoded = decode(unpack_frame(frame))
        if frame['origin'] != 'display_server_root' or (frame['end_us'] < stop['start_us'] and decoded != 4):
            raise ValueError('original marker/capture provenance')
        if not last <= frame['start_us'] <= frame['end_us'] <= row['start_us'] <= row['native_at_us'] <= row['end_us'] <= result['end_us']:
            raise ValueError('shell recovery paired capture order')
        gap = max(gap, frame['start_us'] - last); duration = max(duration, row['end_us'] - frame['start_us']); last = row['end_us']
        rgb(row['overlap'], 180*220*3); rgb(row['background'], 128*96*3)
        if row['native_at_us'] >= exited['at_us'] and not row['old_shell_exited']:
            raise ValueError('old shell resurrected')
    gap = max(gap, result['end_us'] - last)
    if gap > 150000 or duration > 50000:
        raise ValueError('shell recovery capture coverage')
    if control == 'no-restart':
        if [e['event'] for e in events] != ['stop', 'shell-exit'] or 'post' in result or 'new_process' in result:
            raise ValueError('omitted restart invented dependent work')
        if not 2500000 <= result['end_us'] - exited['at_us'] <= 2600000:
            raise ValueError('omitted restart duration')
        return {'native': 'fail', 'marker': 'not_run', 'icons': 'not_run', 'rectangle': 'not_run',
                'background': 'not_run', 'max_gap_us': gap, 'max_capture_us': duration, 'outcome': 'fail'}
    expected = ['stop', 'shell-exit', 'restart-request', 'replacement-started', 'native-ready', 'reattach']
    if [e['event'] for e in events] != expected:
        raise ValueError('shell replacement event sequence')
    request, launch, ready, attach = [event(n) for n in expected[2:]]
    old, new = result['old_process'], result['new_process']
    if not exited['at_us'] + 350000 <= request['at_us'] <= exited['at_us'] + 400000:
        raise ValueError('observed manager absence interval')
    if not request['at_us'] <= launch['at_us'] <= ready['at_us'] <= request['at_us'] + 5000000:
        raise ValueError('replacement readiness deadline')
    if new['pid'] != launch['pid'] or new['pid'] == old['pid'] or new['start_ticks'] <= old['start_ticks'] or new['arguments'] != old['arguments'] or new['executable'] != old['executable']:
        raise ValueError('replacement shell lifetime/command')
    if new['process_group'] != new['pid'] or new['session'] != new['pid'] or launch['old_exit'] != -9:
        raise ValueError('replacement shell group or retained old exit')
    manager, icon = result['new_shell'], result['new_icon']
    if manager['pid'] != [new['pid']] or manager['self'] != [manager['window']] or manager['pid_origin'] != 'XResQueryClientIds' or manager['window'] & ~manager['resource_mask'] != manager['resource_base']:
        raise ValueError('replacement native manager resource')
    if icon['pid'] == result['old_icon']['pid'] or icon['start_ticks'] <= result['old_icon']['start_ticks'] or icon['arguments'] != result['old_icon']['arguments'] or icon['executable'] != result['old_icon']['executable'] or icon['process_group'] != new['pid'] or icon['session'] != new['pid']:
        raise ValueError('replacement DING identity')
    if ready['shell'] != manager or ready['icon'] != icon or not ready['old_icon_exited'] or ready['peer']['pid'] != new['pid'] or ready['peer']['peer_reply'] != '(uint32 ' + str(new['pid']) + ',)':
        raise ValueError('replacement readiness bindings')
    if not ready['at_us'] <= attach['start_us'] <= attach['end_us'] <= ready['at_us'] + 500000 or attach['performed'] != (control == 'live'):
        raise ValueError('bridge reattachment action')
    if result['post']['started_monotonic_ns'] < result['started_monotonic_ns'] + (attach['end_us'] + 250000)*1000:
        raise ValueError('post-recovery settling interval')
    for row in samples:
        if row['native_at_us'] >= ready['at_us'] and (row['shell'] != manager or row['icon'] != icon or not row['new_shell_live'] or not row['new_icon_live'] or not row['old_icon_exited']):
            raise ValueError('replacement native lifetime not retained')
    post = result['post']; trace = post['trace']; progress = evaluate(trace)
    if trace['end_us'] != 2400000 or [s['generation'] for s in trace['stimuli']] != [5,6,7] or any(s.startswith('capture.') for s in progress['uncertainty']):
        raise ValueError('post-recovery marker scenario/coverage')
    if len(trace['frames']) != len(post['overlap_samples']):
        raise ValueError('post-recovery paired samples')
    calibration = [rgb(s['frames'][0]['pixels'],180*220*3) for s in composition['calibrations']]
    pixels = judge_samples(calibration[2],post['overlap_samples'],calibration[:2])
    offset = (post['started_monotonic_ns'] - result['started_monotonic_ns']) // 1000
    observed = [r for r in samples if r.get('post_frame') is not None]
    if len(observed) != len(trace['frames']):raise ValueError('post interval differs from complete outage journal')
    for row,frame,overlap in zip(observed,trace['frames'],post['overlap_samples']):
        if row['post_frame'] != frame or any(frame[k] != row['marker'][k] for k in ['origin','rgb_sha256','rgb_zlib_base64']) or abs(frame['start_us'] + offset - row['marker']['start_us']) > 1:
            raise ValueError('post frame not sourced from raw recovery capture')
        if overlap['pixels'] != row['overlap'] or overlap['start_us'] != row['start_us'] - offset or overlap['end_us'] != row['end_us'] - offset:
            raise ValueError('post composition differs from raw recovery capture')
    background = 'pass' if all(rgb(r['background'],128*96*3) == bytes(FIXTURE['background_rgb'])*128*96 for r in observed) else 'fail'
    expected_pixels = ('pass','pass') if control == 'live' else ('fail','fail')
    if (progress['outcome'],pixels['rectangle']) != expected_pixels or pixels['icons'] != 'pass' or background != 'pass':
        raise ValueError('native replacement produced unexpected visual result')
    return {'native':'pass','marker':progress['outcome'],'icons':pixels['icons'],'rectangle':pixels['rectangle'],
            'background':background,'max_gap_us':gap,'max_capture_us':duration,
            'outcome':'pass' if control=='live' else 'fail'}


def observe(display, environment, shell_pid, workspace, composition, trace_function, channel):
    from native_gnome_bootstrap import mapped_files
    control = environment['SYSPANE_GNOME_SHELL_RECOVERY']
    result = {'version':'0.1.0','control':control,'old_shell':manager_identity(display,ResourceOwner(display)),
              'old_process':process_identity(shell_pid),'old_icon':composition['icon_manager'],
              'old_shell_mapped_files':mapped_files(shell_pid),'old_icon_mapped_files':mapped_files(composition['icon_manager']['pid']),
              'settings_before':settings(environment),'events':[],'samples':[],'not_run':['post-recovery-input']}
    journal = (workspace/'shell-recovery.jsonl').open('x',encoding='utf-8',newline='\n')
    descriptors = []; count = 0
    def preserve(kind,value):
        nonlocal count
        count += 1
        if count > 240:raise ValueError('shell recovery record capacity')
        journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        if journal.tell() > 12*1024**2:raise ValueError('shell recovery journal capacity')
    def held(pid):
        fd=os.pidfd_open(pid);descriptors.append(fd);poll=select.poll();poll.register(fd,select.POLLIN);return fd,poll
    try:
        if control not in CONTROLS or composition['outcome'] != 'pass':raise ValueError('native shell recovery prerequisite')
        old_fd,old_poll=held(shell_pid);_,icon_poll=held(result['old_icon']['pid'])
        if old_poll.poll(0) or icon_poll.poll(0):raise ValueError('original processes already exited')
        result['held_before_ns']=time.monotonic_ns();preserve('identity',result)
        channel.send({'shell_recovery_request':'arm','pid':shell_pid})
        if not channel.poll(1) or channel.recv()!={'armed':shell_pid}:raise ValueError('parent did not arm exact shell fault')
        issue(environment,'SetGeneration','4');time.sleep(.25)
        started=time.monotonic_ns();result['started_monotonic_ns']=started
        now=lambda:(time.monotonic_ns()-started)//1000
        def event(name,**values):
            row={'event':name,**values};result['events'].append(row);preserve('event',row);return row
        next_frame=0;stop=exited=request=ready=attached=post_ns=None
        replacement_pid=None;new_poll=new_icon_poll=None;post_generation=6
        while now()<10000000:
            if stop is None and now()>=250000:
                binding=manager_identity(display,ResourceOwner(display))
                if binding!=result['old_shell'] or process_identity(shell_pid)!=result['old_process'] or old_poll.poll(0):raise ValueError('original shell changed before exact-handle stop')
                at=now();signal.pidfd_send_signal(old_fd,signal.SIGKILL)
                stop=event('stop',start_us=at,end_us=now(),pid=shell_pid,binding=binding,held_live=True)
            if stop and exited is None and old_poll.poll(0):exited=event('shell-exit',at_us=now(),pid=shell_pid,observer='pidfd',readable=True)
            if stop and exited is None and now()>stop['end_us']+2000000:raise TimeoutError('shell exit deadline')
            if exited and control=='no-restart' and now()>=exited['at_us']+2500000:break
            if exited and request is None and control!='no-restart' and now()>=exited['at_us']+350000:
                request=event('restart-request',at_us=now());channel.send({'shell_recovery_request':'restart','pid':shell_pid})
            if channel.poll():
                message=channel.recv()
                if not request or replacement_pid is not None or set(message)!={'replacement_started','old_exit'}:raise ValueError('replacement parent message')
                replacement_pid=message['replacement_started'];result['new_process']=process_identity(replacement_pid);_,new_poll=held(replacement_pid)
                event('replacement-started',at_us=now(),pid=replacement_pid,old_exit=message['old_exit'])
            if request and ready is None and now()>request['at_us']+5000000:raise TimeoutError('replacement native readiness deadline')
            if attached and post_ns is None and now()>=attached['end_us']+250000:
                post_ns=time.monotonic_ns();result['post']={'started_monotonic_ns':post_ns,'trace':{'version':'0.1.0','start_us':0,'end_us':2400000,'stimuli':[{'at_us':0,'generation':5}],'frames':[]},'overlap_samples':[]}
            if post_ns:
                elapsed=(time.monotonic_ns()-post_ns)//1000
                if elapsed>=2400000:break
                if post_generation<=7 and elapsed>=(post_generation-5)*800000:
                    stimulus={'at_us':elapsed,'generation':post_generation};result['post']['trace']['stimuli'].append(stimulus)
                    issue(environment,'SetGeneration',str(post_generation));preserve('generation',stimulus);post_generation+=1
            if now()>=next_frame and (not post_ns or (time.monotonic_ns()-post_ns)//1000 < 2390000):
                begin=now();marker=pack_frame(display.capture(*FIXTURE['marker']),begin,now())
                row={'marker':marker,'start_us':now(),'overlap':rgb_record(display.capture(*FIXTURE['overlap'])),'background':rgb_record(display.capture(*FIXTURE['background_witness']))}
                row['native_at_us']=now();row['shell']=manager_identity(display,ResourceOwner(display))
                row['old_shell_exited']=bool(old_poll.poll(0));row['old_icon_exited']=bool(icon_poll.poll(0))
                row['icon']=safe_icon(display,replacement_pid if ready or (replacement_pid and row['old_icon_exited']) else shell_pid,workspace)
                row['new_shell_live']=None if new_poll is None else not bool(new_poll.poll(0))
                row['new_icon_live']=None if new_icon_poll is None else not bool(new_icon_poll.poll(0));row['end_us']=now()
                if post_ns:
                    offset=(post_ns-started)//1000;frame={**marker,'start_us':marker['start_us']-offset,'end_us':marker['end_us']-offset}
                    row['post_frame']=frame;result['post']['trace']['frames'].append(frame)
                    result['post']['overlap_samples'].append({'marker_start_us':frame['start_us'],'start_us':row['start_us']-offset,'end_us':row['end_us']-offset,'pixels':row['overlap']})
                result['samples'].append(row);preserve('sample',row);next_frame+=50000
                if len(result['samples'])>200:raise ValueError('shell recovery frame capacity')
                if replacement_pid and ready is None and row['shell'] and row['shell']['pid']==[replacement_pid] and row['old_icon_exited'] and row['icon']:
                    peer=bridge_peer(environment,replacement_pid)
                    if peer:
                        _,new_icon_poll=held(row['icon']['pid'])
                        if new_poll.poll(0) or new_icon_poll.poll(0):raise ValueError('replacement already exited')
                        result['new_shell']=row['shell'];result['new_icon']=row['icon']
                        ready=event('native-ready',at_us=now(),shell=row['shell'],icon=row['icon'],old_icon_exited=True,peer=peer)
                        at=now()
                        key=display.x.XKeysymToKeycode(display.handle,display.x.XStringToKeysym(b'Escape'))
                        for pressed in (True,False):
                            if not display.xtest.XTestFakeKeyEvent(display.handle,key,pressed,0):raise ValueError('replacement overview dismissal failed')
                        display.x.XFlush(display.handle);issue(environment,'SetGeneration','5')
                        if control=='live':issue(environment,'SetSceneEnabled','true')
                        attached=event('reattach',start_us=at,end_us=now(),performed=control=='live')
            time.sleep(.002)
        result['end_us']=now();result['settings_after']=settings(environment)
        result['evaluation']=judge(result,composition)
        preserve('recovery-completed',{k:v for k,v in result.items() if k not in ['samples','post']})
        if result['evaluation']['outcome']=='pass':
            import gnome_input
            result['post_input']=gnome_input.observe(display,environment,replacement_pid,workspace,{**composition,'icon_manager':result['new_icon']},trace_function)
            result['not_run']=[]
        if replacement_pid:
            if new_poll.poll(0) or new_icon_poll.poll(0):raise ValueError('replacement exited before final observations')
            result['new_shell_mapped_files']=mapped_files(replacement_pid);result['new_icon_mapped_files']=mapped_files(result['new_icon']['pid'])
        result['outcome']='pass' if result['evaluation']['outcome']=='pass' and result.get('post_input',{}).get('outcome')=='pass' else 'fail'
        return result
    except Exception as error:
        result['outcome']='inconclusive';result['error']=type(error).__name__+': '+str(error);preserve('error',{'message':result['error']});return result
    finally:
        preserve('completed',result)
        for fd in descriptors:os.close(fd)
        journal.close()
