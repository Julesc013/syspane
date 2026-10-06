import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import {NetworkSession} from './networkSession.js';

const XML = `<node><interface name="org.syspane.NetworkLive">
${['Calibrate', 'Start', 'GetState', 'Revoke', 'Stop', 'Cleanup'].map(name =>
    `<method name="${name}"><arg type="s" direction="out"/></method>`).join('')}
</interface></node>`;

// Only a drawing adapter. Native NetworkView retains operational semantics.
export class NetworkLive {
    constructor(parent) {
        this.mode = GLib.getenv('SYSPANE_GNOME_NETWORK_LIVE');
        this.phase = 'new'; this.session = null; this.frozen = null; this.generation = null;
        this.tile = new St.Widget({x: 300, y: 310, width: 448, height: 210,
            reactive: false, can_focus: false, style: 'background-color: rgb(20,30,40);'});
        parent.add_child(this.tile); this.tile.hide(); this.rows = []; this.actors = [];
        this.bus = Gio.DBusExportedObject.wrapJSObject(XML, this);
        this.bus.export(Gio.DBus.session, '/org/syspane/NetworkLive');
    }
    label(text, x, y, width) {
        const actor = new St.Label({text, x, y, width, height: 26, reactive: false, can_focus: false,
            style: 'color: white; font-family: monospace; font-size: 20px;'});
        this.tile.add_child(actor); this.actors.push(actor); return actor;
    }
    prepare() {
        this.erase();
        this.label('Network bytes / bytes per second', 0, 0, 448);
        this.label('Sample age (ms)', 0, 150, 224);
        for (let row = 0; row < 5; row++) {
            const cells = [];
            for (let column = 0; column < (row === 4 ? 16 : 32); column++)
                cells.push(this.label('', column * 14, row === 4 ? 180 : 30 + row * 30, 14));
            this.rows.push(cells);
        }
        this.fresh = new St.Widget({x: 224, y: 180, width: 20, height: 26, reactive: false});
        this.lease = new St.Widget({x: 360, y: 180, width: 20, height: 26, reactive: false});
        for (const actor of [this.fresh, this.lease]) { this.tile.add_child(actor); this.actors.push(actor); }
        this.status = this.label('', 250, 180, 100); this.tile.show();
    }
    text(row, value) {
        const text = value === null ? '-' : value;
        if (typeof text !== 'string' || text.length > this.rows[row].length || !/^[0-9.-]+$/.test(text))
            throw new Error('tile.glyph_bound');
        this.rows[row].forEach((actor, i) => { const next = text[i] ?? ''; if (actor.text !== next) actor.text = next; });
    }
    Calibrate() {
        if (this.phase !== 'new') return 'closed';
        this.phase = 'calibration'; this.prepare();
        ['1234567890', null, '1234567890.000', null, '1234567890'].forEach((value, row) => this.text(row, value));
        this.indicators(false, true); return 'calibrated';
    }
    indicators(stale, active) {
        this.fresh.style = `background-color: ${stale ? 'rgb(240,160,40)' : 'rgb(40,200,80)'};`;
        this.lease.style = `background-color: ${active ? 'rgb(40,140,240)' : 'rgb(240,60,60)'};`;
        this.status.text = stale ? 'Stale' : 'Fresh';
    }
    Start() {
        if (this.phase !== 'calibration') return 'closed';
        this.phase = 'started'; this.erase();
        this.session = new NetworkSession({executable: GLib.getenv('SYSPANE_GNOME_NETWORK_EXECUTABLE'),
            root: GLib.getenv('SYSPANE_GNOME_NETWORK_ROOT'), journal: GLib.getenv('SYSPANE_GNOME_NETWORK_JOURNAL'),
            mode: ['lease-loss', 'hang'].includes(this.mode) ? this.mode : 'hold',
            onProjection: frame => this.draw(frame), onClear: () => {
                if (this.mode !== 'ignore-clear') this.erase();
            }});
        this.session.start(); return 'starting';
    }
    draw(frame) {
        if (this.phase !== 'started' || !this.session.active()) return;
        if (!this.rows.length) this.prepare();
        frame.fields.forEach((field, row) => {
            let value = field.value;
            if (row === 0 && value !== null && this.mode === 'wrong-value')
                value = (value[0] === '9' ? '8' : '9') + value.slice(1);
            this.text(row, value);
        });
        const field = frame.fields[0];
        if (field.age_ns === null) throw new Error('tile.missing_age');
        let age = String(BigInt(field.age_ns) / 1000000n);
        if (this.generation !== frame.generation) { this.generation = frame.generation; this.frozen = age; }
        if (this.mode === 'freeze-age') age = this.frozen;
        this.text(4, age); this.indicators(this.mode !== 'ignore-expiry' && field.effective === 1, frame.lease === 2);
    }
    GetState() {
        return JSON.stringify({phase: this.phase, labels: this.rows.reduce((n, row) => n + row.length, 0),
            session: this.session?.state() ?? null});
    }
    Revoke() { return this.session?.revoke() ?? 'closed'; }
    Stop() { this.session?.close(); this.phase = 'closed'; return 'stopping'; }
    Cleanup() { this.Stop(); this.erase(); return 'cleared'; }
    erase() {
        this.tile.hide();
        for (const actor of this.actors) { if (actor instanceof St.Label) actor.text = ''; actor.destroy(); }
        this.actors = []; this.rows = []; this.fresh = this.lease = this.status = null;
        this.frozen = this.generation = null;
    }
    disable() { this.Cleanup(); this.bus.unexport(); this.tile.destroy(); }
}
