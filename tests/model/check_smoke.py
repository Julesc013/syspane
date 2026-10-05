import json
from pathlib import Path
import subprocess
import sys

expected = json.loads(Path(__file__).with_name('smoke.expected.json').read_text(encoding='utf-8'))
result = subprocess.run([sys.argv[1]], capture_output=True, text=True, encoding='utf-8', timeout=10)
assert result.returncode == 0, (result.returncode, result.stderr)
assert result.stderr == '', result.stderr
assert json.loads(result.stdout) == expected, result.stdout
print('independent smoke expectation: pass')
