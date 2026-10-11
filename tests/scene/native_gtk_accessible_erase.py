"""Independent retained AT-SPI cache experiment; no product qualification."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,select,signal,subprocess,sys,time,traceback,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/fault'),str(ROOT/'source/build')]
from native_diagnostic import launch_xvfb
from check_surface_runtime import verify as surface_runtime
from check_text_runtime import verify as text_runtime
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode()
INITIAL=[['ITEM_CHART_ROOT','ERASURE_CANARY_CHART_ROOT']]+[[f'ITEM_POINT_{i}',f'ERASURE_CANARY_POINT_{i}'] for i in range(3138)]+[['ITEM_RETIRED_ROOT','ERASURE_CANARY_RETIRED_ROOT']]+[[f'ITEM_RETIRED_{i}',f'ERASURE_CANARY_RETIRED_{i}'] for i in range(32)]
FRESH=[['FRESH_ROOT','FRESH_VALUE'],['FRESH_POINT','FRESH_POINT_VALUE']]

def observe(exe,folder,strategy,cohort):
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi,GLib,Gio
    Atspi.set_timeout(200,500);surface_runtime();text_runtime();folder.mkdir()
    started=time.monotonic();deadline=started+120;records=0;buffer=b'';held=[];tree=None
    env=dict(os.environ,G_DEBUG='fatal-warnings',NO_AT_BRIDGE='0');env.pop('AT_SPI_BUS_ADDRESS',None)
    stderr=(folder/'stderr').open('wb');transcript=(folder/'stdout.jsonl').open('wb')
    proc=subprocess.Popen([str(exe),strategy,cohort],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
    report=dict(strategy=strategy,cohort=cohort,outcome='fail',diagnostic_only=True,stages=[],started_at=datetime.now(timezone.utc).isoformat())
    session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    address=session.call_sync('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress',None,GLib.VariantType.new('(s)'),Gio.DBusCallFlags.NONE,500,None).unpack()[0]
    wire=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
    references=[];error_pool=[];error_indices={};wire_rows=[]
    methods=[('GetText','org.a11y.atspi.Text','GetText','(ii)',(0,-1),'(s)'),('Name','org.freedesktop.DBus.Properties','Get','(ss)',('org.a11y.atspi.Accessible','Name'),'(v)'),('CharacterCount','org.freedesktop.DBus.Properties','Get','(ss)',('org.a11y.atspi.Text','CharacterCount'),'(v)')]+[(name,'org.a11y.atspi.Text',name,'(iu)',(0,int(Atspi.TextBoundaryType.WORD_START)),'(sii)') for name in ('GetTextBeforeOffset','GetTextAtOffset','GetTextAfterOffset')]+[('GetStringAtOffset','org.a11y.atspi.Text','GetStringAtOffset','(iu)',(0,int(Atspi.TextGranularity.WORD)),'(sii)')]
    def request(reference,method):
        label,interface,name,signature,args,reply_type=method
        return wire.call_sync(reference[0],reference[1],interface,name,GLib.Variant(signature,args),GLib.VariantType.new(reply_type),Gio.DBusCallFlags.NONE,200,None).unpack()
    def reply():
        nonlocal records,buffer
        while b'\n' not in buffer:
            assert time.monotonic()<deadline,'cache child deadline'
            if select.select([proc.stdout],[],[],.1)[0]:
                raw=os.read(proc.stdout.fileno(),4096);assert raw,'cache native exited before reply';buffer+=raw;assert len(buffer)<=4096
        line,buffer=buffer.split(b'\n',1);records+=1;assert records<=32 and len(line)<=1024;transcript.write(line+b'\n');return json.loads(line)
    def command(name):
        issued=time.monotonic();proc.stdin.write((name+'\n').encode());proc.stdin.flush();value=reply();assert value['ack']==name and value['held_cells']==6344
        report['stages'].append(dict(**value,reply_ms=(time.monotonic()-issued)*1000));return value
    def find():
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];visited=0
        for i in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(i)
            if app and app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            item,depth=pending.pop();item.clear_cache();visited+=1;assert visited<=256 and depth<=20
            if item.get_description()=='syspane.cache.erasure.probe':return item
            if item.get_role() in (Atspi.Role.TABLE,Atspi.Role.TREE_TABLE):continue
            for i in range(item.get_child_count()):pending.append((item.get_child_at_index(i),depth+1))
    def table():
        tree.clear_cache();value=tree.get_table_iface();assert value and value.get_n_columns()==2;return value
    def text(cell):
        cell.clear_cache();interface=cell.get_text_iface();assert interface;value=Atspi.Text.get_text(interface,0,-1);assert isinstance(value,str),'missing remote text';return value
    def leaks(phase):
        counts=dict(text=0,name=0,count=0,word=0);errors=0;successful=0;witness=[]
        for index,reference in enumerate(references):
            values={};words=[]
            for method_index,method in enumerate(methods):
                assert time.monotonic()<deadline,'cache observer deadline'
                try:
                    value=request(reference,method);successful+=1;wire_rows.append([phase,index,method_index,0,value]);values[method[0]]=value[0]
                    if method_index>=3:words.append(value[0])
                except GLib.Error as error:
                    remote=Gio.DBusError.get_remote_error(error);normalized=error.message.replace(reference[1],'{object_path}');record=[remote,error.domain,error.code,normalized]
                    key=json.dumps(record);pool=error_indices.get(key)
                    if pool is None:pool=len(error_pool);error_indices[key]=pool;error_pool.append(record)
                    wire_rows.append([phase,index,method_index,1,pool]);errors+=1
                    if len(witness)<8:witness.append(dict(index=index,method=method[0],remote_error=record,reference=reference))
            counts['text']+=bool(values.get('GetText'));counts['name']+=bool(values.get('Name'));counts['count']+=values.get('CharacterCount',0)!=0;counts['word']+=any(words)
        return dict(cells=len(held),successful_requests=successful,failed_requests=errors,leaks=counts,witness=witness)
    try:
        assert reply()==dict(ready=True,rows=3172,columns=2,held_cells=6344)
        until=time.monotonic()+3
        while tree is None:
            while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
            tree=find();assert time.monotonic()<until;time.sleep(.005)
        current=table();assert current.get_n_rows()==len(INITIAL)
        for row,wanted in enumerate(INITIAL):
            for column,value in enumerate(wanted):
                cell=current.get_accessible_at(row,column);assert text(cell)==value and cell.get_name()==value;interface=cell.get_text_iface();assert interface;held.append((cell,interface))
                reference=[cell.app.bus_name,cell.path];assert reference[0] and reference[1].startswith('/org/a11y/atspi/accessible/');references.append(reference)
                initial=[request(reference,method) for method in methods];assert initial[0]==(value,) and initial[1]==(value,) and initial[2]==(len(value),)
        assert len(held)==6344;report['initial_sha256']=sha(encoded(INITIAL))
        retired=command('retire');assert table().get_n_rows()==(1 if cohort=='collapsed' else 3139)
        if strategy=='lifetime':
            assert retired['retired_checked'] and retired['retired_leaks']==0 and retired['collapsed_leaks']==0
            current=table();active=INITIAL[:3139] if cohort=='expanded' else INITIAL[:1]
            assert [[text(current.get_accessible_at(row,col)) for col in range(2)] for row in range(len(active))]==active,'shared renderer changed live cells'
        erased=command('erase');assert table().get_n_rows()==0
        report['erased']=leaks('erased')
        command('recover');current=table();assert current.get_n_rows()==2
        actual=[[text(current.get_accessible_at(row,col)) for col in range(2)] for row in range(2)];assert actual==FRESH;report['fresh_sha256']=sha(encoded(actual))
        if strategy=='lifetime':
            fresh_refs={(current.get_accessible_at(row,col).app.bus_name,current.get_accessible_at(row,col).path) for row in range(2) for col in range(2)}
            assert not fresh_refs.intersection(map(tuple,references)),'retired wire path rebound to fresh data'
        report['recovered_old_refs']=leaks('recovered')
        command('quit');assert proc.wait(timeout=3)==0;report['actual_exit']=True
        if strategy=='lifetime':
            assert all(stage[key]==0 for stage in report['stages'] if stage['local_checked'] for key in ('text_leaks','name_leaks','count_leaks','word_leaks'))
            for phase,index,method,status,value in wire_rows:
                if status:
                    error=error_pool[value];assert error[0]=='org.freedesktop.DBus.Error.UnknownObject' and '{object_path} does not exist' in error[3],'unverified remote error'
                else:assert value[0]==(0 if method==2 else ''),'retired remote value remains'
            report.update(outcome='pass',lifetime_semantics=True,performance_qualified=False)
            return
        assert all(report[phase]['failed_requests']==0 for phase in ('erased','recovered_old_refs')),'strict remote cache oracle: withdrawn/failed requests are preserved, not empty replies'
        if strategy=='scrub':
            assert erased['callback_us']<=100000 and report['stages'][-3]['reply_ms']<=200
            assert all(erased[k]==0 for k in ('text_leaks','name_leaks','count_leaks','word_leaks'))
            assert all(not n for phase in ('erased','recovered_old_refs') for n in report[phase]['leaks'].values())
            report['cache_candidate']='pass'
        else:
            assert report['erased']['leaks']['text']>0 and erased['text_leaks']>0,'negative erasure control failed to expose retained data'
            report['cache_candidate']='rejected: retained values remain'
        report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        proc.stdin.close();proc.stdout.close();stderr.close();transcript.close()
        raw=(folder/'stderr').read_bytes();assert len(raw)<=2*1024*1024
        if re.search(rb'(WARNING|CRITICAL)',raw):report.update(outcome='fail',native_warning=True)
        assert (folder/'stdout.jsonl').stat().st_size<=2*1024*1024
        report['finished_at']=datetime.now(timezone.utc).isoformat();report['elapsed_seconds']=time.monotonic()-started;report['stderr_sha256']=sha(raw)
        journal=encoded(dict(references=references,methods=[method[0] for method in methods],error_pool=error_pool,requests=wire_rows));assert len(journal)<=12*1024*1024;(folder/'wire.json').write_bytes(journal);report['wire_journal_sha256']=sha(journal)
        output=encoded(report);assert len(output)<=12*1024*1024;(folder/'result.json').write_bytes(output)
        assert not report.get('native_warning'),'native warning/critical'

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4],sys.argv[5]);return
    exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file()
    folder=evidence/('gtk-accessible-erase-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
    lifetime='--lifetime' in sys.argv[3:]
    report=dict(family='GTK-CELL-LIFETIME' if lifetime else 'GTK-ACCESSIBLE-ERASURE',outcome='fail',diagnostic_only=True,scope='Standalone cell lifetime semantics with distinct verified withdrawal; no GUI/erasure performance or edition qualification' if lifetime else 'Standalone toolkit cache experiment with all native/external retained cells; no product/registry/edition qualification',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),ROOT/'tests/scene/gtk_accessible_erase_probe.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.hpp',ROOT/'source/build/surface-runtime.json',ROOT/'source/build/text-runtime.json')},cases=[])
    try:
        server,env=launch_xvfb(folder,(1600,2048));env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for strategy in (('lifetime',) if lifetime else ('blank','detach','scrub')):
            for cohort in ('expanded','collapsed'):
                name=strategy+'-'+cohort;child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)), '--observe',str(exe),str(folder/name),strategy,cohort],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                try:out,err=child.communicate(timeout=120)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
                (folder/(name+'.stdout')).write_bytes(out);(folder/(name+'.stderr')).write_bytes(err);path=folder/name/'result.json'
                value=json.loads(path.read_bytes()) if path.exists() else dict(outcome='fail');report['cases'].append(dict(case=name,exit=child.returncode,outcome='pass' if child.returncode==0 and value['outcome']=='pass' else 'fail',record_sha256=sha(path.read_bytes()) if path.exists() else None))
        assert all(case['outcome']=='pass' for case in report['cases']),report['cases'];report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_bytes(encoded(report));print(folder/'result.json',report['outcome'])

if __name__=='__main__':main()
