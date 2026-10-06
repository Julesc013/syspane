import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

const XML = `<node><interface name="org.syspane.SurfaceLease">
<method name="Attach"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Heartbeat"><arg type="u" direction="in"/><arg type="s" direction="out"/></method>
<method name="Snapshot"><arg type="u" direction="in"/><arg type="s" direction="out"/></method>
<method name="GetState"><arg type="s" direction="out"/></method>
<method name="Disable"/>
</interface></node>`;

// This native bridge consumes only the public marker fixture. Product telemetry
// still belongs to the C++ data/projection owners and its authenticated transport.
export class SurfaceLease {
    constructor(parent, paint) {
        this.mode = GLib.getenv('SYSPANE_GNOME_SURFACE_LEASE');
        this.pids = JSON.parse(GLib.getenv('SYSPANE_GNOME_LEASE_PIDS'));
        if (!['live', 'ignore-expiry', 'disconnect'].includes(this.mode) ||
            this.pids.length !== 2 || this.pids[0] === this.pids[1] ||
            !this.pids.every(p => Number.isSafeInteger(p) && p > 1))
            throw new Error('Retained native lease fixtures required');
        this.paint = paint;
        this.armed = false;
        this.enabled = true;
        this.used = new Set();
        this.owner = null;
        this.epoch = null;
        this.last = null;
        this.alive = false;
        this.needsSnapshot = true;
        this.sequence = null;
        this.generation = null;
        this.lastClock = GLib.get_monotonic_time();
        this.renewed = this.lastClock;
        this.pending = null;
        this.reason = 'none';
        this.clockFault = false;
        this.badge = new St.Widget({x: 460, y: 200, width: 120, height: 80,
            reactive: false, can_focus: false, visible: false});
        this.label = new St.Label({x: 4, y: 24, style: 'color: white; font-size: 13px;',
            reactive: false, can_focus: false});
        this.badge.add_child(this.label);
        parent.add_child(this.badge);
        this.bus = Gio.DBusExportedObject.wrapJSObject(XML, this);
        this.bus.export(Gio.DBus.session, '/org/syspane/SurfaceLease');
        this.ownerSignal = Gio.DBus.session.signal_subscribe('org.freedesktop.DBus',
            'org.freedesktop.DBus', 'NameOwnerChanged', '/org/freedesktop/DBus', null,
            Gio.DBusSignalFlags.NONE, (_c, _s, _p, _i, _n, args) => {
                const [name, oldOwner, newOwner] = args.deep_unpack();
                if (oldOwner && !newOwner) {
                    if (this.pending?.sender === name)
                        this.pending.gone = true;
                    if (this.owner === name)
                        this.close('disconnected');
                }
            });
        this.timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
            this.advance();
            return GLib.SOURCE_CONTINUE;
        });
    }

    advance() {
        const now = GLib.get_monotonic_time();
        if (now < this.lastClock) {
            this.clockFault = true;
            this.close('clock-fault');
        }
        this.lastClock = now;
        if (this.alive && this.mode !== 'ignore-expiry' && now - this.renewed >= 3000000)
            this.close('expired');
        return now;
    }

    close(reason) {
        if (!this.alive)
            return;
        this.alive = false;
        this.needsSnapshot = true;
        this.reason = reason;
        this.draw();
    }

    draw() {
        if (!this.armed || !this.enabled)
            return;
        const state = this.last ? (this.alive && !this.needsSnapshot ? 'ACTIVE' : 'RETAINED') : 'WAITING';
        const rgb = {ACTIVE: '32,160,64', RETAINED: '208,144,32', WAITING: '32,96,192'}[state];
        this.badge.style = `background-color: rgb(${rgb});`;
        this.label.text = state + '\n' + (this.last ? `${this.last.epoch} / ${this.last.generation}` : 'No snapshot');
        this.badge.show();
        this.paint(this.last?.generation ?? null);
    }

    reply(invocation, code) {
        invocation.return_value(new GLib.Variant('(s)', [code]));
    }

    AttachAsync([epoch], invocation) {
        this.advance();
        if (!this.enabled || this.clockFault || this.pending || this.alive || !['lease:1', 'lease:2'].includes(epoch)) {
            this.reply(invocation, this.alive || this.pending ? 'busy' : 'closed');
            return;
        }
        const sender = invocation.get_sender();
        const pending = {sender, gone: false, invocation};
        this.pending = pending;
        Gio.DBus.session.call('org.freedesktop.DBus', '/org/freedesktop/DBus',
            'org.freedesktop.DBus', 'GetConnectionUnixProcessID', new GLib.Variant('(s)', [sender]),
            new GLib.VariantType('(u)'), Gio.DBusCallFlags.NO_AUTO_START, 1000, null, (connection, result) => {
                let pid = null;
                try {
                    [pid] = connection.call_finish(result).deep_unpack();
                } catch (_) { /* Disconnected/unknown peers are never admitted. */ }
                if (this.pending !== pending)
                    return;
                this.pending = null;
                const now = this.advance();
                const slot = this.pids.indexOf(pid);
                if (!this.enabled || this.clockFault || pending.gone || slot < 0 || this.used.has(slot) || epoch !== `lease:${slot + 1}`) {
                    this.reply(invocation, 'unauthorized');
                    return;
                }
                this.used.add(slot);
                this.owner = sender;
                this.epoch = epoch;
                this.alive = true;
                this.needsSnapshot = true;
                this.sequence = null;
                this.generation = null;
                this.renewed = now;
                this.reason = 'none';
                this.armed = true;
                this.draw();
                this.reply(invocation, 'accepted');
            });
    }

    check(invocation) {
        this.advance();
        return this.enabled && this.alive && invocation.get_sender() === this.owner;
    }

    HeartbeatAsync([sequence], invocation) {
        if (!this.check(invocation)) {
            this.reply(invocation, 'closed');
            return;
        }
        if (this.sequence !== null && sequence <= this.sequence) {
            if (sequence < this.sequence)
                this.close('sequence-order');
            this.reply(invocation, sequence === this.sequence ? 'duplicate' : 'closed');
            return;
        }
        this.sequence = sequence;
        this.renewed = this.lastClock;
        this.reply(invocation, 'accepted');
    }

    SnapshotAsync([generation], invocation) {
        if (!this.check(invocation) || generation === 0) {
            this.reply(invocation, 'closed');
            return;
        }
        if (this.generation !== null && generation <= this.generation) {
            this.reply(invocation, generation === this.generation ? 'duplicate' : 'invalid');
            return;
        }
        this.generation = generation;
        this.last = {epoch: this.epoch, generation, accepted_us: this.lastClock};
        this.needsSnapshot = false;
        this.draw();
        this.reply(invocation, 'accepted');
    }

    GetState() {
        this.advance();
        return JSON.stringify({enabled: this.enabled, armed: this.armed, alive: this.alive,
            snapshot_required: this.needsSnapshot, epoch: this.epoch, owner: this.owner,
            last: this.last, reason: this.reason, renewed_us: this.renewed});
    }

    Disable() { this.disable(); }

    disable() {
        if (!this.enabled)
            return;
        this.enabled = false;
        if (this.pending) {
            this.reply(this.pending.invocation, 'closed');
            this.pending = null;
        }
        GLib.source_remove(this.timer);
        Gio.DBus.session.signal_unsubscribe(this.ownerSignal);
        this.bus.unexport();
        this.badge.destroy();
        this.alive = false;
        this.armed = false;
        this.owner = null;
    }
}
