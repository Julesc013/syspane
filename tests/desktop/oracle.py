"""Independent marker 0.1 decoding and temporal observation. No candidate encoder import."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import zlib

WIDTH, HEIGHT, RGB_BYTES = 128, 96, 36864
BLUE, ORANGE, VIOLET = (16, 96, 224), (240, 160, 16), (160, 32, 192)
ZERO, ONE = (32, 32, 32), (224, 224, 224)
ELIGIBLE = {'display_server_root', 'compositor_output'}

def integer(value, high=(1 << 64) - 1):
    return type(value) is int and 0 <= value <= high

def decode(rgb):
    if not isinstance(rgb, bytes) or len(rgb) != RGB_BYTES:
        return None
    def matches(column, row, color):
        for y in range(row * 8 + 2, row * 8 + 6):
            for x in range(column * 8 + 2, column * 8 + 6):
                position = (y * WIDTH + x) * 3
                if any(abs(rgb[position + c] - color[c]) > 8 for c in range(3)):
                    return False
        return True
    bits = []
    for row in range(12):
        for column in range(16):
            if row in (0, 11) or column in (0, 15):
                color = VIOLET if (column, row) == (0, 11) else (BLUE if (column + row) % 2 == 0 else ORANGE)
                if not matches(column, row, color): return None
            elif matches(column, row, ZERO): bits.append(0)
            elif matches(column, row, ONE): bits.append(1)
            else: return None
    if any(bits[136:]): return None
    data = bytes(sum(bits[index + bit] << (7 - bit) for bit in range(8)) for index in range(0, 136, 8))
    if data[:5] != b'SYPN\x01' or zlib.crc32(data[:13]) != int.from_bytes(data[13:17], 'big'):
        return None
    return int.from_bytes(data[5:13], 'big')

def pack_frame(rgb, start_us, end_us, origin='display_server_root'):
    if len(rgb) != RGB_BYTES: raise ValueError('frame dimensions')
    return {'start_us': start_us, 'end_us': end_us, 'origin': origin,
            'rgb_zlib_base64': base64.b64encode(zlib.compress(rgb)).decode('ascii'),
            'rgb_sha256': hashlib.sha256(rgb).hexdigest()}

def unpack_frame(frame):
    if not isinstance(frame, dict) or set(frame) != {'start_us', 'end_us', 'origin', 'rgb_zlib_base64', 'rgb_sha256'}:
        raise ValueError('frame shape')
    encoded = frame['rgb_zlib_base64']
    if not isinstance(encoded, str) or len(encoded) > 65536: raise ValueError('compressed frame limit')
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoder = zlib.decompressobj()
        rgb = decoder.decompress(compressed, RGB_BYTES + 1)
    except (ValueError, zlib.error) as error:
        raise ValueError('frame encoding') from error
    if len(rgb) != RGB_BYTES or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('frame size or trailing data')
    if hashlib.sha256(rgb).hexdigest() != frame['rgb_sha256']: raise ValueError('frame digest')
    return rgb

def evaluate(trace):
    if not isinstance(trace, dict) or set(trace) != {'version', 'start_us', 'end_us', 'stimuli', 'frames'} or trace['version'] != '0.1.0':
        raise ValueError('trace version/shape')
    start, end, stimuli, frames = (trace[key] for key in ('start_us', 'end_us', 'stimuli', 'frames'))
    if not integer(start) or not integer(end) or not start < end or end - start > 60000000:
        raise ValueError('trace interval')
    if not isinstance(stimuli, list) or not 2 <= len(stimuli) <= 128 or not isinstance(frames, list) or not 1 <= len(frames) <= 1200:
        raise ValueError('trace counts')
    previous_time = previous_generation = -1
    for index, stimulus in enumerate(stimuli):
        if not isinstance(stimulus, dict) or set(stimulus) != {'at_us', 'generation'}:
            raise ValueError('stimulus shape')
        time, generation = stimulus['at_us'], stimulus['generation']
        if not integer(time) or not integer(generation) or time <= previous_time or generation <= previous_generation:
            raise ValueError('stimulus order')
        if (index == 0 and time > start) or (index and not start < time < end):
            raise ValueError('stimulus interval')
        next_time = stimuli[index + 1].get('at_us') if index + 1 < len(stimuli) and isinstance(stimuli[index + 1], dict) else end
        if index and (not integer(next_time) or next_time - time < 200000): raise ValueError('stimulus budget')
        previous_time, previous_generation = time, generation
    failures, uncertainty, observed = set(), set(), set()
    last_generation = None
    previous_end, max_gap, max_capture = start, 0, 0
    observations = []
    for frame in frames:
        rgb = unpack_frame(frame)
        begin, finish, origin = frame['start_us'], frame['end_us'], frame['origin']
        if not integer(begin) or not integer(finish) or not previous_end <= begin <= finish <= end or not isinstance(origin, str):
            raise ValueError('frame time/order/origin')
        max_gap, max_capture = max(max_gap, begin - previous_end), max(max_capture, finish - begin)
        previous_end = finish
        generation = decode(rgb)
        observations.append({'at_us': begin, 'generation': str(generation) if generation is not None else None})
        if origin not in ELIGIBLE:
            uncertainty.add('capture.origin_ineligible')
            continue
        if generation is None:
            failures.add('marker.absent_or_invalid')
            continue
        issued = [row for row in stimuli if row['at_us'] <= finish]
        if generation not in {row['generation'] for row in issued}:
            failures.add('generation.unissued')
        if last_generation is not None and generation < last_generation:
            failures.add('generation.regressed')
        last_generation = generation
        due = [row for index, row in enumerate(stimuli) if index == 0 or row['at_us'] + 200000 <= begin]
        if generation < due[-1]['generation']:
            failures.add('generation.deadline')
        for index, row in enumerate(stimuli):
            until = stimuli[index + 1]['at_us'] if index + 1 < len(stimuli) else end
            if generation == row['generation'] and row['at_us'] <= finish and begin < until:
                observed.add(generation)
    max_gap = max(max_gap, end - previous_end)
    if max_gap > 150000: uncertainty.add('capture.gap')
    if max_capture > 50000: uncertainty.add('capture.duration')
    if len(frames) < 3: uncertainty.add('capture.insufficient_frames')
    if observed != {row['generation'] for row in stimuli}: uncertainty.add('generation.unobserved')
    return {'oracle_version': '0.1.0', 'scope': 'temporal_pixel_observation',
            'outcome': 'fail' if failures else ('inconclusive' if uncertainty else 'pass'),
            'failures': sorted(failures), 'uncertainty': sorted(uncertainty), 'samples': len(frames),
            'max_gap_us': max_gap, 'max_capture_us': max_capture, 'observed_generations': [str(n) for n in sorted(observed)],
            'observations': observations}

def read_trace(path):
    with Path(path).open('rb') as file: data = file.read(32 * 1024 * 1024 + 1)
    if len(data) > 32 * 1024 * 1024: raise ValueError('trace file limit')
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value: raise ValueError('duplicate JSON key')
            value[key] = item
        return value
    return json.loads(data.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

if __name__ == '__main__':
    try:
        if len(sys.argv) != 2: raise ValueError('expected one bounded trace file')
        result = evaluate(read_trace(sys.argv[1]))
        print(json.dumps(result))
        sys.exit({'pass': 0, 'fail': 1, 'inconclusive': 3}[result['outcome']])
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print('oracle.invalid: ' + str(error), file=sys.stderr)
        sys.exit(2)
