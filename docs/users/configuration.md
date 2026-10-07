# Configuration, scenes and presets

These are planned controls. Every advertised setting must be editable through
the native UI as well as the shared command API; hand-editing a file is optional.

The current Linux development editor supports selection, drag/resize, keyboard
movement, title/text/geometry fields, duplicate/delete, undo/redo and Apply/Cancel.
Property fields become one draft edit when Set properties is selected. Apply saves
the draft; activation and desktop visibility remain separate facts. This component
is tested in a private laboratory and is not yet an installed desktop edition.

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

These controls currently run in the owned Linux development editor. Binding
creation, new non-text widgets, remaining properties and installed desktop routing
are still pending. See the [recorded scope](../../spec/delivery/content-properties-handoff.md).
