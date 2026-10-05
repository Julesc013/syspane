"""Bind a completed X11 investigation and its failed image lab to raw evidence."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import zlib

ROOT = Path(__file__).resolve().parents[1]
module = importlib.util.spec_from_file_location('pixel_oracle', ROOT / 'tests/desktop/oracle.py')
oracle = importlib.util.module_from_spec(module)
module.loader.exec_module(oracle)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels(record, count):
    if record['bytes'] != count or len(record['rgb_zlib_base64']) > 2 * 1024**2:
        raise ValueError('image record size')
    decoder = zlib.decompressobj()
    data = decoder.decompress(base64.b64decode(record['rgb_zlib_base64'], validate=True), count + 1)
    if len(data) != count or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('image compression bounds')
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('image digest')
    return data


def validate(report, build, completed):
    if report['family'] != 'X11-HOST-01' or report['artifact_sha256'] != sha(build / 'SysPane.OracleProbe'):
        raise ValueError('native family/artifact identity')
    for source, digest in report['source_inputs'].items():
        path = (ROOT / source).resolve(strict=True)
        if not path.is_relative_to(ROOT) or sha(path) != digest:
            raise ValueError('native source changed: ' + source)
    if sha(build / 'x11-lab/identity.json') != report['lab_identity_sha256']:
        raise ValueError('native lab identity changed')
    for name, digest in {**report['system_binaries'], **report['resolved_loader_files']}.items():
        if sha(Path(name)) != digest:
            raise ValueError('native dependency changed: ' + name)
    if not completed:
        if report['execution'] != 'failed' or report['wallpaper_mode'] != 'tile' or not report['cases']:
            raise ValueError('expected original failed image-lab report')
        if not any(row.get('error') for row in report['cases']):
            raise ValueError('failure evidence missing')
        return
    if report['execution'] != 'completed' or [row['candidate'] for row in report['cases']] != ['live', 'desktop', 'desktop-below']:
        raise ValueError('incomplete investigation')
    for row in report['cases']:
        if row['execution'] != 'completed' or row['observer_exit'] != 0 or row['remaining_owned_group_members'] or row['wall_conformant']:
            raise ValueError('execution/cleanup or qualification overclaim')
        if row['icon_input'] != 'not_run':
            raise ValueError('unexecuted icon input promoted to a result')
        if {p['process'] for p in row['cleanup']} != {'candidate', 'pcmanfm', 'openbox', 'bus', 'Xvfb'} or any(p['exit'] is None for p in row['cleanup']):
            raise ValueError('owned process cleanup evidence')
        if next(p for p in row['cleanup'] if p['process'] == 'candidate')['exit'] != 0:
            raise ValueError('candidate exit')
        result = oracle.evaluate(row['trace'])
        if result != row['observation']:
            raise ValueError('pixel/time result does not reproduce')
        if row['candidate'] == 'live' and result['outcome'] != 'fail':
            raise ValueError('ordinary-window negative control did not detect disappearance')
        before = pixels(row['baseline_icon_region'], oracle.RGB_BYTES)
        pixels(row['baseline_desktop'], 800 * 600 * 3)
        pixels(row['wallpaper_region'], oracle.RGB_BYTES)
        background = bytes(channel for y in range(32, 128) for x in range(32, 160)
                           for channel in ((48, 72, 96) if report['wallpaper_mode'] == 'color' or (x // 40 + y // 40) % 2 else (64, 88, 112)))
        mask = [n for n in range(0, len(before), 3) if before[n:n+3] != background[n:n+3]]
        first = oracle.unpack_frame(row['trace']['frames'][0])
        changed = sum(first[n:n+3] != before[n:n+3] for n in mask)
        if len(mask) < 100 or row['icon_pixels']['baseline_non_background'] != len(mask) or row['icon_pixels']['changed_under_candidate'] != changed:
            raise ValueError('icon-concealment evidence differs from pixels')
        placement = 'fail' if changed or oracle.decode(first) is None else 'inconclusive'
        if row['placement'] != placement:
            raise ValueError('placement overclaim')
        exposed = [s for s in row['structures'] if 500000 <= s['at_us'] < 1450000]
        restored = [s for s in row['structures'] if s['at_us'] >= 1750000]
        if not exposed or not restored or any(s['showing_desktop'] != [1] for s in exposed) or any(s['showing_desktop'] != [0] for s in restored):
            raise ValueError('native reveal/restore state not confirmed')
        if [a['intent'] for a in row['actions']] != ['reveal', 'restore']:
            raise ValueError('named action evidence missing')
        preserved = row['preserved_before'] == row['preserved_after'] and row['wallpaper_pixels_unchanged_during'] and row['wallpaper_pixels_unchanged_after']
        if row['wallpaper_preservation'] != ('pass' if preserved else 'fail'):
            raise ValueError('wallpaper preservation overclaim')
        if report['wallpaper_mode'] == 'color' and row['wallpaper_preservation_scope'] != 'Configured solid color; file unchanged but not displayed':
            raise ValueError('color control promoted to image-wallpaper qualification')
        journal = (build / row['capture_journal']['path']).resolve(strict=True)
        if not journal.is_relative_to(build) or sha(journal) != row['capture_journal']['sha256']:
            raise ValueError('capture journal identity')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--failed-image-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    if json.loads((build / '.syspane-owner.json').read_text())['profile'] != 'linux-x64-gcc13':
        raise ValueError('owned build required')
    record = {'version': '0.1.0', 'work_ids': ['W-02', 'W-05'], 'wall_conformant': False, 'reports': [],
              'verification': 'Recomputed all temporal results and icon-concealment counts from preserved RGB bytes; checked native action states, wallpaper scope, cleanup and source/artifact/runtime identity.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for source, label, completed in [(args.report, 'X11-HOST-01', True), (args.failed_image_report, 'X11-IMAGE-FAILURE', False)]:
        source = source.resolve(strict=True)
        if not source.is_relative_to(build / 'native-evidence') or source.stat().st_size > 32 * 1024**2:
            raise ValueError('bounded owned native report required')
        report = json.loads(source.read_text(encoding='utf-8'))
        validate(report, build, completed)
        destination = args.output.with_suffix('.' + label + '.json')
        shutil.copyfile(source, destination)
        record['reports'].append({'record': destination.name, 'sha256': sha(destination), 'execution': report['execution'],
                                  'gtk_rendering': report['gtk_rendering'], 'wallpaper_mode': report['wallpaper_mode']})
    identity_copy = args.output.with_suffix('.lab-identity.json')
    shutil.copyfile(build / 'x11-lab/identity.json', identity_copy)
    record['lab_identity'] = {'record': identity_copy.name, 'sha256': sha(identity_copy)}
    record['source_base'] = report['source_base']
    record['limitations'] = ['Both EWMH candidates fail placement; no wall qualification.',
                             'Image-wallpaper startup is a preserved lab failure; color evidence does not replace it.',
                             'Icon selection, launch, drag, menus, shell recovery and other desktop profiles remain unexecuted.']
    args.output.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('X11 evidence verified and recorded:', args.output)


if __name__ == '__main__':
    main()
