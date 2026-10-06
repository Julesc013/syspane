"""Retained public-marker fixture with one persistent native bus connection."""
import json
import os
from pathlib import Path
import signal
import socket
import struct
import sys
import time

import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

workspace = Path(os.environ['HOME']).parent.resolve(strict=True)
role = sys.argv[1]
if not workspace.name.startswith('GNOME-SURFACE-LEASE-01-') or role not in ['first', 'second']:
    raise ValueError('owned surface lease fixture required')
connection = Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],
    Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)
connection.set_exit_on_close(False)
journal = (workspace / ('lease-producer-' + role + '.jsonl')).open('x', encoding='utf-8', newline='\n')
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind('\0syspane-lease-' + workspace.name.rsplit('-', 1)[1] + '-' + role)
server.listen(1)
server.settimeout(1)
started = time.monotonic()
count = 0
stopping = False


def record(value):
    raw = json.dumps(value, separators=(',', ':')) + '\n'
    if journal.tell() + len(raw.encode()) > 65536:
        raise ValueError('producer journal capacity')
    journal.write(raw)
    journal.flush()


def stop(*_):
    global stopping
    stopping = True


signal.signal(signal.SIGTERM, stop)
record({'event': 'ready', 'pid': os.getpid(), 'role': role, 'owner': connection.get_unique_name(), 'at_ns': time.monotonic_ns()})
try:
    while not stopping and time.monotonic() - started < 40:
        try:
            client, _ = server.accept()
        except socket.timeout:
            continue
        with client:
            client.settimeout(2)
            peer = struct.unpack('3i', client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if peer[1] != os.geteuid():
                raise ValueError('foreign control identity')
            data = bytearray()
            while not data.endswith(b'\n'):
                part = client.recv(4097 - len(data))
                if not part or len(data) + len(part) > 4096:
                    raise ValueError('control capacity/completeness')
                data.extend(part)
            request = json.loads(data)
            if set(request) != {'method', 'value'} or count >= 32:
                raise ValueError('typed bounded control required')
            count += 1
            method, value = request['method'], request['value']
            row = {'event': 'call', 'request': request, 'started_ns': time.monotonic_ns(), 'owner': connection.get_unique_name()}
            if method == 'Exit' and value == 73:
                row.update(reply='exiting', finished_ns=time.monotonic_ns())
                record(row)
                client.sendall((json.dumps(row) + '\n').encode())
                journal.flush()
                os._exit(73)
            if method == 'Attach' and value in ['lease:1', 'lease:2']:
                arguments = GLib.Variant('(s)', (value,))
            elif method in ['Heartbeat', 'Snapshot'] and type(value) is int and 0 <= value <= 0xffffffff:
                arguments = GLib.Variant('(u)', (value,))
            else:
                raise ValueError('unknown control')
            reply = connection.call_sync('org.gnome.Shell', '/org/syspane/SurfaceLease', 'org.syspane.SurfaceLease',
                method, arguments, GLib.VariantType.new('(s)'), Gio.DBusCallFlags.NO_AUTO_START, 1500, None)
            row.update(reply=reply.unpack()[0], finished_ns=time.monotonic_ns())
            record(row)
            client.sendall((json.dumps(row) + '\n').encode())
finally:
    server.close()
    connection.close_sync(None)
    journal.close()
