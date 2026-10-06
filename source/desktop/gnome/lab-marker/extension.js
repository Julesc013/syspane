import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const INTERFACE = `<node><interface name="org.syspane.LabMarker">
<method name="SetGeneration"><arg type="u" direction="in" name="generation"/></method>
</interface></node>`;

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
        Main.layoutManager._backgroundGroup.add_child(this._actor);
        if (this._control === 'hidden')
            this._actor.hide();
        this._bus = Gio.DBusExportedObject.wrapJSObject(INTERFACE, this);
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

    disable() {
        this._bus?.unexport();
        this._bus = null;
        this._actor?.destroy();
        this._actor = null;
    }
}
