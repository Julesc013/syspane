"""Observe optional event-bound focus integration using native acceptance evidence."""
import ast
import ctypes as C
import json
import subprocess
import time

from gnome_composition import FIXTURE as SCENE, settings
from gnome_reveal import FIXTURE, binding
from gnome_input import icon_center
from native_x11_host import rgb_record
from oracle import decode

STEPS = ['icon-focus','unrelated-key','prepare-cycle','cycle-enter','cycle-icon','cycle-restore',
         'prepare-folder','folder-enter','restore-after-folder','minimize-enter','minimize-target',
         'minimize-restore','restore-minimized','disabled-enter','disabled-restore']


def trace(environment):
    command = ['/usr/bin/gdbus','call','--address',environment['DBUS_SESSION_BUS_ADDRESS'],
               '--dest','org.gnome.Shell','--object-path','/org/syspane/LabMarker',
               '--method','org.syspane.LabMarker.GetFocusTrace']
    result = subprocess.run(command,env=environment,capture_output=True,text=True,timeout=1,check=True)
    if len(result.stdout)>70000 or result.stderr:raise ValueError('bounded focus trace required')
    value = ast.literal_eval(result.stdout)
    if not isinstance(value,tuple) or len(value)!=1 or not isinstance(value[0],str):raise ValueError('focus trace reply shape')
    return json.loads(value[0])


def expected(name, mode, foreground, icon):
    show = name in ['cycle-enter','cycle-icon','folder-enter','minimize-enter','minimize-target','disabled-enter']
    visible = not show and name not in ['minimize-restore']
    focus = foreground if name in ['prepare-cycle','prepare-folder','restore-after-folder','restore-minimized'] or (name=='cycle-restore' and mode=='restore') else icon
    minimized = name in ['minimize-target','minimize-restore']
    generation = 6 if STEPS.index(name) < 8 else 3
    return show,visible,focus,minimized,generation


def judge_step(row,mode,foreground,icon):
    from record_gnome_host import rgb
    show,visible,focus,minimized,generation = expected(row['step'],mode,foreground,icon)
    if not 400000 <= row['end_us'] <= 450000 or len(row['samples']) < 6 or not 0 <= row['action']['start_us'] <= row['action']['end_us'] <= 50000:
        raise ValueError('bounded native guard duration/action')
    last=gap=duration=required=0
    for sample in row['samples']:
        if not last <= sample['start_us'] <= sample['end_us'] <= row['end_us']:
            raise ValueError('native guard sample order')
        gap=max(gap,sample['start_us']-last);duration=max(duration,sample['end_us']-sample['start_us']);last=sample['end_us']
        if decode(rgb(sample['marker'],128*96*3)) != generation or rgb(sample['background'],128*96*3) != bytes(SCENE['background_rgb'])*128*96:
            raise ValueError('native guard lost live scene/background')
        native=sample['native'];members=[c for c in native['clients'] if c['window']==foreground]
        if len(members)!=1:raise ValueError('native guard lost foreground client')
        if sample['start_us'] >= row['action']['end_us']+200000:
            required+=1
            color=FIXTURE['foreground_rgb'] if visible else SCENE['background_rgb']
            if native['showing_desktop'] != [int(show)] or native['active_window'] != [focus] or rgb(sample['foreground'],1200) != bytes(color)*400 or sample['wm_state'][0] != (3 if show or minimized else 1):
                raise ValueError('native guard failed: '+row['step'])
    gap=max(gap,row['end_us']-last)
    if gap>150000 or duration>50000 or required<3:raise ValueError('native guard capture coverage')
    return {'step':row['step'],'outcome':'pass','max_gap_us':gap,'max_capture_us':duration}


def observe(display,environment,workspace,baseline,composition,shell_pid,trace_function):
    import gnome_input
    mode=environment['SYSPANE_GNOME_FOCUS_INTEGRATION'];foreground=baseline['foreground'];icon=baseline['icon_manager']
    result={'version':'0.1.0','mode':mode,'initial_trace':trace(environment),'steps':[],
            'not_run':STEPS+['folder-input','disable'],'started_monotonic_ns':time.monotonic_ns()}
    journal=(workspace/'focus-integration.jsonl').open('x',encoding='utf-8',newline='\n');count=0
    def preserve(kind,value):
        nonlocal count
        count+=1
        if count>160:raise ValueError('focus integration record capacity')
        journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');journal.flush()
        if journal.tell()>8*1024**2:raise ValueError('focus integration journal capacity')
    def click(point):
        if not display.xtest.XTestFakeMotionEvent(display.handle,-1,*point,0):raise ValueError('native guard motion')
        for down in (True,False):
            if not display.xtest.XTestFakeButtonEvent(display.handle,1,down,0):raise ValueError('native guard click')
        display.x.XFlush(display.handle)
    def chord(names):
        codes=[display.x.XKeysymToKeycode(display.handle,display.x.XStringToKeysym(n.encode())) for n in names]
        for code,down in [(c,True) for c in codes]+[(c,False) for c in reversed(codes)]:
            if not code or not display.xtest.XTestFakeKeyEvent(display.handle,code,down,0):raise ValueError('native guard key')
        display.x.XFlush(display.handle)
    def minimize():
        display.x.XIconifyWindow.argtypes=[C.c_void_p,C.c_ulong,C.c_int];display.x.XIconifyWindow.restype=C.c_int
        if not display.x.XIconifyWindow(display.handle,foreground['window'],0):raise ValueError('owned foreground minimize request')
        display.x.XFlush(display.handle)
    def step(name,kind,stimulus):
        started=time.monotonic_ns();now=lambda:(time.monotonic_ns()-started)//1000
        row={'step':name,'started_monotonic_ns':started,'action':{'kind':kind,'start_us':now()},'samples':[]}
        stimulus();row['action']['end_us']=now();next_frame=0
        while now()<400000:
            if now()>=next_frame:
                sample={'start_us':now(),'marker':rgb_record(display.capture(*SCENE['marker'])),
                        'background':rgb_record(display.capture(*SCENE['background_witness'])),
                        'foreground':rgb_record(display.capture(*FIXTURE['foreground_witness'])),
                        'native':display.structure(),'wm_state':display.property(foreground['window'],'WM_STATE')}
                sample['end_us']=now();row['samples'].append(sample);next_frame+=50000
            time.sleep(.002)
        row['end_us']=now();result['steps'].append(row);preserve('step',row)
        row['evaluation']=judge_step(row,mode,foreground['window'],icon['window'])
        preserve('verdict',row['evaluation'])
    try:
        preserve('prepared',{k:v for k,v in result.items() if k!='steps'})
        point=icon_center(composition)
        step('icon-focus',{'click':point},lambda:click(point))
        step('unrelated-key',{'keys':['F8']},lambda:chord(['F8']))
        step('prepare-cycle',{'click':[600,110]},lambda:click([600,110]))
        step('cycle-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('cycle-icon',{'click':point},lambda:click(point))
        step('cycle-restore',{'keys':['Super_L','d']},display.reveal_key)
        step('prepare-folder',{'click':[600,110]},lambda:click([600,110]))
        step('folder-enter',{'keys':['Super_L','d']},display.reveal_key)
        result['before_folder_trace']=trace(environment);result['folder_started_ns']=time.monotonic_ns()
        result['folder_input']=gnome_input.observe(display,environment,shell_pid,workspace,composition,trace_function)
        result['folder_finished_ns']=time.monotonic_ns();result['after_folder_trace']=trace(environment)
        preserve('folder-input',{k:result[k] for k in ['before_folder_trace','folder_started_ns','folder_input','folder_finished_ns','after_folder_trace']})
        if result['folder_input']['outcome']!='pass':raise ValueError('native folder input failed')
        step('restore-after-folder',{'keys':['Alt_L','Tab']},lambda:chord(['Alt_L','Tab']))
        step('minimize-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('minimize-target',{'minimize':foreground['window']},minimize)
        step('minimize-restore',{'keys':['Super_L','d']},display.reveal_key)
        step('restore-minimized',{'keys':['Alt_L','Tab']},lambda:chord(['Alt_L','Tab']))
        result['before_disable_trace']=trace(environment);result['disable_started_ns']=time.monotonic_ns()
        reply=subprocess.run(['/usr/bin/gdbus','call','--address',environment['DBUS_SESSION_BUS_ADDRESS'],
                              '--dest','org.gnome.Shell','--object-path','/org/syspane/LabMarker',
                              '--method','org.syspane.LabMarker.DisableFocusIntegration'],
                             env=environment,capture_output=True,text=True,timeout=1,check=True)
        if reply.stdout.strip()!='()' or reply.stderr:raise ValueError('one-way disable reply differs')
        result['disable_finished_ns']=time.monotonic_ns()
        result['after_disable_trace']=trace(environment)
        preserve('disabled',{k:result[k] for k in ['before_disable_trace','disable_started_ns','disable_finished_ns','after_disable_trace']})
        step('disabled-enter',{'keys':['Super_L','d']},display.reveal_key)
        step('disabled-restore',{'keys':['Super_L','d']},display.reveal_key)
        result['final_trace']=trace(environment)
        result['binding_after']=binding(environment);result['background_after']=settings(environment)
        result['finished_monotonic_ns']=time.monotonic_ns()
        result['outcome']='pass';result['not_run']=[]
        return result
    except Exception as error:
        result['outcome']='inconclusive';result['error']=type(error).__name__+': '+str(error)
        preserve('error',{'message':result['error']});return result
    finally:
        preserve('completed',result);journal.close()
