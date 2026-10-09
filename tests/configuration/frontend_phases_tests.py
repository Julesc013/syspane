import unittest
from frontend_phases import decode


class PhaseTests(unittest.TestCase):
    valid = b'GTK diagnostic\nphase-begin 123 3\nphase 1 1 3 1\nphase 1 6 40 1\nphase 1 5 60 1\nphase-end 123 3 0\n'

    def test_nested(self):
        block = decode(self.valid)[0]
        self.assertEqual([r['phase'] for r in block['rows']], ['take', 'editor', 'populate'])
        self.assertEqual(block['rows'][-1]['microseconds'], 60)

    def test_exception_and_refusal(self):
        self.assertFalse(decode(b'phase-begin 1 1\nphase 1 3 20 0\nphase-end 1 1 2\n')[0]['rows'][0]['completed'])
        self.assertEqual(decode(b'phase-begin 1 0\nphase-end 1 0 2\n')[0]['rows'], [])

    def test_multiple_lifetimes(self):
        self.assertEqual(len(decode(self.valid + self.valid.replace(b'123', b'124'))), 2)

    def test_invalid(self):
        bad = [b'', self.valid + self.valid, self.valid[:-1], self.valid[:-20], self.valid.replace(b'123 3 0', b'124 3 0'),
               self.valid.replace(b'123 3\n', b'123 8193\n'), self.valid.replace(b'1 6 40', b'1 12 40'),
               self.valid.replace(b'1 6 40', b'0 6 40'), self.valid.replace(b'1 6 40', b'01 6 40'),
               self.valid.replace(b'1 6 40', b'1 1 40'), self.valid.replace(b'1 6 40 1', b'1 6 40 2'),
               self.valid.replace(b'1 6 40', b'2 6 40'), self.valid.replace(b'40 1', b'18446744073709551616 1'),
               self.valid.replace(b'123 3 0', b'123 3 1'), b'x' * (2 * 1024 * 1024 + 1),
               b'phase-begin 1 0\nphase-end 1 0 0\n', self.valid.replace(b'phase-end', b'other-end')]
        for raw in bad:
            with self.subTest(raw=raw[:80]), self.assertRaises(ValueError):
                decode(raw)


if __name__ == '__main__':
    unittest.main()
