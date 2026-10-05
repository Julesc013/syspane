"""Verify installed GTK development identity; does not install or modify system packages."""
import hashlib
from pathlib import Path
import subprocess

EXPECTED = {
    'libgtk-3-dev': '3.24.41-4ubuntu1.3',
    'libgtk-3-0t64': '3.24.41-4ubuntu1.3',
    'libglib2.0-dev': '2.80.0-6ubuntu3.8',
    'libx11-dev': '2:1.8.7-1build1',
    'xvfb': '2:21.1.12-1ubuntu1.6',
}
for package, version in EXPECTED.items():
    actual = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', package], text=True).strip()
    if actual != version:
        raise ValueError('diagnostic package differs from pinned profile: ' + package)
runtime = Path('/usr/lib/x86_64-linux-gnu/libgtk-3.so.0').resolve(strict=True)
if hashlib.sha256(runtime.read_bytes()).hexdigest() != '0611fd19d1354a39a7cfafceffa3bdf4289d4c497c7f69ff337f86e99cf37d93':
    raise ValueError('diagnostic GTK runtime fingerprint differs')
if hashlib.sha256(Path('/usr/bin/Xvfb').read_bytes()).hexdigest() != '2c7f5a9534410fed5092d782a69ca7ffd9fce80e98b81ffe4944d703dd11d3b1':
    raise ValueError('diagnostic Xvfb test server fingerprint differs')
print('diagnostic toolkit verified: GTK 3.24.41 / Ubuntu 3.24.41-4ubuntu1.3')
