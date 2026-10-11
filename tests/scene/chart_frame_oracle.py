"""Literal independent footprint/semantic oracle; never reads a product result to set a bound."""
import json

LIMIT = 262144
POINT_BYTES = 40  # Pinned Linux GCC 13 x86-64 ABI, not a portable sizeof promise.
FIELDS = ['network.receive_bytes', 'network.transmit_bytes', 'entity.id', 'entity.kind']
LABELS = ['Rx', 'Tx', 'Identity', 'Kind']
IDENTITY = ['P1', 'E1', 'network:interface:1', FIELDS[0], 'provider:native-network',
            'byte', 'clock:1', 'scope:1', 0, True]
STATE = 'support=supported; acquisition=success; presence=present; freshness=current; origin=observed; lease=active; age=0 ns'
CONFIGURED = 'support=supported; acquisition=success; presence=present; freshness=current; origin=configured; lease=active; age=unknown'

def key(*items):
    return json.dumps(items, ensure_ascii=False, separators=(',', ':'))

def row(k, item, information, children=None):
    return dict(key=k, item=item, information=information, children=children or [])

def chart(points):
    # points are explicit (measurement, generation, joins_previous) tuples.
    summary = f'Samples {len(points)} | Segments 1\nRange 0.0 .. 100.0 byte\nWindow 10000 ms | linear'
    scalar = 'Receive\n10 byte\nCurrent'
    text = scalar + '\n' + summary
    accessible_summary = scalar + '\n' + STATE + '\n' + summary
    accessible = accessible_summary + ''.join(f'\nPoint {ns}: 10; generation {g}; '+('join' if joins else 'start') for ns, g, joins in points)
    point_rows = [row(key('scene:surface', 'value', 'point', IDENTITY, str(ns)),
                      f'Point {ns} ns', f'10 byte; generation {g}; '+('join' if joins else 'start')) for ns, g, joins in points]
    footprint = sum(map(len, ['value', 'chart', 'Receive', text, accessible, 'Noto Sans', summary, accessible_summary, *IDENTITY[:8]])) + POINT_BYTES * len(points)
    return dict(id='value', title='Receive', kind='chart', text=text, accessible=accessible,
                fonts=['Noto Sans'], bytes=footprint, summary=summary, accessible_summary=accessible_summary,
                points=[dict(measured_ns=ns, generation=g, value=10, joins_previous=joins) for ns, g, joins in points]), row(key('scene:surface', 'value'), 'Receive', accessible_summary, point_rows)

def table():
    title, summary = 'Interfaces', 'Showing 64 of 64 rows'
    accessible = title + '\n' + summary
    footprint = sum(map(len, ['table', 'table', title, title, 'Noto Sans', summary, *FIELDS, *LABELS]))
    children = []
    for entity in sorted(f'network:interface:{i}' for i in range(1, 65)):
        footprint += len('P2') + len('E1') + len(entity)
        accessible += '\nRow P2/E1/' + entity
        cells = []
        for field, label in zip(FIELDS, LABELS):
            text = '10 byte\nCurrent' if field == FIELDS[0] else '7 byte\nCurrent' if field == FIELDS[1] else (entity if field == FIELDS[2] else 'network.interface') + '\nConfigured'
            info = text + '\n' + (STATE if field in FIELDS[:2] else CONFIGURED)
            footprint += len(text) + len(info)
            label = label + ' [' + field + ']'
            accessible += '\n' + label + ': ' + info
            cells.append(row(key('scene:surface', 'table', 'row', 'P2', 'E1', entity, field), label, info))
        children.append(row(key('scene:surface', 'table', 'row', 'P2', 'E1', entity), entity, 'Producer P2 | Epoch E1 | Generation 1', cells))
    footprint += len(accessible)
    return dict(id='table', kind='table', title=title, text=title, accessible=accessible, fonts=['Noto Sans'], bytes=footprint), row(key('scene:surface', 'table'), title, summary, children)

def sequence(count):
    return [(i * 1000000, i + 1, i != 0) for i in range(count)]

def boundary(mixed):
    # Incremental independent length arithmetic: no product invocation and no
    # repeated construction of all point strings merely to find the threshold.
    extra = table()[0]['bytes'] if mixed else 0
    point_text = 0
    for n in range(1, 4097):
        i = n - 1
        point_text += len(f'\nPoint {i*1000000}: 10; generation {n}; '+('join' if i else 'start'))
        summary = f'Samples {n} | Segments 1\nRange 0.0 .. 100.0 byte\nWindow 10000 ms | linear'
        scalar = 'Receive\n10 byte\nCurrent'
        current = sum(map(len, ['value', 'chart', 'Receive', scalar+'\n'+summary,
                               scalar+'\n'+STATE+'\n'+summary, 'Noto Sans', summary,
                               scalar+'\n'+STATE+'\n'+summary, *IDENTITY[:8]])) + point_text + POINT_BYTES*n + extra
        if current > LIMIT:
            prior = chart(sequence(n-1))[0]['bytes'] + extra
            return dict(points=n-1, fitting_bytes=prior, rejected_bytes=current, table_bytes=extra)
    raise AssertionError('fixture must cross the frame limit')

if __name__ == '__main__':
    print(json.dumps({name: boundary(mixed) for name, mixed in [('chart', False), ('mixed', True)]}, indent=2))
