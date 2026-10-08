"""Observe the relocated application through native controls and durable files."""
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

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/configuration'),str(ROOT/'tests/fault'),str(ROOT/'tests/desktop'),str(ROOT/'source/build')]
from native_settings import Keys, stored
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify
CASES=json.loads((ROOT/'tests/configuration/installed-settings-cases.json').read_bytes())
INITIAL=json.loads((ROOT/CASES['initial_documents']).read_bytes())
ROWS=json.loads((ROOT/'tests/configuration/settings-cases.json').read_bytes())['settings']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def observe(exe,folder,runtime,mode):
    import gi
    gi.require_version('Atspi','2.0');gi.require_version('Gtk','3.0')
    from gi.repository import Atspi,GLib,Gtk
    Gtk.init([]);Atspi.set_timeout(200,500);verify();folder.mkdir(mode=0o700)
    (folder/'policy').write_text('allow\n');(folder/'phase').write_text('');(folder/'release').write_text('')
    env=dict(os.environ,HOME=str(folder/'home'),XDG_CONFIG_HOME=str(folder/'config'),XDG_DATA_HOME=str(folder/'data'),XDG_STATE_HOME=str(folder/'state'),XDG_RUNTIME_DIR=str(runtime))
    (folder/'home').mkdir(mode=0o700)
    if mode=='RUNTIME-UNAVAILABLE':env.pop('XDG_RUNTIME_DIR')
    # This cannot grant authority to the production helper.
    env['SYSPANE_POLICY_FILE']=str(folder/'policy')
    generations=folder/'config/syspane/configuration'/sha(CASES['profile'].encode())/'generations'
    report=dict(case=mode,outcome='fail',observations=[],frontend_sha256=sha(exe.read_bytes()),started_at=datetime.now(timezone.utc).isoformat())
    proc=None;keys=None;err=(folder/'stderr').open('wb');pidfds=[];roots=set(runtime.glob('sp-*'))
    def save(): (folder/'result.json').write_bytes(encoded(report))
    def pump():
        context=GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():break
            context.iteration(False)
    def wait(predicate,seconds=8):
        until=time.monotonic()+seconds
        while True:
            pump()
            try:value=predicate()
            except GLib.GError as error:
                # A replaced form can disappear between enumeration and Get.
                # Discard that entire observation; retry under the original
                # deadline. Denial, timeout and transport errors still fail.
                assert error.domain=='atspi_error' and error.code==1 and re.search(r'object /org/a11y/atspi/accessible/[0-9]+ does not exist',error.message),str(error)
                invalidated=report.setdefault('observation_invalidations',[])
                assert len(invalidated)<128
                invalidated.append(error.message);value=False
            if value:return value
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
            obj.clear_cache();out.append(obj);assert len(out)<=512 and depth<=20
            for n in range(obj.get_child_count()):pending.append((obj.get_child_at_index(n),depth+1))
        return out
    def find(name):return next((o for o in objects() if o.get_description()==name),None)
    def text(obj):
        if obj is None:return ''
        obj.clear_cache();interface=obj.get_text_iface();return Atspi.Text.get_text(interface,0,-1) if interface else obj.get_name() or ''
    def sensitive(obj):return obj and obj.get_state_set().contains(Atspi.StateType.SENSITIVE)
    def status():return text(find('frontend.status'))+' | '+text(find('settings.status')) if proc and proc.poll() is None else 'exited'
    def value():return text(find('settings.value.sampling.resources_ms'))
    def enter(v):
        obj=find('settings.value.sampling.resources_ms');assert obj and sensitive(obj)
        assert Atspi.EditableText.set_text_contents(obj.get_editable_text_iface(),str(v));wait(lambda:value()==str(v))
    def click(name):
        obj=find(name);assert sensitive(obj),(name,status())
        assert obj.get_component_iface().grab_focus();keys.press(0x20)
    def launch():
        nonlocal proc,keys
        args=[str(exe),*(['--profile',CASES['profile']] if mode=='STARTUP' else [])]
        proc=subprocess.Popen(args,cwd=folder,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=err)
        wait(lambda:find('frontend.status'));keys=Keys(proc.pid)
    def ready(v=1000):wait(lambda:value()==str(v) and sensitive(find('settings.value.sampling.resources_ms')),12)
    def child():
        children=set()
        for task in Path('/proc',str(proc.pid),'task').iterdir():
            try:children.update(int(v) for v in (task/'children').read_text().split())
            except FileNotFoundError:pass
        candidates=[]
        for pid in children:
            try:
                if 'memfd:syspane-configuration-host' in os.readlink('/proc/'+str(pid)+'/exe'):candidates.append(pid)
            except FileNotFoundError:pass
        assert len(candidates)==1,candidates
        fd=os.pidfd_open(candidates[0]);pidfds.append(fd);return candidates[0],fd
    def documents(revision='0',edited=False):
        expected=copy.deepcopy(INITIAL['documents'])
        for item in expected.values():item['revision']=revision
        if edited:expected['settings']['sampling']['resources_ms']=CASES['expected']['resources_ms']
        actual=stored(generations);assert actual==expected,(actual,expected)
        selector=json.loads((generations/'current.json').read_bytes());selected=generations/selector['generation']
        manifest=json.loads((selected/'manifest.json').read_bytes());index=json.loads((selected/'resources.json').read_bytes())
        assert sha((selected/'resources.json').read_bytes())==manifest['resources']
        # Exact package bytes are independently pinned in the existing startup oracle.
        expected_files={}
        for package in INITIAL['packages']:
            raw=package['manifest'].encode();expected_files['m-'+sha(raw)+'.json']=raw
            for raw in package['assets'].values():
                raw=raw.encode();expected_files['a-'+sha(raw)+'.bin']=raw
        assert {p.name:p.read_bytes() for p in (selected/'resources').iterdir()}==expected_files
        assert index==dict(version='0.1.0',selection=INITIAL['selection'],theme=INITIAL['theme_pin'],packages=sorted(sha(p['manifest'].encode()) for p in INITIAL['packages']))
        report['observations'].append(dict(revision=revision,settings=actual['settings'],scene=actual['scene'],resources=index,status=status()));save()
    def quit():
        nonlocal proc,keys
        click('frontend.quit');wait(lambda:proc.poll() is not None,8);assert proc.returncode in (0,2)
        assert set(runtime.glob('sp-*'))==roots,'runtime not retired'
        keys.close();keys=None
    def hold(phase): (folder/'phase').write_text(phase+'\n')
    def held():
        p=folder/'held'
        if not p.exists():return False
        try:return json.loads(p.read_bytes())
        except json.JSONDecodeError:return False
    try:
        if mode=='STARTUP':
            result=subprocess.run([str(exe),'--help'],cwd=folder,env=env,capture_output=True,timeout=5)
            assert result.returncode==0 and b'Usage: syspane [--profile ID]' in result.stdout
            for args in (['--unknown'],['--profile'],['--profile','../invalid']):
                result=subprocess.run([str(exe),*args],cwd=folder,env=env,capture_output=True,timeout=5)
                assert result.returncode==2 and not generations.exists()
        launch()
        if mode in ('RUNTIME-UNAVAILABLE','PRODUCTION-POLICY','HELPER-IDENTITY'):
            expected='Configuration service unavailable.' if mode=='PRODUCTION-POLICY' else 'Settings unavailable. Check installation, runtime and policy configuration.'
            wait(lambda:expected in status(),12)
            assert find('settings.value.sampling.resources_ms') is None and not generations.exists()
            quit();report['outcome']='pass';return
        ready();documents()
        for row in ROWS:
            obj=find('settings.value.'+row['id']);assert obj and obj.get_name()==row['label']
            if isinstance(row['initial'],bool):assert obj.get_state_set().contains(Atspi.StateType.CHECKED)==row['initial']
            else:assert text(obj)==str(row['initial']),(row['id'],text(obj))
        if mode=='VALIDATION-PREVIEW-REVERT':
            enter(99);wait(lambda:'Correct invalid fields' in status());assert not sensitive(find('settings.apply'));documents()
            enter(1500);click('settings.preview');wait(lambda:'Preview validated' in status());documents()
            click('settings.revert');ready();documents()
        elif mode=='SAVE-REOPEN':
            enter(1500);click('settings.apply');wait(lambda:'Saved durably; activation pending. Visibility has not been confirmed.' in status());documents('1',True)
            quit();launch();ready(1500);documents('1',True)
        elif mode in ('CANCEL','CLOSE-PENDING','LOST-RESULT'):
            hold('store.durable' if mode=='LOST-RESULT' else 'store.selector_ready');enter(1500);click('settings.apply');mark=wait(held)
            pid,fd=child();assert mark['pid']==pid
            assert 'Saved durably' not in status()
            if mode=='CANCEL':
                click('settings.cancel')
                # XSync proves native input dispatch, not controller receipt. Its
                # unknown result proves cancel was handled while publication is
                # still held; only then may the independent lab release storage.
                wait(lambda:'Outcome unknown' in status())
                (folder/'release').write_text('yes\n');wait(lambda:'Request cancelled' in status());documents()
            elif mode=='CLOSE-PENDING':
                quit();assert select.select([fd],[],[],1)[0];documents();report['outcome']='pass';return
            else:
                documents('1',True);(folder/'phase').write_text('')
                signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
                (folder/'reconcile').write_text('deny\n')
                wait(lambda:'Outcome unknown' in status() and value()=='',12)
                assert not sensitive(find('settings.apply'))
                (folder/'reconcile').write_text('allow\n');ready(1500);documents('1',True)
                assert not any(json.loads(p.read_bytes())['revision']=='2' for p in generations.glob('*/settings.json'))
        elif mode=='REPLACEMENT':
            pid,fd=child();signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
            wait(lambda:'Configuration connection unavailable' in status() or value()=='')
            ready();new_pid,new_fd=child();assert new_pid!=pid and not select.select([new_fd],[],[],0)[0];documents()
        elif mode=='POLICY':
            pid,fd=child();(folder/'policy').write_text('deny\n');wait(lambda:select.select([fd],[],[],0)[0],4)
            observed=time.monotonic();wait(lambda:value()=='',CASES['erasure_after_observed_loss_ms']/1000)
            assert not sensitive(find('settings.apply'));report['erasure_ms']=(time.monotonic()-observed)*1000
        elif mode=='ORACLE':
            wrong=stored(generations);wrong['settings']['sampling']['resources_ms']=999
            detected=False
            try:assert stored(generations)==wrong
            except AssertionError:detected=True
            assert detected;report['fault_detected']=True
        else:assert mode=='STARTUP'
        quit();report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if proc and proc.poll() is None:proc.kill();proc.wait(timeout=8)
        if keys:keys.close()
        for fd in pidfds:
            if not select.select([fd],[],[],1)[0]:signal.pidfd_send_signal(fd,signal.SIGKILL)
            assert select.select([fd],[],[],2)[0], 'owned helper still live during lab teardown'
            os.close(fd)
        err.close();report['finished_at']=datetime.now(timezone.utc).isoformat();save()


def main():
    if sys.argv[1]=='--observe':observe(*[Path(p) for p in sys.argv[2:5]],sys.argv[5]);return
    production,fixture,helper,evidence=[Path(p).resolve() for p in sys.argv[1:5]];build=production.parent
    assert os.geteuid() and fixture.parent==helper.parent==evidence.parent==build
    assert json.loads((build/'.syspane-owner.json').read_bytes())['profile']=='linux-x64-gcc13'
    assert not Path('/etc/syspane/policy.json').exists(),'production-policy negative case requires absent protected policy'
    runtime=build.parent/'F';marker=encoded(dict(format='SysPane.InstalledSettingsLab',root=str(build.parent)))
    if not runtime.exists():runtime.mkdir(mode=0o700);(runtime/'.owner.json').write_bytes(marker)
    assert runtime.resolve()==runtime and (runtime/'.owner.json').read_bytes()==marker and stat.S_IMODE(runtime.stat().st_mode)==0o700
    folder=evidence/('frontend-'+uuid.uuid4().hex[:10]);folder.mkdir(mode=0o700)
    report=dict(family=CASES['family'],outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),cases=[],packages=[],
        artifacts={p.name:sha(p.read_bytes()) for p in (production,fixture,helper)},oracle_sha256=sha(Path(__file__).read_bytes()),runtime_directory=str(runtime))
    def package(name,exe,host,record):
        stage=folder/(name+' original');stage.mkdir(mode=0o700)
        if name=='production':subprocess.run(['cmake','--install',str(build),'--prefix',str(stage),'--component','DevelopmentFrontend'],check=True,capture_output=True)
        else:
            for path,source in [('bin/syspane',exe),('libexec/syspane/syspane-configuration-host',host),('share/syspane/helpers.json',record)]:
                dest=stage/path;dest.parent.mkdir(mode=0o755,parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644 if path.endswith('.json') else 0o755)
        files={p.relative_to(stage).as_posix():p for p in stage.rglob('*') if p.is_file()}
        assert set(files)=={'bin/syspane','libexec/syspane/syspane-configuration-host','share/syspane/helpers.json'}
        archive=folder/(name+'.zip')
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for path,file in sorted(files.items()):z.write(file,path)
        report['packages'].append(dict(name=name,sha256=sha(archive.read_bytes()),files={path:sha(file.read_bytes()) for path,file in files.items()}))
        target=folder/(name+' relocated');assert stage.parent==target.parent==folder;stage.rename(target)
        return target/'bin/syspane'
    server=None
    try:
        real=package('production',production,build/'syspane-configuration-host',build/'generated/helpers.json')
        test=package('fixture',fixture,helper,build/'generated/frontend-fixture/helpers.json')
        server,env=launch_xvfb(folder);env.update(NO_AT_BRIDGE='0',XDG_RUNTIME_DIR=str(runtime));env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            exe=real if mode in ('PRODUCTION-POLICY','HELPER-IDENTITY') else test
            installed=real.parent.parent/'libexec/syspane/syspane-configuration-host';original=installed.read_bytes() if mode=='HELPER-IDENTITY' else None
            if original is not None:installed.write_bytes(helper.read_bytes())
            try:
                args=['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(folder/mode),str(runtime),mode]
                p=subprocess.Popen(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                try:stdout,stderr=p.communicate(timeout=35)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);stdout,stderr=p.communicate(timeout=8);raise AssertionError('observer deadline')
                (folder/(mode+'.stdout')).write_bytes(stdout);(folder/(mode+'.stderr')).write_bytes(stderr)
                assert p.returncode==0,(mode,stderr.decode(errors='replace'))
                case=json.loads((folder/mode/'result.json').read_bytes());assert case['outcome']=='pass'
                report['cases'].append(dict(case=mode,outcome='pass',record_sha256=sha((folder/mode/'result.json').read_bytes())))
            finally:
                if original is not None:installed.write_bytes(original)
        report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=8)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_bytes(encoded(report));print(folder/'result.json',report['outcome'])


if __name__=='__main__':main()
