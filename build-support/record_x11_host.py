"""Bind a completed X11 investigation and its failed image lab to raw evidence."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import zlib
from urllib.parse import unquote, urlsplit

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


def input_evidence(row, build):
    observation = row['input_observation']
    manager = next(p['pid'] for p in row['cleanup'] if p['process'] == 'pcmanfm')
    registry = next(p['pid'] for p in row['cleanup'] if p['process'] == 'registry')
    if row['registry_identity_confirmed'] != registry:
        raise ValueError('accessibility registry identity')
    journal = row['input_journal']
    raw = journal['raw_utf8'].encode('utf-8')
    if len(raw) > 8 * 1024**2 or len(raw) != journal['bytes'] or hashlib.sha256(raw).hexdigest() != journal['sha256']:
        raise ValueError('input journal identity')
    entries = [json.loads(line) for line in journal['raw_utf8'].splitlines()]
    if not entries or len(entries) > 1024 or any(a['at_us'] > b['at_us'] for a, b in zip(entries, entries[1:])):
        raise ValueError('input journal bounds/order')
    if entries[0]['kind'] != 'initialize' or entries[0]['value'] != {'manager_pid': manager, 'desktop': row['desktop_window']}:
        raise ValueError('input observer identity')
    ready = [e['value']['clipboard_window'] for e in entries if e['kind'] == 'ready']
    if len(ready) != 1:
        raise ValueError('private clipboard owner identity')
    steps = observation['steps']
    if [e['value'] for e in entries if e['kind'] == 'check-finish'] != steps:
        raise ValueError('input stage record differs from journal')
    order = ['baseline-clear', 'select', 'clear', 'drag-select', 'context-menu', 'double-click-open', 'restore-clear']
    if not steps or [s['step'] for s in steps] != order[:len(steps)]:
        raise ValueError('input step order/completeness')
    selections = {'baseline-clear': [], 'select': ['Probe Folder'], 'clear': [],
                  'drag-select': ['Probe Folder', 'Second Folder'], 'restore-clear': []}
    opened = None
    for index, step in enumerate(steps):
        pixels(step['desktop_pixels'], 800 * 600 * 3)
        name, structure = step['step'], step['structure']
        candidate = structure['candidate']
        if candidate != row['structures'][0]['candidate']:
            raise ValueError('input candidate identity')
        candidate_clear = structure['focus'] != candidate and structure['active_window'] != [candidate]
        focus_expected = candidate_clear and (name not in selections or structure['active_window'] == [row['desktop_window']])
        if step['candidate_did_not_own_focus'] != candidate_clear or step['native_focus_expected'] != focus_expected:
            raise ValueError('input focus claim')
        tree = step['tree']
        if len(tree) > 256 or any(len(t['name']) > 256 or len(t['path']) > 12 for t in tree):
            raise ValueError('input semantic observation bounds')
        clipboard = step['clipboard']
        names = []
        if clipboard is not None:
            if clipboard['owner_changed']:
                value = clipboard['raw_utf8']
                if len(value.encode('utf-8')) > 4096 or clipboard['owner'] == ready[0]:
                    raise ValueError('clipboard buffer/owner')
                content = value[:-1] if value.endswith('\0') else value
                if '\0' in content:
                    raise ValueError('embedded clipboard NUL')
                uris = content.splitlines()
                if not 1 <= len(uris) <= 2 or len(set(uris)) != len(uris) or uris != clipboard['uris']:
                    raise ValueError('clipboard URI count/content')
                allowed = {str(build / row['workspace'] / 'Desktop' / n): n for n in ('Probe Folder', 'Second Folder')}
                if name == 'double-click-open':
                    allowed = {str(build / row['workspace'] / 'Desktop/Probe Folder/Sentinel.txt'): 'Sentinel.txt'}
                for uri in uris:
                    parsed = urlsplit(uri)
                    path = unquote(parsed.path, errors='strict')
                    if parsed.scheme != 'file' or parsed.netloc or parsed.query or parsed.fragment or path not in allowed:
                        raise ValueError('clipboard file outside exact fixture')
                    names.append(allowed[path])
            elif clipboard['owner'] != ready[0] or clipboard['uris'] or clipboard.get('raw_utf8'):
                raise ValueError('empty clipboard ownership')
            if sorted(names) != clipboard['names']:
                raise ValueError('clipboard names differ from raw URI bytes')
        if name in selections:
            matched = clipboard is not None and sorted(names) == selections[name]
            if name == 'restore-clear' and opened is not None and opened in structure['client_order_bottom_to_top']:
                raise ValueError('opened folder did not close')
        elif name == 'context-menu':
            matched = any(t['role'] == 'menu item' and t['name'] == 'Open in New Window' and t['showing'] for t in tree)
        else:
            before = steps[index - 1]['structure']['client_order_bottom_to_top']
            new = [c for c in structure['clients'] if c['window'] not in before and c['pid'] == [manager] and c['class'] == ['pcmanfm', 'Pcmanfm']]
            matched = (len(new) == 1 and step['opened_window'] == new[0]['window'] and
                       structure['active_window'] == [new[0]['window']] and names == ['Sentinel.txt'] and
                       any(t['role'] == 'frame' and t['name'] == 'Probe Folder' and t['showing'] for t in tree))
            opened = step['opened_window']
        verdict = 'pass' if matched and focus_expected else 'fail'
        if step['outcome'] != verdict or (verdict == 'fail' and index != len(steps) - 1):
            raise ValueError('native input verdict/failed prerequisite')
    expected = 'inconclusive' if observation.get('error') else ('fail' if steps[-1]['outcome'] == 'fail' else 'pass')
    if expected == 'pass' and len(steps) != len(order):
        raise ValueError('partial input sequence promoted to pass')
    if row['icon_input'] != expected or observation['outcome'] != expected:
        raise ValueError('input outcome does not reproduce')
    if row['candidate'] == 'live' and [(s['step'], s['outcome']) for s in steps] != [('baseline-clear', 'pass'), ('select', 'fail')]:
        raise ValueError('ordinary-window negative input control')
    if row['fixture_before'] != row['fixture_after']:
        raise ValueError('native fixture was changed')
    if expected == 'pass' and not row['icon_region_restored']:
        raise ValueError('input restoration did not preserve icon pixels')


def recovery_evidence(row, build, before, mask, wallpaper):
    recovery = row['recovery_observation']
    journal = row['recovery_journal']
    raw = journal['raw_utf8'].encode('utf-8')
    if len(raw) > 8 * 1024**2 or len(raw) != journal['bytes'] or hashlib.sha256(raw).hexdigest() != journal['sha256']:
        raise ValueError('recovery journal identity')
    stored = (build / journal['path']).resolve(strict=True)
    if not stored.is_relative_to(build) or sha(stored) != journal['sha256']:
        raise ValueError('recovery journal differs from owned capture')
    entries = [json.loads(line) for line in journal['raw_utf8'].splitlines()]
    if not entries or len(entries) > 400 or entries[0]['kind'] != 'identity' or entries[-1]['kind'] != 'result':
        raise ValueError('recovery journal bounds/closure')
    for kind, key in [('event', 'events'), ('frame', 'frames'), ('sample', 'samples')]:
        if [e['value'] for e in entries if e['kind'] == kind] != recovery[key]:
            raise ValueError('recovery journal observation mismatch')
    merged = {**entries[0]['value'], **entries[-1]['value'], **{key: recovery[key] for key in ('frames', 'samples', 'events')}}
    if merged != recovery:
        raise ValueError('recovery journal result mismatch')
    original = next(p for p in row['cleanup'] if p['process'] == 'openbox')
    replacement = next(p for p in row['cleanup'] if p['process'] == 'openbox-replacement')
    candidate = next(p for p in row['cleanup'] if p['process'] == 'candidate')
    old = recovery['old_manager']
    if original['exit'] != -9 or old['pid'] != [original['pid']] or old['self'] != [old['window']] or old['pid_origin'] != 'XResQueryClientIds':
        raise ValueError('recovery original manager identity/exit')
    if recovery['candidate_pid'] != candidate['pid'] or recovery['candidate_window'] != row['structures'][0]['candidate']:
        raise ValueError('recovery candidate identity')
    events = recovery['events']
    if [e['event'] for e in events] != ['stimulus', 'stop_requested', 'exit_observed', 'stimulus', 'replacement_started', 'manager_ready', 'stimulus']:
        raise ValueError('recovery event order')
    end = recovery['end_us']
    if recovery['start_us'] != 0 or not oracle.integer(end) or not 0 < end <= 8_000_000:
        raise ValueError('recovery interval')
    times = [e['at_us'] for e in events]
    if any(not oracle.integer(t) or not 0 <= t <= end for t in times) or times != sorted(times):
        raise ValueError('recovery event time')
    if [events[i]['generation'] for i in (0, 3, 6)] != [4, 5, 6] or times[1] < 250_000 or end - times[6] < 700_000:
        raise ValueError('recovery stimulus/coverage schedule')
    if (events[1]['pid'] != original['pid'] or events[2] != {'event': 'exit_observed', 'at_us': times[2], 'pid': original['pid'], 'exit': -9, 'observer': 'pidfd'} or
            events[4]['pid'] != replacement['pid'] or replacement['pid'] == original['pid'] or times[4] - times[2] < 350_000):
        raise ValueError('recovery independent exit/replacement order')
    ready = events[5]
    if ready['pid'] != [replacement['pid']] or ready['self'] != [ready['window']] or ready['pid_origin'] != 'XResQueryClientIds' or times[5] - times[1] > 5_000_000:
        raise ValueError('recovery replacement native identity/deadline')
    if any(identity['window'] & ~identity['resource_mask'] != identity['resource_base'] for identity in (old, ready)):
        raise ValueError('recovery resource owner binding')
    frames, samples = recovery['frames'], recovery['samples']
    if not 3 <= len(frames) <= 160 or len(samples) != len(frames):
        raise ValueError('recovery frame/sample coverage')
    previous = 0
    gaps, durations, decoded, images = [], [], [], []
    for frame, sample in zip(frames, samples):
        image = oracle.unpack_frame(frame)
        begin, finish = frame['start_us'], frame['end_us']
        if (not oracle.integer(begin) or not oracle.integer(finish) or not previous <= begin <= finish <= end or frame['origin'] != 'display_server_root'):
            raise ValueError('recovery frame time/origin')
        gaps.append(begin - previous)
        durations.append(finish - begin)
        previous = finish
        decoded.append(oracle.decode(image))
        images.append(image)
        wall = sample['wallpaper_frame']
        wb, we = wall['start_us'], wall['end_us']
        if not all(oracle.integer(t) for t in (wb, we, sample['at_us'])) or not finish <= wb <= sample['at_us'] <= we <= end or wall['origin'] != 'display_server_root':
            raise ValueError('recovery wallpaper capture time/origin')
        durations.append(we - wb)
        if sample['wallpaper_unchanged'] != (oracle.unpack_frame(wall) == wallpaper):
            raise ValueError('recovery wallpaper pixel claim')
        if sample['accepted'] not in (3, 4, 5, 6) or sample['accepted'] > max(e['generation'] for e in events if e['event'] == 'stimulus' and e['at_us'] <= sample['at_us']):
            raise ValueError('recovery acknowledged unissued generation')
    gaps.append(end - previous)
    max_gap, max_capture = max(gaps), max(durations)
    coverage = max_gap <= 150_000 and max_capture <= 50_000
    post = [i for i, f in enumerate(frames) if f['start_us'] >= times[6] + 200_000]
    defect = any(decoded[i] != 6 or any(images[i][n:n+3] != before[n:n+3] for n in mask) for i in post)
    continuity = any(s['accepted'] == 5 and s['at_us'] < times[5] for s in samples) and any(s['accepted'] == 6 for s in samples)
    expected = {'manager_recovery': 'pass', 'candidate_progress': 'pass' if continuity else 'fail',
                'coverage': 'pass' if coverage else 'inconclusive',
                'surface_recovery': 'fail' if defect else ('pass' if coverage and len(post) >= 3 else 'inconclusive'),
                'wallpaper_pixels': 'pass' if all(s['wallpaper_unchanged'] for s in samples) else 'fail'}
    first = next((f['end_us'] for f, generation in zip(frames, decoded) if generation == 6), None)
    if recovery['outcomes'] != expected or recovery['maximum_gap_us'] != max_gap or recovery['maximum_capture_us'] != max_capture or recovery['first_final_generation_us'] != first:
        raise ValueError('recovery outcomes do not reproduce')


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
        if not report.get('icon_input_requested') and row['icon_input'] != 'not_run':
            raise ValueError('unexecuted icon input promoted to a result')
        processes = {'candidate', 'pcmanfm', 'openbox', 'bus', 'Xvfb'} | ({'registry'} if report.get('icon_input_requested') else set()) | ({'openbox-replacement'} if report.get('window_manager_restart_requested') else set())
        if {p['process'] for p in row['cleanup']} != processes or any(p['exit'] is None for p in row['cleanup']):
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
        wallpaper_region = pixels(row['wallpaper_region'], oracle.RGB_BYTES)
        if report.get('delayed_wallpaper_setup'):
            if row['wallpaper_setup']['exit'] != 0 or not row['wallpaper_fixture_display_verified']:
                raise ValueError('native wallpaper setup not verified')
            fixture = pixels(row['configured_wallpaper_rgb'], 800 * 600 * 3)
            expected = bytes(channel for y in range(600) for x in range(800)
                             for channel in ((48, 72, 96) if (x // 40 + y // 40) % 2 else (64, 88, 112)))
            region = b''.join(expected[(y*800+600)*3:(y*800+728)*3] for y in range(400, 496))
            if report['wallpaper_mode'] == 'color':
                region = bytes((48, 72, 96)) * 128 * 96
            if fixture != expected or wallpaper_region != region:
                raise ValueError('configured wallpaper fixture differs from captured pixels')
            if row['preserved_before']['wallpaper.ppm']['sha256'] != hashlib.sha256(b'P6\n800 600\n255\n' + fixture).hexdigest():
                raise ValueError('configured wallpaper file identity')
        if report.get('icon_input_requested'):
            if report['input_runtime'] != json.loads((ROOT / 'build-support/x11-input-runtime.json').read_text(encoding='utf-8')):
                raise ValueError('native input runtime identity')
            input_evidence(row, build)
        background = bytes(channel for y in range(32, 128) for x in range(32, 160)
                           for channel in ((48, 72, 96) if report['wallpaper_mode'] == 'color' or (x // 40 + y // 40) % 2 else (64, 88, 112)))
        mask = [n for n in range(0, len(before), 3) if before[n:n+3] != background[n:n+3]]
        first = oracle.unpack_frame(row['trace']['frames'][0])
        changed = sum(first[n:n+3] != before[n:n+3] for n in mask)
        if len(mask) < 100 or row['icon_pixels']['baseline_non_background'] != len(mask) or row['icon_pixels']['changed_under_candidate'] != changed:
            raise ValueError('icon-concealment evidence differs from pixels')
        if report.get('window_manager_restart_requested'):
            if report['recovery_runtime'] != json.loads((ROOT / 'build-support/x11-recovery-runtime.json').read_text(encoding='utf-8')):
                raise ValueError('native recovery runtime identity')
            recovery_evidence(row, build, before, mask, wallpaper_region)
        elif row.get('recovery_observation', {}).get('outcomes', {}).get('manager_recovery', 'not_run') != 'not_run':
            raise ValueError('unexecuted recovery claim')
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
    parser.add_argument('--failed-image-report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve(strict=True)
    if json.loads((build / '.syspane-owner.json').read_text())['profile'] != 'linux-x64-gcc13':
        raise ValueError('owned build required')
    record = {'version': '0.1.0', 'work_ids': ['W-02', 'W-05'], 'wall_conformant': False, 'reports': [],
              'verification': 'Recomputed all temporal results and icon-concealment counts from preserved RGB bytes; checked native action states, wallpaper scope, cleanup and source/artifact/runtime identity.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sources = [(args.report, 'X11-HOST-01', True)]
    if args.failed_image_report:
        sources.append((args.failed_image_report, 'X11-IMAGE-FAILURE', False))
    for source, label, completed in sources:
        source = source.resolve(strict=True)
        if not source.is_relative_to(build / 'native-evidence') or source.stat().st_size > 32 * 1024**2:
            raise ValueError('bounded owned native report required')
        report = json.loads(source.read_text(encoding='utf-8'))
        validate(report, build, completed)
        destination = args.output.with_suffix('.' + label + '.json')
        shutil.copyfile(source, destination)
        record['reports'].append({'record': destination.name, 'sha256': sha(destination), 'execution': report['execution'],
                                  'gtk_rendering': report['gtk_rendering'], 'wallpaper_mode': report['wallpaper_mode'],
                                  'delayed_wallpaper_setup': report.get('delayed_wallpaper_setup', False),
                                  'window_manager_restart_requested': report.get('window_manager_restart_requested', False),
                                  'icon_input_requested': report.get('icon_input_requested', False)})
    identity_copy = args.output.with_suffix('.lab-identity.json')
    shutil.copyfile(build / 'x11-lab/identity.json', identity_copy)
    record['lab_identity'] = {'record': identity_copy.name, 'sha256': sha(identity_copy)}
    record['source_base'] = report['source_base']
    record['limitations'] = ['Both EWMH candidates fail placement; no wall qualification.',
                             'Image-wallpaper startup is a preserved lab failure; color evidence does not replace it.',
                             'Input/restart results apply only to explicitly requested dimensions in the named synthetic X11 profile; product recovery and other desktop profiles remain unqualified.']
    args.output.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('X11 evidence verified and recorded:', args.output)


if __name__ == '__main__':
    main()
