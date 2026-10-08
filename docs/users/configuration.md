# Configuration, scenes and presets

These are planned controls. Every advertised setting must be editable through
the native UI as well as the shared command API; hand-editing a file is optional.

The current Linux development editor supports selection, drag/resize, keyboard
movement, title/text/geometry fields, duplicate/delete, undo/redo and Apply/Cancel.
Property fields become one draft edit when Set properties is selected. Apply saves
the draft; activation and desktop visibility remain separate facts. This component
is tested in a private laboratory and is not yet an installed desktop edition.

Select an object and choose Visibility to edit its own condition. Always show
removes that condition; a container's condition can still apply. When condition
matches lets you choose a data source, comparison, typed value and unit. New rules
start with this host's network receive bytes greater than 0 byte. Choose source
opens the existing binding controls. Set visibility creates one reversible draft
edit; Apply saves it. Cancel discards the private input.

For objects with different own conditions, Keep unchanged preserves each rule.
Choosing another mode replaces all selected own rules together. Hidden objects
remain in the object list: select them there to change or clear their condition.
Missing or failed source information remains visible as a diagnostic. During a drag,
conditions and diagnostics update while the captured geometry remains fixed.

Use Snap to grid or Snap to guides while dragging or resizing fixed widgets.
Magenta lines and the guide text show the chosen positions before release.
Hold Ctrl when releasing to bypass snapping. Arrow keys and numeric fields remain
precise, unsnapped alternatives. Show grid is independent of snapping; the Grid
button cycles through 8, 16, 32 and 4 DIP spacing. These preferences last for this
editor session and do not change the saved scene. Escape cancels the current drag;
changing a grid option also cancels it. Release creates one reversible draft edit.

Select two or more fixed widgets in the same parent and display, then choose
Group. The new container becomes selected; click its empty area or its list row
to select it later. Ungroup releases its direct children while preserving their
positions. Undo restores both the hierarchy and selection. Apply saves the draft.
Grouping nonadjacent objects places them together at the first selected drawing
position, which can change overlaps with intervening objects. Ungroup reports
clipped or unsupported layouts instead of changing their visible meaning.

Select at least two fixed widgets in the same group and display to align their
edges or centers. Select at least three for equal horizontal or vertical spacing.
Spacing keeps the endpoints in place and reports when there is insufficient room.
Arrange changes are reversible with Undo and become persistent only after Apply.
Finish or revert property fields before arranging. Responsive or size-expanded
widgets need explicit layout editing; this initial arrange control leaves them alone.

A setting changes application behaviour. A scene arranges widgets and their data
bindings. A theme supplies visual tokens. A preset combines those documents for
a task. Machine bindings map portable roles to local devices and displays.
Organization policy limits all of them.

Effective settings resolve built-in defaults, installation defaults, the selected
preset, user overrides and explicit session overrides, then enforce current
policy. The UI must explain each value's origin and any lock or unavailable
capability. A session flag or portable directory cannot override machine policy.

Customizing a shipped preset creates user overrides. Reset removes an override;
deleting an inherited widget is explicit. Updating a preset previews conflicts
with local edits. Importing content never enables probes, export, executable
extensions, elevation or autostart by itself.

Portable bindings select roles such as this host's physical network adapters.
Explicit device pins do not silently switch to replacement hardware. Missing
monitors retain their authored assignment. Theme/font fallback and responsive
layout change the rendered view without overwriting the source document.

The application default theme applies unless the scene selects another theme.
Policy, high contrast and reduced-motion requirements constrain either choice.
Stale, denied, replay and failure indicators always remain perceivable.

Contracts: [resolution](../../spec/experience/configuration-resolution.md),
[presets](../../spec/experience/presets.md),
[bindings](../../spec/experience/scene-bindings.md) and
[editing](../../spec/experience/editor.md).

## Content properties in the development editor

Custom font editing is still under development. The new theme format supports
font roles, but it is not yet enabled in scene previews or native theme controls.
Continue using the existing theme choices until that integration is available.

Choose **Content** with clean basic property fields. For a table, select a source
column, edit its label and use Move column up/down to move the label and source
together. Chart controls set the history window (1,000–3,600,000 ms), point limit
(2–4,096), interpolation and automatic/fixed axis. Image controls choose an admitted
asset, alternative text, preferred dimensions (1–4,096 DIP) and fit. Scene theme
offers an admitted theme or Inherit settings, even with no selected widget.

**Set content** applies one undoable draft change; **Apply** saves it. Cancel content
discards only the dialog buffer. Invalid values leave the draft unchanged and stay
available for correction. A policy change closes and clears the dialog; disclosure
regrant requires Reload. Text body remains in the basic property fields.

These controls currently run in the owned Linux development editor. All seven widget kinds now have creation controls below. Remaining properties and
installed desktop routing are still pending. See the [recorded scope](../../spec/delivery/content-properties-handoff.md).

## Bindings in the development editor

Select one value, status, chart or table and choose **Bindings**. Target controls
edit a selector, a direct producer/epoch/entity pin or a persistent namespace/key.
Selectors use an explicit host, session or registered-asset scope. Filter and Order
tabs add, remove and reorder predicates and sort keys. Numbers retain exact whole
values within signed/unsigned 64-bit limits. Text and boolean are distinct types.
For tables, choose the column to change its value field; target/filter/order changes
apply to every column together, preserving labels and order. Duplicate fields reject.

**Set bindings** creates one reversible draft change; **Apply** saves it. Invalid
input stays available for correction. Cancel bindings discards private input only.
Missing sources stay missing; entering a persistent key does not create a mapping
or grant access. Existing legacy pins stay inert until explicitly rebound.

Text normally uses literal format. Escaped format accepts one quoted string, such
as `"a\tb"` for a tab or `"a\\tb"` for a literal backslash and t. Existing control
characters automatically open in escaped format. The saved value remains the
decoded text; choosing a format determines how the current buffer is interpreted.
The existing 512-character limit applies after decoding. Policy/owner changes
erase all input, including hidden rows. See the [recorded scope](../../spec/delivery/binding-authoring-handoff.md).

## Adding widgets in the development editor

Choose **Add widget**, then text, value, status, table, chart, image or group.
Placement sets the title and fixed size/position. Choose Scene roots or an existing
group; coordinates inside a group are local to that group. A selected group is
the initial parent. Each kind keeps its own input while the dialog is open.

Content edits text or source fields. New counters/charts start with this host's
network receive counter; tables start with receive/sent columns. These visible
defaults do not acquire a source or grant access. Use **Bindings** to choose other
selectors/pins and **Content** for further options. Images require an explicit
choice from the admitted resource catalog; there is no automatic image selection.

**Add widget** inserts and selects one draft object. Undo restores the prior scene
and selection; Redo selects the restored object. **Apply** saves separately.
Cancel creation discards private input; invalid input stays available for correction.
Policy or owner changes erase the dialog, including hidden kind buffers. The older
**Add text** shortcut remains available. These controls currently run in the owned
Linux development editor, as scoped in the [handoff](../../spec/delivery/widget-creation-handoff.md).

## Layouts and responsive editing

Select one object and choose **Layout**. Leaves offer fixed or flow sizing; groups
offer fixed, canvas, stack or grid. The Geometry tab exposes each kind's dimensions,
constraints, anchor, axis, gap and overflow options. Changing kind keeps its private
input until the panel closes. Invalid numbers stay available for correction.

Choose Base or a breakpoint. **Add breakpoint** copies the selected variant and
requires a minimum display width. Up to eight thresholds must stay strictly
increasing; they are not automatically sorted. **Remove breakpoint** removes the
selected row. Threshold equality activates that variant using the display's safe
width. Direct drag, resize, keyboard and arrangement operations edit the currently
active fixed variant; the status text identifies it. Flow objects use constraints
and sibling order instead of direct movement.

Assignment changes priority and zero-based sibling position. Changing a local
display ID or portable role moves the object's entire top-level group, including
its descendants. Missing displays retain the assignment for later recovery.

**Set layout** makes one undoable draft change; **Apply** saves separately. Cancel
or Escape discards private input. Policy, owner and topology changes erase the
panel. If a topology change switches a variant while numeric geometry is buffered,
**Set properties** rejects it; **Revert fields** loads the active variant. These
controls are currently exercised in the owned Linux development editor, as scoped
in the [handoff](../../spec/delivery/layout-authoring-handoff.md).

The admitted Linux development editor also offers **Fonts** for base and role
fonts. Set changes the draft; Apply saves. See the [checkpoint](../../spec/delivery/theme-controls-handoff.md).


In the admitted Linux X11 development editor, select objects and choose **Copy**.
Choose **Paste** to append copies at the end of the scene's root objects. Ctrl+C and
Ctrl+V work when the canvas or object list has focus. Each paste is one undo step;
**Apply** saves separately. **Cancel paste** or Escape abandons a pending transfer.

Copies retain authored objects and exact image references, use fresh object IDs and
preserve the destination scene's theme. Missing resources refuse the entire paste.
Only SysPane object data is offered: ordinary text applications cannot paste it.
Live telemetry and private property fields are excluded. Changing policy, reloading,
saving, disconnecting or closing clears SysPane's copied snapshot; another app taking
the clipboard also clears it. Data already delivered to another app cannot be recalled.
Other native platforms and installed editions remain pending their own qualification.
See the [clipboard checkpoint](../../spec/delivery/native-clipboard-handoff.md).
