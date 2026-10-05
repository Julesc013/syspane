"""Bind the completed historical-toolset experiment to host tests, inputs and PE evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess

from check_legacy_artifacts import EXECUTABLES, build_inputs, verify
from record_protocol import EXPECTED, RECOVERY_CASES, sha

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'windows-x86-v141-xp'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--smoke-result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
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
    for folder in ('source', 'tests/model', 'tests/protocol', 'tests/fault', 'tests/desktop', 'build-support'):
        sources.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts)
    record = {'version': '0.1.0', 'work_ids': ['W-04', 'W-26'], 'profile': PROFILE, 'outcome': 'pass',
              'recorded_at': datetime.now(timezone.utc).isoformat(),
              'execution_times': [line for line in raw.splitlines() if line.startswith(('Start testing:', 'End testing:'))],
              'source_base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': {p.relative_to(ROOT).as_posix(): sha(p) for p in sources},
              'host': {'platform': platform.platform(), 'machine': platform.machine(), 'guest_execution': 'not_run'},
              'cases': cases, 'artifacts': artifacts, 'build_inputs': inputs,
              'profile_sha256': sha(ROOT/'build-support/targets'/f'{PROFILE}.json'),
              'lock_sha256': sha(ROOT/'build-support/targets'/f'{PROFILE}.lock.json'),
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
    print('Historical-toolset evidence recorded: 51 host checks; no guest qualification')


if __name__ == '__main__':
    main()
