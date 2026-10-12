"""Verify the selected native x64 Windows topology/PDH ABI headers, offline."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
compiler=Path(sys.argv[1]).resolve(strict=True)
include=compiler.parent.parent/'x86_64-w64-mingw32/include'
lock=json.loads((root/'windows-processor-sdk.json').read_bytes())
actual={name:hashlib.sha256((include/name).read_bytes()).hexdigest() for name in lock['headers']}
if actual!=lock['headers']:
    raise ValueError('Windows processor ABI headers differ from the admitted lock')
print('Native Windows processor topology/PDH ABI headers verified')
