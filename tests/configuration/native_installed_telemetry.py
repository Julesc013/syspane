"""Ordinary installed inspector; independent native rows, counters and child exits."""
import copy,json,os,re,select,signal,time
from pathlib import Path
import native_installed_editor as h
from native_network_service import linux_rows
CASES_PATH='tests/configuration/installed-telemetry-cases.json'
CASES=json.loads((h.ROOT/CASES_PATH).read_bytes());h.CASES=CASES

def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value,sensitive=(e[k] for k in ('wait','click','find','value','sensitive'))
    (folder/'network').write_text('allow\n')
    def children():
        result=[];pids=set();parent=e['process']().pid
        for task in Path('/proc',str(parent),'task').iterdir():
            try:pids.update(map(int,(task/'children').read_text().split()))
            except FileNotFoundError:pass
        for pid in pids:
            try:
                args=Path('/proc',str(pid),'cmdline').read_bytes().split(b'\0')[:-1]
                if args==[b'syspane-network-host',b'--network',str(parent).encode()]:result.append(pid)
            except FileNotFoundError:pass
        assert len(result)<=1,result
        return result
    def rows():
        tree=find('syspane.scene.inspector')
        if not tree:return []
        table=tree.get_table_iface();assert table and table.get_n_columns()==2
        return [[e['text'](table.get_accessible_at(r,c)) for c in range(2)] for r in range(table.get_n_rows())]
    def live():
        current=rows();cells=[v for k,v in current if '[network.' in k]
        return current if cells and len(cells)%4==0 and all('lease=active' in v and 'acquisition=success' in v and re.search(r'age=\d+ ns',v) for v in cells) else False
    def epoch(current):
        values={re.search(r' \| Epoch (\S+) \| Generation \d+$',v).group(1) for k,v in current if k.startswith('network:interface:')}
        assert len(values)==1;return next(iter(values))
    def verify(current,before,after):
        entities=[]
        for key,info in current:
            if key.startswith('network:interface:'):entities.append({})
            elif key.endswith('[network.receive_bytes]') or key.endswith('[network.transmit_bytes]'):
                assert entities;number=re.search(r'(?:^|\n)(\d+) byte(?:\n|$)',info);assert number,info
                entities[-1]['receive' if key.endswith('[network.receive_bytes]') else 'transmit']=int(number.group(1))
        assert len(entities)==min(8,len(before)) and set(before)==set(after)
        candidates=set(before)
        for pair in entities:
            assert set(pair)=={'receive','transmit'}
            matches=[key for key in candidates if all(before[key][field]<=pair[field]<=after[key][field] for field in pair)]
            assert matches,(pair,before,after);candidates.remove(matches[0])
    def idle():
        end=time.monotonic()+.25;count=0
        while time.monotonic()<end:e['pump']();assert not children();count+=1;time.sleep(.005)
        assert count
    def open_view():
        before=linux_rows();click('frontend.inspector');current=wait(live);after=linux_rows();verify(current,before,after)
        pid=wait(lambda:children() and children()[0]);fd=e['helper_pidfds'][pid]
        report['observations'].append(dict(rows=current,before=before,after=after,pid=pid));return current,pid,fd
    e['launch']();e['settings_ready']();idle();current,pid,fd=open_view();old_epoch=epoch(current)
    if mode=='NAVIGATION':
        click('frontend.settings');e['settings_ready']();wait(lambda:select.select([fd],[],[],0)[0],3);idle()
        current,new_pid,new_fd=open_view();assert new_pid!=pid and epoch(current)!=old_epoch and not select.select([new_fd],[],[],0)[0]
    elif mode=='REPLACEMENT':
        signal.pidfd_send_signal(fd,signal.SIGKILL);assert select.select([fd],[],[],2)[0]
        retained=wait(lambda:rows() if any('lease=retained' in v and 'age=unknown' in v for _,v in rows()) else False,.2)
        assert epoch(retained)==old_epoch
        current=wait(lambda:live() if live() and epoch(live())!=old_epoch else False)
        assert children() and children()[0]!=pid
    elif mode=='POLICY':
        (folder/'network-policy').write_text('deny\n');wait(lambda:select.select([fd],[],[],0)[0],4)
        start=time.monotonic();wait(lambda:not any(k.startswith('network:interface:') for k,_ in rows()) and value('syspane.scene.requested-summary')=='',.2)
        report['erasure_ms']=(time.monotonic()-start)*1000
        wait(lambda:rows()==[['Network','Network'],['Network interfaces','Unsupported field']]);idle()
    elif mode=='CONFIGURATION-LOSS':
        config,handle=e['child']();assert config!=pid;signal.pidfd_send_signal(handle,signal.SIGKILL);assert select.select([handle],[],[],2)[0]
        wait(lambda:not rows() and value('syspane.scene.requested-summary')=='',.2);wait(lambda:select.select([fd],[],[],0)[0],3)
        wait(live)
    elif mode=='CLOSE-HELD':
        (folder/'network-mode').write_text('hold\n');wait(lambda:(folder/'network-held').exists());assert int((folder/'network-held').read_text())==pid
    elif mode=='ORACLE':
        original=report['observations'][-1];wrong=copy.deepcopy(original['rows'])
        next(row for row in wrong if row[0].endswith('[network.receive_bytes]'))[1]='18446744073709551615 byte\n'
        try:verify(wrong,original['before'],original['after'])
        except AssertionError:report['wrong_counter_rejected']=True
        else:raise AssertionError('native UI oracle accepted a wrong counter')
    else:assert mode=='LIVE'
    e['documents']();e['screenshot']('telemetry');e['quit']()
    assert select.select([fd],[],[],0)[0]

if __name__=='__main__':h.main(exercise,__file__,CASES_PATH,'telemetry-frontend-')
