from pathlib import Path
r=Path(__file__).resolve().parents[2]
def write(p,t):(r/p).write_text(t,encoding='utf-8',newline='\n')
p=r/'tests/editor/native_binding_authoring.py';s=p.read_text();helpers=s[s.index('def value('):s.index('def tab(')].replace('binding.','create.')
head='''"""Independent native widget creation, selection history, storage and erasure."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,signal,subprocess,sys,time,uuid
from native_editor import ROOT,sha,stored,launch_xvfb
from native_content_properties import ContentHarness,canvas
CASES=json.loads((ROOT/'tests/editor/widget-creation-cases.json').read_text())
KINDS=['text','value','status','table','chart','image','group']
class CreationHarness(ContentHarness):
    def __init__(self,*args):
        super().__init__(*args,properties=True);self.cases=CASES;self.report['fixture_sha256']=sha(ROOT/'tests/editor/widget-creation-cases.json')
    def find(self,id):
        if id not in self.controls:
            for obj in self.objects():
                description=obj.get_description() or ''
                if description.startswith('editor.'):self.controls[description[7:]]=obj
            assert len(self.controls)<=128
        return self.controls.get(id)

'''
tail='''
def tab(h,title):
    matches=[o for o in h.objects() if o.get_role()==h.Atspi.Role.PAGE_TAB and h.text(o)==title];assert len(matches)==1
    rect=matches[0].get_component_iface().get_extents(h.Atspi.CoordType.SCREEN);h.input.click(rect.x+rect.width//2,rect.y+rect.height//2)
    h.wait(lambda:matches[0].get_state_set().contains(h.Atspi.StateType.SELECTED))
def open_create(h):
    h.click('insert');h.wait(lambda:h.find('create.add') is not None and h.sensitive('create.add') and not h.sensitive('insert'))
def add(h):h.click('create.add');h.wait(lambda:h.sensitive('insert'));h.input.focus(h.pid)
def pixels(h):return h.pixels(18,18,325,245)
def kind(h,k):
    choose(h,'kind',KINDS.index(k),k);h.wait(lambda:value(h,'title')==k.capitalize())
def preview(h,k):
    label=canvas(h)
    if k=='nested':return 'Nested body' in label
    if k=='text':return '\\nText\\nText' in label
    if k=='value':return 'Value\\n80 byte' in label
    if k=='status':return 'Status\\n80 byte' in label
    if k=='table':return label.count('Receive [network.receive_bytes]: 80 byte')==2
    if k=='chart':return label.count('Point 2000000000: 80')==2
    if k=='image':return 'Image\\nImage\\nImage ready' in label
    return 'Group' in label
def selection(h,k):
    obj=CASES['objects']['text' if k=='nested' else k];base=obj['layout']['base']
    return h.value('title')==('Nested' if k=='nested' else obj['title']) and all(h.number(key)==base[key] for key in ('x','y','width','height'))
def exercise(h):
    h.launch();h.check();h.stage='SOURCE';h.wait(lambda:'Point 2000000000: 80' in canvas(h));h.point(30,30);h.wait(lambda:h.value('title')=='Editable pane')
    baseline=pixels(h);h.report['baseline_pixel_sha256']=hashlib.sha256(baseline).hexdigest();mode=h.mode;k=mode if mode in KINDS else 'group' if mode=='nested' else 'image'
    if mode=='frozen-preview':h.command('freeze-preview')
    h.stage='BUFFER';open_create(h);assert not h.sensitive('apply') and not h.sensitive('undo') and not h.sensitive('value.title');h.check()
    kind(h,k)
    if mode in ('revoke','retain-create'):
        field(h,'title','Private creation');tab(h,'Content');field(h,'body','Private alternative');held=[h.find('create.body'),h.find('create.title'),h.find('create.width')]
        choose(h,'kind',0,'text');h.wait(lambda:value(h,'title')=='Text');field(h,'body','Private text');held.append(h.find('create.body'))
        issued=h.command('revoke');h.stage='ERASE';h.wait(lambda:all(h.erased(o) for o in held) and h.cleared_canvas(),max(.001,issued+.2-time.monotonic()));h.report['erase_ms']=(time.monotonic()-issued)*1000;assert h.report['erase_ms']<=CASES['erase_ms'];h.report['production_erased']=True
        h.stage='RETAINED';assert not any(any(s in h.text(o) for s in ('Private creation','Private alternative','Private text')) for o in h.objects()),'retained creation disclosed'
        h.check();h.command('regrant');assert not h.sensitive('insert') and all(h.erased(o) for o in held);h.input.focus(h.pid);h.click('reload');h.event('event','reloaded');h.wait(lambda:'Move me' in canvas(h));open_create(h);assert value(h,'title')=='Text';kind(h,'image');assert value(h,'body')=='Image' and selected(h,'asset')=='';h.click('create.cancel');h.wait(lambda:h.sensitive('insert'));h.command('quit');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    if mode=='invalid':
        field(h,'width','NaN');h.click('create.add');h.wait(lambda:bool(value(h,'error')));assert value(h,'width')=='NaN' and not h.sensitive('undo');h.check();field(h,'width','160')
    if k=='image':
        tab(h,'Content');assert selected(h,'asset')=='';h.click('create.add');h.wait(lambda:'Choose an admitted' in value(h,'error'));h.check();choose(h,'asset',1,'package:properties-native / 0.1.0 / images/b-gray.png')
    if mode=='buffers':
        field(h,'title','Private image');field(h,'body','Private alternative');choose(h,'kind',0,'text');h.wait(lambda:value(h,'title')=='Text');field(h,'body','Private text');choose(h,'kind',5,'image');h.wait(lambda:value(h,'title')=='Private image');assert value(h,'body')=='Private alternative' and selected(h,'asset')=='package:properties-native / 0.1.0 / images/b-gray.png';field(h,'title','Image');field(h,'body','Image')
    if mode=='cancel-buffer':
        held=h.find('create.title');field(h,'title','Discarded creation');h.click('create.cancel');h.wait(lambda:h.sensitive('insert') and h.erased(held));h.input.focus(h.pid);assert not h.sensitive('apply') and not h.sensitive('undo');h.wait(lambda:pixels(h)==baseline);open_create(h);assert value(h,'title')=='Text';kind(h,'image');tab(h,'Content');assert selected(h,'asset')=='';choose(h,'asset',1,'package:properties-native / 0.1.0 / images/b-gray.png')
    h.screenshot('buffer');h.stage='ADD';add(h);h.wait(lambda:h.sensitive('apply') and selection(h,k))
    if mode=='nested':
        open_create(h);assert selected(h,'parent')=='Group (widget:new1)';field(h,'title','Nested');tab(h,'Content');field(h,'body','Nested body');add(h);k='nested';h.wait(lambda:selection(h,k))
    h.stage='PIXELS';h.wait(lambda:preview(h,k) and pixels(h)!=baseline);h.screenshot('draft');h.report['edited_accessible']=canvas(h);h.report['edited_pixel_sha256']=hashlib.sha256(pixels(h)).hexdigest();expected=CASES['expected'][k]
    h.click('undo');h.wait(lambda:selection(h,'group') if k=='nested' else not h.sensitive('apply') and h.value('title')=='Editable pane')
    if k=='nested':h.click('undo');h.wait(lambda:not h.sensitive('apply') and h.value('title')=='Editable pane')
    h.wait(lambda:pixels(h)==baseline);h.click('redo');h.wait(lambda:h.sensitive('apply') and selection(h,'group' if k=='nested' else k))
    if k=='nested':h.click('redo');h.wait(lambda:selection(h,k))
    h.wait(lambda:preview(h,k));h.check();h.stage='SUBMIT';h.click('apply');submitted=h.event('event','submitted');h.event('event','held');assert not h.sensitive('insert');h.check()
    if mode!='wrong-insert':assert submitted['body']['operations'][0]['scene']==expected
    if mode=='cancel':h.click('cancel-request');h.event('event','cancel-requested')
    h.command('release');result=h.event('event','result')['result']
    if mode=='cancel':assert result['outcome']=='cancelled';h.check();h.wait(lambda:h.sensitive('cancel'));h.click('cancel');h.event('event','closed');assert h.proc.wait(timeout=5)==0;h.report['outcome']='pass';return
    assert result['outcome']=='accepted' and result['revision']=='41' and result['durable'] and not result['visible'];h.stage='STORE';h.check(expected,'41')
    if mode=='restart':
        h.wait(lambda:'Outcome unknown' in h.status());record=(h.directory/'current.json').read_bytes();h.command('restart');h.event('event','reconciled');assert (h.directory/'current.json').read_bytes()==record
    h.wait(lambda:'Saved durably' in h.status());h.command('quit');assert h.proc.wait(timeout=5)==0;h.launch('reopen');h.check(expected,'41');h.stage='REOPEN';h.wait(lambda:preview(h,k));h.command('quit');assert h.proc.wait(timeout=5)==0;assert mode not in ('wrong-insert','frozen-preview','retain-create');h.report['outcome']='pass'
def observe(exe,exit_exe,folder,mode):
    h=CreationHarness(exe,exit_exe,folder,mode);h.report.update(oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),content_harness_sha256=sha(ROOT/'tests/editor/native_content_properties.py'))
    try:exercise(h)
    except AssertionError as exc:
        h.report.update(stage=h.stage,error=str(exc))
        if h.pid and h.proc.poll() is None:h.report['failure_status']=h.status();h.report['accessible']=canvas(h);h.screenshot('failure')
        wrong=mode=='wrong-insert' and h.stage=='STORE' and str(exc)=='stored documents differ' and stored(h.directory)['scene']['widgets'][-1]['title']=='Wrong insertion'
        frozen=mode=='frozen-preview' and h.stage=='PIXELS' and str(exc)=='PIXELS observation deadline' and preview(h,'image') and selection(h,'image') and stored(h.directory)==h.documents() and hashlib.sha256(pixels(h)).hexdigest()==h.report['baseline_pixel_sha256']
        retained=mode=='retain-create' and h.stage=='RETAINED' and str(exc)=='retained creation disclosed' and h.report.get('production_erased') and any(h.text(o)=='Retained creation canary Private creation' for o in h.objects())
        if wrong or frozen or retained:h.report.update(outcome='pass',fault_detected=True)
        else:raise
    finally:h.close()
def main():
    if sys.argv[1]=='--observe':observe(*map(Path,sys.argv[2:5]),sys.argv[5]);return
    exe,exit_exe,evidence=map(Path,sys.argv[1:4]);assert os.geteuid()!=0 and evidence.resolve().is_relative_to(exe.parent.resolve());folder=evidence/('creation-'+uuid.uuid4().hex[:12]);folder.mkdir(mode=0o700);server=None
    report=dict(family='EDITOR-WIDGET-CREATION',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe),exit_executable_sha256=sha(exit_exe),oracle_sha256=sha(Path(__file__)),harness_sha256=sha(ROOT/'tests/editor/native_editor.py'),content_harness_sha256=sha(ROOT/'tests/editor/native_content_properties.py'),fixture_sha256=sha(ROOT/'tests/editor/widget-creation-cases.json'),resources_sha256=sha(ROOT/'tests/editor/content-properties-fixture.json'),cases=[])
    try:
        server,env=launch_xvfb(folder);env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['native_modes']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(exit_exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=40)
            except subprocess.TimeoutExpired:timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr);assert not timed_out and child.returncode==0,(mode,stderr.decode(errors='replace'));case=json.loads((folder/mode/'result.json').read_text());assert case['outcome']=='pass';report['cases'].append(dict(case=mode,outcome='pass',fault_detected=case.get('fault_detected',False),record_sha256=sha(folder/mode/'result.json')))
        report['outcome']='pass'
    except Exception as exc:report['error']=repr(exc);raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['files']={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='xauthority'};(folder/'result.json').write_text(json.dumps(report,indent=2)+'\\n');print(folder/'result.json',report['outcome'])
if __name__=='__main__':main()
'''
write('tests/editor/native_widget_creation.py',head+helpers+tail)
p=r/'CMakeLists.txt';s=p.read_text();anchor='        add_test(NAME native.EDITOR-BINDING-AUTHORING';at=s.index(anchor);s=s[:at]+'''        add_test(NAME native.EDITOR-WIDGET-CREATION COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/editor/native_widget_creation.py"
            "$<TARGET_FILE:syspane_editor_window>" "$<TARGET_FILE:syspane_editor_exit_probe>" "${CMAKE_BINARY_DIR}/native-evidence")
        set_tests_properties(native.EDITOR-WIDGET-CREATION PROPERTIES TIMEOUT 600)
'''+s[at:];write('CMakeLists.txt',s)
p=r/'tests/editor/editor_window.cpp';s=p.read_text();s=s.replace('        if(behavior=="retain-binding")','        if(behavior=="retain-create"){canary=gtk_label_new("Retained creation canary Private creation");gtk_box_pack_start(GTK_BOX(box),canary,FALSE,FALSE,0);}\n        if(behavior=="retain-binding")');s=s.replace('            if(behavior=="wrong-binding")','            if(behavior=="wrong-insert"){auto changed=c::parse_command(body);changed["operations"][0]["scene"]["widgets"].back()["title"]="Wrong insertion";body=changed.dump();}\n            if(behavior=="wrong-binding")');write('tests/editor/editor_window.cpp',s)
