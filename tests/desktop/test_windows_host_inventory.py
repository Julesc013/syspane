"""Fixed structural outcomes; none of these fixtures qualifies a native host."""
import copy
import unittest
from windows_host_inventory import classify


BASE = {'session': 2, 'owner': {'pid': 80, 'session': 2, 'image_matches_system_explorer': True, 'alive_after': True},
        'observations': [{'shell': 100, 'windows': [
            {'hwnd': 100, 'class': 'Progman', 'pid': 80, 'thread': 81, 'parent': None},
            {'hwnd': 200, 'class': 'WorkerW', 'pid': 80, 'thread': 81, 'parent': None},
            {'hwnd': 300, 'class': 'SHELLDLL_DefView', 'pid': 80, 'thread': 81, 'parent': 100},
            {'hwnd': 400, 'class': 'SysListView32', 'pid': 80, 'thread': 81, 'parent': 300}]}]}
BASE['observations'].append(copy.deepcopy(BASE['observations'][0]))


class Inventory(unittest.TestCase):
    def value(self):
        return copy.deepcopy(BASE)

    def test_literal_hierarchy(self):
        self.assertEqual(classify(BASE), {'status': 'observed', 'icon_root': 100, 'worker_roots': [200]})

    def test_absent(self):
        value = self.value()
        value.update(owner=None, observations=[{'shell': 0, 'windows': []}] * 2)
        self.assertEqual(classify(value)['status'], 'absent')

    def test_owner_query_denied(self):
        value = self.value(); value['owner'] = None
        self.assertEqual(classify(value)['status'], 'owner_unverified')

    def test_same_name_other_image(self):
        value = self.value(); value['owner']['image_matches_system_explorer'] = False
        self.assertEqual(classify(value)['status'], 'owner_unverified')

    def test_foreign_session(self):
        value = self.value(); value['owner']['session'] = 3
        self.assertEqual(classify(value)['status'], 'owner_unverified')

    def test_owner_exited(self):
        value = self.value(); value['owner']['alive_after'] = False
        self.assertEqual(classify(value)['status'], 'owner_unverified')

    def test_changed_shell(self):
        value = self.value(); value['observations'][1]['shell'] = 500
        self.assertEqual(classify(value)['status'], 'changed')

    def test_changed_parent(self):
        value = self.value(); value['observations'][1]['windows'][-1]['parent'] = 200
        self.assertEqual(classify(value)['status'], 'changed')

    def test_duplicate_icon_hierarchy(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'].append({'hwnd': 500, 'class': 'SHELLDLL_DefView', 'pid': 80, 'thread': 81, 'parent': 200})
        self.assertEqual(classify(value)['status'], 'ambiguous')

    def test_missing_icons(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'].pop()
        self.assertEqual(classify(value)['status'], 'incomplete')

    def test_disconnected_icon_chain(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'][-1]['parent'] = 200
        self.assertEqual(classify(value)['status'], 'incomplete')

    def test_foreign_child_owner(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'][-1]['pid'] = 90
        self.assertEqual(classify(value)['status'], 'owner_unverified')

    def test_missing_shell_root(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'].pop(0)
        self.assertEqual(classify(value)['status'], 'changed')

    def test_duplicate_handle(self):
        value = self.value()
        for observation in value['observations']:
            observation['windows'][-1]['hwnd'] = 300
        with self.assertRaises(ValueError):
            classify(value)


if __name__ == '__main__':
    unittest.main()
