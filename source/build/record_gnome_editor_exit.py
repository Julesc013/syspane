"""Recompute editor recovery from original native/private desktop evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/desktop'))
from gnome_editor_exit import judge, MODES, require, clipboard_names

EDITOR_BUILD_RECORD = 'out/evidence/w-25-gnome-editor-exit-native-build.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def lifetimes(value, build):
    workspace = Path(value['workspace']); mode = value['controller_recovery_control']
    require(value['family'] == 'GNOME-CONTROLLER-RECOVERY-01' and mode in MODES, 'explicit editor family control')
    names = {'network-controller-recovery.private.json': 16*1024**2, 'network-controller-source.private.jsonl': 4*1024**2,
             'network-controller-delivery.private.jsonl': 4*1024**2, 'network-controller-bracket.private.json': 1024**2}
    require(set(value['network_private_artifacts']) == set(names), 'original private evidence coverage')
    contents = {}
    for name, maximum in names.items():
        entry = value['network_private_artifacts'][name]; path = Path(entry['path'])
        require(path == workspace/name and path.resolve(strict=True) == path and not path.is_symlink() and
                path.stat().st_mode & 0o777 == 0o600, 'original private evidence ownership')
        data = path.read_bytes()
        require(len(data) == entry['bytes'] <= maximum and sha(path) == entry['sha256'], 'original private evidence identity')
        contents[name] = data
    raw = json.loads(contents['network-controller-recovery.private.json'])
    require(not raw.get('error') and raw['mode'] == mode, 'complete native observer')
    for key in ('before_input', 'blocked_input', 'negative_input' if mode == 'editor-no-exit' else 'after_input'):
        copied = raw[key]
        require(clipboard_names(copied, workspace) == copied['names'], 'original native clipboard meaning')
        if copied['owner_changed']:
            binding = copied['owner_binding']
            require(binding['pid'] == raw['identities']['old_shell']['pid'] and
                    copied['owner'] & ~binding['resource_mask'] == binding['resource_base'], 'native clipboard producer identity')
    for key in ('source', 'delivery'):
        original = [json.loads(r) for r in contents['network-controller-'+key+'.private.jsonl'].splitlines()]
        require(original[:len(raw[key])] == raw[key], 'original measurement prefix')
    require(raw['bracket'] == json.loads(contents['network-controller-bracket.private.json']), 'original native brackets')
    events = {}
    for key, name in [('controller', 'controller.log'), ('exit_owner_events', 'editor-exit.log')]:
        path = workspace/name; data = path.read_bytes()
        require(len(data) <= 1024**2 and data.decode() == value['logs'][name], 'original public native log')
        events[key] = [json.loads(line) for line in data.splitlines()]
        require(events[key][:len(raw[key])] == raw[key], 'native event prefix')
    controller = raw['identities']['controller']['pid']; exit_owner = raw['identities']['exit_owner']['pid']
    environment = value['environment']['explicit']
    require(value['controller_pid'] == controller and environment['SYSPANE_GNOME_CONTROLLER_PID'] == str(controller) and
            environment['SYSPANE_GNOME_CONTROLLER_CONTROL'] == mode and environment['SYSPANE_GNOME_CONTROLLER_RENDER'] == '1' and
            environment['SYSPANE_GNOME_RENDER_WATCH'] == 'live', 'native controller/render composition')
    expected = [str(build/'SysPane.CollectorProbe'), 'desktop-watch', environment['SYSPANE_GNOME_NETWORK_ROOT'], 'allow', str(build/'gnome-lab/sysroot/usr/bin/gnome-shell')]
    require([r['command'] for r in value['commands'] if r.get('pid') == controller] == [expected], 'native controller launch')
    editor_command = [str(build/'SysPane.EditorExitProbe'), '--owned-gnome-lab']
    require([r['command'] for r in value['commands'] if r.get('pid') == exit_owner] == [editor_command], 'native independent exit owner launch')
    require(raw['identities']['exit_owner']['arguments'] == editor_command and
            raw['identities']['editor']['arguments'] == ['/proc/self/exe', '--child-maximized', str(exit_owner)] and
            raw['identities']['editor']['executable'] == str(build/'SysPane.EditorExitProbe'), 'native editor executable role')
    compiled = json.loads((ROOT/EDITOR_BUILD_RECORD).read_text())
    require(sha(ROOT/EDITOR_BUILD_RECORD) == value['editor_build_record_sha256'] and
            sha(build/'SysPane.EditorExitProbe') == compiled['artifacts']['SysPane.EditorExitProbe']['sha256'], 'tested editor artifact identity')
    cleanup = [r for r in value['cleanup'] if r['process'] == 'editor-exit']
    require(len(cleanup) == 1 and cleanup[0]['pid'] == exit_owner and not cleanup[0]['members_after_stop'] and
            cleanup[0]['exit'] == (-9 if mode in ('editor-owner-loss', 'editor-no-exit') else 0), 'native editor owner cleanup')
    stopped = [r for r in events['controller'] if r['event'] == 'stopped']
    require(len(stopped) == 2 and {r['pid'] for r in stopped} == {raw['identities']['source']['pid'], raw['identities']['old_shell']['pid']} and
            all(r['os_confirmed'] and r['code'] == 0 and not r['signaled'] and not r['forced'] for r in stopped), 'graceful retained desktop cleanup')
    complete = [r for r in events['controller'] if r['event'] == 'complete']
    require(len(complete) == 1 and complete[0]['requested'] is True, 'controller shutdown acknowledgement')
    from record_gnome_controller_recovery import BUILD_RECORD
    native = json.loads((ROOT/BUILD_RECORD).read_text())
    require(sha(ROOT/BUILD_RECORD) == value['network_build_record_sha256'], 'native measured build identity')
    for name in ('SysPane.CollectorProbe', 'libsyspane_gjs_clock.so', 'SysPaneClock-0.1.typelib'):
        require(sha(build/name) == native['artifacts'][name]['sha256'], 'native measured artifact')
    for name in ('libsyspane_gjs_clock.so', 'SysPaneClock-0.1.typelib'):
        require(value['mapped_files'][str(build/name)] == native['artifacts'][name]['sha256'], 'loaded measured adapter')
    result = judge(raw, value['observation']['composition'])
    require(result == raw['evaluation'] == value['observation']['controller_recovery']['evaluation'] and
            result['outcome'] == value['outcome'] == ('fail' if mode == 'editor-no-exit' else 'pass'), 'recomputed fixed editor outcome')
    return raw, result


def validate(value, build):
    from record_gnome_composition import validate as composition
    raw, result = lifetimes(value, build)
    composition(value, build, family='GNOME-CONTROLLER-RECOVERY-01', outer_outcome=False)
    return {'mode': raw['mode'], **result, 'scope': 'Independent transient editor lifetime on the owned measured GNOME desktop; no scene transactions or installed recovery qualification.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('reports', type=Path, nargs='+')
    args = parser.parse_args(); values = [json.loads(p.read_text()) for p in args.reports]
    require(len(values) == len(MODES) and {v['controller_recovery_control'] for v in values} == set(MODES), 'five editor controls required')
    require(all(v['source_inputs'] == values[0]['source_inputs'] for v in values), 'same source matrix')
    for name, digest in values[0]['source_inputs'].items(): require(sha(ROOT/name) == digest, 'current experiment source differs')
    result = {'outcome': 'pass', 'source_inputs': values[0]['source_inputs'],
              'results': [validate(v, args.build_dir.resolve(strict=True)) for v in values],
              'reports': [{'path': str(p), 'sha256': sha(p)} for p in args.reports]}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('Five independent editor desktop controls revalidated.')
