import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

const XML = `<node><interface name="org.syspane.NetworkCache">
<method name="Attach"><arg type="s" direction="out"/></method>
<method name="Policy"><arg type="s" direction="in"/><arg type="b" direction="in"/><arg type="s" direction="out"/></method>
<method name="Frame"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Heartbeat"><arg type="u" direction="in"/><arg type="s" direction="out"/></method>
<method name="GetState"><arg type="s" direction="out"/></method>
<method name="Disable"><arg type="s" direction="out"/></method>
</interface></node>`;
const uint = s => typeof s === 'string' && /^(0|[1-9][0-9]{0,19})$/.test(s) &&
    (s.length < 20 || s <= '18446744073709551615');
const order = (a, b) => a.length === b.length ? (a === b ? 0 : a < b ? -1 : 1) : a.length < b.length ? -1 : 1;
const id = s => typeof s === 'string' && s.length > 0 && s.length <= 256 && /^[A-Za-z0-9][A-Za-z0-9._:/-]*$/.test(s);

export class NetworkCache {
    constructor(parent) {
        this.pid = Number(GLib.getenv('SYSPANE_GNOME_NETWORK_PID'));
        this.mode = GLib.getenv('SYSPANE_GNOME_NETWORK_CACHE');
        if (!Number.isSafeInteger(this.pid) || this.pid <= 1 || !['live', 'ignore-clear', 'wrong-value', 'owner-loss'].includes(this.mode))
            throw new Error('Retained network cache fixture required');
        this.enabled = true; this.used = false; this.owner = null; this.pending = null;
        this.permit = false; this.revision = '0'; this.sequence = '0'; this.beat = null;
        this.lastClock = GLib.get_monotonic_time(); this.renewed = this.lastClock;
        this.payload = null; this.labels = []; this.rows = []; this.closed = false;
        this.tile = new St.Widget({x: 300, y: 310, width: 448, height: 150, reactive: false, can_focus: false, visible: false});
        this.caption = new St.Label({text: 'Retained sample — age unknown', x: 0, y: 0,
            style: 'color: white; font-size: 16px;', reactive: false, can_focus: false});
        this.tile.add_child(this.caption); parent.add_child(this.tile);
        this.bus = Gio.DBusExportedObject.wrapJSObject(XML, this);
        this.bus.export(Gio.DBus.session, '/org/syspane/NetworkCache');
        this.signal = Gio.DBus.session.signal_subscribe('org.freedesktop.DBus', 'org.freedesktop.DBus',
            'NameOwnerChanged', '/org/freedesktop/DBus', null, Gio.DBusSignalFlags.NONE, (_c, _s, _p, _i, _n, args) => {
                const [name, oldOwner, newOwner] = args.deep_unpack();
                if (oldOwner && !newOwner) {
                    if (this.pending?.sender === name) this.pending.gone = true;
                    if (this.owner === name) this.close();
                }
            });
        this.timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => { this.advance(); return GLib.SOURCE_CONTINUE; });
    }
    clear() {
        for (const label of this.labels) { label.text = ''; label.destroy(); }
        for (const row of this.rows) row.destroy();
        this.labels = []; this.rows = []; this.payload = null; this.tile.hide();
    }
    close() { this.closed = true; this.permit = false; this.clear(); }
    advance() {
        const now = GLib.get_monotonic_time();
        if (now < this.lastClock || (this.owner && now - this.renewed >= 3000000)) this.close();
        this.lastClock = now;
    }
    reply(invocation, code) { invocation.return_value(new GLib.Variant('(s)', [code])); }
    authorized(invocation) {
        this.advance();
        return this.enabled && !this.closed && this.owner !== null && invocation.get_sender() === this.owner;
    }
    AttachAsync(_args, invocation) {
        if (!this.enabled || this.used || this.pending || this.closed) { this.reply(invocation, 'closed'); return; }
        const pending = {sender: invocation.get_sender(), gone: false, invocation}; this.pending = pending;
        Gio.DBus.session.call('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus',
            'GetConnectionUnixProcessID', new GLib.Variant('(s)', [pending.sender]), new GLib.VariantType('(u)'),
            Gio.DBusCallFlags.NO_AUTO_START, 1000, null, (connection, result) => {
                let pid = null;
                try { [pid] = connection.call_finish(result).deep_unpack(); } catch (_) { /* Deny. */ }
                if (this.pending !== pending) return;
                this.pending = null;
                if (!this.enabled || this.closed || pending.gone || pid !== this.pid) { this.reply(invocation, 'unauthorized'); return; }
                this.used = true; this.owner = pending.sender; this.renewed = GLib.get_monotonic_time();
                this.reply(invocation, 'accepted');
            });
    }
    PolicyAsync([revision, permit], invocation) {
        if (!this.authorized(invocation)) { this.reply(invocation, 'unauthorized'); return; }
        if (!uint(revision) || revision === '0' || order(revision, this.revision) < 0 ||
            (revision === this.revision && permit !== this.permit)) { this.reply(invocation, 'invalid'); return; }
        if (revision === this.revision) { this.reply(invocation, 'duplicate'); return; }
        this.revision = revision; this.permit = permit; this.sequence = '0';
        if (!(this.mode === 'ignore-clear' && !permit)) this.clear();
        this.reply(invocation, 'cleared');
    }
    HeartbeatAsync([sequence], invocation) {
        if (!this.authorized(invocation)) { this.reply(invocation, 'unauthorized'); return; }
        if (this.beat !== null && sequence <= this.beat) {
            if (sequence < this.beat) this.close();
            this.reply(invocation, sequence === this.beat ? 'duplicate' : 'closed'); return;
        }
        this.beat = sequence; this.renewed = this.lastClock; this.reply(invocation, 'accepted');
    }
    FrameAsync([revision, sequence, raw], invocation) {
        if (!this.authorized(invocation)) { this.reply(invocation, 'unauthorized'); return; }
        if (!this.permit || revision !== this.revision) { this.reply(invocation, 'restricted'); return; }
        if (!uint(sequence) || order(sequence, this.sequence) <= 0) { this.reply(invocation, 'invalid'); return; }
        let value;
        try {
            if (new TextEncoder().encode(raw).length > 4096) throw new Error('size');
            value = JSON.parse(raw);
            if (!value || Array.isArray(value) || Object.keys(value).sort().join(',') !== 'entity,epoch,generation,producer,values' ||
                !id(value.producer) || !id(value.epoch) || !id(value.entity) || !uint(value.generation) || value.generation === '0' ||
                !Array.isArray(value.values) || value.values.length !== 4 || !value.values.every((s, i) => s === null ||
                    (i < 2 ? uint(s) : typeof s === 'string' && /^(0|[1-9][0-9]*)\.[0-9]{3}$/.test(s)))) throw new Error('shape');
        } catch (_) { this.reply(invocation, 'invalid'); return; }
        if (value.values.some(s => s !== null && s.length > 32)) { this.clear(); this.reply(invocation, 'capacity'); return; }
        this.clear(); this.payload = value; this.sequence = sequence;
        for (let row = 0; row < 4; row++) {
            const background = new St.Widget({x: 0, y: 30 + row * 30, width: 448, height: 26,
                style: 'background-color: rgb(20,30,40);', reactive: false, can_focus: false});
            this.rows.push(background); this.tile.add_child(background);
            let text = value.values[row] ?? '-';
            if (this.mode === 'wrong-value' && value.producer !== 'fixture:calibration' && row === 0)
                text = (text[0] === '9' ? '8' : '9') + text.slice(1);
            for (let column = 0; column < text.length; column++) {
                const label = new St.Label({x: column * 14, y: 0, width: 14, height: 26, text: text[column],
                    style: 'color: white; font-family: monospace; font-size: 20px;', reactive: false, can_focus: false});
                background.add_child(label); this.labels.push(label);
            }
        }
        this.tile.show(); this.reply(invocation, 'accepted');
    }
    GetState() {
        this.advance();
        return JSON.stringify({enabled: this.enabled, closed: this.closed, permitted: this.permit,
            revision: this.revision, sequence: this.sequence, entries: this.payload ? 1 : 0, labels: this.labels.length});
    }
    DisableAsync(_args, invocation) {
        if (!this.authorized(invocation)) { this.reply(invocation, 'unauthorized'); return; }
        this.clear(); this.reply(invocation, 'cleared'); this.disable();
    }
    disable() {
        if (!this.enabled) return;
        this.enabled = false; this.clear();
        if (this.pending) { this.reply(this.pending.invocation, 'closed'); this.pending = null; }
        GLib.source_remove(this.timer); Gio.DBus.session.signal_unsubscribe(this.signal);
        this.bus.unexport(); this.tile.destroy(); this.owner = null;
    }
}
