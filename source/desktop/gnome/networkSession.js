import Gio from 'gi://Gio';
import GLib from 'gi://GLib';

const finish = (begin, end) => new Promise((resolve, reject) => begin((object, result) => {
    try { resolve(end(object, result)); } catch (error) { reject(error); }
}));

// One serialized asynchronous owner, shared by standalone and desktop experiments.
// The caller owns policy authority and synchronously erases its sink on onClear.
class NativeSession {
    constructor(options) {
        this.options = options; this.phase = 'new'; this.error = null;
        this.child = null; this.connection = null; this.view = null;
        this.pid = null; this.exited = false; this.exitStatus = null; this.forced = false;
        this.readCancel = new Gio.Cancellable(); this.writeCancel = new Gio.Cancellable();
        this.queue = []; this.current = null; this.queuedBytes = 0; this.sequence = 0;
        this.subscribed = false; this.events = []; this.timer = 0; this.startTimer = 0;
        this.endTimer = 0; this.killTimer = 0; this.nextBeat = 0; this.closeTask = null;
        this.ready = new Promise((resolve, reject) => { this.readyResolve = resolve; this.readyReject = reject; });
        this.ready.catch(() => {});
        this.full = new Promise((resolve, reject) => { this.fullResolve = resolve; this.fullReject = reject; });
        this.full.catch(() => {});
    }
    active() { return this.phase === 'starting' || this.phase === 'live'; }
    async start() {
        if (this.phase !== 'new') throw new Error('session.used');
        this.phase = 'starting';
        this.startTimer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 2000, () => {
            this.startTimer = 0; this.close('session.startup_timeout'); return GLib.SOURCE_REMOVE;
        });
        this.endTimer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, this.lifetimeMs(), () => {
            this.endTimer = 0; this.close('session.deadline'); return GLib.SOURCE_REMOVE;
        });
        try {
            const native = (await import('gi://SysPaneClock?version=0.1')).default;
            if (!this.active()) return;
            this.preparePeer();
            await this.ready;
            if (!this.active()) return;
            const client = new Gio.SocketClient({enable_proxy: false});
            this.connection = await finish(cb => client.connect_async(new Gio.UnixSocketAddress({path: this.socketPath()}), this.readCancel, cb),
                (object, result) => object.connect_finish(result));
            if (!this.active()) { this.dropConnection(); return; }
            this.view = this.createView(native, this.connection.get_socket().get_fd());
            await this.send(this.view.hello());
            if (!this.active()) return;
            this.readTask = this.readFrames();
            this.timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
                this.advance();
                if (!this.active()) { this.timer = 0; return GLib.SOURCE_REMOVE; }
                return GLib.SOURCE_CONTINUE;
            });
            await this.full;
        } catch (error) {
            if (this.active()) await this.close(error.message);
        }
    }
    lifetimeMs() { return 18000; }
    preparePeer() {
        this.child = Gio.Subprocess.new(this.arguments(), Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
        this.pid = Number(this.child.get_identifier());
        if (!Number.isSafeInteger(this.pid) || this.pid <= 1) throw new Error('session.pid');
        this.waited = finish(cb => this.child.wait_async(null, cb), (child, result) => {
            child.wait_finish(result); this.exited = true;
            this.exitStatus = child.get_if_exited() ? child.get_exit_status() : -child.get_term_sig();
            if (this.killTimer) { GLib.source_remove(this.killTimer); this.killTimer = 0; }
            if (this.active()) this.close('session.peer_exited');
        });
        this.outputDone = this.readEvents(this.child.get_stdout_pipe());
    }
    async readEvents(stream) {
        let pending = ''; let total = 0;
        try {
            for (;;) {
                const bytes = await finish(cb => stream.read_bytes_async(512, GLib.PRIORITY_DEFAULT, null, cb),
                    (object, result) => object.read_bytes_finish(result));
                const raw = bytes.get_data(); if (!raw.length) break;
                total += raw.length;
                if (total > 16384 || raw.some(byte => byte > 127)) throw new Error('session.stdout_capacity');
                pending += String.fromCharCode(...raw);
                let boundary;
                while ((boundary = pending.indexOf('\n')) >= 0) {
                    if (boundary > 512 || this.events.length >= 64) throw new Error('session.stdout_capacity');
                    const row = JSON.parse(pending.slice(0, boundary)); pending = pending.slice(boundary + 1);
                    if (!this.eventNames().includes(row.event)) throw new Error('session.stdout_event');
                    this.events.push(row); this.options.onEvent?.(row);
                    if (row.event === 'ready') this.readyResolve();
                }
                if (pending.length > 512) throw new Error('session.stdout_capacity');
            }
            if (pending) throw new Error('session.stdout_partial');
        } catch (_) { if (this.active()) this.close('session.stdout'); }
        finally { stream.close(null); }
    }
    send(bytes, closing = false) {
        if ((!this.active() && !closing) || !this.connection) return Promise.reject(new Error('session.closed'));
        const raw = bytes.get_data();
        if (this.queue.length + (this.current ? 1 : 0) >= 16 || this.queuedBytes + raw.length > 65536)
            return Promise.reject(new Error('session.write_capacity'));
        return new Promise((resolve, reject) => {
            this.queue.push({raw, resolve, reject}); this.queuedBytes += raw.length; this.pump();
        });
    }
    async pump() {
        if (this.current || !this.queue.length) return;
        const item = this.queue.shift(); this.current = item;
        try {
            const [, size] = await finish(cb => this.connection.get_output_stream().write_all_async(item.raw, GLib.PRIORITY_DEFAULT, this.writeCancel, cb),
                (object, result) => object.write_all_finish(result));
            if (size !== item.raw.length) throw new Error('session.write');
            item.resolve();
        } catch (_) { item.reject(new Error('session.write')); }
        finally { this.queuedBytes -= item.raw.length; this.current = null; this.pump(); }
    }
    async readFrames() {
        try {
            while (this.active()) {
                const bytes = await finish(cb => this.connection.get_input_stream().read_bytes_async(this.readCapacity(), GLib.PRIORITY_DEFAULT, this.readCancel, cb),
                    (object, result) => object.read_bytes_finish(result));
                if (!this.active()) return;
                if (!bytes.get_size()) throw new Error('session.eof');
                await this.accept(bytes);
            }
        } catch (error) { if (this.active()) this.close(error.message); }
    }
    advance() {
        if (!this.active() || !this.view) return;
        try {
            const now = GLib.get_monotonic_time();
            if (this.subscribed && now >= this.nextBeat) {
                this.nextBeat = now + 1000000;
                this.send(this.view.heartbeat(String(this.sequence++))).catch(error => { if (this.active()) this.close(error.message); });
            }
            this.advanceNative();
        } catch (error) { this.close(error.message); }
    }
    accepted() {
        if (this.phase === 'starting') {
            this.phase = 'live'; GLib.source_remove(this.startTimer); this.startTimer = 0; this.fullResolve();
        }
    }
    close(reason = null) {
        if (this.closeTask) return this.closeTask;
        let resolved, rejected;
        this.closeTask = new Promise((resolve, reject) => { resolved = resolve; rejected = reject; });
        this.phase = 'closing'; this.error = reason;
        this.readyReject(new Error('session.closed')); this.fullReject(new Error('session.closed'));
        for (const key of ['timer', 'startTimer', 'endTimer']) if (this[key]) { GLib.source_remove(this[key]); this[key] = 0; }
        this.readCancel.cancel();
        let shutdown = null;
        try { shutdown = this.view?.shutdown(); } catch (_) { /* No negotiated session. */ }
        this.view?.close(); this.view = null; this.options.onClear();
        for (const item of this.queue) { this.queuedBytes -= item.raw.length; item.reject(new Error('session.closed')); }
        this.queue = [];
        if ((this.child && !this.exited) || this.options.peer) this.killTimer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
            this.killTimer = 0; this.writeCancel.cancel(); this.forced = !!this.child;
            this.child?.force_exit(); this.dropConnection(); return GLib.SOURCE_REMOVE;
        });
        this.finishClose(shutdown).then(resolved, rejected); return this.closeTask;
    }
    async finishClose(shutdown) {
        try { if (shutdown && this.connection) await this.send(shutdown, true); } catch (_) { /* Bounded native teardown follows. */ }
        this.dropConnection();
        await this.waited; await this.outputDone; await this.readTask;
        if (this.killTimer) { GLib.source_remove(this.killTimer); this.killTimer = 0; }
        this.child = null; this.subscribed = false; this.sequence = 0;
        // A sibling may initiate normal closure before this child's failure is
        // delivered. Keep its actual nonzero exit visible after every wait.
        if (this.error === null && this.exitStatus !== null && this.exitStatus !== 0)
            this.error = 'session.peer_failed';
        this.phase = this.error ? 'failed' : 'closed';
    }
    dropConnection() {
        try { this.connection?.close(null); } catch (_) { /* Already closed by native exit. */ }
        this.connection = null;
    }
    state() {
        return {phase: this.phase, error: this.error, pid: this.pid, exited: this.exited,
            exitStatus: this.exitStatus, forced: this.forced, view: this.view !== null,
            connection: this.connection !== null, queuedBytes: this.queuedBytes, events: this.events};
    }
}

export class NetworkSession extends NativeSession {
    arguments() { return [this.options.executable, 'stream', this.options.root, this.options.mode, this.options.journal]; }
    socketPath() { return this.options.root + '/v/s'; }
    readCapacity() { return 16384; }
    eventNames() { return ['ready', 'spawned', 'authenticated', 'stopped', 'complete', 'error']; }
    createView(native, fd) { return native.NetworkView.new_from_socket(fd, this.pid, '7', true); }
    async accept(bytes) {
        const code = this.view.feed(bytes);
        if (code !== 'buffered' && !this.subscribed) {
            await this.send(this.view.subscribe()); this.subscribed = true;
        }
    }
    advanceNative() {
        const frame = JSON.parse(this.view.project());
        if (frame.code === 'ready') { this.accepted(); this.options.onProjection(frame); }
    }
    revoke() {
        if (!this.active() || !this.view) return 'closed';
        const code = this.view.policy('8', false);
        this.options.onClear(); this.close(); return code;
    }
}

// The controller is an authenticated external owner, never this session's child.
export class AttachedNetworkSession extends NetworkSession {
    lifetimeMs() { return 60000; }
    preparePeer() {
        this.pid = Number(this.options.peer);
        if (!Number.isSafeInteger(this.pid) || this.pid <= 1) throw new Error('session.pid');
        this.readyResolve();
    }
}

export class RenderSession extends NativeSession {
    constructor(options) { super(options); this.receipts = []; }
    arguments() { return [this.options.executable, 'render-watch', this.socketPath(), this.options.journal]; }
    socketPath() { return this.options.root + '/r/s'; }
    readCapacity() { return 4096; }
    eventNames() { return ['ready', 'authenticated', 'complete', 'error', 'heartbeat', 'challenge', 'progress', 'fault']; }
    createView(native, fd) { return native.HealthView.new_from_socket(fd, this.pid); }
    async accept(bytes) {
        for (const event of JSON.parse(this.view.feed(bytes))) {
            if (this.receipts.length >= 64) throw new Error('health.receipt_capacity');
            this.receipts.push(event);
            if (event.kind === 'ready') { this.subscribed = true; this.accepted(); }
            else if (event.kind === 'challenge') this.options.onChallenge(event.value);
            else if (event.kind === 'shutdown') { this.close('health.shutdown'); break; }
        }
    }
    advanceNative() { this.view.tick(); }
    complete(generation) {
        if (!this.active() || !this.view) return;
        try { this.send(this.view.progress(generation)).catch(error => { if (this.active()) this.close(error.message); }); }
        catch (error) { this.close(error.message); }
    }
    state() { return {...super.state(), receipts: this.receipts}; }
}
