"""Bind the consuming Linux application to the exact built helper closure."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def generate(helper, profile):
    payload = helper.read_bytes()
    if profile != 'linux-x64-gcc13' or not 64 <= len(payload) <= 67108864:
        raise ValueError('helper profile/size')
    if payload[:7] != b'\x7fELF\x02\x01\x01' or struct.unpack_from('<H', payload, 18)[0] != 62:
        raise ValueError('helper native ELF identity')
    phoff = struct.unpack_from('<Q', payload, 32)[0]
    phsize, count = struct.unpack_from('<HH', payload, 54)
    if phsize != 56 or not 1 <= count <= 64 or phoff+phsize*count > len(payload):
        raise ValueError('helper program headers')
    interpreters = []
    for i in range(count):
        kind, flags, offset, address, physical, filesz, memsz, align = struct.unpack_from('<IIQQQQQQ', payload, phoff+i*phsize)
        if kind == 3:
            if offset+filesz > len(payload): raise ValueError('helper interpreter bounds')
            interpreters.append(payload[offset:offset+filesz])
    if interpreters != [b'/lib64/ld-linux-x86-64.so.2\0']:
        raise ValueError('helper interpreter')
    audit = subprocess.check_output(['objdump', '-p', str(helper)], text=True, encoding='utf-8')
    imports = sorted(re.findall(r'^\s*NEEDED\s+(\S+)\s*$', audit, re.MULTILINE))
    if imports != ['libc.so.6', 'libgcc_s.so.1', 'libm.so.6', 'libstdc++.so.6'] or re.search(r'^\s*(RPATH|RUNPATH)\s', audit, re.MULTILINE):
        raise ValueError('helper loader closure')
    digest = hashlib.sha256(payload).hexdigest()
    record = dict(format='SysPane.Helpers', schema_version='0.1.0', target_profile=profile, product_version='0.0.1',
                  configuration_host=dict(path='libexec/syspane/syspane-configuration-host', sha256=digest, bytes=str(len(payload)), imports=imports))
    raw = json.dumps(record, sort_keys=True, separators=(',', ':')).encode()
    expectation = hashlib.sha256(raw).hexdigest()
    header = ('#pragma once\n#include "installation_linux.hpp"\nnamespace syspane::platform {\n'
              'inline HelperExpectation built_helper_expectation(){return {"'+expectation+'","'+digest+'",'+str(len(payload))+'};}\n}\n').encode()
    return raw, header


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--header', type=Path, required=True)
    args = parser.parse_args()
    record, header = generate(args.helper, args.profile)
    for path, raw in ((args.record, record), (args.header, header)):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != raw: path.write_bytes(raw)
    print('helper closure:', hashlib.sha256(record).hexdigest())


if __name__ == '__main__': main()
