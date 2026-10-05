# Troubleshooting and recovery design

Development builds now contain `SysPane.Diag.exe` (Windows) or `syspane-diag`
(Linux). Run it without arguments for a native inspector, or with `--report` for
a small JSON report of the compiled build/profile and policy availability. It starts
without the main controller, scenes/themes, providers, custom renderer, persistent
history or setup provider. No downloadable product release is available yet.

The current inspector has Close and Escape; it reads no application configuration
and offers no repair, reset, preservation or support-bundle action yet. Missing or
unusable mandatory policy permits public diagnostic facts only. Available policy
can restrict report or inspector disclosure. The Linux report works without a
display server; the native inspector needs the development profile's GTK/display.

The following product recovery behavior remains under implementation:

| Condition | Intended response |
|---|---|
| Source denied or unavailable | Explain the source and keep unrelated information usable. |
| Controller stops updating | The surface expires its own lease and marks retained data. |
| Invalid layout or theme | Preserve the file and offer a readable built-in presentation. |
| Repeated worker/surface failure | Stop bounded retries and show the last failure. |
| Full/read-only storage | Keep a useful inspector and show unsaved or recording-gap state. |
| No qualified desktop host | Offer the inspector and report the missing wall capability. |

Safe mode preserves mandatory policy and cannot restore revoked permissions.
Support bundles require a preview and redact restricted fields, including
tooltips, accessibility data and retained exports. Repair restores owned program
files from an intact verified source; it does not erase configuration.

See [recovery](../../spec/architecture/recovery.md) and
[maintenance](../operators/deployment.md) for the proposed contracts.
