"""Drive the installed scene editor and independently verify its persisted documents."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import os
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
import struct
import zlib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/configuration'),str(ROOT/'tests/fault'),str(ROOT/'tests/desktop'),str(ROOT/'source/build')]
from native_settings import Keys, stored
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify
CASES=json.loads((ROOT/'tests/configuration/installed-editor-cases.json').read_bytes())
INITIAL=json.loads((ROOT/CASES['initial_documents']).read_bytes())
EXPECTED=json.loads((ROOT/CASES['expected_scene']).read_bytes())
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def observe(exe,folder,runtime,mode,extension=None):
    import gi
    gi.require_version('Atspi','2.0');gi.require_version('Gtk','3.0')
    from gi.repository import Atspi,GLib,Gtk
    started=time.monotonic();deadline=started+CASES['case_timeout_seconds']
    Gtk.init([]);Atspi.set_timeout(200,500);verify();folder.mkdir(mode=0o700)
    (folder/'policy').write_text('allow\n');(folder/'phase').write_text('');(folder/'release').write_text('')
    env=dict(os.environ,HOME=str(folder/'home'),XDG_CONFIG_HOME=str(folder/'config'),XDG_DATA_HOME=str(folder/'data'),XDG_STATE_HOME=str(folder/'state'),XDG_RUNTIME_DIR=str(runtime),G_DEBUG='fatal-criticals')
    (folder/'home').mkdir(mode=0o700)
    generations=folder/'config/syspane/configuration'/sha(CASES['profile'].encode())/'generations'
    report=dict(case=mode,outcome='fail',observations=[],controllers=[],frontend_sha256=sha(exe.read_bytes()),started_at=datetime.now(timezone.utc).isoformat())
    proc=None;keys=None;err=(folder/'stderr').open('wb');pidfds={};helper_pidfds={};roots=set(runtime.glob('sp-*'))
    timing_streams=[]
    def timings():
        for stream in timing_streams:
            while True:
                try:raw=os.read(stream['pipe'].fileno(),4096)
                except BlockingIOError:break
                if not raw:break
                stream['pending']+=raw
                assert len(stream['pending'])<=8192,'timing output buffer exceeded'
                while b'\n' in stream['pending']:
                    line,stream['pending']=stream['pending'].split(b'\n',1)
                    match=re.fullmatch(rb'timing ([0-9]{1,20}) ([0-9]{1,20})',line)
                    assert match,('invalid timing output',line)
                    rows=report.setdefault('timings',[])
                    assert len(rows)<CASES['maximum_timing_records'],'timing record limit exceeded'
                    rows.append(dict(pid=stream['pid'],work_us=int(match[1]),delay_us=int(match[2])))
    def save(): (folder/'result.json').write_bytes(encoded(report))
    def pump():
        timings()
        if extension and proc and proc.poll() is None:
            children=set()
            for task in Path('/proc',str(proc.pid),'task').iterdir():
                try:children.update(int(v) for v in (task/'children').read_text().split())
                except FileNotFoundError:pass
            for pid in children:
                if pid in helper_pidfds:continue
                fd=None
                try:
                    fd=os.pidfd_open(pid)
                    args=Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')[:-1]
                    path=Path('/proc',str(pid),'exe');target=os.readlink(path)
                    if 'memfd:syspane-' not in target:os.close(fd);continue
                    digest=sha(path.read_bytes())
                except (FileNotFoundError,ProcessLookupError):
                    if fd is not None:os.close(fd)
                    continue
                except PermissionError:
                    # The real image sandbox disables dumpability before input.
                    # Keep exact-child liveness without claiming an executable hash.
                    if select.select([fd],[],[],0)[0]:target='exited-before-executable-observation'
                    else:
                        assert len(args)==3 and args[0]==b'syspane-image-worker' and args[1] in (b'image/png',b'image/jpeg',b'image/svg+xml') and args[2]==str(proc.pid).encode(),args
                        target='sandboxed:syspane-image-worker'
                    digest=None
                helper_pidfds[pid]=fd
                report.setdefault('native_children',[]).append(dict(pid=pid,image=target,sha256=digest,argv=[v.decode() for v in args]))
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(predicate,seconds=8):
        until=min(deadline,time.monotonic()+seconds)
        while True:
            pump()
            try:value=predicate()
            except GLib.GError as error:
                assert error.domain=='atspi_error' and error.code==1 and re.search(r'object /org/a11y/atspi/accessible/[0-9]+ does not exist',error.message),str(error)
                invalidated=report.setdefault('observation_invalidations',[]);assert len(invalidated)<128
                invalidated.append(error.message);value=False
            if value:
                assert time.monotonic()<=until,(mode,'observation exceeded deadline')
                return value
            assert time.monotonic()<until,(mode,'observation deadline',status())
            time.sleep(.005)
    def objects():
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];out=[]
        for n in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(n)
            if app and app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            obj,depth=pending.pop()
            if obj is None:continue
            obj.clear_cache();out.append(obj);assert len(out)<=CASES.get('observer_objects',512) and depth<=20
            for n in range(obj.get_child_count()):pending.append((obj.get_child_at_index(n),depth+1))
        return out
    def find(name):return next((o for o in objects() if o.get_description()==name),None)
    def text(obj):
        if obj is None:return ''
        obj.clear_cache();interface=obj.get_text_iface();return Atspi.Text.get_text(interface,0,-1) if interface else obj.get_name() or ''
    def sensitive(obj):return obj and obj.get_state_set().contains(Atspi.StateType.SENSITIVE)
    def status():
        return ' | '.join(text(find(n)) for n in ('frontend.status','editor.status','settings.status')) if proc and proc.poll() is None else 'exited'
    def value(name):return text(find(name))
    def number(name):
        try:return json.loads(value(name))
        except json.JSONDecodeError:return None
    def screenshot(name):
        raw=keys.capture(0,0,800,600)
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
        rows=b''.join(b'\0'+raw[y*800*3:(y+1)*800*3] for y in range(600))
        data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',800,600,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
        (folder/(name+'.png')).write_bytes(data)
        report.setdefault('captures',[]).append(dict(path=name+'.png',sha256=sha(data)))
    def enter(name,v):
        obj=find(name);assert sensitive(obj),(name,status())
        assert Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(v));wait(lambda:value(name)==str(v))
    def focus(obj):
        assert obj and obj.get_component_iface().grab_focus()
        wait(lambda:obj.get_state_set().contains(Atspi.StateType.FOCUSED))
    def click(name):
        obj=find(name);assert sensitive(obj),(name,status());focus(obj);keys.press(0x20)
    def child():
        children=set()
        for task in Path('/proc',str(proc.pid),'task').iterdir():
            try:children.update(int(v) for v in (task/'children').read_text().split())
            except FileNotFoundError:pass
        candidates=[]
        for pid in children:
            try:
                args=Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')[:-1]
                if args and args[0]==b'syspane-image-worker':continue
                if 'memfd:syspane-configuration-host' in os.readlink('/proc/'+str(pid)+'/exe') and b'--network' not in args:candidates.append(pid)
            except FileNotFoundError:pass
        assert len(candidates)==1,candidates
        pid=candidates[0]
        if pid not in pidfds:
            pidfds[pid]=os.pidfd_open(pid)
            report['controllers'].append(dict(pid=pid,sha256=sha(Path('/proc',str(pid),'exe').read_bytes())))
        return pid,pidfds[pid]
    def launch():
        nonlocal proc,keys
        observe=bool(extension and getattr(extension,'capture_timings',False))
        proc=subprocess.Popen([str(exe),'--profile',CASES['profile']],cwd=folder,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE if observe else subprocess.DEVNULL,stderr=err)
        if observe:
            os.set_blocking(proc.stdout.fileno(),False)
            timing_streams.append(dict(pipe=proc.stdout,pid=proc.pid,pending=b''))
        wait(lambda:find('frontend.status'));keys=Keys(proc.pid)
    def settings_ready():
        wait(lambda:value('settings.value.sampling.resources_ms')=='1000' and sensitive(find('frontend.editor')),12);child()
    def select_network(title='Network',x=24):
        tree=find('editor.objects');focus(tree)
        for key,row,wanted in ((0xff57,1,INITIAL['documents']['scene']['widgets'][1]['title']),(0xff50,0,title)):
            keys.press(key)
            wait(lambda:list(tree.get_table_iface().get_selected_rows())==[row] and value('editor.value.title')==wanted)
        wait(lambda:number('editor.value.x')==x)
    def editor_ready(title='Network',x=24):
        wait(lambda:find('editor.canvas') and sensitive(find('frontend.settings')),12)
        select_network(title,x);child()
    def open_editor(title='Network',x=24):
        click('frontend.editor');editor_ready(title,x)
        assert value('frontend.recovery')=='Draft recovery unavailable. Apply saves the configuration.'
        assert find('editor.recovery-status') is None
        assert title in value('editor.canvas')
    def properties():
        enter('editor.value.title',CASES['title']);enter('editor.value.x',CASES['x'])
        click('editor.properties');wait(lambda:'Draft changes have not been saved.' in status())
        wait(lambda:not sensitive(find('frontend.settings')))
        assert value('editor.value.title')==CASES['title'] and number('editor.value.x')==CASES['x']
    def documents(edited=False):
        expected=copy.deepcopy(INITIAL['documents'])
        if edited:expected['scene']=copy.deepcopy(EXPECTED);expected['settings']['revision']=EXPECTED['revision']
        actual=stored(generations);assert actual==expected,(actual,expected)
        selector=json.loads((generations/'current.json').read_bytes());selected=generations/selector['generation']
        manifest=json.loads((selected/'manifest.json').read_bytes());index=json.loads((selected/'resources.json').read_bytes())
        assert sha((selected/'resources.json').read_bytes())==manifest['resources']
        expected_files={}
        for package in INITIAL['packages']:
            raw=package['manifest'].encode();expected_files['m-'+sha(raw)+'.json']=raw
            for raw in package['assets'].values():
                raw=raw.encode();expected_files['a-'+sha(raw)+'.bin']=raw
        assert {p.name:p.read_bytes() for p in (selected/'resources').iterdir()}==expected_files
        assert index==dict(version='0.1.0',selection=INITIAL['selection'],theme=INITIAL['theme_pin'],packages=sorted(sha(p['manifest'].encode()) for p in INITIAL['packages']))
        report['observations'].append(dict(documents=actual,resources=index,status=status()));save()
    def saved():
        wait(lambda:'Saved durably; activation pending. Visibility unconfirmed.' in status() and sensitive(find('frontend.settings')))
        documents(True)
    def quit(expected=0):
        nonlocal keys
        click('frontend.quit');wait(lambda:proc.poll() is not None,8);assert proc.returncode==expected,(proc.returncode,(folder/'stderr').read_text())
        assert set(runtime.glob('sp-*'))==roots,'runtime not retired'
        for fd in pidfds.values():assert select.select([fd],[],[],1)[0],'controller not reaped'
        for fd in helper_pidfds.values():assert select.select([fd],[],[],1)[0],'native child not exited'
        keys.close();keys=None
    def hold(phase): (folder/'phase').write_text(phase+'\n')
    def held():
        p=folder/'held'
        if not p.exists():return False
        try:return json.loads(p.read_bytes())
        except json.JSONDecodeError:return False
    def erased():
        observed=objects()
        fields=[o for o in observed if (o.get_description() or '').startswith('editor.value.')]
        canvases=[o for o in observed if o.get_description()=='editor.canvas']
        return all(text(o)=='' for o in fields+canvases) and not any(CASES['title'] in (o.get_name() or '') for o in observed)
    def crash():
        nonlocal keys,roots
        proc.kill();proc.wait(timeout=8)
        for fd in pidfds.values():wait(lambda:bool(select.select([fd],[],[],0)[0]),8)
        for fd in helper_pidfds.values():wait(lambda:bool(select.select([fd],[],[],0)[0]),8)
        if keys:keys.close();keys=None
        # Process death cannot run the runtime owner's destructor. Preserve and
        # record orphan roots; subsequent clean exits must retire only new roots.
        after=set(runtime.glob('sp-*'))
        report.setdefault('crash_runtime_roots',[]).extend(str(p) for p in sorted(after-roots))
        roots=after
    try:
        if extension:
            extension(dict(locals(),process=lambda:proc));report['outcome']='pass';return
        launch()
        if mode=='HELPER-FAILURE':
            wait(lambda:'Settings unavailable. Check installation, runtime and policy configuration.' in status(),12)
            assert find('editor.canvas') is None and not sensitive(find('frontend.editor')) and not generations.exists()
            quit(2);report['outcome']='pass';return
        settings_ready();documents()
        if mode=='SETTINGS-NAV':
            for raw in ('-','1500'):
                enter('settings.value.sampling.resources_ms',raw)
                wait(lambda:not sensitive(find('frontend.editor')))
                click('settings.revert');settings_ready();documents()
        open_editor()
        if mode=='OPEN':
            for name in ('frontend.settings','frontend.quit'):
                rect=find(name).get_component_iface().get_extents(Atspi.CoordType.SCREEN)
                assert 0<=rect.x<rect.x+rect.width<=800 and 0<=rect.y<rect.y+rect.height<=600,(name,rect)
            screenshot('editor')
        if mode in ('OPEN','SETTINGS-NAV'):
            click('frontend.settings');settings_ready();documents();open_editor()
        elif mode=='PRIVATE-NAV':
            enter('editor.value.title','Unapplied private field');enter('editor.value.x','-')
            wait(lambda:not sensitive(find('frontend.settings')));click('editor.revert-fields');editor_ready()
            click('editor.fonts');wait(lambda:find('editor.theme.cancel'))
            wait(lambda:not sensitive(find('frontend.settings')));click('editor.theme.cancel');editor_ready();documents()
        elif mode in ('PROPERTIES','SAVE-REOPEN','UNDO-REDO','CANCEL-DRAFT','RELOAD','REQUEST-NAV','LOST-RESULT','POLICY','REPLACEMENT','CLOSE-HELD'):
            properties();documents()
            if mode=='SAVE-REOPEN':
                click('editor.apply');saved()
                click('frontend.settings');settings_ready();documents(True);open_editor(CASES['title'],CASES['x'])
                quit();launch();settings_ready();open_editor(CASES['title'],CASES['x']);documents(True)
            elif mode=='UNDO-REDO':
                click('editor.undo');editor_ready();documents()
                click('editor.redo');wait(lambda:value('editor.value.title')==CASES['title'] and not sensitive(find('frontend.settings')))
                click('editor.apply');saved()
            elif mode=='CANCEL-DRAFT':
                click('editor.cancel');settings_ready();documents();open_editor()
            elif mode=='RELOAD':
                click('editor.reload');editor_ready();documents()
            elif mode in ('REQUEST-NAV','LOST-RESULT','CLOSE-HELD'):
                hold('store.durable' if mode=='LOST-RESULT' else 'store.selector_ready')
                click('editor.apply');mark=wait(held);pid,fd=child();assert mark['pid']==pid
                assert not sensitive(find('frontend.settings')) and 'Saved durably' not in status()
                if mode=='REQUEST-NAV':
                    documents();(folder/'release').write_text('yes\n');saved()
                elif mode=='CLOSE-HELD':
                    quit();documents();report['outcome']='pass';return
                else:
                    documents(True);(folder/'phase').write_text('');(folder/'reconcile').write_text('deny\n')
                    signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
                    wait(lambda:'Outcome unknown' in status() and erased(),12)
                    assert not sensitive(find('editor.apply')) and not sensitive(find('frontend.settings'))
                    (folder/'reconcile').write_text('allow\n');editor_ready(CASES['title'],CASES['x']);documents(True)
                    assert not any(json.loads(p.read_bytes())['revision']=='2' for p in generations.glob('*/scene.json'))
            elif mode in ('POLICY','REPLACEMENT'):
                enter('editor.value.title','Private unsaved field');pid,fd=child()
                if mode=='POLICY':(folder/'policy').write_text('deny\n');wait(lambda:select.select([fd],[],[],0)[0],4)
                else:signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
                observed=time.monotonic();wait(erased,CASES['erasure_after_observed_loss_ms']/1000)
                report['erasure_ms']=(time.monotonic()-observed)*1000
                assert not sensitive(find('editor.apply')) and not sensitive(find('frontend.settings'));documents()
                if mode=='REPLACEMENT':
                    editor_ready();new_pid,new_fd=child();assert new_pid!=pid and not select.select([new_fd],[],[],0)[0];documents()
        elif mode=='ORACLE':
            wrong=copy.deepcopy(INITIAL['documents']);wrong['scene']['widgets'][0]['title']='Wrong expected title'
            detected=False
            try:assert stored(generations)==wrong
            except AssertionError:detected=True
            assert detected;report['fault_detected']=True
        else:raise AssertionError(mode)
        quit();report['outcome']='pass'
    except Exception:
        report['failure']=traceback.format_exc()
        if proc and proc.poll() is None:
            try:report['failed_controls']=[dict(id=o.get_description(),text=text(o),sensitive=bool(sensitive(o))) for o in objects() if o.get_description()]
            except Exception:report['failed_observation']=traceback.format_exc()
            if keys:screenshot('failure')
        raise
    finally:
        if proc and proc.poll() is None:proc.kill();proc.wait(timeout=8)
        if keys:keys.close()
        for fd in pidfds.values():
            if not select.select([fd],[],[],1)[0]:signal.pidfd_send_signal(fd,signal.SIGKILL)
            assert select.select([fd],[],[],2)[0],'owned controller still live during teardown'
            os.close(fd)
        for pid,fd in helper_pidfds.items():
            exited=bool(select.select([fd],[],[],1)[0])
            next(v for v in report['native_children'] if v['pid']==pid)['exited']=exited
            if not exited:
                report.setdefault('forced_native_cleanup',[]).append(pid);signal.pidfd_send_signal(fd,signal.SIGKILL)
                assert select.select([fd],[],[],2)[0]
            os.close(fd)
        try:
            timings()
            for stream in timing_streams:assert not stream['pending'],'incomplete timing record'
            if timing_streams:
                rows=report.get('timings',[])
                report['timing_violations']=[dict(index=i,**v) for i,v in enumerate(rows) if max(v['work_us'],v['delay_us'])>CASES['gui_operation_limit_ms']*1000]
                report['timing_max_us']={key:max((v[key] for v in rows),default=0) for key in ('work_us','delay_us')}
        except Exception:report['timing_failure']=traceback.format_exc();report['outcome']='fail';raise
        finally:
            for stream in timing_streams:stream['pipe'].close()
            err.close();report['finished_at']=datetime.now(timezone.utc).isoformat();report['elapsed_seconds']=time.monotonic()-started;save()


def main(extension=None,script=None,case_file='tests/configuration/installed-editor-cases.json',prefix='editor-frontend-'):
    script=Path(script or __file__).resolve()
    if sys.argv[1]=='--observe':observe(*[Path(p) for p in sys.argv[2:5]],sys.argv[5],extension);return
    production,fixture,helper,evidence=[Path(p).resolve() for p in sys.argv[1:5]];build=production.parent
    assert os.geteuid() and fixture.parent==helper.parent==evidence.parent==build
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    assert not Path('/etc/syspane/policy.json').exists(),'negative production case requires absent protected policy'
    runtime=build.parent/'F';marker=encoded(dict(format='SysPane.InstalledSettingsLab',root=str(build.parent)))
    if not runtime.exists():runtime.mkdir(mode=0o700);(runtime/'.owner.json').write_bytes(marker)
    assert runtime.resolve()==runtime and (runtime/'.owner.json').read_bytes()==marker and stat.S_IMODE(runtime.stat().st_mode)==0o700
    folder=evidence/(prefix+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700)
    report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),cases=[],packages=[],
        artifacts={p.name:sha(p.read_bytes()) for p in (production,fixture,helper,build/'SysPane.ImageWorker',build/'SysPane.RecoveryWorker')},
        oracle_sha256=sha(script.read_bytes()),harness_sha256=sha(Path(__file__).read_bytes()),cases_sha256=sha((ROOT/case_file).read_bytes()),expected_scene_sha256=sha((ROOT/CASES['expected_scene']).read_bytes()),runtime_directory=str(runtime))
    def package(name,exe,host,record):
        stage=folder/(name+' original');stage.mkdir(mode=0o700)
        if name=='production':subprocess.run(['cmake','--install',str(build),'--prefix',str(stage),'--component','DevelopmentFrontend'],check=True,capture_output=True)
        else:
            for path,source in [('bin/syspane',exe),('libexec/syspane/syspane-configuration-host',host),('share/syspane/helpers.json',record),('libexec/syspane/syspane-image-worker',build/'SysPane.ImageWorker'),('libexec/syspane/syspane-recovery-worker',build/'SysPane.RecoveryWorker')]:
                dest=stage/path;dest.parent.mkdir(mode=0o755,parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644 if path.endswith('.json') else 0o755)
        files={p.relative_to(stage).as_posix():p for p in stage.rglob('*') if p.is_file()}
        assert set(files)=={'bin/syspane','libexec/syspane/syspane-configuration-host','share/syspane/helpers.json','libexec/syspane/syspane-image-worker','libexec/syspane/syspane-recovery-worker'}
        manifest=json.loads(files['share/syspane/helpers.json'].read_bytes());assert manifest['schema_version']=='0.2.0'
        for role in manifest['helpers'].values():assert sha(files[role['path']].read_bytes())==role['sha256']
        archive=folder/(name+'.zip')
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for path,file in sorted(files.items()):z.write(file,path)
        with zipfile.ZipFile(archive) as z:
            assert set(z.namelist())==set(files)
            for path,file in files.items():assert z.read(path)==file.read_bytes()
        report['packages'].append(dict(name=name,sha256=sha(archive.read_bytes()),files={path:sha(file.read_bytes()) for path,file in files.items()}))
        target=folder/(name+' relocated');assert stage.parent==target.parent==folder;stage.rename(target)
        return target/'bin/syspane'
    server=None
    try:
        real=package('production',production,build/'syspane-configuration-host',build/'generated/helper-bundle/helpers.json') if 'HELPER-FAILURE' in CASES['cases'] else None
        test=package('fixture',fixture,helper,build/'generated/frontend-fixture/helpers.json')
        server,env=launch_xvfb(folder);env.update(NO_AT_BRIDGE='0',XDG_RUNTIME_DIR=str(runtime));env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            exe=real if mode=='HELPER-FAILURE' else test
            installed=real.parent.parent/'libexec/syspane/syspane-image-worker' if real else None;original=installed.read_bytes() if mode=='HELPER-FAILURE' else None
            if original is not None:
                installed.write_bytes(original+b'\0');report['substitution']=dict(path=str(installed),original_sha256=sha(original),substituted_sha256=sha(installed.read_bytes()))
            try:
                args=['dbus-run-session','--',sys.executable,str(script),'--observe',str(exe),str(folder/mode),str(runtime),mode]
                p=subprocess.Popen(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                try:stdout,stderr=p.communicate(timeout=CASES['case_timeout_seconds'])
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGKILL);stdout,stderr=p.communicate(timeout=8)
                    (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
                    raise AssertionError('observer deadline')
                (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
                case_path=folder/mode/'result.json'
                case=json.loads(case_path.read_bytes()) if case_path.exists() else {'outcome':'fail'}
                passed=p.returncode==0 and case['outcome']=='pass'
                report['cases'].append(dict(case=mode,outcome='pass' if passed else 'fail',record_sha256=sha(case_path.read_bytes()) if case_path.exists() else None))
                assert passed or (extension and getattr(extension,'continue_after_case_failure',False)),(mode,stderr.decode(errors='replace'))
            finally:
                if original is not None:installed.write_bytes(original)
        assert all(v['outcome']=='pass' for v in report['cases']),('failed cases',[v['case'] for v in report['cases'] if v['outcome']!='pass'])
        report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=8)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_bytes(encoded(report));print(folder/'result.json',report['outcome'])


if __name__=='__main__':main()
