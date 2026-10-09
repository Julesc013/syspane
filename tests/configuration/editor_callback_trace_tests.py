"""Literal protocol and overlap/coverage expectations for the callback diagnostic."""
import unittest
from editor_callback_trace import decode,union_ns,correlate

GOOD=(b'callback-trace-begin 12 3 0\n'
      b'callback-trace 1 0 12 2 2 0 123 20 0 1 100 200 70\n'
      b'callback-trace 2 1 12 3 1 1 456 0 0 1 120 150 20\n'
      b'callback-trace 3 0 12 2 2 0 123 20 0 2 400 500 90\n'
      b'callback-trace-end 12 3\n')


class DecodeTests(unittest.TestCase):
    def test_valid(self):
        block=decode(b'GTK message\n'+GOOD)[0]
        self.assertEqual(block['pid'],12);self.assertEqual(len(block['rows']),3)
        self.assertEqual(block['rows'][1]['label'],'apply')
        self.assertEqual(block['rows'][1]['parent'],1)
        self.assertEqual(block['rows'][0]['offset'],0x123)
        self.assertEqual(decode(b'callback-trace-begin 13 0 0\ncallback-trace-end 13 0\n')[0]['rows'],[])

    def test_invalid(self):
        bad=[b'',GOOD[:-1],GOOD.split(b'callback-trace-end')[0],GOOD+GOOD,
             GOOD.replace(b'begin 12 3 0',b'begin 12 3 1'),
             GOOD.replace(b'begin 12 3',b'begin 12 32769'),
             GOOD.replace(b'end 12',b'end 13'),
             GOOD.replace(b'trace 2 1',b'trace 2 0'),
             GOOD.replace(b'trace 2 1',b'trace 2 2'),
             GOOD.replace(b'120 150 20',b'120 250 20'),
             GOOD.replace(b'120 150 20',b'90 150 20'),
             GOOD.replace(b'120 150 20',b'120 150 -1'),
             GOOD.replace(b'120 150 20',b'120 150 18446744073709551616'),
             GOOD.replace(b'0 2 400 500',b'0 3 400 500'),
             GOOD.replace(b'456 0 0',b'456 1 0'),
             GOOD.replace(b'1 1 456',b'1 19 456'),
             GOOD.replace(b'123',b'0'),b'x'*(16*1024*1024+1)]
        for raw in bad:
            with self.subTest(raw=raw[:90]),self.assertRaises((AssertionError,ValueError,IndexError)):
                decode(raw)

    def test_union_and_coverage(self):
        self.assertEqual(union_ns([(100,200),(120,150),(180,250),(300,310)]),160)
        block=decode(GOOD)[0];timings=[dict(pid=12,work_us=0,delay_us=0)]*2
        gaps=correlate(block,timings);self.assertEqual(gaps[0]['gap_ns'],200)
        self.assertEqual(gaps[0]['uncovered_ns'],200);self.assertEqual(gaps[0]['rows'],[])
        with self.assertRaises(AssertionError):correlate(block,timings[:1])
        with self.assertRaises(AssertionError):correlate(block,[dict(pid=13,work_us=0,delay_us=0)]*2)

    def test_independent_clock_readings(self):
        # Preserve cross-clock disagreement as evidence, not an invalid trace.
        rows=decode(GOOD.replace(b'120 150 20',b'120 150 31'))[0]['rows']
        self.assertEqual(rows[1]['cpu_ns'],31);self.assertEqual(rows[1]['cpu_over_wall_ns'],1)


if __name__=='__main__':unittest.main()
