import Gio from 'gi://Gio';
import GioUnix from 'gi://GioUnix';
import GLib from 'gi://GLib';
import SysPaneClock from 'gi://SysPaneClock?version=0.1';

// Standalone synchronous fixture driver only. Shell transport must remain async.
const input = new Gio.DataInputStream({base_stream: new GioUnix.InputStream({fd: 0, close_fd: false})});
const [path, pidText] = ARGV;
const pid = Number(pidText);
const connection = new Gio.SocketClient().connect(new Gio.UnixSocketAddress({path}), null);
const fd = connection.get_socket().get_fd();
const views = new Map();
const outcome = fn => { try { return {value: fn()}; } catch (error) { return {error: error.message}; } };
print(JSON.stringify({event: 'ready', invalid: [
    outcome(() => SysPaneClock.NetworkView.new_from_socket(-1, pid, '7', true)),
    outcome(() => SysPaneClock.NetworkView.new_from_socket(fd, pid + 1, '7', true)),
    outcome(() => SysPaneClock.NetworkView.new_from_socket(fd, pid, '00', true)),
    outcome(() => new SysPaneClock.NetworkView().project()),
]}));
for (;;) {
    const [line] = input.read_line_utf8(null);
    if (line === null) throw new Error('Observer disappeared');
    const request = JSON.parse(line);
    if (request.op === 'exit') break;
    const reply = outcome(() => {
        if (request.op === 'open') {
            if (views.has(request.id)) throw new Error('Duplicate fixture owner');
            views.set(request.id, SysPaneClock.NetworkView.new_from_socket(fd, pid, '7', true));
            return 'opened';
        }
        if (request.op === 'cycles') {
            for (let index = 0; index < 64; index++) {
                const view = SysPaneClock.NetworkView.new_from_socket(fd, pid, '7', true);
                view.close(); view.close();
            }
            return 64;
        }
        const view = views.get(request.id);
        if (!view) throw new Error('Unknown fixture owner');
        if (request.op === 'feed') return view.feed(new GLib.Bytes(GLib.base64_decode(request.data)));
        if (request.op === 'project') return JSON.parse(view.project());
        if (request.op === 'policy') return view.policy(request.revision, request.permit);
        if (request.op === 'hello') return GLib.base64_encode(view.hello().get_data());
        if (request.op === 'shutdown') return GLib.base64_encode(view.shutdown().get_data());
        if (request.op === 'close') { view.close(); view.close(); views.delete(request.id); return 'closed'; }
        throw new Error('Unknown fixture operation');
    });
    print(JSON.stringify({event: request.op, ...reply}));
}
for (const view of views.values()) view.close();
views.clear(); connection.close(null);
