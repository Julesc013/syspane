"""Independently recompute native GNOME reveal and temporal negative controls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest, rgb
from record_gnome_composition import validate as validate_composition
from gnome_reveal import FIXTURE, FIXTURE_PATH, judge


def validate(value, build):
    prerequisite = validate_composition(value, build, family='GNOME-REVEAL-01', outer_outcome=False)
    result = value['observation']['reveal']
    control = result['control']
    if prerequisite['control'] != 'live' or control not in {'live', 'no-action', 'transient-blank'}:
        raise ValueError('live composition and named reveal control required')
    if value['reveal_control'] != control or value['environment']['explicit']['SYSPANE_GNOME_REVEAL'] != control:
        raise ValueError('reveal control identity')
    if result['version'] != FIXTURE['version'] or result['fixture_sha256'] != digest(FIXTURE_PATH.read_bytes()):
        raise ValueError('reveal fixture identity')
    owner = result['foreground']
    script = str(ROOT / 'tests/desktop/gnome_foreground.py')
    commands = [r for r in value['commands'] if r['command'] == ['/usr/bin/python3', script]]
    if len(commands) != 1 or commands[0]['pid'] != owner['pid'] or owner['pid_origin'] != 'XResQueryClientIds':
        raise ValueError('retained foreground process identity')
    if owner['arguments'] != ['/usr/bin/python3', script] or owner['process_group'] != owner['pid'] or owner['session'] != owner['pid'] or owner['start_ticks'] <= 0:
        raise ValueError('foreground lifetime binding')
    if owner['window'] & ~owner['resource_mask'] != owner['resource_base'] or owner['geometry'] != FIXTURE['window'] or owner['type'] != [owner['normal_type_atom']]:
        raise ValueError('foreground normal window identity')
    if owner['executable'] not in value['foreground_mapped_files']:
        raise ValueError('foreground mapped runtime absent')
    cleanup = [r for r in value['cleanup'] if r['process'] == 'foreground']
    if len(cleanup) != 1 or cleanup[0]['pid'] != owner['pid'] or cleanup[0]['exit'] != 0 or cleanup[0]['members_after_stop']:
        raise ValueError('foreground exit unconfirmed')
    if owner['pid'] not in [r['pid'] for r in cleanup[0]['members_before_stop'] if r['state'] != 'Z']:
        raise ValueError('foreground not retained to cleanup')
    if result['binding_before'] != FIXTURE['binding'] or result['binding_after'] != FIXTURE['binding']:
        raise ValueError('Show Desktop binding differs')
    composition = value['observation']['composition']
    if result['background_settings_before'] != composition['background_settings_after'] or result['background_settings_after'] != result['background_settings_before']:
        raise ValueError('reveal background settings differ')
    if result['started_monotonic_ns'] < composition['marker']['started_monotonic_ns'] + 2400000000:
        raise ValueError('reveal precedes composition prerequisite')
    for row in result['samples']:
        clients = [r for r in row['native']['clients'] if r['window'] == owner['window']]
        if len(clients) != 1 or clients[0]['type'] != owner['type'] or clients[0]['pid'] != [owner['pid']]:
            raise ValueError('normal foreground client changed during trace')
    actual = judge(result, composition)
    if actual != result['evaluation'] or value['outcome'] != actual['outcome']:
        raise ValueError('reveal claim differs from raw evidence')
    dimensions = (actual['marker']['outcome'], actual['composition']['icons'], actual['composition']['rectangle'], actual['background'], actual['visual_reveal'])
    expected = {'live': ('pass', 'pass', 'pass', 'pass', 'pass'),
                'no-action': ('pass', 'pass', 'pass', 'pass', 'fail'),
                'transient-blank': ('fail', 'pass', 'fail', 'pass', 'pass')}[control]
    if dimensions != expected:
        raise ValueError('native control outcomes differ: ' + str(dimensions))
    if control == 'transient-blank':
        if 'marker.absent_or_invalid' not in actual['marker']['failures'] or not actual['composition']['samples'][-1]['rectangle']:
            raise ValueError('temporary disappearance and later restoration not observed')
    rgb(result['final_desktop'], 800*600*3)
    journal = value['reveal_journal']
    path = Path(journal['path']).resolve(strict=True)
    if path != Path(value['workspace']) / 'reveal.jsonl':
        raise ValueError('owned reveal journal required')
    raw = path.read_bytes()
    if len(raw) > 8*1024**2 or len(raw) != journal['bytes'] or digest(raw) != journal['sha256']:
        raise ValueError('reveal journal identity')
    rows = [json.loads(line) for line in raw.splitlines()]
    if len(rows) > 180 or any(r['kind'] == 'error' for r in rows):
        raise ValueError('reveal journal incomplete')
    selected = lambda kind: [r['value'] for r in rows if r['kind'] == kind]
    if selected('action') != result['actions'] or selected('fault') != result['faults'] or selected('generation') != result['trace']['stimuli'][1:]:
        raise ValueError('stimuli differ from preserved journal')
    if selected('sample') != [{'marker': f, 'observation': o} for f, o in zip(result['trace']['frames'], result['samples'])]:
        raise ValueError('reveal frames differ from preserved journal')
    if selected('completed') != [{'evaluation': actual, 'binding_after': result['binding_after'], 'background_settings_after': result['background_settings_after']}]:
        raise ValueError('reveal completion differs from journal')
    prepared = selected('prepared')
    if len(prepared) != 1 or prepared[0]['foreground'] != owner or prepared[0]['native']['active_window'] != [owner['window']] or prepared[0]['native']['showing_desktop'] != [0]:
        raise ValueError('foreground preparation differs')
    if rgb(prepared[0]['pixels'], 20*20*3) != bytes(FIXTURE['foreground_rgb'])*(20*20):
        raise ValueError('foreground preparation lacks exact native pixels')
    return {'control': control, 'outcome': actual['outcome'], 'marker': dimensions[0], 'icons': dimensions[1],
            'rectangle': dimensions[2], 'background': dimensions[3], 'visual_reveal': dimensions[4],
            'focus': actual['focus'], 'reveal': actual['reveal'],
            'marker_failures': actual['marker']['failures'], 'samples': len(result['samples']),
            'max_gap_us': actual['composition']['max_gap_us'], 'max_capture_us': actual['composition']['max_capture_us'],
            'transition_latency_us': actual['transition_latency_us'], 'cleanup': 'confirmed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--reports', required=True, nargs=3, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    results, identities = [], []
    for path in args.reports:
        path = path.resolve(strict=True)
        if path.parent != build / 'native-evidence' or path.stat().st_size > 16*1024**2:
            raise ValueError('owned bounded report required')
        raw = path.read_bytes()
        value = json.loads(raw)
        results.append(validate(value, build))
        identities.append({'path': str(path), 'sha256': digest(raw), 'source_base': value['source_base'], 'source_inputs': value['source_inputs']})
    if sorted(r['control'] for r in results) != ['live', 'no-action', 'transient-blank'] or any(r['source_inputs'] != identities[0]['source_inputs'] for r in identities):
        raise ValueError('complete controls with identical source required')
    for name, expected in identities[0]['source_inputs'].items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError('current source differs: ' + name)
    output = args.output.resolve()
    if output.parent != build / 'native-evidence':
        raise ValueError('owned output required')
    record = {'version': '0.1.0', 'recorded_at': datetime.now(timezone.utc).isoformat(), 'outcome': 'pass',
              'scope': 'Pinned GNOME/DING configured Super+D with one normal owned window; temporal negative controls',
              'reports': identities, 'results': results,
              'recorder_inputs': {p: digest((ROOT / p).read_bytes()) for p in ['build-support/record_gnome_reveal.py', 'build-support/record_gnome_composition.py', 'build-support/record_gnome_host.py', 'tests/desktop/gnome_reveal.py', 'tests/desktop/gnome_composition.py', 'tests/desktop/oracle.py']},
              'not_run': ['other reveal actions', 'icon input', 'taskbar/task-switcher absence', 'broader focus behavior', 'image wallpaper/policy', 'shell/icon-manager recovery', 'Wayland', 'full product qualification']}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
