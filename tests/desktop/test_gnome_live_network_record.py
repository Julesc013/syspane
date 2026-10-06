"""Adversarial mutations of original measured pixel evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_live_network import validate_raw
RAW=[]

class NetworkEvidence(unittest.TestCase):
    def reject(self,mutate):
        value=copy.deepcopy(next(r for r in RAW if r['mode']=='live'));mutate(value)
        with self.assertRaises((ValueError,AssertionError,KeyError,IndexError,TypeError)):validate_raw(value)
    def test_original_modes(self):
        for raw in RAW:validate_raw(raw)
    def test_missing_samples(self):self.reject(lambda r:r.update(samples=r['samples'][:2]))
    def test_frozen_pixels(self):self.reject(lambda r:[s.update(pixels=r['samples'][0]['pixels']) for s in r['samples']])
    def test_rebased_source_time(self):
        def change(r):
            for row in r['producer']:
                m=json.loads(row['payload'])
                if m['type']=='snapshot':
                    for o in m['body']['snapshot']['observations']:
                        if o['measured_at']:o['measured_at']['nanoseconds']=str(r['upper_ns']+1)
                    row['payload']=json.dumps(m)
        self.reject(change)
    def test_missing_original(self):self.reject(lambda r:r.update(producer=[]))
    def test_no_capture_driven_time(self):self.reject(lambda r:r['calls'].insert(2,{'method':'GetState','reply':'{}','begin_ns':r['samples'][0]['begin_ns'],'end_ns':r['samples'][0]['end_ns']}))
    def test_gap(self):self.reject(lambda r:r['samples'][1].update(begin_ns=r['samples'][0]['end_ns']+200_000_000))
    def test_reverse_capture(self):self.reject(lambda r:r['samples'][0].update(end_ns=r['samples'][0]['begin_ns']-1))
    def test_erasure_missing(self):self.reject(lambda r:r['erasure'].update(samples=[]))
    def test_erasure_retained(self):self.reject(lambda r:[s.update(pixels=r['samples'][-1]['pixels']) for s in r['erasure']['samples']])
    def test_final_pixels(self):self.reject(lambda r:r['post_clear'].update(pixels=r['samples'][-1]['pixels']))
    def test_missing_exit(self):self.reject(lambda r:r['exits']['worker'].update(pidfd_exit=False))
    def test_wrong_exit(self):self.reject(lambda r:r['exits']['worker'].update(pid=r['peers']['supervisor']['pid']))
    def test_handle_retained(self):self.reject(lambda r:r['final']['session'].update(view=True))
    def test_watch_missing(self):self.reject(lambda r:r.update(watch_registered=False))
    def test_wrong_namespace(self):self.reject(lambda r:r.update(same_time_namespace=False))
    def test_missing_stop(self):self.reject(lambda r:r.update(calls=[c for c in r['calls'] if c['method']!='Stop']))
    def test_forged_result(self):self.reject(lambda r:r['evaluation'].update(age='fail'))

if __name__=='__main__':
    RAW=[json.loads(Path(p).read_text()) for p in sys.argv[1:] if p!='-v'];sys.argv=[sys.argv[0],'-v']
    if len(RAW)!=9:raise ValueError('nine original private observations required')
    unittest.main()
