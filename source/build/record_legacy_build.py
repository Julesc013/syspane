"""Bind the completed historical-toolset experiment to host tests, inputs and PE evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess

from check_legacy_artifacts import EXECUTABLES, build_inputs, verify
from record_protocol import EXPECTED, RECOVERY_CASES, IMPORT_CASES, SUBSCRIPTION_CASES, MEASURED_CASES, sha

ROOT = Path(__file__).resolve().parents[2]
PROFILE = 'windows-x86-v141-xp'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--smoke-result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--failure-metadata', action='store_true', help='Include the shared failure-history codec/projection cases')
    parser.add_argument('--preservation', action='store_true', help='Include the portable preservation policy boundary only')
    parser.add_argument('--data-view', action='store_true', help='Include portable synchronized data view cases')
    parser.add_argument('--telemetry', action='store_true', help='Include bounded telemetry document cases')
    parser.add_argument('--state-import', action='store_true', help='Include complete remote state import cases')
    parser.add_argument('--subscriptions', action='store_true', help='Include bounded portable subscription cases')
    parser.add_argument('--measured-time', action='store_true', help='Include measured telemetry and portable freshness cases; native adapter disabled')
    parser.add_argument('--network-reconciliation', action='store_true', help='Include portable network lifetime and counter interval cases; native readers disabled')
    parser.add_argument('--network-publication', action='store_true', help='Include portable measured network projection; native collector disabled')
    parser.add_argument('--network-presentation', action='store_true', help='Require selected measured network renderer projection and prior regressions')
    args = parser.parse_args()
    if args.network_presentation:
        args.network_publication = True
    if args.network_publication:
        args.network_reconciliation = True
    if args.network_reconciliation:
        args.measured_time = True
    if args.measured_time:
        args.subscriptions = True
    if args.subscriptions:
        args.state_import = True
    if args.state_import:
        args.telemetry = True
    if args.telemetry:
        args.data_view = True
    if args.data_view:
        args.preservation = True
    if args.preservation:
        args.failure_metadata = True
    build, smoke_path = args.build_dir.resolve(strict=True), args.smoke_result.resolve(strict=True)
    if platform.system() != 'Windows' or not build.is_relative_to(ROOT/'out/build') or not smoke_path.is_relative_to(ROOT/'out/campaign'/PROFILE):
        raise ValueError('owned Windows experiment outputs required')
    if json.loads((build/'.syspane-owner.json').read_text())['profile'] != PROFILE:
        raise ValueError('experiment profile mismatch')
    raw = (build/'Testing/Temporary/LastTest.log').read_text(encoding='utf-8')
    cases = []
    for block in re.split(r'\n(?=\d+/\d+ Testing:)', '\n'+raw):
        match = re.search(r'\d+/\d+ Testing: (.+)', block)
        if match:
            cases.append({'case': match.group(1).strip(), 'outcome': 'pass' if 'Test Passed.' in block else 'fail'})
    expected = EXPECTED | {f'recovery.{case}' for case in RECOVERY_CASES} | {
        'diagnostic.DIAG-POLICY', 'diagnostic.DIAG-PROJECTION', 'desktop.ORACLE-UNIT', 'legacy.PE-IMPORTS', 'legacy.PE-REJECT'}
    if args.failure_metadata:
        expected |= {'diagnostic.FAILURE-CODEC', 'diagnostic.FAILURE-INTERRUPT', 'diagnostic.FAILURE-PROJECTION'}
    if args.preservation:
        expected.add('diagnostic.PRESERVE-POLICY')
    if args.data_view:
        expected |= {'data.'+case for case in ('VIEW-ATOMIC','VIEW-REPLAY','VIEW-RECONNECT','VIEW-LEASE','VIEW-POLICY','VIEW-FAULT')}
    if args.telemetry:
        expected |= {'telemetry.TELEMETRY-'+case for case in ('SNAPSHOT','MESSAGES','GRAPH','TIME','BOUNDS','PRESERVE')}
    if args.state_import:
        expected |= {'import.IMPORT-'+case for case in IMPORT_CASES}
    if args.subscriptions:
        expected |= {'subscription.'+case for case in SUBSCRIPTION_CASES}
    if args.measured_time:
        expected |= {'measured.'+case for case in MEASURED_CASES}
    if args.network_reconciliation:
        expected |= {'network.RECONCILE-'+case for case in ('IDENTITY', 'CLOCK-RATE', 'CANCEL-FAILURE', 'CAPACITY')}
    if args.network_publication:
        expected |= {'network.PUBLICATION-'+case for case in ('VALUES', 'FAILURE', 'BOUNDARY')}
    if args.network_presentation:
        expected |= {'presentation.NVIEW-'+case for case in ('VALUES','FORMAT','STATES','SELECTION','BOUNDS','LIFETIME')}
    if len(cases) != len(expected) or {c['case'] for c in cases} != expected or any(c['outcome'] != 'pass' for c in cases):
        raise ValueError('incomplete, duplicated or failed historical-toolset host run')
    artifacts = {}
    for name in EXECUTABLES:
        path = build/'Release'/name
        artifacts[name] = {'sha256': sha(path), 'bytes': path.stat().st_size, **verify(path.read_bytes())}
    inputs = build_inputs(build)
    smoke = json.loads(smoke_path.read_text(encoding='utf-8'))
    if smoke['status'] != 'pass' or smoke['profile'] != PROFILE or smoke['payload_sha256'] != artifacts['SysPane.ModelSmoke.exe']['sha256']:
        raise ValueError('relocated smoke does not match tested artifact')
    if sha(smoke_path.parent/smoke['archive']) != smoke['archive_sha256']:
        raise ValueError('local package archive changed')
    for path, digest in smoke['manifest']['source_inputs'].items():
        resolved = (ROOT/path).resolve(strict=True)
        if not resolved.is_relative_to(ROOT) or sha(resolved) != digest:
            raise ValueError('package source checkpoint changed: '+path)
    sources = [ROOT/'CMakeLists.txt', ROOT/'CMakePresets.json', ROOT/'spec/delivery/packages/w-04-historical-windows.md']
    if args.failure_metadata:
        sources.append(ROOT/'spec/delivery/packages/w-25-failure-metadata.md')
    if args.preservation:
        sources.append(ROOT/'spec/delivery/packages/w-25-preservation.md')
    if args.data_view:
        sources.append(ROOT/'spec/delivery/packages/w-25-data-view.md')
    if args.state_import:
        sources.append(ROOT/'spec/delivery/packages/w-25-state-import.md')
    if args.subscriptions:
        sources.append(ROOT/'spec/delivery/packages/w-25-subscriptions.md')
    if args.measured_time:
        sources.append(ROOT/'spec/delivery/packages/w-25-measured-time.md')
    if args.network_reconciliation:
        sources.append(ROOT/'spec/delivery/packages/w-25-network-reconciliation.md')
    if args.network_publication:
        sources.extend([ROOT/'spec/delivery/packages/w-25-network-publication.md', ROOT/'spec/telemetry/metrics.json'])
    if args.telemetry:
        sources.append(ROOT/'spec/delivery/packages/w-25-telemetry-wire.md')
        for folder in ('spec/contracts', 'spec/fixtures'):
            sources.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    if args.network_presentation:
        sources.append(ROOT/'spec/delivery/packages/w-25-network-presentation.md')
    for folder in ('source', 'tests/model', 'tests/protocol', 'tests/fault', 'tests/desktop', 'tests/rendering'):
        sources.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts)
    record = {'version': '0.1.0', 'work_ids': ['W-04', 'W-25', 'W-26'] if args.failure_metadata else ['W-04', 'W-26'], 'profile': PROFILE, 'outcome': 'pass',
              'recorded_at': datetime.now(timezone.utc).isoformat(),
              'execution_times': [line for line in raw.splitlines() if line.startswith(('Start testing:', 'End testing:'))],
              'source_base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for p in sources},
              'host': {'platform': platform.platform(), 'machine': platform.machine(), 'guest_execution': 'not_run'},
              'cases': cases, 'artifacts': artifacts, 'build_inputs': inputs,
              'profile_sha256': sha(ROOT/'source/build/targets'/f'{PROFILE}.json'),
              'lock_sha256': sha(ROOT/'source/build/targets'/f'{PROFILE}.lock.json'),
              'smoke': {'record': args.output.with_suffix('.smoke.json').name, 'original_sha256': sha(smoke_path)},
              'limitations': ['Tests executed on Windows 10 through WOW64; XP/7 runtime, native APIs and desktop behavior remain unqualified.',
                              'PE/declared-import checks do not establish guest exports or dynamic CRT fallback correctness.',
                              'No existing VM was started, snapshotted, modified or captured. Guest laboratory scope is pending.',
                              'MSBuild deprecation warning MSB8051 is retained; compiler warnings remain errors.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    smoke_copy = args.output.with_suffix('.smoke.json')
    smoke_copy.write_text(smoke_path.read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    record['smoke']['sha256'] = sha(smoke_copy)
    log = args.output.with_suffix('.ctest.txt')
    log.write_text(raw, encoding='utf-8', newline='\n')
    record['ctest_log'] = {'record': log.name, 'sha256': sha(log),
                           'original_sha256': sha(build/'Testing/Temporary/LastTest.log'),
                           'normalization': 'UTF-8 text with LF line endings for canonical Git bytes'}
    args.output.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Historical-toolset evidence recorded: {len(cases)} host checks; no guest qualification')


if __name__ == '__main__':
    main()
