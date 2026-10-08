"""Adversarial mutations of original native render-watch evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'source/build'))
from record_gnome_render_watch import validate_raw
RAW=[]


class RenderEvidence(unittest.TestCase):
    def reject(self,mutate,mode='live'):
        value=copy.deepcopy(next(r for r in RAW if r['mode']==mode)); mutate(value)
        with self.assertRaises((ValueError,AssertionError,KeyError,IndexError,TypeError)):
            validate_raw(value)
    def test_original_modes(self):
        for raw in RAW: validate_raw(raw)
    def test_missing_samples(self): self.reject(lambda r:r.update(baseline=r['baseline'][:2]))
    def test_frozen_live(self): self.reject(lambda r:[s.update(pixels=r['samples'][0]['pixels']) for s in r['samples']])
    def test_missing_original(self): self.reject(lambda r:r.update(producer=[]))
    def test_rebased_source_time(self):
        def change(r):
            for row in r['producer']:
                m=json.loads(row['payload'])
                if m['type']=='snapshot':
                    for o in m['body']['snapshot']['observations']:
                        if o['measured_at']: o['measured_at']['nanoseconds']=str(r['upper_ns']+1)
                    row['payload']=json.dumps(m)
        self.reject(change)
    def test_query_driven_pixels(self): self.reject(lambda r:r['calls'].insert(2,dict(method='GetState',reply='{}',begin_ns=r['baseline'][0]['begin_ns'],end_ns=r['baseline'][0]['end_ns'])))
    def test_gap(self): self.reject(lambda r:r['samples'][1].update(begin_ns=r['samples'][0]['end_ns']+200_000_000))
    def test_capture_clock(self): self.reject(lambda r:r['baseline'][1].update(mono_end_ms=r['baseline'][1]['mono_begin_ms']+100))
    def test_capture_clock_rebased(self): self.reject(lambda r:[s.update(mono_begin_ms=s['mono_begin_ms']+1000,mono_end_ms=s['mono_end_ms']+1000) for s in r['erasure']['samples']])
    def test_erasure_missing(self): self.reject(lambda r:r['erasure'].update(samples=[]))
    def test_erasure_retained(self): self.reject(lambda r:[s.update(pixels=r['baseline'][-1]['pixels']) for s in r['erasure']['samples']])
    def test_final_pixels(self): self.reject(lambda r:r['post_clear'].update(pixels=r['baseline'][-1]['pixels']))
    def test_missing_exit(self): self.reject(lambda r:r['exits']['watcher'].update(pidfd_exit=False))
    def test_wrong_exit(self): self.reject(lambda r:r['exits']['worker'].update(pid=r['peers']['watcher']['pid']))
    def test_handle_retained(self): self.reject(lambda r:r['final']['watch'].update(view=True))
    def test_paint_callback_retained(self): self.reject(lambda r:r['final'].update(paintSignal=True))
    def test_wrong_namespace(self): self.reject(lambda r:r.update(same_time_namespace=False))
    def test_missing_stop(self): self.reject(lambda r:r.update(calls=[c for c in r['calls'] if c['method']!='Stop']))
    def test_forged_result(self): self.reject(lambda r:r['evaluation'].update(age='fail'))
    def test_missing_challenge(self): self.reject(lambda r:r.update(watch_journal=[x for x in r['watch_journal'] if x['event']!='challenge']))
    def test_false_ack(self): self.reject(lambda r:next(x for x in r['watch_journal'] if x['event']=='progress').update(generation=999))
    def test_late_ack(self):
        def change(r):
            issue=next(x for x in r['watch_journal'] if x['event']=='challenge')
            next(x for x in r['watch_journal'] if x['event']=='progress')['observed_ms']=issue['issued_ms']+3000
        self.reject(change)
    def test_no_paint(self): self.reject(lambda r:r['final'].update(renderTrace=[x for x in r['final']['renderTrace'] if x['event']!='paint']))
    def test_no_draw(self): self.reject(lambda r:r['final'].update(renderTrace=[x for x in r['final']['renderTrace'] if x['event']!='draw']))
    def test_false_progress_cannot_pass(self): self.reject(lambda r:r['evaluation'].update(outcome='pass',age='pass'),'false-progress')
    def test_erased_fault(self): self.reject(lambda r:r.update(watch_journal=[x for x in r['watch_journal'] if x['event']!='fault']),'render-stall')
    def test_late_fault(self): self.reject(lambda r:next(x for x in r['watch_journal'] if x['event']=='fault').update(since_challenge_ms=3201),'render-stall')
    def test_stall_needs_live_health(self): self.reject(lambda r:next(x for x in r['watch_journal'] if x['event']=='fault').update(health_alive=False),'render-stall')
    def test_dead_source_during_stall(self): self.reject(lambda r:r['samples'][0]['alive'].update(worker=False),'render-stall')
    def test_rebased_hang(self): self.reject(lambda r:r['erasure'].update(mono_begin_ms=r['erasure']['mono_begin_ms']+100),'watch-hang')
    def test_wrong_signal_pid(self): self.reject(lambda r:r['signals'][0].update(pid=r['peers']['worker']['pid']),'watch-exit')
    def test_shell_replaced(self): self.reject(lambda r:r['shell_after'].update(start_ticks=r['shell_after']['start_ticks']+1),'shell-freeze')
    def test_resume_before_fault(self): self.reject(lambda r:r['signals'][-1].update(mono_begin_ms=r['signals'][0]['mono_begin_ms']),'shell-freeze')
    def test_failure_not_closed(self): self.reject(lambda r:r['final']['watch'].update(phase='closed',error=None),'shell-freeze')
    def test_failed_worker_not_subscription_expiry(self): self.reject(lambda r:next(x for x in r['final']['session']['events'] if x['event']=='stopped').update(code=1),'shell-freeze')


if __name__=='__main__':
    RAW=[json.loads(Path(p).read_text()) for p in sys.argv[1:] if p!='-v']; sys.argv=[sys.argv[0],'-v']
    if len(RAW)!=8: raise ValueError('eight original private observations required')
    unittest.main()
