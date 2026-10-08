"""Bind native Mutter decision logs to the unchanged independent focus observations."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from record_gnome_focus import ROOT, digest, raw_file, validate as validate_focus

TOPICS = 'focus,keybindings,window-state'
PREFIX = re.compile(r'^libmutter-Message: (\d{2}):(\d{2}):(\d{2})\.(\d{3}): (KEYBINDINGS|FOCUS|WINDOW_STATE): (.*)$')
MRU = re.compile(r'Focusing workspace MRU window (0x[0-9a-f]+)$')
HANDLER = 'Running handler for show-desktop'


def interpret(raw, observation):
    lines = raw.decode('utf-8', errors='strict').splitlines()
    entries = []
    for index, line in enumerate(lines):
        match = PREFIX.fullmatch(line)
        if not match:
            continue
        hour, minute, second, millis = map(int, match.group(1, 2, 3, 4))
        if hour > 23 or minute > 59 or second > 59:
            raise ValueError('invalid native log clock')
        entries.append({'line': index + 1, 'time': ((hour*60+minute)*60+second)*1000+millis,
                        'topic': match[5], 'message': match[6]})
    handlers = [i for i, row in enumerate(entries) if row['topic']=='KEYBINDINGS' and row['message']==HANDLER]
    if len(handlers)!=2:
        raise ValueError('exactly two executed native handlers required')
    first, second = [entries[i] for i in handlers]
    separation = (second['time']-first['time']) % 86400000
    actions = observation['interval']['actions']
    if len(actions)!=2 or abs(separation*1000-(actions[1]['start_us']-actions[0]['start_us']))>50000:
        raise ValueError('native handler/action separation differs')
    # Only this synchronous decision sequence can establish restoration selection.
    sequence = []
    previous = 0
    for row in entries[handlers[1]+1:]:
        elapsed = (row['time']-second['time']) % 86400000
        if elapsed < previous or elapsed > 43200000:
            raise ValueError('backwards native decision clock')
        if elapsed > 200 or row['topic']=='KEYBINDINGS' or (' due to button ' in row['message']):
            break
        previous = elapsed
        sequence.append(row)
    choices = [(i, MRU.fullmatch(row['message'])) for i,row in enumerate(sequence) if MRU.fullmatch(row['message'])]
    if len(choices)!=1:
        raise ValueError('one bounded native MRU decision required')
    choice_index, choice = choices[0]
    xid = int(choice[1], 16)
    owners = {observation['foreground']['window']: 'foreground'}
    if observation['icon_manager']:
        owners[observation['icon_manager']['window']] = 'icon'
    if xid not in owners:
        raise ValueError('native MRU selection has unknown owner')
    setting = f'Setting input focus to window {choice[1]}, input: 1 focusable: 1'
    assignments = [row for row in sequence[choice_index+1:] if row['message']==setting]
    if len(assignments)!=1:
        raise ValueError('native MRU focus assignment missing or ambiguous')
    foreground = hex(observation['foreground']['window'])
    shown = [row for row in sequence if row['message'].startswith(f'Showing window {foreground},')]
    if len(shown)!=1:
        raise ValueError('native foreground restoration missing or ambiguous')
    last = max(assignments[0]['line'], shown[0]['line'])
    return {'handler_lines':[first['line'], second['line']], 'handler_separation_ms':separation,
            'selection_line':sequence[choice_index]['line'], 'focus_assignment_line':assignments[0]['line'],
            'foreground_show_line':shown[0]['line'], 'selected_window':xid, 'selected_role':owners[xid],
            'excerpt':[{'line':i+1, 'text':lines[i]} for i in range(second['line']-1,last)]}


def validate(value, build):
    result = validate_focus(value, build)
    traced = value['focus_trace']
    environment = value['environment']['explicit']
    if type(traced) is not bool or any(k in environment for k in ['MUTTER_VERBOSE','MUTTER_USE_LOGFILE']):
        raise ValueError('bounded topic-specific native tracing required')
    if traced:
        if environment.get('MUTTER_DEBUG') != TOPICS:
            raise ValueError('native trace topics differ')
        raw = raw_file(value, 'native_focus_log', Path(value['workspace']), 'shell.log', 1048576)
        if raw.decode('utf-8') != value['logs']['shell.log']:
            raise ValueError('complete native log differs from retained report')
        decision = interpret(raw, value['observation']['focus_baseline'])
    else:
        if 'MUTTER_DEBUG' in environment or 'native_focus_log' in value:
            raise ValueError('untraced control contains native tracing')
        decision = None
    return {**result, 'traced':traced, 'native_decision':decision}


def compare(results):
    modes = ['shell','ding','candidate']
    if len(results)!=6 or any(sum(r['mode']==m and r['traced'] is t for r in results)!=1 for m in modes for t in [False,True]):
        raise ValueError('one traced/untraced pair per mode required')
    fields = ['visual_reveal','focus','phase_roles','f9_delivered','f10_delivered','candidate_acceptance']
    pairs = {}
    for mode in modes:
        off = next(r for r in results if r['mode']==mode and not r['traced'])
        on = next(r for r in results if r['mode']==mode and r['traced'])
        equal = all(off[k]==on[k] for k in fields)
        role = on['native_decision']['selected_role']
        pairs[mode] = {'observations_equal':equal, 'signature':{k:on[k] for k in fields},
                       'native_selected_role':role, 'selection_matches_restored_role':on['phase_roles'][-1]==[role]}
    return {'outcome':'stable' if all(p['observations_equal'] for p in pairs.values()) else 'inconclusive', 'pairs':pairs}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=6,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    build=args.build_dir.resolve(strict=True)
    results,identities=[],[]
    for path in args.reports:
        path=path.resolve(strict=True)
        if path.parent!=build/'native-evidence' or path.stat().st_size>16*1024**2:
            raise ValueError('owned bounded report required')
        raw=path.read_bytes(); value=json.loads(raw)
        results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'os_release':value['environment']['os_release_sha256']}})
    if any(r['source_inputs']!=identities[0]['source_inputs'] or r['runtime']!=identities[0]['runtime'] for r in identities):
        raise ValueError('source/runtime-identical comparison required')
    for name,expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes())!=expected: raise ValueError('current source differs: '+name)
    output=args.output.resolve()
    if output.parent!=build/'native-evidence': raise ValueError('owned output required')
    scripts=['source/build/record_gnome_focus_trace.py','source/build/record_gnome_focus.py','source/build/record_gnome_reveal.py',
             'source/build/record_gnome_composition.py','source/build/record_gnome_host.py','tests/desktop/gnome_focus_baseline.py',
             'tests/desktop/gnome_reveal.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    result={'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass',
            'scope':'Owned native Mutter decision trace; original acceptance unchanged','reports':identities,'results':results,
            'comparison':compare(results),'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
            'not_run':['integration fix','complete focus/input/taskbar qualification','image wallpaper/policy','shell/icon-manager recovery','Wayland','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream: json.dump(result,stream,indent=2); stream.write('\n')
    print(json.dumps(result['comparison'],indent=2))


if __name__=='__main__':main()
