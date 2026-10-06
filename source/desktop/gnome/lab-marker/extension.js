import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import St from 'gi://St';
import Clutter from 'gi://Clutter';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {SurfaceLease} from './surfaceLease.js';
import {NetworkCache} from './networkCache.js';
import {ClockExperiment} from './clockExperiment.js';

const INTERFACE = `<node><interface name="org.syspane.LabMarker">
<method name="SetGeneration"><arg type="u" direction="in" name="generation"/></method>
</interface></node>`;
const COMPOSITION_INTERFACE = INTERFACE.replace('</interface>',
    '<method name="SetSceneEnabled"><arg type="b" direction="in" name="enabled"/></method></interface>');

// Independent painter; the external pixel decoder is never imported here.
function payload(generation) {
    const bytes = [83, 89, 80, 78, 1, 0, 0, 0, 0,
        generation >>> 24, (generation >>> 16) & 255,
        (generation >>> 8) & 255, generation & 255];
    let crc = 0xffffffff;
    for (const byte of bytes) {
        crc ^= byte;
        for (let n = 0; n < 8; n++)
            crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
    crc = (crc ^ 0xffffffff) >>> 0;
    bytes.push(crc >>> 24, (crc >>> 16) & 255, (crc >>> 8) & 255, crc & 255);
    return bytes;
}

class RevealFocusIntegration {
    constructor(mode) {
        if (!['observe', 'restore'].includes(mode) || Meta.is_wayland_compositor())
            throw new Error('Named X11 focus integration mode required');
        this.mode = mode;
        this.enabled = true;
        this.records = [];
        this.target = null;
        this.pending = null;
        this.targetSignals = [];
        this.settings = new Gio.Settings({schema_id: 'org.gnome.desktop.wm.keybindings'});
        this.signals = [
            [global.display, global.display.connect('notify::focus-window', () => this.remember())],
            [global.workspace_manager, global.workspace_manager.connect('active-workspace-changed', () => this.clear('workspace'))],
            [global.workspace_manager, global.workspace_manager.connect('showing-desktop-changed', () => this.changed())],
        ];
        this.remember();
    }

    eligible(window) {
        return window && window.get_window_type() === Meta.WindowType.NORMAL &&
            !window.minimized && !window.get_transient_for() && window.get_compositor_private() &&
            window.located_on_workspace(global.workspace_manager.get_active_workspace());
    }

    record(event, detail = {}) {
        this.records.push({event, monotonic_us: GLib.get_monotonic_time(), ...detail});
        if (this.records.length > 256 || JSON.stringify(this.records).length > 65536) {
            this.disable();
            throw new Error('Focus integration diagnostic capacity');
        }
    }

    clear(reason) {
        for (const [window, id] of this.targetSignals)
            window.disconnect(id);
        this.targetSignals = [];
        this.target = null;
        this.pending = null;
        this.record('clear', {reason});
    }

    remember() {
        const window = global.display.get_focus_window();
        if (!this.eligible(window) || !window.showing_on_its_workspace() || window === this.target)
            return;
        this.clear('new-normal-focus');
        this.target = window;
        this.targetSignals = ['unmanaging', 'workspace-changed', 'notify::minimized'].map(signal =>
            [window, window.connect(signal, () => this.clear(signal))]);
        this.record('remember', {pid: window.get_pid(), sequence: window.get_stable_sequence()});
    }

    changed() {
        if (!this.enabled)
            return;
        const event = Clutter.get_current_event();
        const key = event?.type() === Clutter.EventType.KEY_PRESS;
        const state = key ? event.get_state() : 0;
        const superMask = Clutter.ModifierType.SUPER_MASK | Clutter.ModifierType.MOD4_MASK;
        const allowed = superMask | Clutter.ModifierType.LOCK_MASK | Clutter.ModifierType.MOD2_MASK;
        const symbol = key ? event.get_key_symbol() : 0;
        const binding = this.settings.get_strv('show-desktop');
        const eligibleEvent = key && [Clutter.KEY_d, Clutter.KEY_D].includes(symbol) &&
            (state & superMask) !== 0 && (state & ~allowed) === 0 && event.get_time() !== 0 &&
            binding.length === 1 && binding[0] === '<Super>d';
        const window = this.target;
        const workspace = global.workspace_manager.get_active_workspace();
        const focus = global.display.get_focus_window();
        const row = {event_type: event?.type() ?? null, key_symbol: symbol, state,
            native_time: key ? event.get_time() : 0, eligible_event: Boolean(eligibleEvent),
            target_pid: window?.get_pid() ?? null, target_sequence: window?.get_stable_sequence() ?? null,
            focus_pid: focus?.get_pid() ?? null, workspace: workspace.index()};
        if (!eligibleEvent || !this.eligible(window)) {
            this.pending = null;
            this.record('abstain', row);
            return;
        }
        row.showing = window.showing_on_its_workspace();
        if (!row.showing) {
            this.pending = {window, workspace};
            this.record('entry', row);
            return;
        }
        const restore = this.pending?.window === window && this.pending.workspace === workspace &&
            focus?.get_window_type() === Meta.WindowType.DESKTOP;
        this.pending = null;
        if (!restore) {
            this.record('abstain', row);
            return;
        }
        this.record('restore', {...row, performed: this.mode === 'restore'});
        if (this.mode === 'restore')
            window.focus(event.get_time());
    }

    disable() {
        if (!this.enabled)
            return;
        this.enabled = false;
        for (const [owner, id] of this.signals)
            owner.disconnect(id);
        this.signals = [];
        for (const [window, id] of this.targetSignals)
            window.disconnect(id);
        this.targetSignals = [];
        this.target = null;
        this.pending = null;
    }
}

export default class LabMarker extends Extension {
    enable() {
        this._control = GLib.getenv('SYSPANE_GNOME_MARKER_CONTROL') ?? 'live';
        if (!['live', 'hidden', 'frozen'].includes(this._control))
            throw new Error('Unknown laboratory control');
        this._composition = GLib.getenv('SYSPANE_GNOME_COMPOSITION');
        if (this._composition && !['live', 'above-icons', 'below-wallpaper'].includes(this._composition))
            throw new Error('Unknown composition control');
        this._generation = 1;
        this._actor = new St.DrawingArea({x: 300, y: 200, width: 128, height: 96,
            reactive: false, can_focus: false, track_hover: false});
        this._actor.connect('repaint', area => {
            const context = area.get_context();
            const bytes = payload(this._generation);
            let bit = 0;
            for (let row = 0; row < 12; row++) {
                for (let column = 0; column < 16; column++) {
                    let color;
                    if (row === 0 || row === 11 || column === 0 || column === 15) {
                        color = column === 0 && row === 11 ? [160, 32, 192] :
                            ((column + row) % 2 === 0 ? [16, 96, 224] : [240, 160, 16]);
                    } else {
                        const one = bit < 136 && ((bytes[bit >> 3] >> (7 - (bit & 7))) & 1);
                        color = one ? [224, 224, 224] : [32, 32, 32];
                        bit++;
                    }
                    context.setSourceRGB(...color.map(value => value / 255));
                    context.rectangle(column * 8, row * 8, 8, 8);
                    context.fill();
                }
            }
            context.$dispose();
        });
        const parent = this._composition === 'above-icons' ? Main.uiGroup : Main.layoutManager._backgroundGroup;
        const attach = actor => {
            if (this._composition === 'below-wallpaper')
                parent.insert_child_at_index(actor, 0);
            else
                parent.add_child(actor);
        };
        attach(this._actor);
        if (this._composition) {
            this._witness = new St.DrawingArea({x: 0, y: 32, width: 180, height: 220,
                reactive: false, can_focus: false, track_hover: false});
            this._witness.connect('repaint', area => {
                const context = area.get_context();
                context.setSourceRGB(192 / 255, 32 / 255, 128 / 255);
                context.paint();
                context.$dispose();
            });
            attach(this._witness);
            const inputControl = GLib.getenv('SYSPANE_GNOME_INPUT_CONTROL');
            if (inputControl && !['live', 'block-pointer', 'no-selection'].includes(inputControl))
                throw new Error('Unknown native input control');
            if (inputControl === 'block-pointer') {
                this._inputShield = new St.Widget({x: 0, y: 32, width: 180, height: 220,
                    reactive: true, can_focus: false});
                this._inputShield.connect('button-press-event', () => Clutter.EVENT_STOP);
                this._inputShield.connect('button-release-event', () => Clutter.EVENT_STOP);
                Main.layoutManager.addChrome(this._inputShield, {affectsInputRegion: true,
                    affectsStruts: false, trackFullscreen: false});
            }
            const wallpaperControl = GLib.getenv('SYSPANE_GNOME_WALLPAPER_CONTROL');
            if (wallpaperControl && !['live', 'replace-file', 'redirect-setting', 'cover-wallpaper'].includes(wallpaperControl))
                throw new Error('Unknown wallpaper control');
            if (wallpaperControl === 'cover-wallpaper') {
                this._wallpaperCover = new St.DrawingArea({x: 600, y: 400, width: 128, height: 96,
                    reactive: false, can_focus: false, track_hover: false});
                this._wallpaperCover.connect('repaint', area => {
                    const context = area.get_context();
                    context.setSourceRGB(1 / 255, 2 / 255, 3 / 255);
                    context.paint();
                    context.$dispose();
                });
                attach(this._wallpaperCover);
                this._wallpaperOccluded = false;
            }
            this.SetSceneEnabled(false);
        }
        if (this._control === 'hidden')
            this._actor.hide();
        let interfaceXml = this._composition ? COMPOSITION_INTERFACE : INTERFACE;
        const integration = GLib.getenv('SYSPANE_GNOME_FOCUS_INTEGRATION');
        if (integration) {
            this._focusIntegration = new RevealFocusIntegration(integration);
            interfaceXml = interfaceXml.replace('</interface>',
                '<method name="GetFocusTrace"><arg type="s" direction="out" name="trace"/></method>' +
                '<method name="DisableFocusIntegration"/></interface>');
        }
        this._recoveryControl = GLib.getenv('SYSPANE_GNOME_ICON_RECOVERY');
        if (this._recoveryControl && !['live', 'frozen-surface', 'no-stop'].includes(this._recoveryControl))
            throw new Error('Unknown icon-recovery control');
        this._recoveryFrozen = false;
        if (this._recoveryControl === 'frozen-surface')
            interfaceXml = interfaceXml.replace('</interface>',
                '<method name="FreezeRecoveryMarker"><arg type="b" direction="in" name="frozen"/></method></interface>');
        if (this._wallpaperCover)
            interfaceXml = interfaceXml.replace('</interface>',
                '<method name="SetWallpaperOccluded"><arg type="b" direction="in" name="occluded"/></method></interface>');
        this._bus = Gio.DBusExportedObject.wrapJSObject(interfaceXml, this);
        this._bus.export(Gio.DBus.session, '/org/syspane/LabMarker');
        if (GLib.getenv('SYSPANE_GNOME_CLOCK_AGE'))
            this._clockExperiment = new ClockExperiment(parent);
        if (GLib.getenv('SYSPANE_GNOME_NETWORK_CACHE'))
            this._networkCache = new NetworkCache(parent);
        if (GLib.getenv('SYSPANE_GNOME_SURFACE_LEASE'))
            this._surfaceLease = new SurfaceLease(parent, generation => {
                this._actor.visible = generation !== null;
                if (generation !== null) {
                    this._generation = generation;
                    this._actor.queue_repaint();
                }
            });
    }

    SetGeneration(generation) {
        if (this._surfaceLease?.armed)
            throw new Error('An attached producer owns marker updates');
        if (!Number.isInteger(generation) || generation < 1 || generation > 0xffffffff)
            throw new Error('Generation outside the laboratory uint32 range');
        if (this._control === 'frozen' || this._recoveryFrozen)
            return;
        this._generation = generation;
        this._actor.queue_repaint();
    }

    SetSceneEnabled(enabled) {
        if (!this._composition || typeof enabled !== 'boolean')
            throw new Error('Scene visibility is available only in the composition experiment');
        if (enabled && this._composition === 'below-wallpaper') {
            const parent = Main.layoutManager._backgroundGroup;
            parent.set_child_below_sibling(this._actor, null);
            parent.set_child_below_sibling(this._witness, null);
        }
        this._actor.visible = enabled;
        this._witness.visible = enabled;
        if (this._inputShield)
            this._inputShield.visible = enabled;
        if (this._wallpaperCover)
            this._wallpaperCover.visible = enabled && this._wallpaperOccluded;
    }

    SetWallpaperOccluded(occluded) {
        if (!this._wallpaperCover || typeof occluded !== 'boolean')
            throw new Error('Wallpaper occlusion is available only in its explicit control');
        this._wallpaperOccluded = occluded;
        this._wallpaperCover.visible = this._witness.visible && occluded;
    }

    FreezeRecoveryMarker(frozen) {
        if (this._recoveryControl !== 'frozen-surface' || frozen !== true)
            throw new Error('One-way freeze is available only in the recovery control');
        this._recoveryFrozen = true;
    }

    GetFocusTrace() {
        return JSON.stringify({version: '0.1.0', mode: this._focusIntegration.mode,
            enabled: this._focusIntegration.enabled, records: this._focusIntegration.records});
    }

    DisableFocusIntegration() {
        this._focusIntegration.disable();
    }

    disable() {
        this._clockExperiment?.disable();
        this._clockExperiment = null;
        this._networkCache?.disable();
        this._networkCache = null;
        this._surfaceLease?.disable();
        this._surfaceLease = null;
        this._focusIntegration?.disable();
        this._focusIntegration = null;
        this._bus?.unexport();
        this._bus = null;
        this._actor?.destroy();
        this._actor = null;
        this._witness?.destroy();
        this._witness = null;
        if (this._inputShield) {
            Main.layoutManager.removeChrome(this._inputShield);
            this._inputShield.destroy();
        }
        this._inputShield = null;
        this._wallpaperCover?.destroy();
        this._wallpaperCover = null;
    }
}
