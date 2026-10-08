"""Verify optional focus restoration against unchanged native acceptance and guards."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from record_gnome_host import ROOT, digest
from record_gnome_focus import raw_file, validate as focus
from record_gnome_composition import validate as composition
from record_gnome_input import validate_observations as input_observations
from gnome_focus_integration import STEPS, judge_step
from gnome_input import icon_center


def validate(value, build):
    baseline = focus(value, build)
    initial = composition(value, build, family='GNOME-FOCUS-BASELINE-01', outer_outcome=False)
    observation = value['observation']; result = observation['focus_integration']; mode = result['mode']
    native_baseline = observation['focus_baseline']; foreground = native_baseline['foreground']; icon = native_baseline['icon_manager']
    env = value['environment']['explicit']; workspace = Path(value['workspace'])
    if mode not in ['observe','restore'] or value['focus_integration_mode'] != mode or env.get('SYSPANE_GNOME_FOCUS_INTEGRATION') != mode or value['focus_trace'] or native_baseline['mode'] != 'candidate':
        raise ValueError('explicit untraced candidate integration required')
    if result['version'] != '0.1.0' or result['outcome'] != 'pass' or result['not_run'] or result.get('error'):
        raise ValueError('complete bounded integration required')
    desired = 'pass' if mode == 'restore' else 'fail'
    if baseline['focus'] != desired or baseline['f9_delivered'] != (mode == 'restore') or not baseline['f10_delivered'] or baseline['candidate_acceptance'] != desired:
        raise ValueError('original reveal/key receipt does not demonstrate named control')
    if result['binding_after'] != native_baseline['binding_after'] or result['background_after'] != native_baseline['background_settings_after']:
        raise ValueError('guard settings changed')
    raw = raw_file(value,'focus_integration_journal',workspace,'focus-integration.jsonl',8*1024**2)
    records = [json.loads(line) for line in raw.splitlines()]
    selected = lambda kind:[r['value'] for r in records if r['kind'] == kind]
    expected_kinds = ['prepared'] + ['step','verdict']*8 + ['folder-input'] + ['step','verdict']*5 + ['disabled'] + ['step','verdict']*2 + ['completed']
    if [r['kind'] for r in records] != expected_kinds or selected('completed') != [result]:
        raise ValueError('complete integration journal differs')
    prepared = {k:result[k] for k in ['version','mode','initial_trace','started_monotonic_ns']}
    prepared['not_run'] = STEPS + ['folder-input','disable']
    if selected('prepared') != [prepared] or selected('step') != [{k:v for k,v in r.items() if k != 'evaluation'} for r in result['steps']] or selected('verdict') != [r['evaluation'] for r in result['steps']]:
        raise ValueError('guard claims differ from raw native records')
    for kind, keys in [('folder-input',['before_folder_trace','folder_started_ns','folder_input','folder_finished_ns','after_folder_trace']),
                       ('disabled',['before_disable_trace','disable_started_ns','disable_finished_ns','after_disable_trace'])]:
        if selected(kind) != [{k:result[k] for k in keys}]:raise ValueError('intermediate journal differs')
    steps = result['steps']
    if [r['step'] for r in steps] != STEPS:raise ValueError('required guard order/completeness')
    point = icon_center(observation['composition'])
    action = lambda keys:{'keys':keys}
    actions = [{'click':point},action(['F8']),{'click':[600,110]},action(['Super_L','d']),{'click':point},action(['Super_L','d']),
               {'click':[600,110]},action(['Super_L','d']),action(['Alt_L','Tab']),action(['Super_L','d']),
               {'minimize':foreground['window']},action(['Super_L','d']),action(['Alt_L','Tab']),action(['Super_L','d']),action(['Super_L','d'])]
    previous = result['started_monotonic_ns']
    if previous <= native_baseline['focused_key']['finished_ns']+200000000:
        raise ValueError('guards precede original keyboard acceptance')
    icon_type = next(c['type'] for c in native_baseline['interval']['samples'][0]['native']['clients'] if c['window'] == icon['window'])
    if len(icon_type) != 1 or icon_type == foreground['type']:raise ValueError('original icon native role differs')
    verdicts = []
    for row, stimulus in zip(steps, actions):
        if row['started_monotonic_ns'] < previous or row['action']['kind'] != stimulus:
            raise ValueError('native guard ordering/stimulus differs')
        verdict = judge_step(row,mode,foreground['window'],icon['window'])
        if verdict != row['evaluation']:raise ValueError('guard verdict differs')
        verdicts.append(verdict)
        for sample in row['samples']:
            native = sample['native']
            for owner in [foreground,icon]:
                clients = [c for c in native['clients'] if c['window'] == owner['window']]
                if len(clients) != 1 or clients[0]['pid'] != [owner['pid']] or clients[0]['type'] != (foreground['type'] if owner is foreground else icon_type):
                    raise ValueError('guard native lifetime/type differs')
            if set(native['client_order_bottom_to_top']) != {foreground['window'],icon['window']}:
                raise ValueError('unexpected native guard client')
        previous = row['started_monotonic_ns'] + row['end_us']*1000
    if not previous <= result['finished_monotonic_ns'] or not 0 < result['finished_monotonic_ns']-result['started_monotonic_ns'] < 20000000000:
        raise ValueError('bounded integration clock')
    end = lambda row:row['started_monotonic_ns'] + row['end_us']*1000
    if not end(steps[7]) <= result['folder_started_ns'] < result['folder_finished_ns'] <= steps[8]['started_monotonic_ns']:
        raise ValueError('folder guard ordering')
    if not end(steps[12]) <= result['disable_started_ns'] < result['disable_finished_ns'] <= steps[13]['started_monotonic_ns'] or result['disable_finished_ns']-result['disable_started_ns'] > 1000000000:
        raise ValueError('one-way disable ordering/deadline')
    input_result = result['folder_input']
    input_observations(value,build,initial,input_result,icon)
    if input_result['accessibility_registration']['started_ns'] < result['folder_started_ns'] or end(steps[7]) >= input_result['steps'][0]['at_ns'] or input_result['steps'][-1]['at_ns'] >= result['folder_finished_ns']:
        raise ValueError('native input precedes its guard')
    opened = input_result['steps'][6]
    if opened['native']['showing_desktop'] != [0] or opened['native']['active_window'] != [input_result['folder']['window']]:
        raise ValueError('actual folder choice did not end desktop mode')
    names = ['initial_trace','before_folder_trace','after_folder_trace','before_disable_trace','after_disable_trace','final_trace']
    snapshots = [result[n] for n in names]
    all_rows = snapshots[-1]['records']
    if not 4 <= len(all_rows) <= 256 or len(json.dumps(all_rows).encode()) > 65536:
        raise ValueError('bounded diagnostic trace required')
    last = 0
    for row in all_rows:
        if row['monotonic_us'] <= last or row['monotonic_us']*1000 >= result['disable_started_ns']:
            raise ValueError('diagnostic ordering or callback after disable')
        last = row['monotonic_us']
        if row['event'] not in ['clear','remember','entry','restore','abstain']:
            raise ValueError('unknown native decision')
    for index, snapshot in enumerate(snapshots):
        if snapshot['version'] != '0.1.0' or snapshot['mode'] != mode or snapshot['enabled'] != (index < 4) or snapshot['records'] != all_rows[:len(snapshot['records'])]:
            raise ValueError('trace prefix/mode/enabled state differs')
        if index and len(snapshot['records']) < len(snapshots[index-1]['records']):raise ValueError('diagnostics went backward')
    if snapshots[3]['records'] != snapshots[4]['records'] or snapshots[4] != snapshots[5]:
        raise ValueError('disabled controller continued callbacks')
    windows = [(observation['reveal']['started_monotonic_ns'],observation['reveal']['actions'][0],'entry'),
               (observation['reveal']['started_monotonic_ns'],observation['reveal']['actions'][1],'restore')]
    windows += [(steps[i]['started_monotonic_ns'],steps[i]['action'],event) for i,event in [(3,'entry'),(5,'restore'),(7,'entry'),(9,'entry')]]
    decisions = [r for r in all_rows if r['event'] in ['entry','restore']]
    if len(decisions) != len(windows):raise ValueError('missing or unsolicited focus decision')
    sequence = snapshots[0]['records'][1]['sequence']
    for row,(start,action,event) in zip(decisions,windows):
        low = start//1000 + action['start_us']; high = start//1000 + action['end_us'] + 200000
        if row['event'] != event or not low <= row['monotonic_us'] <= high or row['event_type'] != 1 or row['key_symbol'] != 100 or row['state'] != 64 or not row['eligible_event'] or row['native_time'] <= 0:
            raise ValueError('focus decision not bound to exact native chord')
        if row['target_pid'] != foreground['pid'] or row['target_sequence'] != sequence or row['focus_pid'] != icon['pid'] or row['workspace'] != 0 or row['showing'] != (event == 'restore'):
            raise ValueError('focus decision target/workspace differs')
        if event == 'restore' and row['performed'] != (mode == 'restore'):
            raise ValueError('observation control or actual restoration differs')
    if [r['event'] for r in snapshots[0]['records']] != ['clear','remember','entry','restore'] or snapshots[0]['records'][1]['pid'] != foreground['pid'] or sequence <= 0:
        raise ValueError('original retained focus identity differs')
    def between(start,end):return [r for r in all_rows if start <= r['monotonic_us']*1000 < end]
    folder_rows = between(result['folder_started_ns'],result['folder_finished_ns'])
    if [r['event'] for r in folder_rows] != ['clear','abstain','clear','remember','clear']:
        raise ValueError('native folder transition/lifetime differs')
    abstain = folder_rows[1]
    if folder_rows[0]['reason'] != 'notify::minimized' or abstain['eligible_event'] or abstain['event_type'] is not None or abstain['native_time'] != 0 or abstain['target_pid'] is not None or folder_rows[3]['pid'] != input_result['folder']['pid'] or folder_rows[4]['reason'] != 'unmanaging':
        raise ValueError('non-key folder transition did not abstain')
    minimized_rows = between(steps[10]['started_monotonic_ns'],steps[12]['started_monotonic_ns'])
    if [r['event'] for r in minimized_rows] != ['clear','abstain'] or minimized_rows[0]['reason'] != 'notify::minimized' or not minimized_rows[1]['eligible_event'] or minimized_rows[1]['target_pid'] is not None:
        raise ValueError('minimized target was retained/restored')
    return {'mode':mode,'outcome':'pass','original_focus':baseline['focus'],'f9_delivered':baseline['f9_delivered'],
            'f10_delivered':baseline['f10_delivered'],'guards':verdicts,'native_folder_input':'pass',
            'non_key_abstention':'pass','minimized_target_preserved':'pass','disable_restores_default_failure':'pass','cleanup':'confirmed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',required=True,type=Path)
    parser.add_argument('--reports',required=True,nargs=2,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args(); build = args.build_dir.resolve(strict=True); results = []; identities = []
    for path in args.reports:
        path = path.resolve(strict=True)
        if path.parent != build/'native-evidence' or path.stat().st_size > 16*1024**2:raise ValueError('owned bounded report required')
        raw = path.read_bytes(); value = json.loads(raw); results.append(validate(value,build))
        identities.append({'path':str(path),'sha256':digest(raw),'source_base':value['source_base'],'source_inputs':value['source_inputs'],
                           'runtime':{'lab':value['lab_identity_sha256'],'uid':value['environment']['uid'],'folder':value['folder_runtime_identity']['sha256'],'accessibility':value['input_runtime_files']}})
    if sorted(r['mode'] for r in results) != ['observe','restore'] or any(r['source_inputs'] != identities[0]['source_inputs'] or r['runtime'] != identities[0]['runtime'] for r in identities):
        raise ValueError('source/runtime-identical native integration comparison required')
    for name, expected in identities[0]['source_inputs'].items():
        if digest((ROOT/name).read_bytes()) != expected:raise ValueError('current source differs: '+name)
    scripts = ['source/build/record_gnome_focus_integration.py','source/build/record_gnome_focus.py','source/build/record_gnome_reveal.py',
               'source/build/record_gnome_input.py','source/build/record_gnome_composition.py','source/build/record_gnome_host.py',
               'tests/desktop/gnome_focus_integration.py','tests/desktop/gnome_focus_baseline.py','tests/desktop/gnome_input.py',
               'tests/desktop/gnome_reveal.py','tests/desktop/gnome_composition.py','tests/desktop/oracle.py']
    output = args.output.resolve()
    if output.parent != build/'native-evidence':raise ValueError('owned output required')
    record = {'version':'0.1.0','recorded_at':datetime.now(timezone.utc).isoformat(),'outcome':'pass',
              'scope':'Optional owned GNOME X11 event-bound focus restoration and declared interaction guards only',
              'reports':identities,'results':results,'recorder_inputs':{p:digest((ROOT/p).read_bytes()) for p in scripts},
              'not_run':['multiple normal windows/modal focus','workspace changes','lock/session lifecycle','alternate reveal triggers',
                         'default/general enablement','wallpaper policy','Wayland/GPU','other native profiles','full product qualification']}
    with output.open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps(results,indent=2))


if __name__ == '__main__':main()
