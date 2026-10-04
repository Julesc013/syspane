# Troubleshooting and recovery design

No diagnostic executable is shipped yet. The planned independent diagnostic
entry must start without the main controller, custom scenes/themes, third-party
providers, GPU initialization, persistent history or the setup provider.

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
