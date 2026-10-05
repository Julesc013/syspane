"""Record an existing complete portable CTest run; does not attest native IPC."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODEL_CASES = 'STATE-01 STATE-02 STATE-03 STATE-04 STATE-05 VALIDITY-01 VALIDITY-02 CLOCK-01 CLOCK-02 BOUNDS-01 BOUNDS-02 BOUNDS-03 OBSERVATION-01 EPOCH-01 FRESHNESS-01 smoke'.split()
PROTOCOL_CASES = 'FRAME-01 FRAME-02 FRAME-03 JSON-01 WIRE-01 NEGOTIATE-01 IPC-BUDGET-01 IPC-BUDGET-02 IPC-BUDGET-03 IPC-BUDGET-04 LEDGER-01 POLICY-01 POLICY-02 DISCLOSURE-01 QUEUE-01 SESSION-01 dependencies'.split()
EXPECTED = {f'model.{case}' for case in MODEL_CASES} | {f'protocol.{case}' for case in PROTOCOL_CASES} | {'composition.graph', 'composition.reject_forbidden'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    if json.loads((build/'.syspane-owner.json').read_text())['profile'] != args.profile:
        raise ValueError('build ownership/profile mismatch')
    log = build/'Testing/Temporary/LastTest.log'
    raw = log.read_text(encoding='utf-8')
    cases = []
    for block in re.split(r'\n(?=\d+/\d+ Testing:)', '\n' + raw):
        match = re.search(r'\d+/\d+ Testing: (.+)', block)
        if match:
            name = match.group(1).strip()
            cases.append({'case': name, 'outcome': 'pass' if 'Test Passed.' in block else 'fail',
                          'command': 'ctest --preset ' + args.profile + ' -R ^' + re.escape(name) + '$ --output-on-failure'})
    if len(cases) != len(EXPECTED) or {case['case'] for case in cases} != EXPECTED or any(case['outcome'] != 'pass' for case in cases):
        raise ValueError('missing, repeated, unexpected or failing case; preserve log before rerun')
    suffix = '.exe' if platform.system() == 'Windows' else ''
    artifacts = {name: {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
                 for name in ('syspane_protocol_tests'+suffix, 'libsyspane_protocol.a', 'libsyspane_configuration.a', 'generated/settings_descriptors.hpp')}
    paths = [ROOT/'CMakeLists.txt', ROOT/'CMakePresets.json', ROOT/'spec/experience/settings-registry.json',
             ROOT/'spec/delivery/packages/w-24-transport.md', ROOT/'spec/assurance/acceptance-traces.md']
    for directory in ('source', 'tests', 'build-support', 'spec/contracts'):
        paths.extend(sorted((ROOT/directory).rglob('*')))
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths
              if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts}
    log_output = args.output.with_suffix('.ctest.txt')
    report = {'work_id': 'W-24', 'slice': 'portable transport, session and policy', 'work_status': 'in_progress',
              'profile': args.profile, 'outcome': 'pass', 'recorded_at': datetime.now().astimezone().isoformat(timespec='seconds'),
              'execution_times': [line for line in raw.splitlines() if line.startswith(('Start testing:', 'End testing:'))],
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory='+str(ROOT.resolve()), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': inputs, 'artifacts': artifacts, 'cases': cases,
              'bindings': {'portable_cases': 'tests/protocol/protocol_tests.cpp', 'contract': 'spec/delivery/packages/w-24-transport.md',
                           'request_oracles': 'spec/assurance/acceptance-traces.md', 'descriptor_input': 'spec/experience/settings-registry.json'},
              'environment': {'os': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
                              'execution': 'native Windows process' if suffix else 'Linux ELF process under WSL2'},
              'original_ctest_log_sha256': sha(log), 'normalized_ctest_log': log_output.name,
              'limits': ['Typed authentication contexts in tests are fixtures, not OS peer-authentication evidence.',
                         'No native IPC adapter, persistent commit, telemetry subscription, GUI, recovery or desktop qualification.',
                         'W-24 is incomplete; its native/session-stream integration cases remain required.',
                         'No public release, privileged operation, human review or project-license decision is attested.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log_output.write_text(raw.replace(str(build), '<build>').replace(str(ROOT), '<source>'), encoding='utf-8', newline='\n')
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'profile': args.profile, 'cases': len(cases), 'outcome': 'pass', 'native_ipc': 'not_run'}))


if __name__ == '__main__':
    main()
