"""Independent current-profile and single-consumption checks on the real backend."""
from pathlib import Path
import copy, time
import native_frontend_recovery as h


def exercise(e):
    for case in h.CASES['cases']:
        begin=time.monotonic();q=e['Run'](case)
        try:
            p=q.ready();e['documents'](q);q.call('remember')
            assert q.call('settings-ready',copied=True)=={'consumed':False}
            if case=='SINGLE':
                assert q.call('settings-ready')=={'consumed':True}
                assert q.call('settings-ready')=={'consumed':False}
                assert q.call('editor-ready')=={'consumed':True}
                assert q.call('editor-ready')=={'consumed':False}
            elif case in ('RELOAD','REPEATED-RELOAD'):
                for _ in range(8 if case=='REPEATED-RELOAD' else 1):q.call('reload')
                assert q.call('settings-ready',old=True)=={'consumed':False}
                fresh=q.ready(p['serial']);assert fresh['epoch']==p['epoch']
                assert q.call('settings-ready',old=True)=={'consumed':False}
                assert q.call('settings-ready')=={'consumed':True}
            elif case=='PENDING':
                command=copy.deepcopy(h.COMMAND);command['intent']='commit'
                assert 'request' in q.call('submit',command=command,digest=None)
                assert q.call('settings-ready')=={'consumed':False}
                def accepted():
                    reply=q.call('view')['reply']
                    if reply:
                        result=reply['body'];assert result['outcome']=='accepted' and result['durable'] and result['revision']=='1'
                        return True
                q.wait(accepted);e['documents'](q,True);q.call('reload');q.ready(p['serial'])
                assert q.call('settings-ready',old=True)=={'consumed':False}
                assert q.call('settings-ready')=={'consumed':True}
            elif case=='POLICY':
                (q.root/'policy').write_text('deny\n');q.wait(lambda:q.call('view')['profile'] is None)
                assert q.call('settings-ready',old=True)=={'consumed':False}
                (q.root/'policy').write_text('allow\n');q.ready(p['serial'])
                assert q.call('settings-ready')=={'consumed':True}
            elif case=='RESTART':
                q.kill_controller();fresh=q.ready(p['serial']);assert fresh['epoch']!=p['epoch']
                assert q.call('settings-ready',old=True)=={'consumed':False}
                assert q.call('settings-ready')=={'consumed':True}
            elif case=='CLOSE':
                q.call('close');assert q.call('settings-ready',old=True)=={'consumed':False}
            else:raise AssertionError('unknown prepared editor case')
            q.close();e['report']['cases'].append(dict(case=case,outcome='pass',seconds=time.monotonic()-begin));e['save']()
        finally:q.finish()


if __name__=='__main__':
    h.main(exercise,Path(__file__).with_name('prepared-settings-cases.json'))
