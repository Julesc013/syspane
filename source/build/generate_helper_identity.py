"""Bind the consuming Linux application to the exact built helper closure."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


BASE_IMPORTS = ['libc.so.6', 'libgcc_s.so.1', 'libm.so.6', 'libstdc++.so.6']
IMAGE_IMPORTS = ['libc.so.6', 'libgcc_s.so.1', 'libgdk_pixbuf-2.0.so.0', 'libglib-2.0.so.0', 'libgobject-2.0.so.0', 'libstdc++.so.6']


def identify(helper, profile, role):
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
    if imports != (IMAGE_IMPORTS if role == 'image_worker' else BASE_IMPORTS) or re.search(r'^\s*(RPATH|RUNPATH)\s', audit, re.MULTILINE):
        raise ValueError('helper loader closure')
    digest = hashlib.sha256(payload).hexdigest()
    names = {'configuration_host': 'syspane-configuration-host', 'image_worker': 'syspane-image-worker', 'recovery_worker': 'syspane-recovery-worker'}
    return dict(path='libexec/syspane/'+names[role], sha256=digest, bytes=str(len(payload)), imports=imports)


def generate(helper, profile, image_helper=None, recovery_helper=None):
    if (image_helper is None) != (recovery_helper is None):
        raise ValueError('both editor helpers are required')
    configuration = identify(helper, profile, 'configuration_host')
    record = dict(format='SysPane.Helpers', schema_version='0.1.0', target_profile=profile, product_version='0.0.1',
                  configuration_host=configuration)
    if image_helper is not None:
        record.pop('configuration_host'); record['schema_version'] = '0.2.0'
        record['helpers'] = dict(configuration_host=configuration, image_worker=identify(image_helper, profile, 'image_worker'),
                                 recovery_worker=identify(recovery_helper, profile, 'recovery_worker'))
    raw = json.dumps(record, sort_keys=True, separators=(',', ':')).encode()
    expectation = hashlib.sha256(raw).hexdigest()
    header = '#pragma once\n#include "installation_linux.hpp"\nnamespace syspane::platform {\n'
    if image_helper is None:
        header += 'inline HelperExpectation built_helper_expectation(){return {"'+expectation+'","'+configuration['sha256']+'",'+configuration['bytes']+'};}\n}\n'
    else:
        entries = ','.join('{"'+v['sha256']+'",'+v['bytes']+'}' for v in record['helpers'].values())
        header += 'inline HelperBundleExpectation built_helper_bundle_expectation(){return {"'+expectation+'",{{'+entries+'}}};}\n}\n'
    return raw, header.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--image-helper', type=Path)
    parser.add_argument('--recovery-helper', type=Path)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--header', type=Path, required=True)
    args = parser.parse_args()
    record, header = generate(args.helper, args.profile, args.image_helper, args.recovery_helper)
    for path, raw in ((args.record, record), (args.header, header)):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != raw: path.write_bytes(raw)
    print('helper closure:', hashlib.sha256(record).hexdigest())


if __name__ == '__main__': main()
