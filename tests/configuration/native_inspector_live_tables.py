"""Installed table limits with deterministic acquisition and real native delivery."""
import copy,json,select,time
import native_installed_editor as h
import inspector_live_table_inputs as inputs

CASES_PATH='tests/configuration/inspector-live-table-cases.json'
CASES=json.loads((h.ROOT/CASES_PATH).read_bytes());h.CASES=CASES
launch_xvfb=h.launch_xvfb
h.launch_xvfb=lambda folder:launch_xvfb(folder,(1600,2048))

def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value,sensitive=(e[k] for k in ('wait','click','find','value','sensitive'))
    fixture=inputs.generation(h.ROOT,mode)
    report['input']=dict(files={k:h.sha(v) for k,v in fixture[2].items()},rows=inputs.count(mode),columns=inputs.columns(mode),screen=[1600,2048],font_dip=9)
    assert report['input']==json.loads((h.ROOT/'tests/configuration/inspector-live-table-inputs.json').read_bytes())[mode]
    report['recipe_sha256']=h.sha((h.ROOT/'tests/configuration/inspector_live_table_inputs.py').read_bytes())
    e['env']['SYSPANE_TEST_TIMING']='1'
    (folder/'network').write_text('allow\n');(folder/'workload-rows').write_text(str(inputs.count(mode)))
    (folder/'workload-round').write_text('1')
    def rows():
        tree=find('syspane.scene.inspector')
        if not tree:return []
        table=tree.get_table_iface();assert table and table.get_n_columns()==2
        return [[e['text'](table.get_accessible_at(r,c)) for c in range(2)] for r in range(table.get_n_rows())]
    def candidate(round):
        current=rows()
        # Readiness may span one native publication; exact stable snapshots below
        # are the oracle. Preserve each nonready observation for diagnosis.
        try:inputs.verify(current,mode,round)
        except AssertionError:
            report['last_nonready_rows']=current
            return False
        return current
    def ready(round):
        current=wait(lambda:candidate(round),12)
        owner=inputs.verify(current,mode,round)
        report['observations'].append(dict(round=round,owner=owner,rows=current))
        return current,owner
    def open_view(round):
        click('frontend.inspector');return ready(round)
    e['launch']();e['settings_ready']();e['documents']();e['quit']()
    inputs.authored.install(e['generations'],fixture)
    generations=sorted(p.name for p in e['generations'].iterdir())
    e['launch']();e['settings_ready']();keys=h.Keys(e['process']().pid)
    try:
        if mode=='OVER-CELLS':
            click('frontend.inspector')
            wait(lambda:value('frontend.status')==CASES['unavailable'] and (folder/'workload-read').exists(),12)
            assert rows()==[] and value('syspane.scene.requested-summary')==''
            report['explicit_refusal']=True
        else:
            current,owner=open_view(1)
            tree=find('syspane.scene.inspector');e['focus'](tree);keys.press(0xff57)
            wait(lambda:list(tree.get_table_iface().get_selected_rows())==[len(current)-1])
            button=next(o for o in e['objects']() if o.get_role()==e['Atspi'].Role.PUSH_BUTTON and o.get_name()=='Summary')
            e['focus'](button);keys.press(0x20)
            wait(lambda:bool(value('syspane.scene.requested-summary')))
            requested=value('syspane.scene.requested-summary')
            assert requested.split('\n',1)[0]==current[-1][0]
            (folder/'workload-round.next').write_text('2')
            (folder/'workload-round.next').replace(folder/'workload-round')
            updated,new_owner=ready(2);assert new_owner[0]==owner[0]
            assert value('syspane.scene.requested-summary')==requested
            assert list(tree.get_table_iface().get_selected_rows())==[len(current)-1]
            if mode=='ORACLE':
                wrong=copy.deepcopy(updated);wrong[2][1]=wrong[2][1].replace('2001 byte','999999 byte',1)
                assert wrong!=updated
                try:inputs.verify(wrong,mode,2)
                except AssertionError:report['wrong_counter_rejected']=True
                else:raise AssertionError('incorrect counter accepted')
            start=time.monotonic();observed=0
            while time.monotonic()-start<CASES['steady_seconds']:
                ready(2);observed+=1;time.sleep(.02)
            report['steady_observations']=observed
            if mode=='NAVIGATION':
                click('frontend.settings');e['settings_ready']();_,new= open_view(2);assert new[0]!=owner[0]
            elif mode=='POLICY':
                _,fd=e['child']();(folder/'policy').write_text('deny\n')
                wait(lambda:select.select([fd],[],[],0)[0],4)
                start=time.monotonic();wait(lambda:not rows() and value('syspane.scene.requested-summary')=='',.2)
                report['erasure_ms']=(time.monotonic()-start)*1000
        e['screenshot']('inspector-live-table');e['quit']()
    finally:keys.close()
    inputs.authored.verify(e['generations'],fixture)
    assert sorted(p.name for p in e['generations'].iterdir())==generations
    e['timings']();samples=report.get('timings',[]);assert samples
    report['timing_violations']=[dict(index=i,**v) for i,v in enumerate(samples) if max(v['work_us'],v['delay_us'])>100000]
    assert not report['timing_violations'],('GUI timing limit exceeded',report['timing_violations'])

exercise.capture_timings=True
exercise.continue_after_case_failure=True
if __name__=='__main__':h.main(exercise,__file__,CASES_PATH,'inspector-live-table-')
