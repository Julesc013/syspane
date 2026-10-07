"""Independent native binding controls, exact stored descriptors and erasure."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
from native_editor import ROOT,sha,stored,launch_xvfb
from native_content_properties import ContentHarness,canvas,region,select_widget
CASES=json.loads((ROOT/'tests/editor/binding-authoring-cases.json').read_text())
TEXT=json.loads((ROOT/'tests/editor/binding-text-cases.json').read_text())
class BindingHarness(ContentHarness):
    def __init__(self,*args):
        super().__init__(*args,properties=True);self.cases=CASES;self.report['fixture_sha256']=sha(ROOT/'tests/editor/binding-authoring-cases.json')
    def find(self,id):
        if id not in self.controls:
            for obj in self.objects():
                description=obj.get_description() or ''
                if description.startswith('editor.'):self.controls[description[7:]]=obj
            assert len(self.controls)<=128
        return self.controls.get(id)

def value(h,id):return h.text(h.find('binding.'+id))
def field(h,id,text):
    obj=h.find('binding.'+id);h.wait(lambda:h.sensitive('binding.'+id))
    assert h.Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(text));h.wait(lambda:value(h,id)==str(text))
def selected(h,id):
    obj=h.find('binding.'+id);obj.clear_cache();selection=obj.get_selection_iface()
    try:
        if selection and selection.get_n_selected_children():return h.text(selection.get_selected_child(0))
    except h.GLib.GError as error:
        if error.domain!='atspi_error' or 'does not exist' not in str(error):raise
    return ''
def choose(h,id,index,expected):
    obj=h.find('binding.'+id);rect=obj.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN);h.input.click(rect.x+rect.width-12,rect.y+rect.height//2)
    def option():
        matches=[o for o in h.objects() if o.get_role()==h.Atspi.Role.MENU_ITEM and o.get_state_set().contains(h.Atspi.StateType.SHOWING) and h.text(o)==expected]
        bounds=[o.get_component_iface().get_extents(h.Atspi.CoordType.SCREEN) for o in matches]
        # GTK exports its popup through both the combo and application hierarchy.
        positions={(b.x,b.y,b.width,b.height) for b in bounds if b.x>=0 and b.width>0}
        assert len(positions)<=1
        return next(iter(positions)) if positions else None
    x,y,width,height=h.wait(option);h.input.click(x+width//2,y+height//2)
    h.wait(lambda:selected(h,id)==expected)

def tab(h,id):
    # GTK exports notebook tabs as PAGE_TAB, not the private GtkLabel child.
    title={'target':'Target','filter':'Filter','order':'Order'}[id]
    matches=[o for o in h.objects() if o.get_role()==h.Atspi.Role.PAGE_TAB and h.text(o)==title]
    assert len(matches)==1
    rect=matches[0].get_component_iface().get_extents(h.Atspi.CoordType.SCREEN)
    h.input.click(rect.x+rect.width//2,rect.y+rect.height//2)
    h.wait(lambda:h.find('binding.'+('predicate-Add' if id=='filter' else 'sort-Add' if id=='order' else 'scope')).get_state_set().contains(h.Atspi.StateType.SHOWING))
def open_binding(h):h.click('bindings');h.wait(lambda:h.find('binding.set') is not None and h.sensitive('binding.set') and not h.sensitive('bindings'))
def set_binding(h):h.click('binding.set');h.wait(lambda:h.sensitive('bindings'));h.input.focus(h.pid)
def predicate(h,f,op,kind,v):
    previous=selected(h,'predicate');h.click('binding.predicate-Add');h.wait(lambda:selected(h,'predicate')!=previous and value(h,'predicate_field')=='')
    field(h,'predicate_field',f);choose(h,'op',0,op);choose(h,'type',0,kind);field(h,'value',v)
def order(h,f,direction):
    previous=selected(h,'sort');h.click('binding.sort-Add');h.wait(lambda:selected(h,'sort')!=previous and value(h,'sort_field')=='')
    field(h,'sort_field',f);choose(h,'direction',0,direction)
def populate(h,mode):
    if mode=='text':
        tab(h,'filter');predicate(h,'entity.id','eq','text',TEXT['text'][0]['input']);choose(h,'encoding',1,'escaped');return
    if mode=='table':
        field(h,'limit','1');tab(h,'filter');predicate(h,'entity.id','ne','text','nic:absent');tab(h,'order');order(h,'entity.id','descending');return
    field(h,'field','network.transmit_bytes')
    if mode=='direct':
        choose(h,'kind',1,'direct');field(h,'producer_id','P1');field(h,'producer_epoch','E1');field(h,'entity_id','nic:one')
    elif mode=='persistent':
        choose(h,'kind',2,'persistent_pin');choose(h,'scope',2,'registered_asset');field(h,'asset_id','asset:remote');field(h,'entity_type','network.adapter');field(h,'namespace','network.adapter');field(h,'key','Adapter\nα')
    elif mode=='selector':
        choose(h,'scope',1,'current_session');field(h,'entity_type','network.adapter');field(h,'limit','7');tab(h,'filter')
        predicate(h,'network.receive_bytes','eq','number','9007199254740993');predicate(h,'entity.display_name','ne','text','Ghost');h.click('binding.predicate-Up');h.wait(lambda:selected(h,'predicate')=='Predicate 1')
        # Switching rows preserves exact numeric text and the private row order.
        choose(h,'predicate',1,'Predicate 2');assert value(h,'value')=='9007199254740993'
        tab(h,'order');order(h,'entity.id','ascending');order(h,'entity.display_name','descending');h.click('binding.sort-Up');h.wait(lambda:selected(h,'sort')=='Sort key 1')
    elif mode=='empty':
        field(h,'field','network.receive_bytes');tab(h,'filter');predicate(h,'entity.id','eq','text','nic:absent')
def preview(h,mode,baseline=None):
    label=canvas(h)
    if mode=='table':return 'Showing 1 of 1 rows' in label and 'Receive [network.receive_bytes]: 80 byte' in label and 'Sent [network.transmit_bytes]: 0 byte' in label
    if 'Chart\n' not in label:return False
    chart=label[label.index('Chart\n'):]
    if mode in ('direct','empty','text'):
        if 'No matching entity' not in chart:return False
    elif mode in ('persistent','selector'):
        if 'Unsupported field' not in chart:return False
    elif 'Point 2000000000: 0' not in chart or 'Point 2000000000: 80' in chart:return False
    return baseline is None or region(h,'chart')!=baseline
def exercise(h):
    h.launch();h.check();h.stage='SOURCE';h.wait(lambda:'Point 2000000000: 80' in canvas(h));mode=h.mode;kind='table' if mode=='table' else 'chart';select_widget(h,kind);baseline=region(h,kind);h.report['baseline_pixel_sha256']=hashlib.sha256(baseline).hexdigest()
    if mode=='frozen-preview':h.command('freeze-preview')
    h.stage='BUFFER';open_binding(h);assert not h.sensitive('apply') and not h.sensitive('undo') and not h.sensitive('value.title');h.check()
    if mode=='field':
        set_binding(h);assert not h.sensitive('apply') and not h.sensitive('undo');h.wait(lambda:region(h,kind)==baseline);open_binding(h)
    if mode in ('revoke','retain-binding'):
        tab(h,'filter');predicate(h,'entity.display_name','eq','text','Private filter');held=[h.find('binding.value'),h.find('binding.predicate_field'),h.find('binding.entity_type')]
        issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:all(h.erased(o) for o in held) and h.cleared_canvas(),max(.001,issued+.2-time.monotonic()));h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms'];h.report['production_erased']=True
        h.stage='RETAINED';assert not any('Private filter' in h.text(o) for o in h.objects()),'retained binding disclosed';h.check();h.command('regrant');assert not h.sensitive('bindings') and all(h.erased(o) for o in held);h.input.focus(h.pid);h.click('reload');h.event('event','reloaded');h.wait(lambda:'Move me' in canvas(h));h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode=='invalid':
        tab(h,'filter');predicate(h,'network.receive_bytes','eq','number','18446744073709551616');h.click('binding.set');h.wait(lambda:bool(value(h,'error')));assert value(h,'value')=='18446744073709551616';h.check();h.click('binding.predicate-Remove');tab(h,'target')
    populate(h,mode);h.check();h.screenshot('buffer')
    if mode=='cancel-buffer':
        held=h.find('binding.field');h.click('binding.cancel');h.wait(lambda:h.sensitive('bindings') and h.erased(held));h.input.focus(h.pid);assert not h.sensitive('apply') and not h.sensitive('undo');h.wait(lambda:region(h,kind)==baseline);open_binding(h);assert value(h,'field')=='network.receive_bytes';populate(h,mode)
    h.stage='SET';set_binding(h);h.wait(lambda:h.sensitive('apply'));h.stage='PIXELS';h.wait(lambda:preview(h,mode,baseline));h.screenshot('draft');h.report['edited_accessible']=canvas(h);h.report['edited_pixel_sha256']=hashlib.sha256(region(h,kind)).hexdigest()
    expected=TEXT['expected'] if mode=='text' else CASES['expected'][mode if mode in CASES['expected'] else 'field'];h.click('undo');h.wait(lambda:not h.sensitive('apply'));h.wait(lambda:'Point 2000000000: 80' in canvas(h));h.click('redo');h.wait(lambda:h.sensitive('apply'));h.wait(lambda:preview(h,mode));h.check()
    h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');assert not h.sensitive('bindings');h.check()
    if mode!='wrong-binding':assert submitted['body']['operations'][0]['scene']==expected
    if mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
    h.command('release');result=h.event('event','result')['result']
    if mode=='cancel':assert result['outcome']=='cancelled';h.check();h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());record=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==record
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.stage='REOPEN';h.wait(lambda:preview(h,mode))
    if mode=='text':
        select_widget(h,'chart');open_binding(h);tab(h,'filter');assert selected(h,'encoding')=='escaped' and value(h,'value')==TEXT['text'][0]['input'];set_binding(h);assert not h.sensitive('apply') and not h.sensitive('undo');h.check(expected,'41')
    h.command('quit');assert h.proc.wait(timeout=5)==0;assert mode not in ('wrong-binding','frozen-preview','retain-binding');h.report['outcome']='pass'
def observe(exe,exit_exe,folder,mode):
    h=BindingHarness(exe,exit_exe,folder,mode);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),content_harness_sha256=sha(ROOT/'tests/editor/native_content_properties.py'),text_fixture_sha256=sha(ROOT/'tests/editor/binding-text-cases.json'))
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.report['accessible']=canvas(h);h.screenshot('failure')
        wrong=mode=='wrong-binding' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][2]['bindings'][0]['field']=='network.receive_bytes'
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(exc)=='PIXELS observation deadline' and 'Point 2000000000: 0' in canvas(h) and stored(h.directory)==h.documents() and hashlib.sha256(region(h,'chart')).hexdigest()==h.report['baseline_pixel_sha256']
        retained=mode=='retain-binding' and h.stage=='RETAINED' and str(exc)=='retained binding disclosed' and h.report.get('production_erased') and any(h.text(o)=='Retained binding canary Private filter' for o in h.objects())
        if wrong or frozen or retained:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve());folder=evidence/('binding-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-BINDING-AUTHORING',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),content_harness_sha256=sha(ROOT/'tests/editor/native_content_properties.py'),fixture_sha256=sha(ROOT/'tests/editor/binding-authoring-cases.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        report['text_fixture_sha256']=sha(ROOT/'tests/editor/binding-text-cases.json')
        for mode in CASES['native_modes']+['text']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr);assert not timed_out and child.returncode==0,(mode,stderr.decode(errors='replace'));case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass';report['cases'].append(dict(case=mode,outcome='pass',fault_detected=case.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
