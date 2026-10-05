"""Capture existing CTest/artifact evidence; this command does not execute tests."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    marker = json.loads((build/'.syspane-owner.json').read_text())
    if marker['profile'] != args.profile:
        raise ValueError('profile mismatch')
    log_path = build/'Testing/Temporary/LastTest.log'
    raw = log_path.read_text(encoding='utf-8')
    blocks = re.split(r'\n(?=\d+/\d+ Testing:)', '\n' + raw)
    cases = []
    for block in blocks:
        match = re.search(r'\d+/\d+ Testing: (.+)', block)
        if match:
            cases.append({'case': match.group(1).strip(), 'outcome': 'pass' if 'Test Passed.' in block else 'fail',
                          'command': 'ctest --preset ' + args.profile + ' -R ^' + re.escape(match.group(1).strip()) + '$ --output-on-failure'})
    if len(cases) != 18 or not all(case['outcome'] == 'pass' for case in cases):
        raise ValueError('incomplete or failing foundation result; preserve log and investigate')
    suffix = '.exe' if platform.system() == 'Windows' else ''
    artifacts = {name: {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
                 for name in ('SysPane.ModelSmoke'+suffix, 'syspane_model_tests'+suffix, 'libsyspane_model.a')}
    paths = [ROOT/'CMakeLists.txt', ROOT/'CMakePresets.json', *sorted((ROOT/'source').rglob('*')),
             *sorted((ROOT/'tests/model').rglob('*')), *sorted((ROOT/'build-support').rglob('*'))]
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths if p.is_file() and '__pycache__' not in p.parts and 'evidence' not in p.parts}
    normalized_log = raw.replace(str(build), '<build>').replace(str(ROOT), '<source>')
    log_output = args.output.with_suffix('.ctest.txt')
    report = {'work_id': 'W-01', 'profile': args.profile, 'outcome': 'pass',
              'recorded_at': datetime.now().astimezone().isoformat(timespec='seconds'),
              'execution_times': [line for line in raw.splitlines() if line.startswith(('Start testing:', 'End testing:'))],
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory='+str(ROOT.resolve()), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': inputs, 'artifacts': artifacts, 'cases': cases,
              'environment': {'os': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
                              'execution': 'native Windows process' if suffix else 'Linux ELF process under WSL2'},
              'original_ctest_log_sha256': sha(log_path),
              'normalized_ctest_log': log_output.name,
              'limits': ['Synthetic model, smoke and component-graph cases only.',
                         'No native desktop, actual clock adapter, collector, IPC/policy or recovery qualification.',
                         'Configure/build commands ran before these tests; this recorder captures their existing outputs.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log_output.write_text(normalized_log, encoding='utf-8', newline='\n')
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'profile': args.profile, 'cases': len(cases), 'outcome': 'pass'}))

if __name__ == '__main__':
    main()
