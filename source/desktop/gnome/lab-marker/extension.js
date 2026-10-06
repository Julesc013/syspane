import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

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
            this.SetSceneEnabled(false);
        }
        if (this._control === 'hidden')
            this._actor.hide();
        this._bus = Gio.DBusExportedObject.wrapJSObject(this._composition ? COMPOSITION_INTERFACE : INTERFACE, this);
        this._bus.export(Gio.DBus.session, '/org/syspane/LabMarker');
    }

    SetGeneration(generation) {
        if (!Number.isInteger(generation) || generation < 1 || generation > 0xffffffff)
            throw new Error('Generation outside the laboratory uint32 range');
        if (this._control === 'frozen')
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
    }

    disable() {
        this._bus?.unexport();
        this._bus = null;
        this._actor?.destroy();
        this._actor = null;
        this._witness?.destroy();
        this._witness = null;
    }
}
