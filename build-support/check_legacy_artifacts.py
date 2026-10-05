"""Audit this experiment's PE32 headers and mandatory import closure; not an XP runtime test."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
EXECUTABLES = ('SysPane.ModelSmoke.exe', 'syspane_model_tests.exe', 'syspane_protocol_tests.exe',
               'syspane_recovery_tests.exe', 'syspane_diagnostic_tests.exe', 'syspane_data_view_tests.exe', 'syspane_telemetry_tests.exe', 'syspane_state_import_tests.exe', 'syspane_subscription_tests.exe', 'syspane_measured_time_tests.exe', 'syspane_network_state_tests.exe', 'syspane_network_publication_tests.exe')


def build_inputs(build):
    lock = json.loads((ROOT/'build-support/targets/windows-x86-v141-xp.lock.json').read_text(encoding='utf-8'))
    expected = {str(Path(path).resolve()).casefold(): (path, lock['identity']['fingerprints'][name])
                for name, path in lock['files'].items() if path.lower().endswith('.lib')}
    observed, journals = {}, {}
    for name in EXECUTABLES:
        target = 'syspane_model_smoke' if name == 'SysPane.ModelSmoke.exe' else name[:-4]
        target_root = build/(target+'.dir')/'Release'
        read_logs = list(target_root.rglob('link.read.1.tlog'))
        command_logs = list(target_root.rglob('CL.command.1.tlog'))
        if len(read_logs) != 1 or len(command_logs) != 1:
            raise ValueError('ambiguous/missing MSBuild input logs')
        libraries = set()
        for path in read_logs[0].read_text(encoding='utf-16').splitlines():
            if not path.lower().endswith('.lib'):
                continue
            resolved = Path(path).resolve(strict=True)
            if resolved.is_relative_to(build):
                continue
            key = str(resolved).casefold()
            if key not in expected:
                raise ValueError('linker selected an unpinned external library: '+path)
            if key not in observed:
                original, digest = expected[key]
                if hashlib.sha256(resolved.read_bytes()).hexdigest() != digest:
                    raise ValueError('resolved linker input differs from profile: '+path)
                observed[key] = {'path': original, 'sha256': digest}
            libraries.add(resolved.name.lower())
        if not {'libcmt.lib', 'libcpmt.lib', 'libvcruntime.lib', 'libucrt.lib', 'kernel32.lib'} <= libraries:
            raise ValueError('required static CRT/SDK inputs not observed')
        commands = command_logs[0].read_text(encoding='utf-16')
        if any(flag not in commands.split() for flag in ('/MT', '/W4', '/WX', '/std:c++17', '/arch:SSE2')) or '/MD' in commands:
            raise ValueError('actual compiler flags differ from experiment')
        for path in read_logs+command_logs:
            journals[path.relative_to(build).as_posix()] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                                           'text': path.read_text(encoding='utf-16')}
    return {'resolved_external_libraries': list(observed.values()), 'msbuild_input_logs': journals}


def inspect(data):
    if not 256 <= len(data) <= 64 * 1024**2 or data[:2] != b'MZ':
        raise ValueError('PE input size/signature')
    def unpack(format, offset):
        if offset < 0 or offset + struct.calcsize(format) > len(data):
            raise ValueError('PE field outside file')
        return struct.unpack_from(format, data, offset)
    pe, = unpack('<I', 0x3c)
    if data[pe:pe+4] != b'PE\0\0':
        raise ValueError('PE signature')
    machine, sections = unpack('<HH', pe+4)
    optional_size, characteristics = unpack('<HH', pe+20)
    optional = pe + 24
    if machine != 0x14c or not 1 <= sections <= 96 or optional_size != 224 or characteristics & 0x2000:
        raise ValueError('expected x86 executable with PE32 optional header')
    if unpack('<H', optional)[0] != 0x10b or unpack('<I', optional+92)[0] != 16:
        raise ValueError('PE32 directory shape')
    os_version = unpack('<HH', optional+40)
    subsystem_version = unpack('<HH', optional+48)
    subsystem, = unpack('<H', optional+68)
    if os_version != (5, 1) or subsystem_version != (5, 1) or subsystem != 3:
        raise ValueError('experimental XP console version floor')
    table = []
    for n in range(sections):
        size, address, raw_size, offset = unpack('<IIII', optional+optional_size+n*40+8)
        if offset+raw_size > len(data) or address+max(size, raw_size) > 0x100000000:
            raise ValueError('PE section bounds')
        table.append((address, raw_size, offset))
    def rva(address, size):
        matches = [offset+address-start for start, count, offset in table
                   if start <= address and address+size <= start+count]
        if len(matches) != 1:
            raise ValueError('PE unmapped or ambiguous RVA')
        return matches[0]
    def string(address):
        value = bytearray()
        for n in range(256):
            byte = data[rva(address+n, 1)]
            if byte == 0:
                if not value:
                    raise ValueError('PE empty import name')
                return value.decode('ascii')
            if not 33 <= byte <= 126:
                raise ValueError('PE non-ASCII import name')
            value.append(byte)
        raise ValueError('PE import name limit')
    for index in (11, 13):
        if unpack('<II', optional+96+index*8) != (0, 0):
            raise ValueError('bound or delay imports outside this experimental closure')
    address, count = unpack('<II', optional+104)
    if not address or not 40 <= count <= 20*17 or count % 20:
        raise ValueError('PE import directory budget')
    imports = {}
    terminated = False
    for n in range(count//20):
        lookup, stamp, chain, name, first = unpack('<IIIII', rva(address+n*20, 20))
        if (lookup, stamp, chain, name, first) == (0, 0, 0, 0, 0):
            if n != count//20-1:
                raise ValueError('PE trailing import descriptor data')
            terminated = True
            break
        dll = string(name).lower()
        if dll in imports or not lookup or not first or stamp or chain:
            raise ValueError('PE import descriptor identity')
        names = []
        for i in range(513):
            symbol, = unpack('<I', rva(lookup+i*4, 4))
            if symbol == 0:
                break
            if i == 512 or symbol & 0x80000000:
                raise ValueError('PE import count or ordinal outside closure')
            names.append(string(symbol+2))
        else:
            raise ValueError('PE unterminated imports')
        if not names or len(names) != len(set(names)):
            raise ValueError('PE duplicate/empty imports')
        imports[dll] = sorted(names)
    if not terminated:
        raise ValueError('PE unterminated import directory')
    return {'machine': 'x86', 'format': 'PE32', 'os_version': list(os_version),
            'subsystem_version': list(subsystem_version), 'subsystem': 'console', 'imports': imports}


def verify(data):
    result = inspect(data)
    closure = json.loads((ROOT/'build-support/targets/windows-x86-v141-xp.imports.json').read_text(encoding='utf-8'))
    if set(result['imports']) != {'kernel32.dll'} or not set(result['imports']['kernel32.dll']) <= set(closure['kernel32.dll']):
        raise ValueError('mandatory imports exceed the declared experiment closure')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    build = args.build.resolve(strict=True)
    if not build.is_relative_to(ROOT/'out/build') or json.loads((build/'.syspane-owner.json').read_text())['profile'] != 'windows-x86-v141-xp':
        raise ValueError('owned historical build required')
    result = {'profile': 'windows-x86-v141-xp', 'outcome': 'pass', 'artifacts': {},
              'qualification': 'Header and declared mandatory-import closure only; dynamic CRT fallback and XP/7 execution remain unproven.'}
    result['build_inputs'] = build_inputs(build)
    for name in EXECUTABLES:
        data = (build/'Release'/name).read_bytes()
        result['artifacts'][name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), **verify(data)}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Historical PE/header/import audit: pass ({len(EXECUTABLES)} artifacts; no runtime qualification)')


if __name__ == '__main__':
    main()
