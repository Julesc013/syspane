"""Reject internally consistent false cache/pixel evidence, beyond file hashes."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'source/build'))
import record_gnome_network_cache as verifier
from gnome_network_cache import judge,templates,decode
from native_x11_host import rgb_record
from gnome_composition import FIXTURE

BUILD=Path(sys.argv.pop(1)).resolve(strict=True)
REPORTS=[json.loads(Path(sys.argv.pop(1)).read_text()) for _ in range(4)]
MODES={r['network_cache_control']:r for r in REPORTS}

class CacheEvidence(unittest.TestCase):
    def reject(self,mutate,mode='live'):
        value=copy.deepcopy(MODES[mode]);result=value['observation']['network_cache']
        raw=json.loads(Path(result['private']['path']).read_text());mutate(value,raw)
        try:
            raw['evaluation']=judge(raw);result['evaluation']=raw['evaluation'];value['outcome']=raw['evaluation']['outcome']
        except (ValueError,KeyError):pass
        original=verifier.private_file
        def load(record,workspace,name,maximum):
            if name=='network-cache.private.json':return json.dumps(raw).encode()
            if name=='network-relay.private.jsonl':
                lines=original(record,workspace,name,maximum).splitlines()
                return b'\n'.join([lines[0],*[json.dumps(c['native']).encode() for c in raw['calls']]])+b'\n'
            return original(record,workspace,name,maximum)
        with patch.object(verifier,'private_file',side_effect=load):
            with self.assertRaises((ValueError,AssertionError,KeyError)):verifier.validate(value,BUILD)

    def test_four_native_modes(self):
        for value in REPORTS:
            with self.subTest(control=value['network_cache_control']):self.assertEqual(verifier.validate(value,BUILD)['outcome'],'pass')
    def test_private_digest(self):
        value=copy.deepcopy(MODES['live']);value['observation']['network_cache']['private']['sha256']='0'*64
        with self.assertRaises(ValueError):verifier.validate(value,BUILD)
    def test_private_path(self):
        value=copy.deepcopy(MODES['live']);value['observation']['network_cache']['private']['path']=str(BUILD/'outside.json')
        with self.assertRaises(ValueError):verifier.validate(value,BUILD)
    def test_extra_private_payload(self):self.reject(lambda v,r:v['network_private_artifacts'].update(extra={}))
    def test_native_pid(self):self.reject(lambda v,r:r['relay'].update(pid=r['relay']['pid']+1))
    def test_native_exit(self):self.reject(lambda v,r:next(c for c in v['cleanup'] if c['process']=='network-relay').update(exit=0),mode='owner-loss')
    def test_exit_timeout_not_proof(self):self.reject(lambda v,r:r['exit'].update(observer='timeout'),mode='owner-loss')
    def test_stale_callback_cache(self):self.reject(lambda v,r:r['closed_state'].update(entries=1),mode='owner-loss')
    def test_unauthorized_peer(self):self.reject(lambda v,r:r['unauthorized'].__setitem__(1,'cleared'))
    def test_native_receipt(self):self.reject(lambda v,r:r['calls'][0]['native'].update(owner=':999.999'))
    def test_missing_replay(self):self.reject(lambda v,r:r['calls'].pop(next(i for i,c in enumerate(r['calls']) if c['method']=='Frame' and c['native']['reply']=='restricted' and c['args'][0]=='7')))
    def test_conflicting_grant(self):self.reject(lambda v,r:next(c for c in r['calls'] if c['method']=='Policy' and c['args']==['8',True])['native'].update(reply='cleared'))
    def test_capacity_prefix(self):self.reject(lambda v,r:r['capacity_state'].update(entries=1,labels=1))
    def test_unbound_erasure_ack(self):self.reject(lambda v,r:r['erasure'][0].update(start_ns=r['erasure'][0]['start_ns']-50_000_000))
    def test_capture_gap(self):self.reject(lambda v,r:r['erasure'][0]['samples'].__delitem__(slice(1,5)))
    def test_missing_regrant_gap(self):self.reject(lambda v,r:r['erasure'].pop(1))
    def test_residual_pixels(self):
        self.reject(lambda v,r:r['erasure'][0]['samples'][-1].update(pixels=r['displayed'][0]['pixels']))
    def test_calibration_missing_digit(self):self.reject(lambda v,r:r['calibration'].update(pixels=rgb_record(bytes((20,30,40))*448*150)))
    def test_value_oracle_redefinition(self):
        def mutate(v,r):
            values=r['displayed'][0]['frame']['values']
            values[0]='1' if values[0]=='0' else '0'
        self.reject(mutate)
    def test_changed_full_epoch(self):self.reject(lambda v,r:r['displayed'][1]['frame'].update(epoch=r['displayed'][0]['frame']['epoch']))
    def test_collector_artifact(self):self.reject(lambda v,r:r['collectors'][0].update(artifact_sha256='0'*64))
    def test_collector_comparison_count(self):self.reject(lambda v,r:r['collectors'][0].update(fields_compared=0))
    def test_disable_residue(self):self.reject(lambda v,r:r.update(post_clear=r['displayed'][0]['pixels']))
    def test_wrong_value_control_cannot_pass(self):
        def conceal(v,r):
            table=templates(r['calibration']['pixels'])
            for row in r['displayed']:row['frame']['values']=decode(row['pixels'],table)
        self.reject(conceal,mode='wrong-value')
    def test_clear_control_cannot_pass(self):
        def conceal(v,r):
            blank=rgb_record(bytes(FIXTURE['background_rgb'])*448*150)
            for interval in r['erasure']:
                for sample in interval['samples']:sample['pixels']=blank
        self.reject(conceal,mode='ignore-clear')

if __name__=='__main__':unittest.main()
