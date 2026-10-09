"""Independent transcript invariants for the native paint experiment."""
import unittest
from native_editor_paint_trace import decode

GOOD=b'paint-trace-begin 12 1 2 0\npaint-trace 0 2 1 2 2 123 456\npaint-trace-end 12 1 2\n'


class DecodeTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(decode(b'native diagnostic\n'+GOOD),[dict(pid=12,total=2,stacks=[dict(calls=2,first=1,last=2,offsets=[0x123,0x456])])])

    def test_empty_helper(self):
        self.assertEqual(decode(b'paint-trace-begin 13 0 0 0\npaint-trace-end 13 0 0\n')[0]['stacks'],[])

    def test_bad(self):
        bad=[b'',GOOD[:-1],GOOD.split(b'paint-trace-end')[0],GOOD+GOOD,
             GOOD.replace(b'1 2 0\n',b'1 2 1\n'),
             GOOD.replace(b'begin 12 1',b'begin 12 129'),
             GOOD.replace(b'0 2 1 2 2',b'0 3 1 2 2'),
             GOOD.replace(b'0 2 1 2 2',b'0 2 3 2 2'),
             GOOD.replace(b'0 2 1 2 2',b'0 2 1 2 33'),
             GOOD.replace(b'123 456',b'0 456'),
             GOOD.replace(b'123 456',b'123'),
             GOOD.replace(b'end 12',b'end 13'),
             GOOD.replace(b'trace 0',b'trace 1'),
             GOOD.replace(b'begin 12',b'begin -1'),
             b'x'*(2*1024*1024+1)]
        for raw in bad:
            with self.subTest(raw=raw[:80]),self.assertRaises((AssertionError,ValueError,IndexError)):
                decode(raw)


if __name__=='__main__':unittest.main()
