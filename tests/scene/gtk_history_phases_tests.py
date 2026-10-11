from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gtk_history_phases import decode,summarize

class Phases(unittest.TestCase):
    raw=b'history-phases-begin 1 1\nhistory-phase 0 1 1 2 1 100 34 10 60 2 8 5 40 30 7\nhistory-phases-end 1\n'
    timing=[dict(work_us=100,delay_us=34)]
    def bad(self,raw,timings=None):
        with self.assertRaises(ValueError):decode(raw,self.timing if timings is None else timings)
    def field(self,index,value):
        lines=self.raw.splitlines();fields=lines[1].split();fields[index+1]=str(value).encode();lines[1]=b' '.join(fields);return b'\n'.join(lines)+b'\n'
    def test_literal_nested_and_residual(self):
        rows=decode(self.raw,self.timing);self.assertEqual((rows[0]['residual_us'],rows[0]['delivery_residual_us'],rows[0]['adoption_other_us']),(20,15,10))
        report=summarize(rows,99);self.assertEqual(len(report['slow']),1);self.assertEqual(report['maxima']['presentation_us'],30)
    def test_completion_version_and_counts(self):
        for raw in (self.raw[:-1],self.raw.replace(b'begin 1',b'begin 2'),self.raw.replace(b'end 1',b'end 2'),self.raw.replace(b'begin 1 1',b'begin 1 0'),self.raw.replace(b'begin 1 1',b'begin 1 32769'),self.raw.replace(b'history-phase 0',b'junk 0')):self.bad(raw)
        self.bad(self.raw,[]);self.bad(self.raw,self.timing*2)
    def test_identity_integer_and_capacity(self):
        for index,value in ((0,1),(1,6),(2,4100),(4,4097),(5,-1),(5,2**64),(14,1),(14,8)):self.bad(self.field(index,value))
    def test_original_timing_equality(self):
        self.bad(self.raw,[dict(work_us=101,delay_us=34)]);self.bad(self.raw,[dict(work_us=100,delay_us=35)])
    def test_accounting_and_unobserved_phases(self):
        for index,value in ((6,50),(11,30),(13,41),(14,3),(14,0)):self.bad(self.field(index,value))
    def test_fixture_publication_state(self):
        self.bad(self.field(1,0));self.bad(self.field(3,3))
    def test_full_storage_bound(self):self.bad(self.raw+b' '* (6*1024*1024))

if __name__=='__main__':unittest.main()
