# Configuration, scenes and presets

These are planned controls. Every advertised setting must be editable through
the native UI as well as the shared command API; hand-editing a file is optional.

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
