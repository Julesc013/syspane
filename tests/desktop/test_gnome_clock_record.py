"""Adversarial mutations of original native clock observations, not new oracles."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_clock import validate_raw

RAW=[]
class ClockEvidence(unittest.TestCase):
    def original(self):return copy.deepcopy(next(r for r in RAW if r['mode']=='live'))
    def reject(self,mutate):
        value=self.original();mutate(value)
        with self.assertRaises((ValueError,KeyError,IndexError,TypeError)):validate_raw(value)
    def test_original_modes(self):
        for raw in RAW:validate_raw(raw)
    def test_peer_sample_rebased(self):self.reject(lambda r:r['peer_journal'][1].update(sample_ns=str(int(r['ready']['sample'])+1)))
    def test_closed_handle(self):self.reject(lambda r:r['final'].update(clock=True))
    def test_closed_connection(self):self.reject(lambda r:r['final'].update(connection=True))
    def test_missing_exit(self):self.reject(lambda r:r['exit'].update(pidfd_exit=False))
    def test_wrong_exit(self):self.reject(lambda r:r['exit'].update(pid=r['exit']['pid']+1))
    def test_actor_survives(self):self.reject(lambda r:r['final'].update(labels=1))
    def test_missing_captures(self):self.reject(lambda r:r.update(samples=r['samples'][:2]))
    def test_missing_clear_interval(self):self.reject(lambda r:r['erasure'].update(samples=[]))
    def test_wrong_parent(self):self.reject(lambda r:r['peer_journal'][0].update(parent=r['peer']['pid']))
    def test_removed_disable(self):self.reject(lambda r:r.update(calls=[c for c in r['calls'] if c['method']!='Disable']))
    def test_future_sample(self):self.reject(lambda r:r['ready'].update(sample=str(int(r['ready']['after'])+1)))
    def test_capture_gap(self):self.reject(lambda r:r['samples'][1].update(begin_ns=r['samples'][0]['end_ns']+200_000_000))
    def test_claimed_false_pass(self):self.reject(lambda r:r['evaluation'].update(age='fail'))
    def test_reversed_capture(self):self.reject(lambda r:r['samples'][0].update(end_ns=r['samples'][0]['begin_ns']-1))
    def test_changed_final_receipt(self):self.reject(lambda r:r['final'].update(updates=r['final']['updates']+1))

if __name__=='__main__':
    paths=[Path(p) for p in sys.argv[1:] if p!='-v'];sys.argv=[sys.argv[0],'-v']
    RAW=[json.loads(p.read_text()) for p in paths]
    if {r['mode'] for r in RAW}!={'live','freeze-age','ignore-expiry','peer-exit','pending-disable','wrong-peer'}:raise ValueError('original six native clock observations required')
    unittest.main()
