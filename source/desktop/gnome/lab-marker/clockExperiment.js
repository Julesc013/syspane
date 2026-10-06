import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

const XML = `<node><interface name="org.syspane.ClockExperiment">
<method name="Start"><arg type="s" direction="out"/></method>
<method name="GetState"><arg type="s" direction="out"/></method>
<method name="StopPeer"><arg type="s" direction="out"/></method>
<method name="Disable"><arg type="s" direction="out"/></method>
</interface></node>`;
const canonical = value => typeof value === 'string' && /^(0|[1-9][0-9]{0,19})$/.test(value) && BigInt(value) <= 18446744073709551615n;
const finish = (begin, end) => new Promise((resolve, reject) => begin((object, result) => {
    try { resolve(end(object, result)); } catch (error) { reject(error); }
}));

export class ClockExperiment {
    constructor(parent) {
        this.mode = GLib.getenv('SYSPANE_GNOME_CLOCK_AGE');
        if (!['live', 'freeze-age', 'ignore-expiry', 'peer-exit', 'pending-disable', 'wrong-peer'].includes(this.mode))
            throw new Error('Named native clock fixture required');
        this.enabled = true; this.phase = 'calibration'; this.error = null;
        this.pid = null; this.exited = false; this.exitStatus = null;
        this.clock = null; this.connection = null; this.child = null; this.stdout = null;
        this.sample = null; this.before = null; this.after = null;
        this.cancel = new Gio.Cancellable(); this.timer = 0; this.deadline = 0; this.killTimer = 0;
        this.updates = 0; this.labels = []; this.frozen = null;
        this.tile = new St.Widget({x: 300, y: 310, width: 448, height: 60, reactive: false, can_focus: false});
        this.caption = new St.Label({text: 'Clock sample age (ms)', x: 0, y: 0,
            style: 'color: white; font-size: 16px;', reactive: false, can_focus: false});
        this.row = new St.Widget({x: 0, y: 30, width: 224, height: 26, reactive: false, can_focus: false,
            style: 'background-color: rgb(20,30,40);'});
        this.indicator = new St.Widget({x: 224, y: 30, width: 20, height: 26, reactive: false, can_focus: false});
        this.status = new St.Label({x: 254, y: 30, style: 'color: white; font-size: 16px;', reactive: false, can_focus: false});
        for (const actor of [this.caption, this.row, this.indicator, this.status]) this.tile.add_child(actor);
        parent.add_child(this.tile); this.paint('1234567890', false);
        this.bus = Gio.DBusExportedObject.wrapJSObject(XML, this);
        this.bus.export(Gio.DBus.session, '/org/syspane/ClockExperiment');
    }
    paint(text, stale) {
        for (const label of this.labels) { label.text = ''; label.destroy(); }
        this.labels = [];
        for (let i = 0; i < text.length; i++) {
            const label = new St.Label({x: i * 14, y: 0, width: 14, height: 26, text: text[i],
                style: 'color: white; font-family: monospace; font-size: 20px;', reactive: false, can_focus: false});
            this.row.add_child(label); this.labels.push(label);
        }
        this.indicator.set_style(`background-color: rgb(${stale ? '240,160,40' : '40,200,80'});`);
        this.status.text = stale ? 'Stale' : 'Fresh'; this.tile.show();
    }
    active() { return this.enabled && ['starting', 'ready'].includes(this.phase); }
    Start() {
        if (!this.enabled || this.phase !== 'calibration') return 'closed';
        this.phase = 'starting'; this.tile.hide();
        this.deadline = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1500, () => {
            this.deadline = 0; this.close('startup.timeout'); return GLib.SOURCE_REMOVE;
        });
        this.start(); return 'starting';
    }
    async line(stream) {
        let data = '';
        while (data.length < 64) {
            const bytes = await finish(cb => stream.read_bytes_async(64-data.length, GLib.PRIORITY_DEFAULT, this.cancel, cb),
                (object, result) => object.read_bytes_finish(result));
            const raw = bytes.get_data();
            if (!raw.length || raw.some(byte => byte > 127)) throw new Error('clock.frame');
            data += String.fromCharCode(...raw);
            if (data.endsWith('\n')) return data.slice(0, -1);
        }
        throw new Error('clock.frame');
    }
    async start() {
        try {
            const native = (await import('gi://SysPaneClock?version=0.1')).default;
            if (!this.active()) return;
            this.child = Gio.Subprocess.new(['/usr/bin/python3', GLib.getenv('SYSPANE_GNOME_CLOCK_HELPER'),
                GLib.getenv('SYSPANE_GNOME_CLOCK_SOCKET'), this.mode === 'pending-disable' ? 'slow-ready' : 'normal'],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
            this.pid = Number(this.child.get_identifier());
            this.stdout = this.child.get_stdout_pipe();
            if (!Number.isSafeInteger(this.pid) || this.pid <= 1) throw new Error('clock.child');
            this.child.wait_async(null, (child, result) => {
                try {
                    child.wait_finish(result); this.exited = true;
                    this.exitStatus = child.get_if_exited() ? child.get_exit_status() : -child.get_term_sig();
                } catch (_) { this.exitStatus = 'unknown'; }
                if (this.killTimer) { GLib.source_remove(this.killTimer); this.killTimer = 0; }
                if (this.active()) this.close('clock.peer_exited');
                this.child = null;
            });
            if (await this.line(this.stdout) !== 'ready') throw new Error('clock.ready');
            this.stdout.close(null); this.stdout = null;
            if (!this.active()) return;
            const client = new Gio.SocketClient({enable_proxy: false});
            this.connection = await finish(cb => client.connect_async(new Gio.UnixSocketAddress({path: GLib.getenv('SYSPANE_GNOME_CLOCK_SOCKET')}), this.cancel, cb),
                (object, result) => object.connect_finish(result));
            if (!this.active()) { this.dropConnection(); return; }
            this.clock = native.Clock.new_from_socket(this.connection.get_socket().get_fd(), this.pid + (this.mode === 'wrong-peer' ? 1 : 0));
            this.before = this.clock.sample();
            const command = new TextEncoder().encode('sample\n');
            const [, written] = await finish(cb => this.connection.get_output_stream().write_all_async(command, GLib.PRIORITY_DEFAULT, this.cancel, cb),
                (object, result) => object.write_all_finish(result));
            if (written !== command.length) throw new Error('clock.write');
            const stamp = await this.line(this.connection.get_input_stream());
            if (!this.active()) return;
            this.after = this.clock.sample();
            if (!canonical(stamp) || BigInt(stamp) < BigInt(this.before) || BigInt(stamp) > BigInt(this.after)) throw new Error('clock.bracket');
            this.sample = stamp; this.phase = 'ready';
            GLib.source_remove(this.deadline); this.deadline = 0;
            this.update();
            if (this.active()) this.timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
                this.update();
                if (!this.active()) { this.timer = 0; return GLib.SOURCE_REMOVE; }
                return GLib.SOURCE_CONTINUE;
            });
        } catch (error) { if (this.active()) this.close(error.message); }
        finally {
            if (!this.active()) {
                this.dropConnection();
                try { this.stdout?.close(null); } catch (_) { /* Cancelled read completes here. */ }
                this.stdout = null;
            }
        }
    }
    update() {
        try {
            const now = this.clock.sample();
            if (!canonical(now) || BigInt(now) < BigInt(this.sample)) throw new Error('clock.range');
            const age = BigInt(now)-BigInt(this.sample);
            const text = (age/1000000n).toString();
            if (this.frozen === null) this.frozen = text;
            this.paint(this.mode === 'freeze-age' ? this.frozen : text, this.mode !== 'ignore-expiry' && age >= 3000000000n);
            this.updates++;
        } catch (error) { this.close(error.message); }
    }
    dropConnection() {
        this.clock?.close(); this.clock = null;
        try { this.connection?.close(null); } catch (_) { /* Native handle already closed. */ }
        this.connection = null;
    }
    stopPeer() {
        if (!this.child || this.exited) return;
        this.child.send_signal(15);
        if (!this.killTimer) this.killTimer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
            this.killTimer = 0; if (!this.exited) this.child.force_exit(); return GLib.SOURCE_REMOVE;
        });
    }
    close(reason = null) {
        if (['closed', 'failed'].includes(this.phase)) return;
        this.phase = reason ? 'failed' : 'closed'; this.error = reason;
        // Signal while the socket still retains the peer in its receive loop;
        // closing it first can race Python's final signal-handler teardown.
        this.cancel.cancel(); this.stopPeer(); this.dropConnection();
        if (this.deadline) { GLib.source_remove(this.deadline); this.deadline = 0; }
        if (this.timer) { GLib.source_remove(this.timer); this.timer = 0; }
        for (const label of this.labels) { label.text = ''; label.destroy(); }
        this.labels = []; this.tile.destroy(); this.tile = null;
        this.caption = this.row = this.indicator = this.status = null;
    }
    StopPeer() { this.stopPeer(); return 'requested'; }
    Disable() { this.close(); return 'closed'; }
    GetState() {
        return JSON.stringify({phase: this.phase, error: this.error, pid: this.pid, exited: this.exited,
            exitStatus: this.exitStatus, sample: this.sample, before: this.before, after: this.after,
            updates: this.updates, clock: this.clock !== null, connection: this.connection !== null, labels: this.labels.length});
    }
    disable() {
        if (!this.enabled) return;
        this.close(); this.enabled = false; this.bus.unexport();
    }
}
