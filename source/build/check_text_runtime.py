"""Read-only identity check for the installed native text experiment."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def identify():
    for name in ('FONTCONFIG_FILE', 'FONTCONFIG_PATH', 'FONTCONFIG_SYSROOT'):
        if name in os.environ:
            raise ValueError('text experiment forbids fontconfig override: ' + name)
    packages = ['libpango1.0-dev', 'libpango-1.0-0', 'libpangocairo-1.0-0',
                'libcairo2-dev', 'libcairo2', 'fonts-noto-core', 'libharfbuzz0b',
                'libfontconfig1', 'libfreetype6']
    versions = subprocess.check_output(['dpkg-query', '-W', *packages], text=True)
    paths = [Path('/usr/lib/x86_64-linux-gnu')/name for name in
             ['libpango-1.0.so.0', 'libpangocairo-1.0.so.0', 'libcairo.so.2',
              'libharfbuzz.so.0', 'libfontconfig.so.1', 'libfreetype.so.6']]
    fonts = sorted(set(subprocess.check_output(['fc-list', '-f', '%{file}\n'], text=True).splitlines()))
    configuration = subprocess.check_output(['fc-conflist'], text=True)
    # fc-conflist reports selected (+) and rejected (-) readable configuration.
    for line in configuration.splitlines():
        if line.startswith(('+ ', '- ')):
            name = line[2:].split(': ', 1)[0]
            if Path(name).is_file():
                paths.append(Path(name))
    paths.extend(Path(p) for p in fonts)
    return dict(packages=versions, font_configuration=configuration,
                files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))})


def verify():
    actual = identify()
    expected = json.loads((ROOT/'text-runtime.json').read_text())
    if actual != expected:
        raise ValueError('native text package/font/configuration identity differs; revise explicitly')
    return actual


if __name__ == '__main__':
    value = verify()
    print('native text dependency identity verified:', len(value['files']), 'files')
