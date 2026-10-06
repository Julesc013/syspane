"""Observe native multi-window/modal choices and invalidation across lifetimes/workspaces."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import time

from native_oracle import ROOT
from native_x11_host import rgb_record
from x11_recovery import ResourceOwner, ErrorEvent
from gnome_focus_integration import trace
from gnome_composition import FIXTURE as SCENE, settings
from gnome_reveal import binding
from oracle import decode, evaluate

COLORS = {'alpha':[32,160,64],'beta':[176,64,160],'modal':[208,144,32]}
STEPS = ['beta-ready','beta-enter','beta-return','alpha-ready','alpha-enter','alpha-return',
         'beta-for-dialog','dialog-open','dialog-enter','dialog-return','dialog-reselect','dialog-close',
         'beta-before-close','close-enter','close-target','close-return','alpha-before-workspace',
         'workspace-enter','workspace-away','workspace-home','workspace-settle','alpha-fresh','fresh-enter','fresh-return']
RETURNS = {'beta-return':'beta','alpha-return':'alpha','dialog-return':'modal','fresh-return':'alpha'}
SETUP = {'beta-ready':'beta','alpha-ready':'alpha','beta-for-dialog':'beta','dialog-open':'modal',
         'dialog-reselect':'modal','dialog-close':'beta','beta-before-close':'beta','alpha-before-workspace':'alpha','alpha-fresh':'alpha'}
ENTER = ['beta-enter','alpha-enter','dialog-enter','close-enter','close-target','workspace-enter','fresh-enter']
KEY_SETTINGS = [('org.gnome.mutter','dynamic-workspaces'),('org.gnome.desktop.wm.preferences','num-workspaces'),
                ('org.gnome.desktop.wm.keybindings','switch-to-workspace-1'),('org.gnome.desktop.wm.keybindings','switch-to-workspace-2')]


def workspace_settings(environment):
    result = {}
    for schema,key in KEY_SETTINGS:
        reply = subprocess.run(['/usr/bin/gsettings','get',schema,key],env=environment,capture_output=True,text=True,timeout=1,check=True)
        if reply.stderr or len(reply.stdout)>512:raise ValueError('bounded native workspace settings')
        result[schema+'/'+key] = reply.stdout.strip()
    return result


def receipt_file(workspace):
    descriptor = os.open(workspace/'focus-control-events.jsonl',os.O_RDONLY|os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor); raw = os.read(descriptor,32769)
        if not stat.S_ISREG(identity.st_mode) or identity.st_uid != os.geteuid() or stat.S_IMODE(identity.st_mode)!=0o600 or len(raw)>32768 or len(raw)!=identity.st_size or not raw.endswith(b'\n'):
            raise ValueError('private complete bounded control journal')
        rows = [json.loads(line) for line in raw.splitlines()]
        if len(rows)>128:raise ValueError('control receipt capacity')
        return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'device':identity.st_dev,'inode':identity.st_ino,
                'uid':identity.st_uid,'mode':stat.S_IMODE(identity.st_mode),'events':rows}
    finally:os.close(descriptor)


def identity(display,pid,role):
    owner = ResourceOwner(display)
    matches = [c for c in display.structure()['clients'] if c['class']==['syspane-focus-'+role,'SysPaneFocus'+role.title()]]
    if not matches:return None
    if len(matches)!=1:raise ValueError('unique native focus control required')
    client=matches[0];native=owner.pid(client['window'])
    if not native or native[0]!=pid or client['pid']!=[pid]:raise ValueError('native control owner differs')
    window=client['window'];x,y,child=C.c_int(),C.c_int(),C.c_ulong()
    if not display.x.XTranslateCoordinates(display.handle,window,display.root,0,0,C.byref(x),C.byref(y),C.byref(child)):raise ValueError('native control coordinates')
    root,gx,gy,width,height,border,depth=C.c_ulong(),C.c_int(),C.c_int(),C.c_uint(),C.c_uint(),C.c_uint(),C.c_uint()
    display.x.XGetGeometry.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
    if not display.x.XGetGeometry(display.handle,window,C.byref(root),C.byref(gx),C.byref(gy),C.byref(width),C.byref(height),C.byref(border),C.byref(depth)):raise ValueError('native control geometry')
    geometry=[x.value,y.value,width.value,height.value]
    if not 0<=x.value<x.value+width.value<=800 or not 0<=y.value<y.value+height.value<=600 or width.value<128 or height.value<96:raise ValueError('bounded native control geometry')
    path=Path(f'/proc/{pid}');arguments=(path/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
    state=(path/'stat').read_text().rsplit(')',1)[1].split()
    return {'role':role,'window':window,'pid':pid,'resource_base':native[1],'resource_mask':native[2],
            'geometry':geometry,'type':client['type'],'normal_type_atom':display.atom('_NET_WM_WINDOW_TYPE_NORMAL'),
            'dialog_type_atom':display.atom('_NET_WM_WINDOW_TYPE_DIALOG'),'modal_atom':display.atom('_NET_WM_STATE_MODAL'),
            'state':display.property(window,'_NET_WM_STATE'),'transient_for':display.property(window,'WM_TRANSIENT_FOR'),
            'desktop':display.property(window,'_NET_WM_DESKTOP'),'arguments':[s.decode() for s in arguments],
            'executable':str((path/'exe').resolve(strict=True)),'process_group':int(state[2]),'session':int(state[3]),'start_ticks':int(state[19])}


def native_snapshot(display):
    errors=[];caught=None;result={}
    callback_type=C.CFUNCTYPE(C.c_int,C.c_void_p,C.POINTER(ErrorEvent))
    def failed(_display,event):
        e=event.contents;errors.append({'code':e.code,'request':e.request,'resource':e.resource,'serial':e.serial});return 0
    callback=callback_type(failed)
    display.x.XSetErrorHandler.argtypes=[C.c_void_p];display.x.XSetErrorHandler.restype=C.c_void_p
    display.x.XSync(display.handle,False)
    previous=display.x.XSetErrorHandler(C.cast(callback,C.c_void_p))
    try:
        result['workspace']=display.property(display.root,'_NET_CURRENT_DESKTOP')
        result['workspace_count']=display.property(display.root,'_NET_NUMBER_OF_DESKTOPS')
        result['native']=display.structure()
        result['memberships']={str(c['window']):display.property(c['window'],'_NET_WM_DESKTOP') for c in result['native']['clients']}
    except ValueError as error:caught=error
    finally:
        display.x.XSync(display.handle,False);display.x.XSetErrorHandler(previous)
    if errors:
        result['native']=None;result['memberships']={}
    elif caught:raise caught
    result['native_errors']=errors
    return result


def judge_step(row,roles,icon):
    from record_gnome_host import rgb
    name=row['step'];target=RETURNS.get(name,SETUP.get(name));required=passed=0;last=gap=duration=0;first=None
    if not 400000<=row['end_us']<=450000 or len(row['samples'])<7 or not 0<=row['action']['start_us']<=row['action']['end_us']<=50000:raise ValueError('bounded focus scenario capture/action')
    for sample in row['samples']:
        if not last<=sample['start_us']<=sample['end_us']<=row['end_us']:raise ValueError('ordered focus scenario captures')
        gap=max(gap,sample['start_us']-last);duration=max(duration,sample['end_us']-sample['start_us']);last=sample['end_us']
        if decode(rgb(sample['marker'],128*96*3))!=6 or rgb(sample['background'],128*96*3)!=bytes(SCENE['background_rgb'])*128*96:raise ValueError('scenario lost original scene/background')
        native=sample['native'];workspace=sample['workspace']
        if native is None:
            if name not in ['dialog-close','close-target'] or not sample.get('native_errors') or sample['start_us']>=row['action']['end_us']+200000:
                raise ValueError('unexpected or settled native query failure')
            role='modal' if name=='dialog-close' else 'beta'
            if any(e['code']!=3 or e['request']!=20 or e['resource']!=roles[role]['window'] for e in sample['native_errors']):
                raise ValueError('foreign native query failure')
            continue
        if sample.get('native_errors'):raise ValueError('failed native queries cannot supply client state')
        active=native['active_window'];members=native['client_order_bottom_to_top']
        good=workspace==[1 if name=='workspace-away' else 0] and sample['workspace_count']==[2]
        if name in ENTER:good &= native['showing_desktop']==[1] and active==[icon['window']]
        elif name not in ['workspace-away','workspace-home']:good &= native['showing_desktop']==[0]
        if target:
            good &= active==[roles[target]['window']] and target in sample['witnesses'] and rgb(sample['witnesses'][target],1200)==bytes(COLORS[target])*400
        if name=='workspace-away':good &= active in [[],[0],[icon['window']]]
        if STEPS.index(name)>=STEPS.index('close-target'):
            good &= roles['beta']['window'] not in members and active!=[roles['beta']['window']]
        if STEPS.index(name)>=STEPS.index('dialog-close'):
            good &= roles['modal']['window'] not in members and active!=[roles['modal']['window']]
        if good and first is None:first=sample['end_us']
        if sample['start_us']>=row['action']['end_us']+200000:
            required+=1;passed+=int(bool(good))
    gap=max(gap,row['end_us']-last)
    if gap>150000 or duration>50000 or required<3:raise ValueError('focus scenario temporal coverage')
    good=passed==required and first is not None and first<=row['action']['end_us']+200000
    return {'step':name,'outcome':'pass' if good else 'fail','first_match_us':first,
            'max_gap_us':gap,'max_capture_us':duration,'required_samples':required}


def observe(display,environment,workspace,baseline,composition,channel,trace_function):
    mode=environment['SYSPANE_GNOME_FOCUS_SCENARIOS']
    result={'version':'0.1.0','mode':mode,'initial_trace':trace(environment),'steps':[],'roles':{},
            'not_run':STEPS+['final-marker'],'started_monotonic_ns':time.monotonic_ns(),
            'workspace_settings_before':workspace_settings(environment),'background_before':settings(environment),'binding_before':binding(environment)}
    journal=(workspace/'focus-scenarios.jsonl').open('x',encoding='utf-8',newline='\n');count=0;descriptor=None
    def preserve(kind,value):
        nonlocal count
        count+=1
        if count>400:raise ValueError('scenario journal capacity')
        journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        if journal.tell()>12*1024**2:raise ValueError('scenario journal byte capacity')
    def chord(names):
        codes=[display.x.XKeysymToKeycode(display.handle,display.x.XStringToKeysym(n.encode())) for n in names]
        for code,down in [(c,True) for c in codes]+[(c,False) for c in reversed(codes)]:
            if not code or not display.xtest.XTestFakeKeyEvent(display.handle,code,down,0):raise ValueError('native scenario key')
        display.x.XFlush(display.handle)
    def click(role):
        x,y,w,h=result['roles'][role]['geometry']
        if not display.xtest.XTestFakeMotionEvent(display.handle,-1,x+w//2,y+h//2,0):raise ValueError('native scenario motion')
        for down in (True,False):
            if not display.xtest.XTestFakeButtonEvent(display.handle,1,down,0):raise ValueError('native scenario click')
        display.x.XFlush(display.handle)
    def bind(role):
        found=identity(display,result['helper_pid'],role)
        if found:
            result['roles'][role]=found;preserve('identity',found)
        return found
    def step(name,kind,action):
        started=time.monotonic_ns();now=lambda:(time.monotonic_ns()-started)//1000
        row={'step':name,'started_monotonic_ns':started,'action':{'kind':kind,'start_us':now()},'samples':[]}
        action();row['action']['end_us']=now();next_frame=0
        while now()<400000:
            if poller.poll(0):raise ValueError('retained focus helper exited')
            if name=='dialog-open' and 'modal' not in result['roles']:bind('modal')
            if now()>=next_frame:
                sample={'start_us':now(),'marker':rgb_record(display.capture(*SCENE['marker'])),
                        'background':rgb_record(display.capture(*SCENE['background_witness'])),'witnesses':{}}
                for role,owner in result['roles'].items():
                    x,y,w,h=owner['geometry'];sample['witnesses'][role]=rgb_record(display.capture(x+w//2-10,y+h//2-10,20,20))
                sample.update(native_snapshot(display))
                sample['end_us']=now();row['samples'].append(sample);preserve('sample',{'step':name,'sample':sample});next_frame+=50000
            time.sleep(.002)
        row['end_us']=now();result['steps'].append(row);preserve('step',row)
        row['evaluation']=judge_step(row,result['roles'],baseline['icon_manager']);preserve('verdict',row['evaluation'])
        if name not in RETURNS and row['evaluation']['outcome']!='pass':raise ValueError('scenario prerequisite failed: '+name)
        if name in RETURNS:
            before=receipt_file(workspace);start=time.monotonic_ns();chord(['F9']);end=time.monotonic_ns();time.sleep(.15)
            after=receipt_file(workspace)
            row['keyboard']={'started_ns':start,'finished_ns':end,'before':before,'after':after}
            events=after['events'][len(before['events']):]
            row['keyboard']['delivered']=len(events)==1 and events[0]['event']=='key' and events[0]['role']==RETURNS[name] and start<=events[0]['monotonic_ns']<=end+200000000
            preserve('keyboard',{'step':name,**row['keyboard']})
    try:
        preserve('prepared',{k:v for k,v in result.items() if k not in ['steps','roles']})
        result['launch_requested_ns']=time.monotonic_ns();channel.send({'focus_scenarios_request':'launch'})
        if not channel.poll(2):raise TimeoutError('retained helper launch reply')
        reply=channel.recv();result['launch_received_ns']=time.monotonic_ns()
        if set(reply)!={'focus_scenarios_pid'} or type(reply['focus_scenarios_pid']) is not int:raise ValueError('retained helper reply')
        result['helper_pid']=reply['focus_scenarios_pid'];descriptor=os.pidfd_open(result['helper_pid']);poller=select.poll();poller.register(descriptor,select.POLLIN)
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            for role in ['alpha','beta']:
                if role not in result['roles']:bind(role)
            if len(result['roles'])==2:break
            time.sleep(.02)
        else:raise TimeoutError('native normal controls not ready')
        preserve('launched',{k:result[k] for k in ['helper_pid','launch_requested_ns','launch_received_ns']})
        for role in ['beta','alpha']:
            step(role+'-ready',{'click':role},lambda role=role:click(role))
            step(role+'-enter',{'keys':['Super_L','d']},display.reveal_key)
            step(role+'-return',{'keys':['Super_L','d']},display.reveal_key)
        step('beta-for-dialog',{'click':'beta'},lambda:click('beta'))
        step('dialog-open',{'keys':['F6']},lambda:chord(['F6']))
        step('dialog-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('dialog-return',{'keys':['Super_L','d']},display.reveal_key)
        step('dialog-reselect',{'click':'modal'},lambda:click('modal'))
        step('dialog-close',{'keys':['Escape']},lambda:chord(['Escape']))
        step('beta-before-close',{'click':'beta'},lambda:click('beta'))
        step('close-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('close-target',{'close':result['roles']['beta']['window']},lambda:display.send(result['roles']['beta']['window']))
        step('close-return',{'keys':['Super_L','d']},display.reveal_key)
        step('alpha-before-workspace',{'click':'alpha'},lambda:click('alpha'))
        step('workspace-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('workspace-away',{'keys':['Control_L','Alt_L','2']},lambda:chord(['Control_L','Alt_L','2']))
        step('workspace-home',{'keys':['Control_L','Alt_L','1']},lambda:chord(['Control_L','Alt_L','1']))
        reset=display.property(display.root,'_NET_SHOWING_DESKTOP')==[1]
        step('workspace-settle',{'show_desktop_if_active':reset},display.reveal_key if reset else lambda:None)
        step('alpha-fresh',{'click':'alpha'},lambda:click('alpha'))
        step('fresh-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('fresh-return',{'keys':['Super_L','d']},display.reveal_key)
        result['final_trace']=trace(environment);result['events_after']=receipt_file(workspace)
        result['final_marker']=trace_function(display,environment,dismiss=False)
        result['workspace_settings_after']=workspace_settings(environment);result['background_after']=settings(environment);result['binding_after']=binding(environment)
        result['finished_monotonic_ns']=time.monotonic_ns();result['not_run']=[]
        good=all(s['evaluation']['outcome']=='pass' and s.get('keyboard',{}).get('delivered',True) for s in result['steps'])
        result['outcome']='pass' if mode=='observe' or good else 'fail'
        if evaluate(result['final_marker']['trace'])['outcome']!='pass':result['outcome']='fail'
        return result
    except Exception as error:
        result['outcome']='inconclusive';result['error']=type(error).__name__+': '+str(error);preserve('error',{'message':result['error']});return result
    finally:
        preserve('completed',result);journal.close()
        if descriptor is not None:os.close(descriptor)
