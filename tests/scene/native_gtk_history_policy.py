"""Maximum actual inspector revocation: held native cells and lossless raw AT-SPI reads."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,select,signal,subprocess,sys,time,traceback,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tests/scene'),str(ROOT/'tests/fault'),str(ROOT/'source/build')]
import native_gtk_history_limits as history
from native_diagnostic import launch_xvfb
from native_inspector import Keys
from check_surface_runtime import verify
CASES=history.CASES
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda value:(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()

def observe(exe,folder,mode):
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi,GLib,Gio
    Atspi.set_timeout(200,500);verify();folder.mkdir()
    started=time.monotonic();deadline=started+CASES['child_seconds'];buffer=b'';records=0;keys=None
    report=dict(case=mode,outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),observations=[],progress=[])
    refs=[];seen_refs=set();journal=[];errors=[];error_ids={}
    stderr=(folder/'stderr').open('wb');transcript=(folder/'stdout.jsonl').open('wb')
    env=dict(os.environ,G_DEBUG='fatal-warnings',NO_AT_BRIDGE='0');env.pop('SYSPANE_GTK_HISTORY_PHASE_FILE',None)
    proc=subprocess.Popen([str(exe),str(ROOT/'spec/fixtures/valid'),'GTK-HISTORY-POLICY',mode,str(CASES[mode]['points'])],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
    def save():
        raw=encoded(report);assert len(raw)<=CASES['observation_bytes'];(folder/'result.json').write_bytes(raw)
    def reply():
        nonlocal buffer,records
        while b'\n' not in buffer:
            assert time.monotonic()<deadline,'maximum policy native deadline'
            if select.select([proc.stdout],[],[],.2)[0]:
                raw=os.read(proc.stdout.fileno(),4096);assert raw,'maximum policy native exited before reply';buffer+=raw;assert len(buffer)<=4096
        line,buffer=buffer.split(b'\n',1);assert len(line)<=512;records+=1;assert records<=CASES['reply_records'];transcript.write(line+b'\n');return json.loads(line)
    def receive(name):
        while True:
            value=reply()
            if 'progress' in value:report['progress'].append(value);save();print(mode+' progress '+str(value['progress']),flush=True);continue
            assert value['ack']==name and value['command_work_us']<=CASES['gui_limit_us'],value
            report['observations'].append(value);save();return value
    def command(name):
        proc.stdin.write((name+'\n').encode());proc.stdin.flush();return receive(name)
    def wait(predicate,seconds=3):
        until=min(deadline,time.monotonic()+seconds)
        while True:
            context=GLib.MainContext.default()
            for _ in range(100):
                if not context.pending():break
                context.iteration(False)
            value=predicate()
            if value:assert time.monotonic()<=until;return value
            assert time.monotonic()<until,'maximum policy native observation deadline';time.sleep(.005)
    def find(description=None,button=None):
        desktop=Atspi.get_desktop(0);desktop.clear_cache();pending=[];visited=0
        for i in range(desktop.get_child_count()):
            app=desktop.get_child_at_index(i)
            if app and app.get_process_id()==proc.pid:pending.append((app,0))
        while pending:
            item,depth=pending.pop();item.clear_cache();visited+=1;assert visited<=512 and depth<=20
            if description and item.get_description()==description:return item
            if button and item.get_role()==Atspi.Role.PUSH_BUTTON and item.get_name()==button:return item
            if item.get_role() in (Atspi.Role.TABLE,Atspi.Role.TREE_TABLE):continue
            for i in range(item.get_child_count()):pending.append((item.get_child_at_index(i),depth+1))
    methods=[('GetText','org.a11y.atspi.Text','GetText','(ii)',(0,-1),'(s)'),('Name','org.freedesktop.DBus.Properties','Get','(ss)',('org.a11y.atspi.Accessible','Name'),'(v)'),('CharacterCount','org.freedesktop.DBus.Properties','Get','(ss)',('org.a11y.atspi.Text','CharacterCount'),'(v)')]+[(name,'org.a11y.atspi.Text',name,'(iu)',(0,int(Atspi.TextBoundaryType.WORD_START)),'(sii)') for name in ('GetTextBeforeOffset','GetTextAtOffset','GetTextAfterOffset')]+[('GetStringAtOffset','org.a11y.atspi.Text','GetStringAtOffset','(iu)',(0,int(Atspi.TextGranularity.WORD)),'(sii)')]
    wire=None;tree=None;summary=None
    def call(reference,interface,method,signature,args,reply_type):
        assert time.monotonic()<deadline,'maximum policy raw read deadline'
        return wire.call_sync(reference[0],reference[1],interface,method,GLib.Variant(signature,args),GLib.VariantType.new(reply_type),Gio.DBusCallFlags.NONE,200,None).unpack()
    def request(reference,method):return call(reference,*method[1:])
    def table_count():
        tree.clear_cache();table=tree.get_table_iface();assert table and table.get_n_columns()==2;count=table.get_n_rows();assert 0<=count<=1+4096+321;return count
    def reference(row,col):
        result=call([tree.app.bus_name,tree.path],'org.a11y.atspi.Table','GetAccessibleAt','(ii)',(row,col),'((so))')[0]
        assert result[0] and result[1].startswith('/org/a11y/atspi/accessible/'),'missing raw native table cell'
        return list(result)
    def matrix(wanted=None,retain=False):
        count=table_count();actual=[];fresh=[]
        if wanted is not None:assert count==len(wanted),'maximum policy exact row count'
        for row in range(count):
            values=[]
            for col in range(2):
                ref=reference(row,col);fresh.append(ref)
                if retain:
                    assert tuple(ref) not in seen_refs,'duplicate initial raw identity';seen_refs.add(tuple(ref));index=len(refs);refs.append(ref)
                    replies=[request(ref,method) for method in methods];assert replies[0]==(wanted[row][col],) and replies[1]==(wanted[row][col],) and replies[2]==(len(wanted[row][col]),),'initial native text/name/count differ from independent literal oracle'
                    journal.extend([['initial',index,m,0,value] for m,value in enumerate(replies)])
                    values.append(replies[0][0])
                else:values.append(request(ref,methods[0])[0])
            actual.append(values)
        if wanted is not None:history.equal(actual,wanted)
        return actual,fresh
    def summary_text():
        summary.clear_cache();return request([summary.app.bus_name,summary.path],methods[0])[0]
    def old_reads(phase):
        successful=withdrawn=0
        for index,ref in enumerate(refs):
            for m,method in enumerate(methods):
                try:
                    value=request(ref,method);journal.append([phase,index,m,0,value]);successful+=1
                    assert value[0]==(0 if m==2 else ''),'maximum policy old reference contains data'
                except GLib.Error as error:
                    normalized=error.message.replace(ref[1],'{object_path}');record=[Gio.DBusError.get_remote_error(error),error.domain,error.code,normalized]
                    key=json.dumps(record);pool=error_ids.get(key)
                    if pool is None:pool=len(errors);error_ids[key]=pool;errors.append(record)
                    journal.append([phase,index,m,1,pool]);withdrawn+=1
                    assert record[0]=='org.freedesktop.DBus.Error.UnknownObject' and '{object_path} does not exist' in normalized,'unverified remote error is not empty data'
        return dict(cells=len(refs),successful=successful,verified_withdrawal=withdrawn,requests=successful+withdrawn)
    try:
        assert reply()==dict(ready=True);tree=wait(lambda:find('syspane.scene.inspector'));keys=Keys(proc.pid)
        session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        address=session.call_sync('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress',None,GLib.VariantType.new('(s)'),Gio.DBusCallFlags.NONE,500,None).unpack()[0]
        wire=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
        command('fill');count=CASES[mode]['points'];held=command('hold');wanted=history.expected(history.oracle.sequence(count),mode=='mixed',count)
        assert held['held']==dict(cells=len(wanted)*2,checks=0,empty=False,defunct=0,modern_unsupported=True)
        actual,_=matrix(wanted,True);report['initial']=dict(rows=len(actual),cells=len(refs),sha256=sha(encoded(actual)));(folder/'initial-rows.json').write_bytes(encoded(actual));save()
        assert tree.get_component_iface().grab_focus();keys.press(0xff57);wait(lambda:list(tree.get_table_iface().get_selected_rows())==[len(wanted)-1])
        summary=wait(lambda:find('syspane.scene.requested-summary'));button=wait(lambda:find(button='Summary'));assert button.get_component_iface().grab_focus();keys.press(0x20);wait(lambda:summary_text()=='\n'.join(wanted[-1]))
        issued=time.monotonic();proc.stdin.write(b'revoke\nregrant\n');proc.stdin.flush();revoked=receive('revoke');granted=receive('regrant');paired=reply()
        assert paired['callback']=='paired' and paired['commands']==2 and paired['work_us']<=CASES['gui_limit_us'];report['paired_callback']=paired
        assert revoked['native_pending']>0 and granted['native_pending']>0 and revoked['held']['empty'] and granted['held']['empty'] and granted['points']==0
        assert table_count()==0 and summary_text()=='';report['erasure_ms']=(time.monotonic()-issued)*1000;assert report['erasure_ms']<=CASES['erasure_ms'];save()
        report['revoked_reads']=old_reads('revoked');checked=command('held-check');assert checked['held']['empty'] and checked['native_pending']==0 and checked['held']['defunct']==len(refs) and checked['points']==0
        waiting,_=matrix();assert len(waiting)<=2 and all(row[0] in ('Receive','Interfaces') and '10 byte' not in row[1] and '7 byte' not in row[1] and 'network:interface:' not in row[1] and 'generation ' not in row[1] for row in waiting),'old delivery became current operational data';report['old_scope_rows']=waiting;save()
        command('fresh');fresh_wanted=history.expected([(21000000000,4099,False)],mode=='mixed',4099);fresh,fresh_refs=matrix(fresh_wanted);assert not set(map(tuple,refs)).intersection(map(tuple,fresh_refs)),'old native path rebound to fresh data';assert summary_text()==''
        report['fresh']=dict(rows=len(fresh),sha256=sha(encoded(fresh)));(folder/'fresh-rows.json').write_bytes(encoded(fresh));report['fresh_old_reads']=old_reads('fresh')
        checked=command('held-check');assert checked['held']['defunct']==len(refs) and checked['held']['empty'] and checked['native_pending']==0
        closed=command('close');assert table_count()==0 and summary_text()=='';producer=closed['producer'];retirement=closed['retirement']
        assert producer['accepted']==count+1 and producer['receiver_owner'] and producer['stopped'] and producer['renderer_stopped'] and producer['failure']==0 and producer['clock_gap_max_ms']<=250,producer
        assert retirement['pending']==0 and retirement['accepted']==retirement['delivered'] and retirement['polls']>1 and retirement['max_us']<=CASES['gui_limit_us'] and not retirement['failed'],retirement
        report.update(producer=producer,retirement=retirement);checked=command('held-check');assert checked['held']['empty'] and checked['held']['defunct']==len(refs)
        command('quit');destroyed=reply();assert destroyed==dict(destroyed_held=len(refs),empty=True,defunct_once=True,modern_unsupported=True);assert proc.wait(timeout=3)==0;report.update(after_destroy=destroyed,actual_exit=True,outcome='pass')
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
        if keys:keys.close()
        proc.stdin.close();proc.stdout.close();stderr.close();transcript.close();raw=(folder/'stderr').read_bytes()
        losses=[json.loads(line[len(b'history-loss '):]) for line in raw.splitlines() if line.startswith(b'history-loss ')];assert len(losses)<=1
        if losses:report['lost_points']=losses[0]
        try:
            samples=history.decode_timings(raw);report['timing_max_us']={k:max(v[k] for v in samples) for k in ('work_us','delay_us')};report['timing_records']=len(samples);report['timing_violations']=[dict(index=i,**v) for i,v in enumerate(samples) if max(v.values())>CASES['gui_limit_us']]
            if report['timing_violations']:report['outcome']='fail'
        except Exception:report['timing_failure']=traceback.format_exc();report['outcome']='fail'
        data=encoded(dict(references=refs,methods=[m[0] for m in methods],error_pool=errors,requests=journal));assert len(data)<=12*1024*1024;(folder/'wire.json').write_bytes(data);report['wire_journal_sha256']=sha(data);report['stderr_sha256']=sha(raw);report['finished_at']=datetime.now(timezone.utc).isoformat();report['elapsed_seconds']=time.monotonic()-started;save()
    assert report['outcome']=='pass',report.get('timing_violations')

def main():
    if sys.argv[1]=='--observe':observe(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4]);return
    exe,evidence=map(lambda p:Path(p).resolve(),sys.argv[1:3]);assert os.geteuid()!=0 and evidence.parent==exe.parent and (exe.parent/'.syspane-owner.json').is_file();history.controls()
    folder=evidence/('gtk-history-policy-'+uuid.uuid4().hex[:12]);folder.mkdir();server=None
    inputs=[Path(__file__),Path(history.__file__),history.CASES_PATH,Path(history.oracle.__file__),ROOT/'tests/scene/gtk_history_limits.hpp',ROOT/'tests/scene/gtk_history_policy.hpp',ROOT/'tests/scene/gtk_history_producer.hpp',ROOT/'source/interfaces/scene_inspector_linux.cpp',ROOT/'source/interfaces/scene_inspector_text_linux.cpp',ROOT/'source/build/surface-runtime.json']
    report=dict(family='GTK-HISTORY-POLICY',outcome='fail',started_at=datetime.now(timezone.utc).isoformat(),executable_sha256=sha(exe.read_bytes()),inputs={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in inputs},cases=[])
    try:
        server,env=launch_xvfb(folder,tuple(CASES['screen']));env['NO_AT_BRIDGE']='0';env.pop('AT_SPI_BUS_ADDRESS',None)
        for mode in CASES['cases']:
            child=subprocess.Popen(['dbus-run-session','--',sys.executable,str(Path(__file__)),'--observe',str(exe),str(folder/mode),mode],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            try:out,err=child.communicate(timeout=CASES['child_seconds'])
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate(timeout=5)
            (folder/(mode+'.stdout')).write_bytes(out);(folder/(mode+'.stderr')).write_bytes(err);path=folder/mode/'result.json';value=json.loads(path.read_bytes()) if path.exists() else dict(outcome='fail')
            report['cases'].append(dict(case=mode,exit=child.returncode,outcome='pass' if child.returncode==0 and value['outcome']=='pass' else 'fail',record_sha256=sha(path.read_bytes()) if path.exists() else None))
        assert all(c['outcome']=='pass' for c in report['cases']),report['cases'];report['outcome']='pass'
    except Exception:report['failure']=traceback.format_exc();raise
    finally:
        if server:server.terminate();server.communicate(timeout=5)
        report['finished_at']=datetime.now(timezone.utc).isoformat();(folder/'result.json').write_bytes(encoded(report));print(folder/'result.json',report['outcome'])

if __name__=='__main__':main()
