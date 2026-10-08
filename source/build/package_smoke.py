"""Create and relocate an unsigned local development smoke package; never publish."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True, choices=['windows-x64-gcc15', 'linux-x64-gcc13', 'windows-x86-v141-xp'])
    parser.add_argument('--build-dir', type=Path, required=True)
    args = parser.parse_args()
    windows = platform.system() == 'Windows'
    if windows != args.profile.startswith('windows-'):
        raise ValueError('package smoke must execute on its named development OS')
    name = 'SysPane.ModelSmoke' + ('.exe' if windows else '')
    legacy = args.profile == 'windows-x86-v141-xp'
    binary = args.build_dir.resolve() / ('Release/' + name if legacy else name)
    marker = json.loads((args.build_dir / '.syspane-owner.json').read_text(encoding='utf-8'))
    if marker['profile'] != args.profile:
        raise ValueError('build ownership/profile mismatch')
    pe_audit = None
    if legacy:
        from check_legacy_artifacts import verify
        pe_audit = verify(binary.read_bytes())
        imports = list(pe_audit['imports'])
    else:
        imports_text = subprocess.check_output(['objdump', '-p', str(binary)], text=True, encoding='utf-8')
        imports = re.findall(r'DLL Name:\s+(\S+)', imports_text) if windows else re.findall(r'NEEDED\s+(\S+)', imports_text)
    if not imports:
        raise ValueError('dependency audit produced no imports')
    if windows:
        allowed = lambda item: item.lower() == 'kernel32.dll' or re.fullmatch(r'api-ms-win-crt-[a-z0-9-]+\.dll', item.lower())
    else:
        allowed = lambda item: item in ('libstdc++.so.6', 'libgcc_s.so.1', 'libc.so.6', 'libm.so.6')
    if not all(allowed(item) for item in imports):
        raise ValueError('unexpected runtime dependency; update closure before packaging')
    source_files = [ROOT/'CMakeLists.txt', ROOT/'CMakePresets.json', *sorted((ROOT/'source').rglob('*')),
                    *sorted((ROOT/'tests/model').rglob('*'))]
    inputs = {path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in source_files
              if path.is_file() and '__pycache__' not in path.parts and 'evidence' not in path.parts}
    payload = binary.read_bytes()
    manifest = {
        'kind': 'local-development-smoke', 'version': '0.0.1', 'profile': args.profile,
        # This exact shared checkout is explicitly admitted; do not change global
        # Git trust or access credentials from the unprivileged Linux account.
        'source_base': subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT.resolve()), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_inputs': inputs, 'component': 'model-smoke',
        'files': {'bin/' + name: digest(payload)}, 'imports': sorted(imports),
        'qualification': 'model-smoke-only; no desktop or historical-platform claim',
        'publication': 'not authorized; license/notices and product release gates remain open'
    }
    if pe_audit is not None:
        manifest['pe_audit'] = pe_audit
    output_root = ROOT / 'out/campaign' / args.profile
    if not output_root.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('output escapes checkout')
    output_root.mkdir(parents=True, exist_ok=True)
    maximum = json.loads((ROOT/'source/build/campaign-workspace.json').read_text(encoding='utf-8'))['maximum_bytes']
    if sum(p.stat().st_size for p in (ROOT/'out').rglob('*') if p.is_file() and not p.is_relative_to(ROOT/'out/evidence')) + len(payload) * 4 > maximum:
        raise ValueError('campaign output budget exceeded')
    attempt = Path(tempfile.mkdtemp(prefix='smoke-', dir=output_root)).resolve()
    if not attempt.is_relative_to(output_root.resolve()):
        raise ValueError('attempt escapes owned output')
    (attempt/'.syspane-owner.json').write_text(json.dumps({'owner': 'W-26', 'profile': args.profile}), encoding='utf-8')
    filename = f'syspane-0.0.1-{args.profile}-model-development.zip'
    archive = attempt / filename
    entries = {'bin/' + name: payload, 'manifest.json': (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode(),
               'README.txt': b'Local SysPane model smoke experiment. Not a desktop edition or public release.\n'}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for entry, contents in sorted(entries.items()):
            info = zipfile.ZipInfo(entry, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if entry.startswith('bin/') else 0o100644) << 16
            output.writestr(info, contents)
    # Extract only our generated fixed entries. Refuse unexpected members before writing.
    relocated = attempt / 'relocated'
    with zipfile.ZipFile(archive) as packaged:
        if set(packaged.namelist()) != set(entries):
            raise ValueError('package closure mismatch')
        for entry in packaged.namelist():
            destination = relocated / entry
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(packaged.read(entry))
    relocated_binary = relocated / 'bin' / name
    if digest(relocated_binary.read_bytes()) != manifest['files']['bin/' + name]:
        raise ValueError('relocated payload differs')
    # DrvFS cannot chmod under this account. On Linux execute the same archive bytes
    # from a native, owned cache directory; the mounted copy remains inspection evidence.
    execution_dir = relocated
    if not windows:
        cache = Path(os.environ['SYSPANE_LINUX_BUILD_ROOT']).resolve()
        if not cache.is_relative_to((Path.home()/'.cache/syspane').resolve()):
            raise ValueError('unowned Linux execution root')
        execution_dir = Path(tempfile.mkdtemp(prefix='smoke-relocated-', dir=cache))
        (execution_dir/'.syspane-owner.json').write_text('{"owner":"W-26 smoke"}\n')
        relocated_binary = execution_dir / name
        relocated_binary.write_bytes((relocated/'bin'/name).read_bytes())
        relocated_binary.chmod(0o755)
    env = dict(os.environ)
    env['PATH'] = ''
    env.pop('LD_LIBRARY_PATH', None)
    env.pop('LD_PRELOAD', None)
    result = subprocess.run([str(relocated_binary)], cwd=execution_dir, env=env, capture_output=True, text=True, encoding='utf-8', timeout=10)
    expected = json.loads((ROOT/'tests/model/smoke.expected.json').read_text(encoding='utf-8'))
    passed = result.returncode == 0 and result.stderr == '' and json.loads(result.stdout) == expected
    evidence = {'status': 'pass' if passed else 'fail', 'profile': args.profile,
                'archive': filename, 'archive_sha256': digest(archive.read_bytes()),
                'payload_sha256': digest(payload), 'imports': sorted(imports),
                'relocated_execution': {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'path_empty': True},
                'manifest': manifest}
    (attempt/'result.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': evidence['status'], 'result': str((attempt/'result.json').relative_to(ROOT)), 'archive_sha256': evidence['archive_sha256']}))
    if not passed:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
