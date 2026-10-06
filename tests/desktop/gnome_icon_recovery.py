"""Observe one owned DING exit/replacement and the separate visual/input recovery."""
import ctypes as C
import json
import os
from pathlib import Path
import select
import signal
import time

from native_x11_host import rgb_record
from gnome_composition import FIXTURE, bind_icon_window, masks, settings
from gnome_reveal import issue
from x11_recovery import ErrorEvent, ResourceOwner, manager_identity
from oracle import evaluate, pack_frame

CONTROLS=['live','frozen-surface','no-stop']


def safe_icon(display,shell_pid,workspace):
    errors=[]
    callback_type=C.CFUNCTYPE(C.c_int,C.c_void_p,C.POINTER(ErrorEvent))
    def on_error(_display,event):errors.append(event.contents.code);return 0
    callback=callback_type(on_error)
    display.x.XSetErrorHandler.argtypes=[C.c_void_p];display.x.XSetErrorHandler.restype=C.c_void_p
    display.x.XSync(display.handle,False)
    previous=display.x.XSetErrorHandler(C.cast(callback,C.c_void_p))
    try:
        try:result=bind_icon_window(display,shell_pid,workspace)
        except ValueError:
            display.x.XSync(display.handle,False)
            if errors and all(e==3 for e in errors):return None
            raise
        display.x.XSync(display.handle,False)
        return None if errors else result
    finally:
        display.x.XSetErrorHandler(previous)
        if any(e!=3 for e in errors):raise ValueError('unexpected native icon query error')


def judge(result,composition):
    from record_gnome_host import rgb
    trace=result['trace'];samples=result['samples'];events=result['events'];control=result['control']
    if not 0<trace['end_us']<=6000000 or len(samples)!=len(trace['frames']) or not 3<=len(samples)<=120:raise ValueError('recovery interval completeness')
    calibration=[rgb(s['frames'][0]['pixels'],180*220*3) for s in composition['calibrations']]
    anchors,clean=masks(calibration[2],calibration[:2]);checks=[];last=0;gap=duration=0
    stops=[e for e in events if e['event']=='stop'];exits=[e for e in events if e['event']=='exit-observed'];ready=[e for e in events if e['event']=='replacement-ready']
    if len(stops)!=1 or len(exits)>1 or len(ready)>1:raise ValueError('native recovery event cardinality')
    stop=stops[0]
    if stop['performed']!=(control!='no-stop') or not 250000<=stop['start_us']<=300000 or not stop['start_us']<=stop['end_us']<=stop['start_us']+50000:
        raise ValueError('native stop schedule/control')
    if stop['pid']!=result['old_icon']['pid'] or stop['binding']!=result['old_icon'] or not stop['held_live']:raise ValueError('stop does not bind held original')
    if len([f for f in trace['frames'] if f['end_us']<stop['start_us']])<3:raise ValueError('pre-fault coverage incomplete')
    if exits and (exits[0]['pid']!=result['old_icon']['pid'] or exits[0]['observer']!='pidfd' or not exits[0]['readable'] or not stop['end_us']<=exits[0]['at_us']<=stop['end_us']+2000000):
        raise ValueError('old exit proof/timing')
    if ready and (not exits or not exits[0]['at_us']<=ready[0]['at_us']<=stop['start_us']+5000000 or ready[0]['binding']!=result['new_icon']):
        raise ValueError('replacement readiness identity/timing')
    if ready:
        old,new=result['old_icon'],result['new_icon']
        if (new['pid'],new['start_ticks'])==(old['pid'],old['start_ticks']) or new['process_group']!=old['process_group'] or new['session']!=old['session'] or new['arguments']!=old['arguments'] or new['executable']!=old['executable']:
            raise ValueError('replacement is not a distinct owned native lifetime')
    stimuli=trace['stimuli']
    if not stimuli or stimuli[0]!={'at_us':0,'generation':4}:raise ValueError('recovery initial generation')
    if exits:
        if [s['generation'] for s in stimuli]!=[4,5,6] or not exits[0]['at_us']<=stimuli[1]['at_us']<=exits[0]['at_us']+50000:
            raise ValueError('post-exit generation stimulus')
        if not ready or not max(ready[0]['at_us'],exits[0]['at_us']+350000)<=stimuli[2]['at_us']<=max(ready[0]['at_us'],exits[0]['at_us']+350000)+50000:
            raise ValueError('post-ready generation stimulus')
        if not 750000<=trace['end_us']-stimuli[2]['at_us']<=850000:raise ValueError('post-recovery observation interval')
    elif control!='no-stop' or [s['generation'] for s in stimuli]!=[4,5] or not 500000<=stimuli[1]['at_us']<=550000:
        raise ValueError('no-stop liveness stimulus differs')
    for frame,row in zip(trace['frames'],samples):
        if not last<=frame['start_us']<=frame['end_us']<=row['start_us']<=row['native_at_us']<=row['end_us']<=trace['end_us']:raise ValueError('recovery capture ordering')
        gap=max(gap,frame['start_us']-last);duration=max(duration,row['end_us']-frame['start_us']);last=row['end_us']
        pixels=rgb(row['overlap'],180*220*3)
        checks.append({'at_us':frame['start_us'],'end_us':row['end_us'],
                       'icons':all(pixels[n*3:n*3+3]==calibration[2][n*3:n*3+3] for group in anchors for n in group),
                       'rectangle':all(pixels[n*3:n*3+3]==bytes(FIXTURE['overlap_rgb']) for n in clean),
                       'background':rgb(row['background'],128*96*3)==bytes(FIXTURE['background_rgb'])*128*96})
        if row['shell']!=result['old_shell'] or not row['shell_live']:raise ValueError('shell lifetime changed during icon recovery')
        if exits and row['native_at_us']>=exits[0]['at_us'] and not row['old_exited']:raise ValueError('old process resurrected')
        if ready and row['native_at_us']>=ready[0]['at_us'] and (row['icon']!=result['new_icon'] or not row['new_live']):raise ValueError('replacement identity/lifetime changed')
        if not exits and (row['icon']!=result['old_icon'] or row['old_exited']):raise ValueError('no-stop control did not retain original')
    gap=max(gap,trace['end_us']-last)
    if gap>150000 or duration>50000:raise ValueError('recovery capture coverage')
    progress=evaluate(trace)
    if any(s.startswith('capture.') for s in progress['uncertainty']):raise ValueError('marker capture coverage')
    post=[r for r in checks if exits and r['at_us']>=stimuli[-1]['at_us']+200000]
    if exits and len(post)<3:raise ValueError('post-recovery pixel coverage incomplete')
    replacement='pass' if exits and ready else 'fail'
    icons=None if not exits else ('pass' if all(r['icons'] for r in post) else 'fail')
    rectangle='pass' if all(r['rectangle'] for r in checks) else 'fail'
    background='pass' if all(r['background'] for r in checks) else 'fail'
    good=replacement=='pass' and progress['outcome']=='pass' and icons==rectangle==background=='pass'
    return {'replacement':replacement,'marker':progress,'post_ready_icons':icons,'rectangle':rectangle,'background':background,
            'checks':checks,'max_gap_us':gap,'max_capture_us':duration,
            'first_icon_absence_us':next((r['at_us'] for r in checks if not r['icons']),None),
            'first_post_ready_icons_us':next((r['end_us'] for r in post if r['icons']),None),
            'outcome':'pass' if good else 'fail'}


def observe(display,environment,shell_pid,workspace,composition,trace_function):
    from native_gnome_bootstrap import mapped_files
    control=environment['SYSPANE_GNOME_ICON_RECOVERY']
    result={'version':'0.1.0','control':control,'old_icon':composition['icon_manager'],
            'old_icon_mapped_files':mapped_files(composition['icon_manager']['pid']),
            'old_shell':manager_identity(display,ResourceOwner(display)),'settings_before':settings(environment),
            'events':[],'samples':[],'not_run':['post-recovery-input']}
    journal=(workspace/'icon-recovery.jsonl').open('x',encoding='utf-8',newline='\n')
    descriptors=[];count=0;new_poll=None
    def preserve(kind,value):
        nonlocal count
        count+=1
        if count>180:raise ValueError('recovery journal record capacity')
        journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        if journal.tell()>8*1024**2:raise ValueError('recovery journal byte capacity')
    def held(pid):
        fd=os.pidfd_open(pid);descriptors.append(fd);poll=select.poll();poll.register(fd,select.POLLIN);return fd,poll
    try:
        if composition['outcome']!='pass' or control not in CONTROLS:raise ValueError('recovery prerequisite/control')
        old_fd,old_poll=held(result['old_icon']['pid']);_,shell_poll=held(shell_pid)
        if old_poll.poll(0) or shell_poll.poll(0) or safe_icon(display,shell_pid,workspace)!=result['old_icon']:raise ValueError('original native lifetime unavailable')
        result['held_before']={'old_live':True,'shell_live':True,'at_ns':time.monotonic_ns()}
        preserve('identity',result)
        issue(environment,'SetGeneration','4');time.sleep(.25)
        started=time.monotonic_ns();result['started_monotonic_ns']=started
        now=lambda:(time.monotonic_ns()-started)//1000
        trace={'version':'0.1.0','start_us':0,'end_us':6000000,'stimuli':[{'at_us':0,'generation':4}],'frames':[]};result['trace']=trace
        next_frame=0;stop=exit_time=ready_time=final_time=None
        def event(value):result['events'].append(value);preserve('event',value)
        def generation(value):
            row={'at_us':now(),'generation':value};trace['stimuli'].append(row);issue(environment,'SetGeneration',str(value));preserve('generation',row)
            return row['at_us']
        while now()<6000000:
            if stop is None and now()>=250000:
                binding=safe_icon(display,shell_pid,workspace)
                if binding!=result['old_icon'] or old_poll.poll(0):raise ValueError('original changed before exact-handle stop')
                if control=='frozen-surface':
                    freeze={'event':'freeze','start_us':now()};issue(environment,'FreezeRecoveryMarker','true');freeze['end_us']=now();event(freeze)
                stop={'event':'stop','start_us':now(),'pid':result['old_icon']['pid'],'binding':binding,'held_live':True,'performed':control!='no-stop'}
                if stop['performed']:signal.pidfd_send_signal(old_fd,signal.SIGKILL)
                stop['end_us']=now();event(stop)
            if stop and exit_time is None and old_poll.poll(0):
                exit_time=now();event({'event':'exit-observed','at_us':exit_time,'pid':result['old_icon']['pid'],'observer':'pidfd','readable':True})
                generation(5)
            if control=='no-stop' and len(trace['stimuli'])==1 and now()>=500000:generation(5)
            if ready_time is not None and final_time is None and now()>=max(ready_time,exit_time+350000):final_time=generation(6)
            if final_time is not None and now()>=final_time+750000:break
            if control=='no-stop' and now()>=2500000:break
            if stop and not exit_time and control!='no-stop' and now()>stop['end_us']+2000000:raise TimeoutError('old icon-manager exit deadline')
            if stop and not ready_time and now()>stop['start_us']+5000000:raise TimeoutError('native icon-manager replacement deadline')
            if now()>=next_frame:
                before=now();frame=pack_frame(display.capture(*FIXTURE['marker']),before,now())
                row={'start_us':now(),'overlap':rgb_record(display.capture(*FIXTURE['overlap'])),'background':rgb_record(display.capture(*FIXTURE['background_witness']))}
                row['native_at_us']=now();row['icon']=safe_icon(display,shell_pid,workspace)
                row['shell']=manager_identity(display,ResourceOwner(display));row['shell_live']=not bool(shell_poll.poll(0));row['old_exited']=bool(old_poll.poll(0))
                if exit_time is not None and ready_time is None and row['icon'] and (row['icon']['pid'],row['icon']['start_ticks'])!=(result['old_icon']['pid'],result['old_icon']['start_ticks']):
                    result['new_icon']=row['icon'];_,new_poll=held(row['icon']['pid'])
                    if new_poll.poll(0):raise ValueError('replacement already exited')
                    ready_time=row['native_at_us'];event({'event':'replacement-ready','at_us':ready_time,'binding':row['icon']})
                row['new_live']=None if new_poll is None else not bool(new_poll.poll(0));row['end_us']=now()
                trace['frames'].append(frame);result['samples'].append(row);preserve('sample',{'marker':frame,'observation':row})
                if len(trace['frames'])>120:raise ValueError('recovery frame capacity')
                if not row['shell_live']:raise ValueError('shell exited during icon-manager fault')
                next_frame+=50000
            time.sleep(.002)
        trace['end_us']=now();result['settings_after']=settings(environment)
        result['evaluation']=judge(result,composition)
        preserve('recovery-completed',{k:v for k,v in result.items() if k not in ['samples','trace']})
        if result['evaluation']['outcome']=='pass':
            import gnome_input
            if not new_poll or new_poll.poll(0):raise ValueError('replacement unavailable before input')
            recovered={**composition,'icon_manager':result['new_icon']}
            result['post_input']=gnome_input.observe(display,environment,shell_pid,workspace,recovered,trace_function)
            result['not_run']=[]
            if new_poll.poll(0) or safe_icon(display,shell_pid,workspace)!=result['new_icon']:raise ValueError('replacement changed during post-recovery input')
        if 'new_icon' in result:result['new_icon_mapped_files']=mapped_files(result['new_icon']['pid'])
        result['shell_after']=manager_identity(display,ResourceOwner(display))
        result['outcome']='pass' if result['evaluation']['outcome']=='pass' and result.get('post_input',{}).get('outcome')=='pass' else 'fail'
        return result
    except Exception as error:
        result['outcome']='inconclusive';result['error']=type(error).__name__+': '+str(error)
        preserve('error',{'message':result['error']});return result
    finally:
        preserve('completed',result)
        for descriptor in descriptors:os.close(descriptor)
        journal.close()
