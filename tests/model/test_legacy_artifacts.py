"""Reject compatibility overclaims using independent mutations of a built PE image."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'source/build'))
from check_legacy_artifacts import verify

DATA = Path(sys.argv.pop(1)).read_bytes()
PE, = struct.unpack_from('<I', DATA, 0x3c)
OPTIONAL = PE + 24


class ImportAudit(unittest.TestCase):
    def test_real_artifact(self):
        result = verify(DATA)
        self.assertEqual(result['os_version'], [5, 1])
        self.assertEqual(set(result['imports']), {'kernel32.dll'})

    def rejected_field(self, offset, format, value):
        data = bytearray(DATA)
        struct.pack_into(format, data, offset, value)
        with self.assertRaises(ValueError):
            verify(data)

    def test_wrong_architecture(self):
        self.rejected_field(PE+4, '<H', 0x8664)

    def test_newer_subsystem(self):
        self.rejected_field(OPTIONAL+48, '<H', 6)

    def test_newer_os_header(self):
        self.rejected_field(OPTIONAL+40, '<H', 6)

    def test_unclosed_delay_imports(self):
        self.rejected_field(OPTIONAL+96+13*8, '<I', 1)

    def test_invalid_rva(self):
        self.rejected_field(OPTIONAL+104, '<I', 0xfffffff0)

    def test_unclosed_sidecar(self):
        data = DATA.replace(b'KERNEL32.dll\0', b'VCRUNTIM.dll\0')
        self.assertNotEqual(data, DATA)
        with self.assertRaisesRegex(ValueError, 'declared experiment closure'):
            verify(data)

    def test_unclosed_function(self):
        data = DATA.replace(b'EncodePointer\0', b'ModernPointer\0')
        self.assertNotEqual(data, DATA)
        with self.assertRaisesRegex(ValueError, 'declared experiment closure'):
            verify(data)

    def test_truncation(self):
        with self.assertRaises(ValueError):
            verify(DATA[:1024])


if __name__ == '__main__':
    unittest.main()
