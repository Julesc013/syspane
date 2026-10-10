"""Strict bounded decoder for completed fixture-only numeric phase journals."""
import re

KINDS = ('take', 'withdrawal', 'reply', 'reply_reload', 'populate', 'editor',
         'settings', 'recovery', 'attach', 'topology', 'controls', 'inspector', 'inspector_prepare')
NUMBER = rb'(0|[1-9][0-9]{0,19})'
BEGIN = re.compile(rb'phase-begin ' + NUMBER + rb' ' + NUMBER)
ROW = re.compile(rb'phase ' + rb' '.join([NUMBER] * 4))
END = re.compile(rb'phase-end ' + rb' '.join([NUMBER] * 3))


def decode(raw):
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError('phase transcript size')
    lines = raw.splitlines(); blocks = []; seen = set(); i = 0
    if lines and lines[-1].startswith(b'phase') and not raw.endswith(b'\n'):
        raise ValueError('phase incomplete line')
    while i < len(lines):
        line = lines[i]; i += 1
        if not line.startswith(b'phase'):
            continue  # Preserve unrelated stderr in the original artifact.
        match = BEGIN.fullmatch(line)
        if not match:
            raise ValueError('phase begin')
        pid, count = map(int, match.groups())
        if not 0 < pid <= 2**31 - 1 or pid in seen or count > 8192 or len(blocks) >= 8:
            raise ValueError('phase identity/capacity')
        seen.add(pid); rows = []; last_tick = 0; phases = set()
        for _ in range(count):
            if i >= len(lines):
                raise ValueError('phase truncated')
            match = ROW.fullmatch(lines[i]); i += 1
            if not match:
                raise ValueError('phase row')
            tick, kind, us, completed = map(int, match.groups())
            if not last_tick <= tick <= 2**64 - 1 or tick == 0 or not 1 <= kind <= len(KINDS) or us > 2**64 - 1 or completed > 1:
                raise ValueError('phase values')
            if tick != last_tick:
                phases.clear()
            if kind in phases:
                raise ValueError('duplicate phase within tick')
            phases.add(kind); last_tick = tick
            rows.append(dict(tick=tick, phase=KINDS[kind-1], microseconds=us, completed=bool(completed)))
        if i >= len(lines):
            raise ValueError('phase end missing')
        match = END.fullmatch(lines[i]); i += 1
        if not match:
            raise ValueError('phase end')
        end_pid, end_count, result = map(int, match.groups())
        if (end_pid, end_count) != (pid, count) or result not in (0, 2) or (result == 0 and not rows):
            raise ValueError('phase end identity/result')
        blocks.append(dict(pid=pid, result=result, rows=rows))
    if not blocks:
        raise ValueError('phase transcript missing')
    return blocks
