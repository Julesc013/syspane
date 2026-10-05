"""Record an existing complete CTest run and its explicitly selected IPC scope."""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MODEL_CASES = 'STATE-01 STATE-02 STATE-03 STATE-04 STATE-05 VALIDITY-01 VALIDITY-02 CLOCK-01 CLOCK-02 BOUNDS-01 BOUNDS-02 BOUNDS-03 OBSERVATION-01 EPOCH-01 FRESHNESS-01 smoke'.split()
PROTOCOL_CASES = 'FRAME-01 FRAME-02 FRAME-03 JSON-01 WIRE-01 NEGOTIATE-01 IPC-BUDGET-01 IPC-BUDGET-02 IPC-BUDGET-03 IPC-BUDGET-04 LEDGER-01 POLICY-01 POLICY-02 DISCLOSURE-01 QUEUE-01 SESSION-01 dependencies'.split()
RECOVERY_CASES = 'LEASE-01 LEASE-02 LEASE-03 LEASE-04 LEASE-05 RENDER-01 RENDER-02 RETRY-01 RETRY-02 RETRY-03 RECOVERY-CLOCK'.split()
EXPECTED = {f'model.{case}' for case in MODEL_CASES} | {f'protocol.{case}' for case in PROTOCOL_CASES} | {'composition.graph', 'composition.reject_forbidden'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native', action='store_true', help='Require both real local-IPC families and their concrete case records')
    parser.add_argument('--recovery', action='store_true', help='Record W-25 portable guards; requires native regression cases as well')
    parser.add_argument('--supervision', action='store_true', help='Require the native owned-child supervision family')
    parser.add_argument('--diagnostic', action='store_true', help='Require independent diagnostic entry and native close checks')
    parser.add_argument('--oracle', action='store_true', help='Require portable temporal oracle and Linux native pixel calibration')
    parser.add_argument('--failure-metadata', action='store_true', help='Require bounded failure metadata and all current native regression families')
    parser.add_argument('--preservation', action='store_true', help='Require explicit private file preservation and native UI bindings')
    parser.add_argument('--data-view', action='store_true', help='Require synchronized model/lease/policy view cases')
    parser.add_argument('--telemetry', action='store_true', help='Require bounded telemetry document cases; no native subscription claim')
    args = parser.parse_args()
    if args.telemetry:
        args.data_view = True
    if args.data_view:
        args.preservation = True
    if args.preservation:
        args.failure_metadata = True
    if args.failure_metadata:
        args.oracle = True
    if args.oracle:
        args.diagnostic = True
    if args.diagnostic:
        args.supervision = True
    if args.supervision:
        args.recovery = True
    if args.recovery:
        args.native = True
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
    expected = EXPECTED | ({'native.NATIVE-01', 'native.NATIVE-02'} if args.native else set())
    if args.recovery:
        expected |= {f'recovery.{case}' for case in RECOVERY_CASES}
    if args.supervision:
        expected.add('native.RECOVERY-01')
    if args.diagnostic:
        expected |= {'diagnostic.DIAG-POLICY', 'diagnostic.DIAG-PROJECTION', 'native.DIAG-01'}
    if args.oracle:
        expected.add('desktop.ORACLE-UNIT')
        if platform.system() != 'Windows':
            expected.add('native.ORACLE-01')
    if args.failure_metadata:
        expected |= {'diagnostic.FAILURE-CODEC', 'diagnostic.FAILURE-INTERRUPT', 'diagnostic.FAILURE-PROJECTION', 'native.FAILURE-STORE'}
    if args.preservation:
        expected |= {'diagnostic.PRESERVE-POLICY', 'native.PRESERVE'}
    if args.data_view:
        expected |= {'data.'+case for case in ('VIEW-ATOMIC', 'VIEW-REPLAY', 'VIEW-RECONNECT', 'VIEW-LEASE', 'VIEW-POLICY', 'VIEW-FAULT')}
    if args.telemetry:
        expected |= {'telemetry.TELEMETRY-'+case for case in ('SNAPSHOT', 'MESSAGES', 'GRAPH', 'TIME', 'BOUNDS', 'PRESERVE')}
    if len(cases) != len(expected) or {case['case'] for case in cases} != expected or any(case['outcome'] != 'pass' for case in cases):
        raise ValueError('missing, repeated, unexpected or failing case; preserve log before rerun')
    suffix = '.exe' if platform.system() == 'Windows' else ''
    artifacts = {name: {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
                 for name in ('syspane_protocol_tests'+suffix, 'libsyspane_protocol.a', 'libsyspane_configuration.a', 'generated/settings_descriptors.hpp')}
    native_records = []
    if args.telemetry:
        name = 'syspane_telemetry_tests'+suffix
        artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
    if args.data_view:
        for name in ('syspane_data_view_tests'+suffix, 'libsyspane_data_view.a', 'libsyspane_model.a'):
            artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
    import_audit = None
    if args.recovery:
        for name in ('syspane_recovery_tests'+suffix, 'libsyspane_recovery.a', 'component-graph.txt'):
            artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
    if args.native:
        for name in ('SysPane.IpcProbe'+suffix, 'libsyspane_local_ipc.a'):
            artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
        required = {
            'NATIVE-01': {'JOURNEY', 'LOST-ACK', 'SATURATION', 'PARTIAL-EOF', 'MALFORMED', 'NEGOTIATED-LIMIT', 'HELLO-TIMEOUT', 'FRAME-TIMEOUT', 'WRITE-TIMEOUT'},
            'NATIVE-02': {'COLLISION', 'SERVER-PROCESS-DENIAL', 'CLIENT-PROCESS-DENIAL', 'ROLE-SPOOF', 'FORGED-AUTHORITY', 'OLD-EPOCH'}
        }
        if not suffix:
            required['NATIVE-02'].add('POSIX-SESSION-DENIAL')
        if args.supervision:
            for name in ('SysPane.RecoveryProbe'+suffix, 'libsyspane_child.a', 'libsyspane_health.a'):
                artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
            required['RECOVERY-01'] = {'CHILD-GRACEFUL','PRODUCER-HANG','RENDER-STALL','CRASH-CIRCUIT','QUARANTINE','PARENT-LOSS','ROLE-DENIAL','WRONG-EPOCH','PROGRESS-DENIAL'}
        if args.diagnostic:
            for name in (('SysPane.Diag.exe' if suffix else 'syspane-diag'), 'syspane_diagnostic_tests'+suffix,
                         'libsyspane_diagnostic.a', 'libsyspane_machine_policy.a', 'libsyspane_diagnostic_inspector.a'):
                artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
            required['DIAG-01'] = {'REPORT', 'DAMAGED', 'ARGUMENTS', 'NATIVE-CLOSE'}
            if not suffix:
                required['DIAG-01'].add('NO-DISPLAY')
        if args.oracle and not suffix:
            artifacts['SysPane.OracleProbe'] = {'sha256': sha(build/'SysPane.OracleProbe'), 'bytes': (build/'SysPane.OracleProbe').stat().st_size}
            required['ORACLE-01'] = {'LIVE','DISAPPEAR','FREEZE','OCCLUDE','GAP'}
        if args.failure_metadata:
            for name in ('syspane_failure_store_tests'+suffix, 'libsyspane_failure_store.a'):
                artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
            required['DIAG-01'].add('FAILURE-METADATA')
            required['FAILURE-STORE'] = {'ROUNDTRIP-UNICODE', 'EXCLUSIVE', 'CAPACITY', 'REGRESSION-LATCH', 'OPEN-WRITER-READ',
                                         'INTERRUPTED-INVALID', 'OVERSIZE', 'HARDLINK', 'PATH-TYPE',
                                         'WINDOWS-PRIVATE-DACL' if suffix else 'POSIX-PERMISSIONS-LINK-FIFO'}
        seen = set()
        if args.preservation:
            for name in ('syspane_preservation_tests'+suffix, 'libsyspane_preservation_job.a'):
                artifacts[name] = {'sha256': sha(build/name), 'bytes': (build/name).stat().st_size}
            required['PRESERVE'] = {'BINARY-UNICODE-PRIVATE', 'EXACT-NAMES', 'EMPTY', 'EXISTING-NAMES', 'PATH-TYPE', 'POLICY-CANCEL-PHASES',
                'PUBLICATION-COLLISION', 'STAGING-COLLISION', 'HARDLINK', 'EXTERNAL-TERMINATION', 'REAL-CLI-DENIAL',
                'UI-COPY', 'UI-CLOSE', 'UI-REVOKE', 'UI-CANCEL', 'SIZE-BOUNDARY',
                'WRITER-SHARING-DACL' if suffix else 'SOURCE-CHANGE-PERMISSIONS-FIFO'}
            if not suffix:
                required['PRESERVE'].add('LEAF-LINKS')
        for name in re.findall(r'^Native evidence: (.+)$', raw, re.M):
            path = Path(name.strip()).resolve()
            if not path.is_relative_to(build/'native-evidence'):
                raise ValueError('native evidence path escaped owned build')
            native = json.loads(path.read_text(encoding='utf-8'))
            family = native['family']
            if family not in required or family in seen:
                raise ValueError('unknown/repeated native family')
            seen.add(family)
            expected_cases = {family+'.'+case for case in required[family]}
            if family == 'PRESERVE' and suffix:
                if any(case['case'] == 'PRESERVE.LEAF-LINKS' for case in native['cases']):
                    expected_cases.add('PRESERVE.LEAF-LINKS')
                elif 'Windows symlink creation privilege unavailable; source/dangling reparse cases not executed.' not in native['limitations']:
                    raise ValueError('Windows preservation link case needs execution or its exact privilege limitation')
            if args.failure_metadata and family == 'FAILURE-STORE' and suffix:
                if any(case['case'] == 'FAILURE-STORE.WINDOWS-REPARSE' for case in native['cases']):
                    expected_cases.add('FAILURE-STORE.WINDOWS-REPARSE')
                elif 'Windows symlink creation requires an unavailable privilege; reparse rejection case not executed.' not in native['limitations']:
                    raise ValueError('Windows reparse case must execute or retain its exact privilege limitation')
            if native['outcome'] != 'pass' or len(native['cases']) != len(expected_cases) or {case['case'] for case in native['cases']} != expected_cases or any(case['outcome'] != 'pass' for case in native['cases']):
                raise ValueError('native case missing or failed; preserve original report')
            if family in ('RECOVERY-01', 'DIAG-01', 'ORACLE-01', 'FAILURE-STORE', 'PRESERVE'):
                executable = {'RECOVERY-01':'SysPane.RecoveryProbe'+suffix, 'DIAG-01':'SysPane.Diag.exe' if suffix else 'syspane-diag', 'ORACLE-01':'SysPane.OracleProbe', 'FAILURE-STORE':'syspane_failure_store_tests'+suffix, 'PRESERVE':'syspane_preservation_tests'+suffix}[family]
                if family == 'PRESERVE' and native['diagnostic_sha256'] != sha(build/('SysPane.Diag.exe' if suffix else 'syspane-diag')):
                    raise ValueError('preservation CLI artifact changed after run')
                if native['executable_sha256'] != sha(build/executable):
                    raise ValueError('native executable changed after run')
                for source, digest in native['source_inputs'].items():
                    if sha(ROOT/source) != digest:
                        raise ValueError('recovery input changed after native run: '+source)
                if family == 'RECOVERY-01':
                    for case in native['cases']:
                        if not case['child_observations'] or not all(c['observed_alive'] and c['observed_exited'] for c in case['child_observations']):
                            raise ValueError('native child observation missing')
                        if args.failure_metadata:
                            metadata = case['failure_metadata']
                            journal = (build/'native-evidence'/metadata['record']).resolve()
                            if not journal.is_relative_to(build/'native-evidence') or sha(journal) != metadata['sha256'] or journal.read_text(encoding='utf-8') != metadata['text']:
                                raise ValueError('failure journal source/bytes differ from observed native faults')
                elif family == 'DIAG-01':
                    close = next(case for case in native['cases'] if case['case'] == 'DIAG-01.NATIVE-CLOSE')
                    if native['profile'] != args.profile or not close['pid_verified'] or not close['title_verified'] or not close['class_verified'] or close['exit'] != 0:
                        raise ValueError('diagnostic native close identity/exit evidence missing')
                elif family == 'ORACLE-01':
                    specification = importlib.util.spec_from_file_location('syspane_external_oracle', ROOT/'tests/desktop/oracle.py')
                    oracle = importlib.util.module_from_spec(specification)
                    specification.loader.exec_module(oracle)
                    outcomes = {'LIVE':'pass','DISAPPEAR':'fail','FREEZE':'fail','OCCLUDE':'fail','GAP':'inconclusive'}
                    for case in native['cases']:
                        computed = oracle.evaluate(case['trace'])
                        if computed != case['observation'] or computed['outcome'] != outcomes[case['case'].split('.')[-1]]:
                            raise ValueError('native pixel evidence does not reproduce the fixed oracle')
                        if case['candidate_exit'] != 0 or case['observer_exit'] != 0 or case['server_exit'] is None or not case['root_restored'] or case['root_before_sha256'] != case['root_after_sha256'] or case['root_configuration_before'] != case['root_configuration_after']:
                            raise ValueError('native calibration cleanup/root evidence missing')
                        journal = (build/case['capture_journal']['path']).resolve()
                        if not journal.is_relative_to(build) or sha(journal) != case['capture_journal']['sha256']:
                            raise ValueError('capture journal identity/ownership differs')
            destination = args.output.with_suffix('.'+family+'.json')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
            native_records.append({'family': family, 'record': destination.name, 'sha256': sha(path), 'cases': len(expected_cases),
                                   'qualification': native['qualification']})
        if seen != set(required):
            raise ValueError('required native family has no bound report in this CTest log')
        inspector = 'objdump' if suffix else 'readelf'
        executable = ('SysPane.Diag.exe' if suffix else 'syspane-diag') if args.diagnostic else (('SysPane.RecoveryProbe' if args.supervision else 'SysPane.IpcProbe')+suffix)
        if args.oracle and not suffix:
            executable = 'SysPane.OracleProbe'
        command = [inspector, '-p' if suffix else '-d', str(build/executable)]
        inspected = subprocess.check_output(command, text=True, encoding='utf-8')
        imports = re.findall(r'DLL Name:\s*(\S+)', inspected) if suffix else re.findall(r'\(NEEDED\).*?\[([^]]+)\]', inspected)
        if not imports:
            raise ValueError('native import inspection returned no dependency records')
        import_audit = {'command': command, 'tool': subprocess.check_output([inspector, '--version'], text=True).splitlines()[0],
                        'direct_dependencies': imports, 'scope': 'Observed direct imports only; no inferred historical OS or loader qualification.'}
    paths = [ROOT/'CMakeLists.txt', ROOT/'CMakePresets.json', ROOT/'spec/experience/settings-registry.json',
             ROOT/'spec/delivery/packages/w-24-transport.md', ROOT/'spec/assurance/acceptance-traces.md']
    if args.recovery:
        paths.extend([ROOT/'spec/delivery/packages/w-25-recovery.md', ROOT/'spec/architecture/recovery.md'])
    if args.oracle:
        paths.extend([ROOT/'spec/delivery/packages/w-02-desktop-oracle.md', ROOT/'spec/assurance/desktop-oracle.md'])
    if args.failure_metadata:
        paths.append(ROOT/'spec/delivery/packages/w-25-failure-metadata.md')
    if args.preservation:
        paths.append(ROOT/'spec/delivery/packages/w-25-preservation.md')
    if args.data_view:
        paths.append(ROOT/'spec/delivery/packages/w-25-data-view.md')
    if args.telemetry:
        paths.append(ROOT/'spec/delivery/packages/w-25-telemetry-wire.md')
        paths.extend(sorted((ROOT/'spec/fixtures').rglob('*')))
    for directory in ('source', 'tests', 'build-support', 'spec/contracts'):
        paths.extend(sorted((ROOT/directory).rglob('*')))
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths
              if p.is_file() and 'evidence' not in p.parts and '__pycache__' not in p.parts}
    log_output = args.output.with_suffix('.ctest.txt')
    report = {'work_id': 'W-24', 'slice': 'native local IPC and portable transport/policy' if args.native else 'portable transport, session and policy',
              'work_status': 'implemented' if args.native else 'in_progress',
              'profile': args.profile, 'outcome': 'pass', 'recorded_at': datetime.now().astimezone().isoformat(timespec='seconds'),
              'execution_times': [line for line in raw.splitlines() if line.startswith(('Start testing:', 'End testing:'))],
              'source_base': subprocess.check_output(['git', '-c', 'safe.directory='+str(ROOT.resolve()), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_inputs': inputs, 'artifacts': artifacts, 'cases': cases,
              'bindings': {'portable_cases': 'tests/protocol/protocol_tests.cpp', 'contract': 'spec/delivery/packages/w-24-transport.md',
                           'request_oracles': 'spec/assurance/acceptance-traces.md', 'descriptor_input': 'spec/experience/settings-registry.json'},
              'environment': {'os': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
                              'execution': 'native Windows process' if suffix else 'Linux ELF process under WSL2',
                              'preset_environment': {} if suffix else {'SYSPANE_LINUX_BUILD_ROOT': str(build.parent)}},
              'original_ctest_log_sha256': sha(log), 'normalized_ctest_log': log_output.name, 'native_records': native_records,
              'import_audit': import_audit,
              'limits': ['Typed authentication contexts in tests are fixtures, not OS peer-authentication evidence.',
                         'No native IPC adapter, persistent commit, telemetry subscription, GUI, recovery or desktop qualification.',
                         'W-24 is incomplete; its native/session-stream integration cases remain required.',
                         'No public release, privileged operation, human review or project-license decision is attested.']}
    if args.native:
        report['limits'] = ['Initial native probe is single-connection and bounded to two sequential clients; not a production service.',
                            'Actual same-user Windows user/logon/session and Linux UID/POSIX-session checks ran; cross-user and Windows cross-logon qualification are blocked.',
                            'Linux requires SO_PEERPIDFD and the measured WSL2 environment; POSIX session is not a desktop login session.',
                            'No persistent commit, telemetry subscription, GUI, independent recovery or desktop qualification.',
                            'No public release, privileged operation, human review or project-license decision is attested.']
    if args.recovery:
        report.update(work_id='W-25', slice='portable producer lease, render progress and restart budget', work_status='in_progress')
        report['bindings']['recovery_cases'] = 'tests/fault/recovery_tests.cpp'
        report['bindings']['recovery_contract'] = 'spec/delivery/packages/w-25-recovery.md'
        report['limits'] = [
            'Recovery cases use injected local monotonic time and typed events; no real producer freeze, render stall or process termination is attested.',
            'Guard decisions do not prove native scheduling latency, process ownership, policy data erasure or visible recovery.',
            'Independent native diagnostic entry, conservative inspector and keyboard/exit recovery remain mandatory W-25 work.',
            'Native local IPC regression cases retain their original development-only scope and blocked cross-user/logon qualification.',
            'W-25 and the full campaign remain incomplete; no desktop support, public release or privileged operation is claimed.'
        ]
    if args.supervision:
        report['slice'] = 'native owned-child supervision and independent health/render-worker progress'
        report['bindings']['native_recovery_cases'] = 'tests/fault/native_recovery.py'
        report['limits'] = [
            'Nine real native synthetic worker cases; render-worker completion draws no pixels and does not qualify a renderer or desktop host.',
            'Only self-child launch is enabled; inherited environment is trusted development input, not a hostile-code isolation boundary.',
            'No full snapshot/delta, diagnostic entry/inspector, native editor exit or policy-driven payload erasure is implemented by this boundary.',
            'W-25 and the full campaign remain incomplete. Historical/Mac and cross-user/logon qualification remain pending or blocked.',
            'No privileged operation, public release or human review is attested.'
        ]
    if args.diagnostic:
        report['slice'] = 'independent read-only diagnostic entry, native inspector and protected-policy reader'
        report['bindings']['diagnostic_cases'] = 'tests/fault/diagnostic_tests.cpp'
        report['bindings']['native_diagnostic_cases'] = 'tests/fault/native_diagnostic.py'
        report['limits'] = [
            'Only public built-in profile/build metadata is read; recent-failure metadata, preservation and recovery controls remain pending.',
            'Native window-close checks are hidden; no visible pixels, accessibility qualification, editor-exit recovery or desktop host is attested.',
            'Installed protected machine policy was not created or changed; positive provenance/revocation deployment needs a separately admitted administrative lab.',
            'GTK dependency identities cover selected installed packages/runtime, not complete transitive redistribution or Wayland qualification.',
            'W-25 and the campaign remain incomplete. No privileged operation, public release or human review is attested.'
        ]
    if args.oracle:
        report.update(work_id='W-02', slice='independent temporal pixel oracle and native X11 calibration', work_status='in_progress')
        report['bindings']['oracle'] = 'tests/desktop/oracle.py'
        report['bindings']['oracle_contract'] = 'spec/delivery/packages/w-02-desktop-oracle.md'
        report['bindings']['oracle_cases'] = 'tests/desktop/test_oracle.py'
        report['bindings']['native_oracle_cases'] = 'tests/desktop/native_oracle.py'
        report['limits'] = [
            'Calibration uses actual owned Xvfb root pixels on Linux and portable golden/time cases on Windows. No user desktop is captured.',
            'Expected fail/inconclusive observations are successful negative calibrations, not product desktop passes.',
            'No named shell reveal action, icon-manager input/focus, real wallpaper policy/file or Windows external desktop capture is qualified.',
            'X11 window PID properties are structural checks within the private trusted test server, not peer authentication for arbitrary clients.',
            'W-02, W-25 and the full campaign remain incomplete. No privileged action, shell restart, public release or human review is attested.'
        ]
    if args.failure_metadata:
        report.update(work_id='W-25', slice='bounded recent-failure recording and independent policy-gated diagnosis', work_status='in_progress')
        report['bindings']['failure_metadata'] = 'spec/delivery/packages/w-25-failure-metadata.md'
        report['limits'] = [
            'Failure files are unverified advisory records from synthetic owned-process faults; they do not establish live health, configuration durability or product retention.',
            'Native unavailable-policy reporting and hidden Close ran; positive disclosure/revocation uses typed portable fixtures, not installed protected-policy deployment.',
            'Windows symlink/reparse creation may remain unexecuted under current privileges; the native report preserves the exact limitation.',
            'Configuration preservation, real renderer/data recovery and independent editor exit remain required W-25 work.',
            'Oracle captures remain owned Xvfb calibration; no new desktop or historical OS qualification, privileged action or public release is attested.'
        ]
    if args.preservation:
        report.update(work_id='W-25', slice='explicit private configuration preservation and native controls', work_status='in_progress')
        report['bindings']['preservation'] = 'spec/delivery/packages/w-25-preservation.md'
        report['limits'] = [
            'Opaque preservation never repairs, activates or restores configuration; file flush/readback is not power-loss durability.',
            'Native UI success/revocation/cancellation uses typed policy fixtures and programmatic widgets; installed positive policy and external accessibility/input qualification remain pending.',
            'Foreign-owner and unsupported-filesystem execution remain unqualified; Windows leaf-link privilege limitations are preserved explicitly.',
            'Actual unavailable-policy CLI denies without creating copy/partial files; no protected policy was installed or changed.',
            'W-25 product retention, live telemetry/renderer recovery, payload revocation and independent editor exit remain open.',
            'No desktop host, historical OS, privileged action or public release is attested.'
        ]
    if args.data_view:
        report.update(work_id='W-25', slice='synchronized model, independent producer lease and policy-bound data lifetime', work_status='in_progress')
        report['bindings']['data_view'] = 'spec/delivery/packages/w-25-data-view.md'
        report['limits'].insert(0, 'Data view cases use typed in-process candidates; no wire subscription, collector, renderer, native data-erasure or visible-recovery qualification follows.')
    if args.telemetry:
        report['slice'] = 'bounded telemetry document decoding and exact replay preservation'
        report['bindings']['telemetry'] = 'spec/delivery/packages/w-25-telemetry-wire.md'
        report['limits'].insert(0, 'Telemetry codec checks preserve complete documents, including partial/gap and reported retained values; no native subscription, model-state import or policy grant is enabled.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log_output.write_text(raw.replace(str(build), '<build>').replace(str(ROOT), '<source>'), encoding='utf-8', newline='\n')
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'profile': args.profile, 'cases': len(cases), 'outcome': 'pass', 'native_ipc': 'executed' if args.native else 'not_run',
                      'recovery': 'native_supervision' if args.supervision else ('portable_only' if args.recovery else 'not_recorded')}))


if __name__ == '__main__':
    main()
