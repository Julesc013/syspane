"""Maximum-input qualification through the actual frontend workers and native bundle."""
from pathlib import Path
import json,time,traceback
import native_frontend_recovery as h
import recovery_limits_inputs as inputs

CASES_PATH=h.ROOT/'tests/configuration/recovery-limits-cases.json'
CASES=json.loads(CASES_PATH.read_bytes())


def exercise(e):
    report=e['report'];report['extension_sha256']=h.sha(Path(__file__).read_bytes())
    report['recipe_sha256']=h.sha(Path(inputs.__file__).read_bytes())
    assert inputs.identities()==CASES['inputs']
    failures=[]
    for name in CASES['cases']:
        started=time.monotonic();q=e['Run'](name,enforce_timing=False);row=dict(case=name,outcome='fail')
        try:
            p=q.ready();e['documents'](q);e['scope'](q,p)
            scene=inputs.scene(name!='MAX-WIDGETS')
            data=inputs.record(scene,p['recovery']['generation'],name in ('MAX-RECORD','OVER-RECORD-REJECT'),name=='MAX-COMMAND-REJECT')
            if name=='OVER-RECORD-REJECT':data+=b' '
            (q.root/'input.record').write_bytes(data)
            row.update(input_bytes=len(data),input_sha256=h.sha(data),scene_sha256=h.sha(inputs.encoded(scene)))
            prepared_at=time.monotonic();admitted=q.call('prepare',bytes=data.decode())
            if name=='OVER-RECORD-REJECT':assert admitted=={'error':'recovery.size'},admitted
            else:
                assert admitted['created'],admitted;row['creation_us']=admitted['timings_us']
                while True:
                    value=q.call('prepared');current=q.call('view')
                    assert current['profile'] and current['profile']['epoch']==p['epoch'] and not current['loading'] and not current['failed'],('supervisor withdrawn during preparation',current)
                    if name=='SUPERVISOR-CLOSE' and value['running']:
                        row['observed_acquired_work']=True;closing=time.monotonic();q.close();row['close_seconds']=time.monotonic()-closing;break
                    if value['stopped']:
                        assert name!='SUPERVISOR-CLOSE','preparation finished before acquired-work observation'
                        row['preparation_seconds']=time.monotonic()-prepared_at
                        if name=='MAX-COMMAND-REJECT':assert not value['ready'] and value['error']=='recovery.command',value
                        else:
                            assert value['ready'] and value['scene']==scene,value
                            row['restore_us']=value['restore_us']
                        break
                    q.left();time.sleep(.002)
            if not q.closed:q.close()
            e['documents'](q)
            assert not q.record.get('timing_violations'),q.record.get('timing_violations')
            row['outcome']='pass'
        except Exception:
            row['failure']=traceback.format_exc();failures.append(name)
            if q.proc.poll() is None and not q.closed:
                try:q.close()
                except Exception:row['cleanup_failure']=traceback.format_exc()
        finally:
            q.finish();row['seconds']=time.monotonic()-started;report['cases'].append(row);e['save']()
    assert not failures,('recovery qualification failed',failures)


if __name__=='__main__':h.main(exercise,CASES_PATH)
