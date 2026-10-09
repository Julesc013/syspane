"""Maximum recovery inputs through the installed GTK loop and independent files."""
from pathlib import Path
import copy,json,select,time
import native_installed_editor as h
import recovery_limits_inputs as inputs

CASES_PATH='tests/configuration/recovery-gui-limits-cases.json'
CASES=json.loads((h.ROOT/CASES_PATH).read_bytes());h.CASES=CASES


def exercise(e):
    folder,mode,report=(e[k] for k in ('folder','mode','report'))
    wait,click,find,value,sensitive=(e[k] for k in ('wait','click','find','value','sensitive'))
    launch,settings,quit=(e[k] for k in ('launch','settings_ready','quit'))
    report['recipe_sha256']=h.sha(Path(inputs.__file__).read_bytes())
    assert inputs.identities()==json.loads((h.ROOT/CASES['recipe_expectations']).read_bytes())['inputs']
    e['env']['SYSPANE_TEST_TIMING']='1';(folder/'history').write_text('allow\n')
    scene=inputs.scene(mode!='MAX-WIDGETS')
    record=folder/'state/syspane/state'/h.sha(CASES['profile'].encode())/'recovery/draft.json'
    def bytes_at(expected):
        actual=record.read_bytes() if record.exists() else None
        assert actual==expected,('recovery bytes differ',h.sha(actual) if actual else None,h.sha(expected) if expected else None)
    def documents(saved=False):
        expected=copy.deepcopy(h.INITIAL['documents'])
        if saved:
            expected['scene']=copy.deepcopy(scene);expected['scene']['revision']='1';expected['settings']['revision']='1'
        actual=h.stored(e['generations']);assert actual==expected,'saved documents differ from independent recipe'
        report['observations'].append(dict(saved=saved,documents_sha256=h.sha(h.encoded(actual))))
        assert not any(json.loads(p.read_bytes())['revision']=='2' for p in e['generations'].glob('*/scene.json'))
    def retained():
        wait(lambda:value('editor.recovery-status')=='Recovery draft retained. Configuration remains unsaved.' and sensitive(find('editor.apply')),12)
        bytes_at(canonical);documents()
    launch();settings();documents();quit()
    generation=h.sha((e['generations']/'current.json').read_bytes())
    raw=inputs.record(scene,generation,mode in ('MAX-RECORD','OVER-RECORD-REJECT'),mode=='MAX-COMMAND-REJECT')
    if mode=='OVER-RECORD-REJECT':raw+=b' '
    canonical=inputs.record(scene,generation)
    record.write_bytes(raw);record.chmod(0o600)
    (folder/'input.record').write_bytes(raw)
    report.update(input_bytes=len(raw),input_sha256=h.sha(raw),scene_sha256=h.sha(inputs.encoded(scene)))
    launch();settings();click('frontend.editor')
    if mode=='CLOSE-PREPARING':
        wait(lambda:value('editor.recovery-status')=='Checking recovery draft...' and not sensitive(find('editor.recovery-restore')))
        report['observed_loading']=True;quit();bytes_at(raw);documents()
    elif mode=='OVER-RECORD-REJECT':
        wait(lambda:value('editor.recovery-status').startswith('Recovery unavailable.') and sensitive(find('frontend.settings')),12)
        bytes_at(raw);documents();quit()
    else:
        wait(lambda:sensitive(find('editor.recovery-keep')),12)
        assert bool(sensitive(find('editor.recovery-restore')))==(mode!='MAX-COMMAND-REJECT')
        assert not sensitive(find('editor.apply')) and not sensitive(find('frontend.settings'));bytes_at(raw)
        if mode=='MAX-COMMAND-REJECT':documents();quit();bytes_at(raw)
        else:
            click('editor.recovery-restore');retained()
            if mode=='POLICY':
                pid,fd=e['child']();(folder/'policy').write_text('deny\n')
                wait(lambda:bool(select.select([fd],[],[],0)[0]),4)
                observed=time.monotonic();wait(e['erased'],CASES['erasure_after_observed_loss_ms']/1000)
                report.update(erasure_limit_ms=CASES['erasure_after_observed_loss_ms'],erasure_ms=(time.monotonic()-observed)*1000)
                bytes_at(canonical);documents();assert not sensitive(find('editor.apply'));quit()
            else:
                click('editor.undo')
                wait(lambda:value('editor.recovery-status')=='Recovery ready. No unsaved draft.' and sensitive(find('frontend.settings')),12)
                bytes_at(None);documents()
                click('editor.redo');retained()
                click('editor.apply')
                wait(lambda:'Configuration saved durably at revision 1.' in e['status']() and value('editor.recovery-status')=='Recovery ready. No unsaved draft.' and sensitive(find('frontend.settings')),12)
                bytes_at(None);documents(True);quit();documents(True)
    e['timings']()
    rows=report.get('timings',[]);assert rows,'missing GUI timing observations'
    violations=[dict(index=i,**v) for i,v in enumerate(rows) if max(v['work_us'],v['delay_us'])>CASES['gui_operation_limit_ms']*1000]
    report['timing_violations']=violations
    assert not violations,('GUI timing limit exceeded',violations)


exercise.capture_timings=True
exercise.continue_after_case_failure=True
if __name__=='__main__':h.main(exercise,__file__,CASES_PATH,'rgl-')
