"""Adversarial checks against an actual live GNOME marker record."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build-support'))
from record_gnome_host import validate

BUILD = Path(sys.argv.pop(1)).resolve(strict=True)
VALUE = json.loads(Path(sys.argv.pop(1)).read_text())


class EvidenceChecks(unittest.TestCase):
    def reject(self, mutate):
        value = copy.deepcopy(VALUE)
        mutate(value)
        with self.assertRaises(ValueError):
            validate(value, BUILD)

    def test_native_record(self):
        self.assertEqual(validate(VALUE, BUILD)['candidate_outcome'], 'pass')

    def test_foreign_manager(self):
        self.reject(lambda r: r['observation']['manager'].update(pid=[1]))

    def test_unbound_resource(self):
        self.reject(lambda r: r['observation']['manager'].update(resource_base=0))

    def test_false_pixel_digest(self):
        self.reject(lambda r: r['observation']['marker']['trace']['frames'][0].update(rgb_sha256='0' * 64))

    def test_ineligible_capture(self):
        self.reject(lambda r: r['observation']['marker']['trace']['frames'][0].update(origin='candidate_screenshot'))

    def test_missing_generation(self):
        self.reject(lambda r: r['observation']['marker']['trace']['stimuli'].pop())

    def test_unconfirmed_cleanup(self):
        self.reject(lambda r: r['cleanup'][0].update(exit=None))

    def test_changed_source(self):
        self.reject(lambda r: r['source_inputs'].update({'tests/desktop/native_gnome_bootstrap.py': '0' * 64}))

    def test_changed_background(self):
        self.reject(lambda r: r['observation']['marker']['background_after'].update(sha256='0' * 64))


if __name__ == '__main__':
    unittest.main()
