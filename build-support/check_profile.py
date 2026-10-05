"""Verify an installed toolchain against the selected development lock, offline."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def output(*args):
    return subprocess.check_output(args, text=True, encoding='utf-8').strip()

def compiler_file(compiler, name):
    value = output(compiler, '-print-file-name=' + name)
    if value == name:
        raise ValueError('compiler cannot resolve ' + name)
    return Path(value).resolve()

def fingerprints(compiler):
    files = {name: Path(shutil.which(name) or '') for name in ('cmake', 'ninja')}
    files['compiler'] = Path(shutil.which(compiler) or compiler).resolve()
    files['cc1plus'] = Path(output(compiler, '-print-prog-name=cc1plus')).resolve()
    files['libstdc++.a'] = compiler_file(compiler, 'libstdc++.a')
    files['libgcc.a'] = compiler_file(compiler, 'libgcc.a')
    return {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}

def main():
    profile, compiler = sys.argv[1:3]
    lock = json.loads((ROOT / 'targets' / (profile + '.lock.json')).read_text(encoding='utf-8'))
    if profile == 'windows-x86-v141-xp':
        actual = {'host_family': platform.system(), 'fingerprints': {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                  for name, path in lock['files'].items()}}
        if Path(compiler).resolve() != Path(lock['files']['compiler']).resolve():
            raise ValueError('historical compiler path differs from pinned toolset')
    else:
        actual = {
            'host_family': platform.system(),
            'compiler_version': output(compiler, '-dumpfullversion'),
            'compiler_target': output(compiler, '-dumpmachine'),
            'fingerprints': fingerprints(compiler)
        }
    if actual != lock['identity']:
        raise ValueError('installed tools differ from pinned profile; record and review an explicit profile revision')
    if len(sys.argv) > 3:
        repo = ROOT.parent.resolve()
        if profile.startswith('linux-'):
            output_root = Path(os.environ['SYSPANE_LINUX_BUILD_ROOT']).resolve()
            allowed = (Path.home() / '.cache/syspane').resolve()
            if not output_root.is_relative_to(allowed) or output_root == allowed:
                raise ValueError('Linux build root must be a bounded task directory under ~/.cache/syspane/')
        else:
            output_root = (repo / 'out/build').resolve()
            if not output_root.is_relative_to(repo):
                raise ValueError('build output escapes repository')
        destination = Path(sys.argv[3]).resolve()
        if not destination.is_relative_to(output_root) or destination == output_root:
            raise ValueError('build output must stay in the owned profile directory')
        if sum(path.stat().st_size for path in output_root.rglob('*') if path.is_file()) > 1024**3:
            raise ValueError('owned build output exceeds the 1 GiB campaign budget')
        destination.mkdir(parents=True, exist_ok=True)
        (destination / '.syspane-owner.json').write_text(json.dumps({'owner': 'SysPane foundation campaign', 'profile': profile, 'generated': True}) + '\n', encoding='utf-8')
    print('profile verified: ' + profile)

if __name__ == '__main__':
    main()
