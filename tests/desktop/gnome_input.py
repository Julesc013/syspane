"""Native stimuli and independent clipboard/AT-SPI evidence on an owned DING desktop."""
import ctypes as C
import json
import os
from pathlib import Path
import select
import time

from x11_input import InputObserver, NativeEvent
from x11_recovery import ResourceOwner
from native_x11_host import rgb_record
from gnome_composition import FIXTURE, masks, settings, judge_samples

STEPS=['baseline-clear','select','clear','drag-select','context-menu','menu-dismissed','double-click-open','restore-clear']


def icon_center(composition):
    from record_gnome_host import rgb
    size=FIXTURE['overlap'][2]*FIXTURE['overlap'][3]*3
    stages=[rgb(s['frames'][0]['pixels'],size) for s in composition['calibrations']]
    groups,_=masks(stages[2],stages[:2])
    points=[(n%180,n//180) for group in groups for n in group]
    x,y=min(p[0] for p in points),min(p[1] for p in points)
    if len(points)!=4096 or set(points)!={(a,b) for a in range(x,x+64) for b in range(y,y+64)}:
        raise ValueError('complete independent icon square required')
    return [x+32,y+32+32]


def clipboard_names(record, workspace, contents=False):
    if not record['owner_changed']:
        return []
    raw=record['raw_utf8']
    if raw.endswith('\0'):raw=raw[:-1]
    if '\0' in raw:raise ValueError('embedded clipboard NUL')
    lines=raw.splitlines()
    if not contents:
        if not lines or lines.pop(0)!='copy':raise ValueError('native copy operation required')
        if not lines:return []
    expected=(Path(workspace)/'home/Desktop/Probe Folder')
    if contents:expected/= 'Sentinel.txt'
    if lines!=[expected.as_uri()]:raise ValueError('native clipboard names an unexpected file')
    return ['Sentinel.txt' if contents else 'Probe Folder']


class Observer(InputObserver):
    def __init__(self,display,owner,workspace,shell_pid):
        self.count=0
        self.shell_pid=shell_pid
        self.icon_descriptor=os.pidfd_open(owner['pid'])
        self.icon_poll=select.poll();self.icon_poll.register(self.icon_descriptor,select.POLLIN)
        super().__init__(display,owner['pid'],workspace,owner['window'])

    def tree(self):
        rows=super().tree()
        if not rows or len({row['bus_name'] for row in rows})!=1:
            raise ValueError('one native accessibility application required')
        pid=self.bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',
                              'GetConnectionUnixProcessID',self.glib.Variant('(s)',(rows[0]['bus_name'],)),
                              None,self.api.DBusCallFlags.NO_AUTO_START,250,None).unpack()[0]
        if pid!=self.manager_pid:raise ValueError('accessibility native peer changed')
        return [{**row,'native_bus_pid':pid} for row in rows]

    def close(self):
        super().close()
        os.close(self.icon_descriptor)

    def wait_application(self):
        started=time.monotonic_ns();deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            children=self.bus.call_sync('org.a11y.atspi.Registry','/org/a11y/atspi/accessible/root',
                'org.a11y.atspi.Accessible','GetChildren',None,None,self.api.DBusCallFlags.NO_AUTO_START,250,None).unpack()[0]
            if len(children)>8:raise ValueError('private accessibility application capacity')
            matches=[]
            for app in children:
                if time.monotonic()>=deadline:raise TimeoutError('native accessibility registration deadline')
                pid=self.bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',
                    'GetConnectionUnixProcessID',self.glib.Variant('(s)',(app[0],)),None,
                    self.api.DBusCallFlags.NO_AUTO_START,250,None).unpack()[0]
                if pid==self.manager_pid:matches.append(app[0])
            if len(matches)>1:raise ValueError('ambiguous native accessibility registration')
            if matches:
                row={'pid':self.manager_pid,'bus_name':matches[0],'started_ns':started,'finished_ns':time.monotonic_ns()}
                self.preserve('accessibility-ready',row)
                return row
            time.sleep(.02)
        raise TimeoutError('native accessibility registration deadline')

    def preserve(self,kind,value):
        self.count+=1
        if self.count>256:raise ValueError('input journal record capacity')
        super().preserve(kind,value)
        if self.journal.tell()>8*1024**2:raise ValueError('input journal byte capacity')

    def copy_selection(self,folder_contents=False):
        d=self.display
        d.x.XDestroyWindow(d.handle,self.clipboard_window)
        self.clipboard_window=d.x.XCreateSimpleWindow(d.handle,d.root,0,0,1,1,0,0,0)
        selection,target,prop=[d.atom(n) for n in ('CLIPBOARD','text/uri-list' if folder_contents else 'x-special/gnome-copied-files','_SYSPANE_INPUT_SELECTION')]
        d.x.XSetSelectionOwner(d.handle,selection,self.clipboard_window,0)
        d.x.XSync(d.handle,False)
        if d.x.XGetSelectionOwner(d.handle,selection)!=self.clipboard_window:raise ValueError('clipboard initialization')
        started=time.monotonic_ns()
        self.control_key(b'c')
        issued=time.monotonic_ns()
        deadline=time.monotonic()+.5
        owner=self.clipboard_window
        while time.monotonic()<deadline:
            owner=d.x.XGetSelectionOwner(d.handle,selection)
            if owner!=self.clipboard_window:break
            time.sleep(.005)
        observed=time.monotonic_ns()
        result={'requestor':self.clipboard_window,'owner':owner,'owner_changed':owner!=self.clipboard_window,
                'started_ns':started,'issued_ns':issued,'owner_observed_ns':observed,'target':target,
                'target_name':'text/uri-list' if folder_contents else 'x-special/gnome-copied-files'}
        if owner!=self.clipboard_window:
            binding=ResourceOwner(d).pid(owner)
            if not binding or binding[0]!=(self.manager_pid if folder_contents else self.shell_pid):
                raise ValueError('clipboard owner is not the retained native producer')
            result['owner_binding']={'pid':binding[0],'resource_base':binding[1],'resource_mask':binding[2]}
            d.x.XConvertSelection(d.handle,selection,target,prop,self.clipboard_window,0)
            d.x.XFlush(d.handle)
            deadline=time.monotonic()+.5
            received=False; events=0
            while time.monotonic()<deadline and not received:
                while d.x.XPending(d.handle):
                    events+=1
                    if events>256:raise ValueError('clipboard event capacity')
                    event=NativeEvent(); d.x.XNextEvent(d.handle,C.byref(event)); reply=event.selection
                    if reply.type==31 and reply.requestor==self.clipboard_window and reply.selection==selection:
                        if reply.target!=target or reply.property!=prop:raise ValueError('native clipboard conversion refused')
                        received=True;break
                if not received:time.sleep(.005)
            if not received:raise TimeoutError('native clipboard response deadline')
            kind,form,count,remaining,data=C.c_ulong(),C.c_int(),C.c_ulong(),C.c_ulong(),C.c_void_p()
            status=d.x.XGetWindowProperty(d.handle,self.clipboard_window,prop,0,1024,True,0,C.byref(kind),C.byref(form),C.byref(count),C.byref(remaining),C.byref(data))
            try:
                if status or kind.value!=target or form.value!=8 or not 0<count.value<=4096 or remaining.value:
                    raise ValueError('native clipboard shape/capacity')
                result['raw_utf8']=C.string_at(data,count.value).decode('utf-8')
            finally:
                if data:d.x.XFree(data)
            if d.x.XGetSelectionOwner(d.handle,selection)!=owner:raise ValueError('clipboard owner changed during response')
        result['finished_ns']=time.monotonic_ns()
        self.preserve('clipboard-raw',result)
        result['names']=clipboard_names(result,self.workspace,folder_contents)
        self.preserve('clipboard',result)
        return result


def observe(display,environment,shell_pid,workspace,composition,trace_function):
    from record_gnome_host import rgb
    owner=composition['icon_manager']; control=environment['SYSPANE_GNOME_INPUT_CONTROL']
    observer=Observer(display,owner,workspace,shell_pid)
    result={'version':'0.1.0','control':control,'icon_manager':owner,'icon_center':icon_center(composition),
            'background_before':settings(environment),'steps':[]}
    folder_descriptor=None
    try:
        observer.preserve('identity',{k:v for k,v in result.items() if k!='steps'})
        result['accessibility_registration']=observer.wait_application()
        def check(name,selected=None,menu=None,contents=False):
            if observer.icon_poll.poll(0):raise ValueError('icon manager exited during input')
            clipboard=observer.copy_selection(contents) if selected is not None else None
            if menu is not None:
                tree,matched=observer.wait(lambda rows:any(r['role']=='menu item' and r['name']=='Open' and r['showing'] for r in rows)==menu)
            else:
                tree=observer.tree();matched=clipboard['owner_changed'] and clipboard['names']==selected
            native=display.structure()
            expected=result['folder']['window'] if contents else owner['window']
            if selected is not None:matched &= native['active_window']==[expected]
            row={'step':name,'outcome':'pass' if matched else 'fail','clipboard':clipboard,'tree':tree,'native':native,
                 'desktop_pixels':rgb_record(display.capture(0,0,800,600)),
                 'marker_pixels':rgb_record(display.capture(*FIXTURE['marker'])),'at_ns':time.monotonic_ns()}
            if observer.icon_poll.poll(0):raise ValueError('icon manager exited during observation')
            result['steps'].append(row);observer.preserve('step',row)
            return matched
        def failed():
            result['outcome']='fail';result['not_run']=STEPS[len(result['steps']):]
            return result
        x,y=result['icon_center']
        observer.click(700,550)
        if not check('baseline-clear',selected=[]):return failed()
        observer.preserve('selection-stimulus',{'point':[x,y],'performed':control!='no-selection'})
        if control!='no-selection':observer.click(x,y)
        if not check('select',selected=['Probe Folder']):return failed()
        observer.click(700,550)
        if not check('clear',selected=[]):return failed()
        observer.move(1,33);observer.preserve('drag',{'from':[1,33],'to':[179,251],'steps':12})
        observer.button(1,True)
        for n in range(1,13):observer.move(1+178*n//12,33+218*n//12);time.sleep(.02)
        observer.button(1,False)
        if not check('drag-select',selected=['Probe Folder']):return failed()
        observer.click(700,550);observer.click(x,y,3)
        if not check('context-menu',menu=True):return failed()
        observer.escape()
        if not check('menu-dismissed',menu=False):return failed()
        observer.click(700,550)
        before=set(display.property(display.root,'_NET_CLIENT_LIST_STACKING'))
        observer.click(x,y);time.sleep(.05);observer.click(x,y)
        deadline=time.monotonic()+3
        expected_executable=environment['SYSPANE_GNOME_FOLDER_EXECUTABLE']
        while time.monotonic()<deadline:
            found=[]
            for window in display.property(display.root,'_NET_CLIENT_LIST_STACKING'):
                if window in before or display.property(window,'_NET_WM_WINDOW_TYPE')!=[display.atom('_NET_WM_WINDOW_TYPE_NORMAL')]:continue
                binding=ResourceOwner(display).pid(window)
                if not binding:continue
                path=Path('/proc')/str(binding[0])
                try:
                    executable=str((path/'exe').resolve(strict=True))
                    if executable!=expected_executable:continue
                    stat=(path/'stat').read_text().rsplit(')',1)[1].split()
                    arguments=[s.decode() for s in (path/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
                    if int(stat[2])!=shell_pid or int(stat[3])!=shell_pid:raise ValueError('folder process escaped retained shell group')
                    found.append({'window':window,'pid':binding[0],'resource_base':binding[1],'resource_mask':binding[2],
                                  'executable':executable,'arguments':arguments,'process_group':int(stat[2]),'session':int(stat[3]),'start_ticks':int(stat[19])})
                except FileNotFoundError:continue
            if len(found)>1:raise ValueError('ambiguous native folder window')
            if found:break
            time.sleep(.02)
        else:raise TimeoutError('native folder did not open')
        result['folder']=found[0];folder_descriptor=os.pidfd_open(found[0]['pid'])
        result['folder']['type']=[display.atom('_NET_WM_WINDOW_TYPE_NORMAL')]
        result['folder']['normal_type_atom']=display.atom('_NET_WM_WINDOW_TYPE_NORMAL')
        poller=select.poll();poller.register(folder_descriptor,select.POLLIN)
        observer.manager_pid=found[0]['pid']
        result['folder']['accessibility_registration']=observer.wait_application()
        tree,visible=observer.wait(lambda rows:any(r['role']=='frame' and r['name']=='Probe Folder' and r['showing'] for r in rows))
        if not visible or poller.poll(0):raise ValueError('native folder frame/lifetime unavailable')
        observer.control_key(b'a')
        if not check('double-click-open',selected=['Sentinel.txt'],contents=True):return failed()
        if poller.poll(0):raise ValueError('folder process exited during observation')
        result['folder']['mapped_files']={}
        from native_gnome_bootstrap import mapped_files
        result['folder']['mapped_files']=mapped_files(found[0]['pid'])
        observer.preserve('close-folder',{'window':found[0]['window']})
        display.send(found[0]['window'])
        deadline=time.monotonic()+3
        while found[0]['window'] in display.property(display.root,'_NET_CLIENT_LIST_STACKING'):
            if time.monotonic()>=deadline:raise TimeoutError('native folder window did not close')
            time.sleep(.02)
        result['folder_closed']=True
        observer.manager_pid=owner['pid']
        observer.click(700,550)
        if not check('restore-clear',selected=[]):return failed()
        overlaps=[]
        def sample(frame,now):
            start=now();pixels=display.capture(*FIXTURE['overlap'])
            overlaps.append({'marker_start_us':frame['start_us'],'start_us':start,'end_us':now(),'pixels':rgb_record(pixels)})
        marker=trace_function(display,environment,sample=sample,dismiss=False)
        size=180*220*3
        calibration=[rgb(s['frames'][0]['pixels'],size) for s in composition['calibrations']]
        evaluation=judge_samples(calibration[2],overlaps,calibration[:2])
        result['final_composition']={'marker':marker,'overlap_samples':overlaps,'evaluation':evaluation}
        result['background_after']=settings(environment)
        result['outcome']='pass' if marker['evaluation']['outcome']=='pass' and evaluation['icons']==evaluation['rectangle']=='pass' and result['background_before']==result['background_after'] else 'fail'
        result['not_run']=[]
        return result
    except Exception as error:
        result['outcome']='inconclusive';result['error']=type(error).__name__+': '+str(error)
        result['not_run']=STEPS[len(result['steps']):]
        observer.preserve('error',{'message':result['error']})
        return result
    finally:
        observer.preserve('completed',result)
        observer.escape();observer.button(1,False);observer.close()
        if folder_descriptor is not None:os.close(folder_descriptor)
