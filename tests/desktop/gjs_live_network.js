import Gio from 'gi://Gio';
import GioUnix from 'gi://GioUnix';
import GLib from 'gi://GLib';
import {NetworkSession} from '../../source/desktop/gnome/networkSession.js';

const [executable, root, mode, journal] = ARGV;
const loop = new GLib.MainLoop(null, false);
let latest = null;
const session = new NetworkSession({executable, root, mode, journal,
    onEvent: row => print(JSON.stringify({event: 'native', supervisor_pid: session.pid, row})),
    onProjection: frame => { latest = frame; print(JSON.stringify({event: 'projection', frame})); },
    onClear: () => { latest = null; print(JSON.stringify({event: 'cleared'})); },
});
const input = new Gio.DataInputStream({base_stream: new GioUnix.InputStream({fd: 0, close_fd: false})});
function read() {
    input.read_line_async(GLib.PRIORITY_DEFAULT, null, async (object, result) => {
        try {
            const [line] = object.read_line_finish_utf8(result);
            if (line === null) throw new Error('fixture.parent_lost');
            if (line === 'state') print(JSON.stringify({event: 'state', state: session.state(), payload: latest !== null}));
            else if (line === 'revoke') print(JSON.stringify({event: 'revoked', code: session.revoke(), payload: latest !== null}));
            else if (line === 'stop') {
                await session.close(); print(JSON.stringify({event: 'stopped', state: session.state(), payload: latest !== null}));
                loop.quit(); return;
            } else throw new Error('fixture.command');
            read();
        } catch (_) { await session.close('fixture.control'); loop.quit(); }
    });
}
session.start().then(() => print(JSON.stringify({event: 'started', state: session.state()})));
read(); loop.run();
