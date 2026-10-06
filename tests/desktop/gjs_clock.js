import Gio from 'gi://Gio';
import GioUnix from 'gi://GioUnix';
import SysPaneClock from 'gi://SysPaneClock?version=0.1';

const input = new Gio.DataInputStream({base_stream: new GioUnix.InputStream({fd: 0, close_fd: false})});
const [path, pidText, invalidText] = ARGV;
const pid = Number(pidText);
const connect = () => new Gio.SocketClient().connect(new Gio.UnixSocketAddress({path}), null);
function rejected(fn, code) {
    try { fn(); } catch (error) {
        if (error.message !== code) throw new Error(`Expected ${code}, got ${error.message}`);
        return code;
    }
    throw new Error(`Expected rejection ${code}`);
}
function sample(clock) {
    const value = clock.sample();
    if (typeof value !== 'string' || !/^(0|[1-9][0-9]*)$/.test(value) || BigInt(value) > 18446744073709551615n)
        throw new Error('Clock did not return exact uint64 text');
    return value;
}
let connection = connect();
const borrowed = connection.get_socket().get_fd();
const clock = SysPaneClock.Clock.new_from_socket(borrowed, pid);
const codes = [rejected(() => SysPaneClock.Clock.new_from_socket(-1, pid), 'peer.handle'),
    rejected(() => SysPaneClock.Clock.new_from_socket(borrowed, 0), 'peer.process'),
    rejected(() => SysPaneClock.Clock.new_from_socket(borrowed, pid + 1), 'peer.process')];
for (const fd of JSON.parse(invalidText))
    codes.push(rejected(() => SysPaneClock.Clock.new_from_socket(fd, pid), 'peer.socket'));
const empty = new SysPaneClock.Clock();
codes.push(rejected(() => empty.sample(), 'clock.closed'));
empty.close();
// Closing the borrowed GIO connection must not close the adapter's duplicate.
connection.close(null);
connection = null;
const cyclesConnection = connect();
print(JSON.stringify({event: 'ready', codes}));
for (;;) {
    const [line] = input.read_line_utf8(null);
    if (line === null) throw new Error('Observer disappeared');
    const op = JSON.parse(line).op;
    if (op === 'sample') print(JSON.stringify({event: op, value: sample(clock)}));
    else if (op === 'cycles') {
        for (let i = 0; i < 64; i++) {
            const c = SysPaneClock.Clock.new_from_socket(cyclesConnection.get_socket().get_fd(), pid);
            sample(c); c.close(); c.close();
            rejected(() => c.sample(), 'clock.closed');
        }
        print(JSON.stringify({event: op, count: 64}));
    } else if (op === 'peer-exit') {
        print(JSON.stringify({event: op, codes: [rejected(() => clock.sample(), 'clock.peer_exited'),
            rejected(() => clock.sample(), 'clock.unavailable')]}));
    } else if (op === 'close') {
        clock.close(); clock.close(); cyclesConnection.close(null);
        print(JSON.stringify({event: op, code: rejected(() => clock.sample(), 'clock.closed')}));
    } else if (op === 'exit') break;
    else throw new Error('Unknown observer operation');
}
