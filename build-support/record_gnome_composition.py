"""Recompute DING composition from independently calibrated raw native pixels."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from record_gnome_host import ROOT, digest, rgb, validate_runtime
sys.path.insert(0, str(ROOT / 'tests/desktop'))
from gnome_composition import FIXTURE, FIXTURE_PATH, judge_samples, png_icon
from oracle import evaluate


def validate(value, build, family='GNOME-COMPOSITION-01', outer_outcome=True):
    observation = validate_runtime(value, build, family, family + '-')
    result = observation['composition']
    control = result['control']
    if control not in {'live', 'above-icons', 'below-wallpaper'} or value['composition_control'] != control or value['environment']['explicit']['SYSPANE_GNOME_COMPOSITION'] != control:
        raise ValueError('composition control identity')
    if result['version'] != '0.2.0' or result['fixture_sha256'] != digest(FIXTURE_PATH.read_bytes()):
        raise ValueError('composition fixture identity')
    manager = result['icon_manager']
    expected_script = str(Path(value['workspace']) / 'data/gnome-shell/extensions/ding@rastersoft.com/app/ding.js')
    shell_pid = observation['manager']['pid'][0]
    if (manager['pid_origin'] != 'XResQueryClientIds' or manager['window'] & ~manager['resource_mask'] != manager['resource_base'] or
        manager['pid'] == shell_pid or manager['process_group'] != shell_pid or manager['session'] != shell_pid or
        expected_script not in manager['arguments'] or manager['start_ticks'] <= 0):
        raise ValueError('native DING lifetime binding')
    retained = next(row for row in value['cleanup'] if row['process']=='shell')['members_before_stop']
    if manager['pid'] not in [row['pid'] for row in retained if row['state']!='Z'] or manager['executable'] not in value['icon_manager_mapped_files']:
        raise ValueError('icon manager was not retained through cleanup')
    identity = json.loads((build / 'gnome-lab/identity.json').read_text())
    prefix = 'usr/share/gnome-shell/extensions/ding@rastersoft.com/'
    expected_ding = {key[len(prefix):]: entry for key, entry in identity['files'].items() if key.startswith(prefix)}
    if value['ding_inputs'] != expected_ding:
        raise ValueError('DING differs from pinned native extension')
    if value['fixture_after'] != value['fixture_inputs'] or value['desktop_entries'] != ['Probe Folder', 'Probe Folder/Sentinel.txt'] or value['desktop_entries_after'] != value['desktop_entries']:
        raise ValueError('native fixture mutated')
    icon = value['fixture_inputs']['data/icons']['SysPaneFixture/64x64/places/folder.png']
    if icon != {'bytes': len(png_icon()), 'sha256': digest(png_icon())}:
        raise ValueError('opaque icon fixture identity')
    expected_settings = {'picture-uri': "''", 'picture-uri-dark': "''", 'picture-options': "'none'",
                         'primary-color': "'#304860'", 'color-shading-type': "'solid'"}
    if result['background_settings_before'] != expected_settings or result['background_settings_after'] != expected_settings:
        raise ValueError('background settings differ from the fixed scene')
    size = FIXTURE['overlap'][2] * FIXTURE['overlap'][3] * 3
    before_enable = result['scene_enabled_ns']
    previous = 0
    calibrated = []
    for index, stage in enumerate(result['calibrations']):
        if index >= 3 or stage['background'] != (FIXTURE['transparency_backgrounds'] + [FIXTURE['background_rgb']])[index]:
            raise ValueError('calibration backgrounds/order')
        if rgb(stage['background_witness'], 128*96*3) != bytes(stage['background']) * (128*96):
            raise ValueError('independent calibration background witness')
        if len(stage['frames']) != 3:
            raise ValueError('calibration stability frame count')
        data = None
        for frame in stage['frames']:
            if not previous <= frame['started_ns'] <= frame['finished_ns'] < before_enable:
                raise ValueError('calibration must precede candidate enablement')
            previous = frame['finished_ns']
            decoded = rgb(frame['pixels'], size)
            if data is not None and data != decoded:
                raise ValueError('calibration was not stable')
            data = decoded
        calibrated.append(data)
    if len(calibrated) != 3 or len(result['baseline']) != 3:
        raise ValueError('calibration completeness')
    for frame in result['baseline']:
        if not previous <= frame['started_ns'] <= frame['finished_ns'] < before_enable or rgb(frame['pixels'], size) != calibrated[2]:
            raise ValueError('restored baseline differs or occurred after candidate enablement')
        previous = frame['finished_ns']
    marker = result['marker']
    if marker['started_monotonic_ns'] <= before_enable:
        raise ValueError('marker interval precedes candidate enablement')
    marker_result = evaluate(marker['trace'])
    if marker_result != marker['evaluation'] or any(r.startswith('capture.') for r in marker_result['uncertainty']):
        raise ValueError('marker evidence differs or capture is incomplete')
    if marker['trace']['end_us'] != 2400000 or [s['generation'] for s in marker['trace']['stimuli']] != [1,2,3]:
        raise ValueError('marker scenario changed')
    if len(marker['trace']['frames']) != len(result['overlap_samples']):
        raise ValueError('missing paired overlap capture')
    for frame, overlap in zip(marker['trace']['frames'], result['overlap_samples']):
        if frame['start_us'] != overlap['marker_start_us'] or frame['end_us'] > overlap['start_us']:
            raise ValueError('paired capture timing mismatch')
    outcome = judge_samples(calibrated[2], result['overlap_samples'], calibrated[:2])
    if outcome != result['evaluation']:
        raise ValueError('composition claim differs from raw calibrated samples')
    for key in ('background_before', 'background_after'):
        if rgb(marker[key],128*96*3) != bytes(FIXTURE['background_rgb']) * (128*96):
            raise ValueError('background pixels changed during candidate interval')
    actual = (marker_result['outcome'], outcome['icons'], outcome['rectangle'])
    expected = {'live': ('pass','pass','pass'), 'above-icons': ('pass','fail','pass'),
                'below-wallpaper': ('fail','pass','fail')}[control]
    if actual != expected or result['outcome'] != ('pass' if control == 'live' else 'fail') or (outer_outcome and value['outcome'] != result['outcome']):
        raise ValueError('candidate did not produce the required independent control results')
    journal_path = Path(value['composition_journal']['path']).resolve(strict=True)
    if journal_path != Path(value['workspace']) / 'composition.jsonl':
        raise ValueError('owned journal path')
    raw = journal_path.read_bytes()
    if len(raw) > 8*1024**2 or len(raw) != value['composition_journal']['bytes'] or digest(raw) != value['composition_journal']['sha256']:
        raise ValueError('journal identity')
    records = [json.loads(line) for line in raw.splitlines()]
    if len(records)>160 or any(row['kind']=='error' for row in records):
        raise ValueError('journal incomplete/overflowed')
    selected = lambda kind: [r['value'] for r in records if r['kind']==kind]
    if selected('baseline') != result['baseline'] or selected('sample') != [{'marker': f,'overlap':o} for f,o in zip(marker['trace']['frames'],result['overlap_samples'])]:
        raise ValueError('raw samples differ from the preserved journal')
    if selected('calibration_frame') != [{'background':s['background'],'frame':f} for s in result['calibrations'] for f in s['frames']]:
        raise ValueError('calibration differs from the preserved journal')
    return {'control': control, 'outcome': result['outcome'], 'marker': actual[0], 'icons': actual[1], 'rectangle': actual[2],
            'anchor_counts': outcome['anchor_counts'], 'clean_count': outcome['clean_count'],
            'samples':len(outcome['samples']), 'max_gap_us':outcome['max_gap_us'], 'max_capture_us':outcome['max_capture_us'],
            'native_manager_pid':manager['pid'], 'cleanup':'confirmed', 'background':'unchanged synthetic color/settings'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=3,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    build=args.build_dir.resolve(strict=True)
    results, identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:
            raise ValueError('owned bounded report required')
        raw=path.read_bytes(); value=json.loads(raw)
        results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_inputs':value['source_inputs'],'source_base':value['source_base']})
    if sorted(r['control'] for r in results)!=['above-icons','below-wallpaper','live'] or any(i['source_inputs']!=identities[0]['source_inputs'] for i in identities):
        raise ValueError('complete controls with identical source required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected:raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence':raise ValueError('owned evidence output required')
    result={'version':'0.2.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass',
            'scope':'Pinned GNOME/DING solid-color composition controls only','reports':identities,'results':results,
            'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in ['build-support/record_gnome_composition.py','build-support/record_gnome_host.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']},
            'not_run':['native reveal','icon input','focus/taskbar behavior','image wallpaper/policy','shell/icon-manager recovery','Wayland','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,indent=2); stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
