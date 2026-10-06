"""Adversarial checks using original private native controller/pixel observations."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'build-support'))
from record_gnome_controller_recovery import judge
ORIGINALS={}


class ControllerEvidence(unittest.TestCase):
    def reject(self,change,mode='live'):
        raw,composition=copy.deepcopy(ORIGINALS[mode]);change(raw)
        try: result=judge(raw,composition)
        except (ValueError,AssertionError,KeyError,IndexError,TypeError): return
        self.assertNotEqual(result['outcome'],'pass')
    def test_originals(self):
        for mode,(raw,composition) in ORIGINALS.items():
            self.assertEqual(judge(raw,composition),raw['evaluation'])
            self.assertEqual(raw['evaluation']['outcome'],'fail' if mode=='no-reattach' else 'pass')
    def test_wrong_session(self):self.reject(lambda r:r['identities']['new_shell'].update(session=0))
    def test_wrong_parent(self):self.reject(lambda r:r['identities']['new_shell'].update(parent=0))
    def test_reused_lifetime(self):self.reject(lambda r:r['identities']['new_shell'].update(start_ticks=r['identities']['old_shell']['start_ticks']))
    def test_missing_exit(self):self.reject(lambda r:r['old_shell_exit'].update(pidfd_exit=False))
    def test_wrong_fault(self):self.reject(lambda r:r['fault'].update(pid=r['identities']['source']['pid']))
    def test_dead_source(self):self.reject(lambda r:r['final_live'].update(source=False))
    def test_dead_controller(self):self.reject(lambda r:r['final_live'].update(controller=False))
    def test_old_icons(self):self.reject(lambda r:r.update(old_icon_exited=False))
    def test_wrong_bus(self):self.reject(lambda r:r['native_ready'].update(bus_pid=0))
    def test_forged_resource(self):self.reject(lambda r:r['native_ready']['manager'].update(pid_origin='property'))
    def test_observer_started(self):self.reject(lambda r:r['calls'].append(dict(method='Start',begin_ns=r['fault']['end_ns'])))
    def test_query_drove_pixels(self):self.reject(lambda r:r['calls'].append(dict(method='GetState',begin_ns=r['post'][0]['begin_ns'])))
    def test_capture_gap(self):self.reject(lambda r:r['outage'][1].update(begin_ns=r['outage'][0]['end_ns']+200_000_000))
    def test_slow_capture(self):self.reject(lambda r:r['post'][0].update(end_ns=r['post'][0]['begin_ns']+100_000_000))
    def test_short_capture(self):self.reject(lambda r:r.update(post=r['post'][:5]))
    def test_replayed_pixels(self):self.reject(lambda r:[s.update(pixels=r['baseline'][-1]['pixels']) for s in r['post']])
    def test_epoch_replaced(self):
        def change(r):
            m=json.loads(r['source'][-1]['payload']);m['body']['snapshot']['producer_epoch']='forged';r['source'][-1]['payload']=json.dumps(m)
        self.reject(change)
    def test_measurement_rebased(self):
        def change(r):
            row=next(row for row in r['delivery'] if json.loads(row['payload'])['type']=='snapshot')
            m=json.loads(row['payload']);m['body']['snapshot']['observations'][0]['measured_at']['nanoseconds']=str(r['upper_ns']+1);row['payload']=json.dumps(m)
        self.reject(change)
    def test_collection_paused(self):self.reject(lambda r:r.update(source=r['source'][:2]))
    def test_revocation_erased(self):self.reject(lambda r:r.update(controller=[e for e in r['controller'] if e['event']!='consumer_policy']),'revoke')
    def test_post_revocation_delivery(self):
        def change(r):
            revision=next(e for e in r['controller'] if e['event']=='consumer_policy');r['delivery'][-1]['observed_ms']=revision['observed_ms']+1
        self.reject(change,'revoke')


if __name__=='__main__':
    for name in sys.argv[1:]:
        report=json.loads(Path(name).read_text());raw=json.loads(Path(report['network_private_artifacts']['network-controller-recovery.private.json']['path']).read_text())
        ORIGINALS[raw['mode']]=(raw,report['observation']['composition'])
    if set(ORIGINALS)!={'live','no-reattach','revoke'}:raise ValueError('three original native reports required')
    sys.argv=[sys.argv[0],'-v'];unittest.main()
