"""Native GNOME application-list observations over a private read-only AT-SPI bus."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time

from native_oracle import ROOT
from native_x11_host import rgb_record
from x11_recovery import ResourceOwner
from gnome_composition import FIXTURE as SCENE, settings, judge_samples

FIXTURE_PATH = ROOT/'tests/desktop/fixtures/gnome-switcher.json'
FIXTURE = json.loads(FIXTURE_PATH.read_text())
STEPS = ['baseline','switcher','cancelled','selected-beta','selected-alpha','overview','restored']


def visible_entries(observation, kind):
    """Derive the complete native list from its structure, then inspect its icons."""
    from record_gnome_host import rgb
    rows=observation['tree']['rows'];by_path={tuple(r['path']):r for r in rows}
    children=lambda path:[r for r in rows if r['path'][:-1]==list(path) and r['path']]
    inside=lambda node,parent:len(node['path'])>len(parent) and node['path'][:len(parent)]==list(parent)
    if kind=='switcher':
        labels=[r for r in rows if r['showing'] and r['role']=='label' and r['name']==FIXTURE['applications']['alpha']['name']]
        if not labels:return {'visible':False,'entries':[]}
        if len(labels)!=1:raise ValueError('unique switcher positive label required')
        ancestors=[by_path[tuple(labels[0]['path'][:n])] for n in range(len(labels[0]['path']))]
        buttons=[r for r in ancestors if r['role']=='push button' and r['showing']]
        if len(buttons)!=1:raise ValueError('native switcher item ancestry')
        container=buttons[0]['path'][:-1];items=children(container)
        if not items or any(r['role']!='push button' or not r['showing'] for r in items):raise ValueError('complete switcher button list required')
        named=[]
        for button in items:
            labels=[r for r in rows if inside(r,button['path']) and r['role']=='label' and r['showing']]
            if len(labels)!=1 or not labels[0]['name']:raise ValueError('switcher item label required')
            named.append((button,labels[0]['name']))
    else:
        overview=[r for r in rows if r['name']=='Overview' and r['role']=='panel' and r['showing']]
        controls=[r for r in rows if r['name']=='Show Apps' and r['role']=='toggle button' and r['showing']]
        if not overview or not controls:return {'visible':False,'entries':[]}
        if len(overview)!=1 or len(controls)!=1 or not inside(controls[0],overview[0]['path']):raise ValueError('native overview/dash identity')
        container=controls[0]['path'][:-2]
        wrappers=children(container)
        if len(wrappers)!=2 or wrappers[1]['path']!=controls[0]['path'][:-1]:raise ValueError('native dash layout identity')
        items=children(wrappers[0]['path']);named=[]
        for item in items:
            buttons=[r for r in children(item['path']) if r['role']=='push button' and r['showing']]
            if len(buttons)!=1 or not buttons[0]['name']:raise ValueError('complete running-application dash item required')
            named.append((buttons[0],buttons[0]['name']))
    pixels=rgb(observation['pixels'],800*600*3);entries=[]
    by_name={r['name']:r for r in FIXTURE['applications'].values()}
    for button,name in named:
        squares=[r for r in rows if inside(r,button['path']) and r['showing'] and r['rectangle'] and
                 r['rectangle'][2]==r['rectangle'][3] and 16<=r['rectangle'][2]<=128]
        if not squares:raise ValueError('native application icon rectangle required')
        icon=min(squares,key=lambda r:r['rectangle'][2]);x,y,w,h=icon['rectangle']
        if not 0<=x<x+w<=800 or not 0<=y<y+h<=600:raise ValueError('application icon outside captured display')
        px,py=x+w//2-4,y+h//2-4
        sample=b''.join(pixels[((py+n)*800+px)*3:((py+n)*800+px+8)*3] for n in range(8))
        matching=name in by_name and sample==bytes(by_name[name]['icon_rgb'])*64
        entries.append({'name':name,'button_path':button['path'],'icon_rectangle':icon['rectangle'],
                        'pixel_witness':[px,py,8,8],'icon_pixels':rgb_record(sample),'icon_matches':matching})
    return {'visible':True,'container_path':container,'entries':entries}


def focused(observation,role,applications):
    from record_gnome_host import rgb
    item=FIXTURE['applications'][role];x,y,_,_=item['window'];pixels=rgb(observation['pixels'],800*600*3)
    sample=b''.join(pixels[((y+30+n)*800+x+30)*3:((y+30+n)*800+x+50)*3] for n in range(20))
    return observation['native']['active_window']==[applications[role]['window']] and sample==bytes(item['rgb'])*400


def judge(result,composition):
    from record_gnome_host import rgb
    from oracle import evaluate
    rows=result['observations'];control=result['control'];names=[r['step'] for r in rows]
    expected=STEPS[:2] if control=='no-switcher' else STEPS
    if names!=expected:raise ValueError('native switcher sequence differs')
    entries=visible_entries(rows[1],'switcher')
    controls={FIXTURE['applications'][r]['name'] for r in ['alpha','beta']}
    def absence(value):
        return value['visible'] and len(value['entries'])==2 and {e['name'] for e in value['entries']}==controls and all(e['icon_matches'] for e in value['entries'])
    focus_checks=[focused(rows[0],'alpha',result['applications'])]
    overview=None;final=None
    if control!='no-switcher':
        focus_checks += [focused(rows[index],role,result['applications']) for index,role in [(2,'alpha'),(3,'beta'),(4,'alpha'),(6,'alpha')]]
        overview=visible_entries(rows[5],'overview')
        marker=result['final_marker'];trace=marker['trace'];paired=result['final_samples']
        if trace['end_us']!=2400000 or [s['generation'] for s in trace['stimuli']]!=[1,2,3] or len(trace['frames'])!=len(paired):raise ValueError('final marker completeness')
        calibration=[rgb(s['frames'][0]['pixels'],180*220*3) for s in composition['calibrations']]
        overlaps=[]
        for frame,row in zip(trace['frames'],paired):
            if not frame['start_us']<=frame['end_us']<=row['start_us']<=row['end_us']:raise ValueError('final paired timing')
            overlaps.append({'marker_start_us':frame['start_us'],**{k:row[k] for k in ['start_us','end_us','pixels']}})
            focus_checks.append(row['native']['active_window']==[result['applications']['alpha']['window']])
        mark=evaluate(trace);comp=judge_samples(calibration[2],overlaps,calibration[:2])
        if marker['evaluation']!=mark:raise ValueError('final marker verdict differs')
        for key in ['background_before','background_after']:
            if rgb(marker[key],128*96*3)!=bytes(SCENE['background_rgb'])*128*96:raise ValueError('final background pixels differ')
        final={'marker':mark['outcome'],'icons':comp['icons'],'rectangle':comp['rectangle'],
               'max_gap_us':comp['max_gap_us'],'max_capture_us':comp['max_capture_us']}
    focus=all(focus_checks)
    good_final=final and all(final[k]=='pass' for k in ['marker','icons','rectangle'])
    return {'switcher':entries,'overview':overview,'focus':'pass' if focus else 'fail','final':final,
            'switcher_absence':'pass' if absence(entries) else 'fail',
            'dash_absence':None if overview is None else ('pass' if absence(overview) else 'fail'),
            'outcome':'pass' if absence(entries) and overview and absence(overview) and focus and good_final else 'fail'}


def prepare(workspace):
    apps = workspace/'data/applications'; apps.mkdir()
    icons = workspace/'data/icons'; icons.mkdir(exist_ok=True)
    records = {}
    for role, item in FIXTURE['applications'].items():
        icon = icons/(item['id']+'.svg')
        color = ','.join(map(str, item['icon_rgb']))
        icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" fill="rgb('+color+')"/></svg>\n')
        text = ('[Desktop Entry]\nType=Application\nName='+item['name']+'\nExec=/usr/bin/python3 '+
                str(ROOT/'tests/desktop/gnome_switcher_app.py')+' '+role+'\nIcon='+str(icon)+
                '\nStartupWMClass='+item['id']+'\nTerminal=false\nDBusActivatable=false\n')
        (apps/(item['id']+'.desktop')).write_text(text)
        records[role] = {'desktop': text, 'icon': icon.read_text()}
    return records


def native_settings(environment):
    values = {}
    for schema, key in [('org.gnome.shell', 'favorite-apps'), ('org.gnome.desktop.wm.keybindings', 'switch-applications')]:
        value = subprocess.run(['/usr/bin/gsettings', 'get', schema, key], env=environment,
                               capture_output=True, text=True, timeout=1, check=True)
        if value.stderr or len(value.stdout)>512: raise ValueError('native switcher settings response')
        values[key] = value.stdout.strip()
    return values


def identity(display, pid, role):
    matches = []
    for window in display.property(display.root, '_NET_CLIENT_LIST_STACKING'):
        owner = ResourceOwner(display).pid(window)
        if not owner or owner[0]!=pid: continue
        kind = display.property(window, '_NET_WM_WINDOW_TYPE')
        if kind!=[display.atom('_NET_WM_WINDOW_TYPE_NORMAL')]: raise ValueError('normal fixture window required')
        x, y, child = C.c_int(), C.c_int(), C.c_ulong()
        if not display.x.XTranslateCoordinates(display.handle, window, display.root, 0, 0, C.byref(x), C.byref(y), C.byref(child)):
            raise ValueError('fixture client coordinates unavailable')
        path = Path('/proc')/str(pid)
        arguments = [p.decode() for p in (path/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
        state = (path/'stat').read_text().rsplit(')',1)[1].split()
        if arguments!=['/usr/bin/python3',str(ROOT/'tests/desktop/gnome_switcher_app.py'),role] or int(state[2])!=pid or int(state[3])!=pid:
            raise ValueError('owned application process identity')
        root,gx,gy,width,height,border,depth=C.c_ulong(),C.c_int(),C.c_int(),C.c_uint(),C.c_uint(),C.c_uint(),C.c_uint()
        display.x.XGetGeometry.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_int),C.POINTER(C.c_int),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
        if not display.x.XGetGeometry(display.handle,window,C.byref(root),C.byref(gx),C.byref(gy),C.byref(width),C.byref(height),C.byref(border),C.byref(depth)):raise ValueError('fixture geometry unavailable')
        geometry=[x.value,y.value,width.value,height.value]
        if geometry!=FIXTURE['applications'][role]['window']: raise ValueError('fixture geometry differs')
        matches.append({'window':window,'pid':pid,'role':role,'resource_base':owner[1],'resource_mask':owner[2],
                        'arguments':arguments,'process_group':int(state[2]),'session':int(state[3]),'start_ticks':int(state[19]),
                        'executable':str((path/'exe').resolve(strict=True)),'geometry':geometry,'type':kind,
                        'normal_type_atom':display.atom('_NET_WM_WINDOW_TYPE_NORMAL')})
    if len(matches)!=1: raise ValueError('one owned application window required')
    return matches[0]


class ShellObserver:
    def __init__(self, display, environment, workspace, shell_pid):
        from gi.repository import Gio, GLib
        self.api,self.glib = Gio,GLib
        self.bus = Gio.DBusConnection.new_for_address_sync(environment['AT_SPI_BUS_ADDRESS'],
            Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
        self.display,self.shell_pid = display,shell_pid
        self.journal = (workspace/'switcher.jsonl').open('x',encoding='utf-8',newline='\n')
        self.count = 0
        display.xtest.XTestFakeMotionEvent.argtypes = [C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_ulong]
        display.xtest.XTestFakeButtonEvent.argtypes = [C.c_void_p,C.c_uint,C.c_int,C.c_ulong]

    def preserve(self,kind,value):
        self.count+=1
        if self.count>180: raise ValueError('switcher journal record capacity')
        self.journal.write(json.dumps({'kind':kind,'value':value},separators=(',',':'))+'\n');self.journal.flush()
        if self.journal.tell()>8*1024**2: raise ValueError('switcher journal byte capacity')

    def key(self,name,pressed):
        d=self.display;code=d.x.XKeysymToKeycode(d.handle,d.x.XStringToKeysym(name.encode()))
        if not code or not d.xtest.XTestFakeKeyEvent(d.handle,code,pressed,0):raise ValueError('native key stimulus failed')
        d.x.XFlush(d.handle)
        self.preserve('key',{'name':name,'pressed':pressed,'at_ns':time.monotonic_ns()})

    def tap(self,name):self.key(name,True);self.key(name,False)

    def click(self,role):
        x,y,w,h=FIXTURE['applications'][role]['window'];d=self.display
        if not d.xtest.XTestFakeMotionEvent(d.handle,-1,x+w//2,y+h//2,0):raise ValueError('fixture pointer motion')
        for down in (True,False):
            if not d.xtest.XTestFakeButtonEvent(d.handle,1,down,0):raise ValueError('fixture click')
        d.x.XFlush(d.handle);self.preserve('click',{'role':role,'point':[x+w//2,y+h//2],'at_ns':time.monotonic_ns()})

    def tree(self):
        started=time.monotonic_ns();deadline=time.monotonic()+3
        def call(destination,path,interface,method,args=None):
            if time.monotonic()>=deadline:raise TimeoutError('shell tree deadline')
            return self.bus.call_sync(destination,path,interface,method,args,None,self.api.DBusCallFlags.NO_AUTO_START,250,None).unpack()
        accessible='org.a11y.atspi.Accessible'
        children=call('org.a11y.atspi.Registry','/org/a11y/atspi/accessible/root',accessible,'GetChildren')[0]
        if len(children)>8:raise ValueError('private application capacity')
        apps=[]
        for app in children:
            pid=call('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetConnectionUnixProcessID',self.glib.Variant('(s)',(app[0],)))[0]
            if pid==self.shell_pid:apps.append(app)
        if len(apps)!=1:raise ValueError('unique native shell accessibility peer required: '+str(children))
        rows=[];queue=[(apps[0],[],0)]
        self.partial_tree = rows
        while queue:
            if len(rows)>=512:raise ValueError('shell tree node capacity')
            obj,path,depth=queue.pop(0)
            if depth>24:raise ValueError('shell tree depth capacity')
            destination,object_path=obj
            if destination!=apps[0][0]:raise ValueError('foreign shell subtree peer')
            name=call(destination,object_path,'org.freedesktop.DBus.Properties','Get',self.glib.Variant('(ss)',(accessible,'Name')))[0] or ''
            if len(name)>256:raise ValueError('shell tree name capacity')
            states=call(destination,object_path,accessible,'GetState')[0]
            if len(states)!=2:raise ValueError('shell tree state shape')
            role=call(destination,object_path,accessible,'GetRoleName')[0]
            interfaces=call(destination,object_path,accessible,'GetInterfaces')[0]
            rectangle=None
            if 'org.a11y.atspi.Component' in interfaces:
                rectangle=list(call(destination,object_path,'org.a11y.atspi.Component','GetExtents',self.glib.Variant('(u)',(0,)))[0])
            rows.append({'path':path,'name':name,'role':role,'states':list(states),'showing':bool(states[0]&(1<<25)),
                         'selected':bool(states[0]&(1<<23)),'rectangle':rectangle,
                         'bus_name':destination,'object_path':object_path,'native_bus_pid':self.shell_pid})
            children=call(destination,object_path,accessible,'GetChildren')[0]
            if len(children)>64:raise ValueError('shell tree child capacity')
            rows[-1]['children_count']=len(children)
            rows[-1]['pruned_hidden']=bool(path and not rows[-1]['showing'] and children)
            if not rows[-1]['pruned_hidden']:
                queue.extend((child,path+[n],depth+1) for n,child in enumerate(children))
        return {'started_ns':started,'finished_ns':time.monotonic_ns(),'rows':rows,'bus_name':apps[0][0],'native_bus_pid':self.shell_pid}

    def capture(self,step):
        started=time.monotonic_ns();tree=self.tree()
        row={'step':step,'started_ns':started,'tree':tree,'pixels':rgb_record(self.display.capture(0,0,800,600)),
             'native':self.display.structure(),'finished_ns':time.monotonic_ns()}
        self.preserve('observation',row);return row

    def await_observation(self,step,predicate,trigger_ns):
        while time.monotonic_ns()-trigger_ns<3000000000:
            row=self.capture(step)
            if predicate(row):
                row['trigger_ns']=trigger_ns
                if row['finished_ns']-trigger_ns>3000000000:raise TimeoutError('native UI transition deadline')
                self.preserve('accepted-observation',row)
                return row
            time.sleep(.05)
        row['trigger_ns']=trigger_ns
        self.preserve('rejected-observation',row)
        return row

    def close(self):self.bus.close_sync(None);self.journal.close()


def observe(display,environment,shell_pid,workspace,composition,trace_function):
    observer=ShellObserver(display,environment,workspace,shell_pid)
    pids=json.loads(environment['SYSPANE_GNOME_SWITCHER_PIDS']);descriptors=[]
    result={'version':'0.1.0','control':environment['SYSPANE_GNOME_SWITCHER_CONTROL'],
            'fixture_sha256':hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
            'applications':{},'observations':[],'settings_before':native_settings(environment),
            'background_before':settings(environment),'actions':[]}
    try:
        if composition['outcome']!='pass':raise ValueError('live composition prerequisite')
        poller=select.poll()
        for role,pid in pids.items():
            descriptors.append(os.pidfd_open(pid));result['applications'][role]=identity(display,pid,role)
            poller.register(descriptors[-1],select.POLLIN)
        observer.preserve('identity',result)
        def step(name,action,predicate,performed=True):
            started=time.monotonic_ns()
            if performed:action()
            issued=time.monotonic_ns()
            record={'step':name,'performed':performed,'started_ns':started,'issued_ns':issued}
            result['actions'].append(record);observer.preserve('action',record)
            time.sleep(.2)
            row=observer.await_observation(name,predicate,issued)
            result['observations'].append(row)
            if poller.poll(0):raise ValueError('fixture process exited during observation')
            return predicate(row)
        def focus(role):return lambda row:focused(row,role,result['applications'])
        def switch():observer.key('Alt_L',True);observer.tap('Tab');observer.key('Alt_L',False)
        def ready(kind):return lambda row:visible_entries(row,kind)['visible']
        if not step('baseline',lambda:(observer.click('beta'),time.sleep(.1),observer.click('alpha')),focus('alpha')):raise ValueError('initial focus prerequisite')
        popup_expected=result['control']!='no-switcher'
        step('switcher',lambda:(observer.key('Alt_L',True),observer.tap('Tab')),
             lambda row:visible_entries(row,'switcher')['visible']==popup_expected,popup_expected)
        popup=visible_entries(result['observations'][-1],'switcher')['visible']
        if popup:
            if not step('cancelled',lambda:(observer.tap('Escape'),observer.key('Alt_L',False)),focus('alpha')):raise ValueError('popup cancel focus failed')
            for role in ['beta','alpha']:
                if not step('selected-'+role,switch,focus(role)):raise ValueError('native application switch failed')
            if not step('overview',lambda:observer.tap('Super_L'),ready('overview')):raise ValueError('overview absent')
            if not step('restored',lambda:observer.tap('Escape'),focus('alpha')):raise ValueError('overview dismissal focus failed')
            result['final_samples']=[]
            def sample(frame,now):
                row={'start_us':now(),'pixels':rgb_record(display.capture(*SCENE['overlap'])),'native':display.structure(),'end_us':now()}
                result['final_samples'].append(row);observer.preserve('final-sample',{'marker':frame,'observation':row})
                if poller.poll(0):raise ValueError('fixture exited during final composition')
            result['final_marker']=trace_function(display,environment,sample=sample,dismiss=False)
        elif result['control']!='no-switcher':raise ValueError('positive native switcher prerequisite failed')
        result['settings_after']=native_settings(environment)
        result['background_after']=settings(environment)
        result['applications_after']={role:identity(display,pid,role) for role,pid in pids.items()}
        result['not_run']=STEPS[len(result['observations']):]+(['final-composition'] if not popup else [])
        if result['applications_after']!=result['applications'] or poller.poll(0):raise ValueError('fixture lifetime changed')
        result['evaluation']=judge(result,composition);result['outcome']=result['evaluation']['outcome']
        observer.preserve('completed',result)
        return result
    except Exception as error:
        if hasattr(observer,'partial_tree'):observer.preserve('tree-incomplete',observer.partial_tree)
        observer.preserve('error',{'message':type(error).__name__+': '+str(error)})
        raise
    finally:
        for descriptor in descriptors:os.close(descriptor)
        observer.close()
