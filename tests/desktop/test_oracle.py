"""Fixed marker/time oracles; no native painter implementation is imported."""
import base64
import copy
import json
from pathlib import Path
import unittest
import zlib
from oracle import decode, evaluate, pack_frame, unpack_frame, read_trace

COLORS = {'B': (16,96,224), 'O': (240,160,16), 'V': (160,32,192), '0': (32,32,32), '1': (224,224,224)}
GOLDEN = json.loads((Path(__file__).parent/'fixtures/marker-golden.json').read_text(encoding='utf-8'))

def pixels(generation):
    rows = next(row['cells'] for row in GOLDEN['vectors'] if row['generation'] == str(generation))
    return bytes(channel for row in rows for _ in range(8) for cell in row for _ in range(8) for channel in COLORS[cell])

def trace():
    return {'version':'0.1.0', 'start_us':0, 'end_us':2000000,
            'stimuli':[{'at_us':0,'generation':1},{'at_us':500000,'generation':2},{'at_us':1200000,'generation':3}],
            'frames':[pack_frame(pixels(1 if n < 5 else (2 if n < 12 else 3)),n*100000,n*100000+1000) for n in range(20)]}

class OracleTests(unittest.TestCase):
    def test_literal_golden_vectors(self):
        for vector in GOLDEN['vectors']:
            self.assertEqual(decode(pixels(int(vector['generation']))),int(vector['generation']))
    def test_every_sample_matters(self):
        data=bytearray(pixels(1));data[(2*128+2)*3]=0
        self.assertIsNone(decode(bytes(data)))
    def test_exact_color_tolerance(self):
        data=bytearray(pixels(1));position=(2*128+2)*3
        data[position]+=8;self.assertEqual(decode(bytes(data)),1)
        data[position]+=1;self.assertIsNone(decode(bytes(data)))
    def test_shape_crc_padding_orientation(self):
        self.assertIsNone(decode(pixels(1)[:-1]))
        self.assertIsNone(decode(pixels(1)+b'\0'))
        for row,column in [(1,1),(10,14),(11,0)]:
            data=bytearray(pixels(1))
            for y in range(row*8,row*8+8):
                for x in range(column*8,column*8+8):
                    at=(y*128+x)*3;data[at:at+3]=bytes((224,224,224))
            self.assertIsNone(decode(bytes(data)))
    def test_live(self):
        result=evaluate(trace());self.assertEqual(result['outcome'],'pass');self.assertEqual(result['observed_generations'],['1','2','3'])
    def test_intervening_disappearance_fails(self):
        t=trace();t['frames'][8]=pack_frame(bytes(36864),800000,801000)
        self.assertIn('marker.absent_or_invalid',evaluate(t)['failures'])
    def test_freeze_fails_despite_valid_marker(self):
        t=trace();t['frames']=[pack_frame(pixels(1),f['start_us'],f['end_us']) for f in t['frames']]
        self.assertIn('generation.deadline',evaluate(t)['failures'])
    def test_presentation_deadline_equality(self):
        t=trace();t['frames'][5]=pack_frame(pixels(1),500000,501000);t['frames'][6]=pack_frame(pixels(1),600000,601000)
        self.assertEqual(evaluate(t)['outcome'],'pass')
        t['frames'][7]=pack_frame(pixels(1),700000,701000)
        self.assertEqual(evaluate(t)['outcome'],'fail')
    def test_unissued_and_regressed_generation(self):
        t=trace();t['frames'][3]=pack_frame(pixels(3),300000,301000)
        self.assertIn('generation.unissued',evaluate(t)['failures'])
        t=trace();t['frames'][6]=pack_frame(pixels(1),600000,601000)
        # Frame 5 already showed 2; old content cannot regress even inside the update budget.
        self.assertIn('generation.regressed',evaluate(t)['failures'])
    def test_gap_inconclusive_definite_failure_wins(self):
        t=trace();del t['frames'][7:11]
        self.assertEqual(evaluate(t)['outcome'],'inconclusive')
        t['frames'][3]=pack_frame(bytes(36864),300000,301000)
        self.assertEqual(evaluate(t)['outcome'],'fail')
    def test_coverage_and_capture_exact_bounds(self):
        t=trace();t['frames'][0]['end_us']=50000
        t['frames'][1]['start_us']=200000;t['frames'][1]['end_us']=201000
        del t['frames'][2]
        self.assertEqual(evaluate(t)['outcome'],'pass')
        t['frames'][1]['start_us']+=1
        self.assertIn('capture.gap',evaluate(t)['uncertainty'])
        t=trace();t['frames'][0]['end_us']=50001
        self.assertIn('capture.duration',evaluate(t)['uncertainty'])
    def test_candidate_claims_never_supply_pixels(self):
        for origin in ['candidate_buffer','window_flags','unknown']:
            t=trace()
            for frame in t['frames']:frame['origin']=origin
            self.assertEqual(evaluate(t)['outcome'],'inconclusive')
    def test_invalid_evidence(self):
        for mutate in [lambda t:t.update(start_us=True),lambda t:t['frames'][1].update(start_us=0),
                       lambda t:t['stimuli'][1].update(generation=1<<64),lambda t:t['stimuli'][1].update(generation=1),
                       lambda t:t.update(end_us=60000001),lambda t:t.update(frames=[]),lambda t:t['frames'][0].update(rgb_sha256='0'*64)]:
            t=trace();mutate(t)
            with self.assertRaises(ValueError):evaluate(t)
    def test_bounded_compression(self):
        f=pack_frame(pixels(1),0,1000)
        self.assertEqual(unpack_frame(f),pixels(1))
        for data in [zlib.compress(b'0'*40000),zlib.compress(pixels(1))+b'junk',b'invalid']:
            invalid=copy.deepcopy(f);invalid['rgb_zlib_base64']=base64.b64encode(data).decode('ascii')
            with self.assertRaises(ValueError):unpack_frame(invalid)
    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):read_trace(Path(__file__).parent/'fixtures/duplicate-trace.json')
    def test_missing_generation_and_final_coverage(self):
        t=trace();t['frames']=t['frames'][:8]
        result=evaluate(t)
        self.assertEqual(result['outcome'],'inconclusive')
        self.assertIn('capture.gap',result['uncertainty'])
        self.assertIn('generation.unobserved',result['uncertainty'])

if __name__=='__main__':unittest.main(verbosity=2)
