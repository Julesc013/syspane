# Provider and SDK boundaries

The SDK is experimental and has no native implementation. Initial consumers are
out-of-process providers, local control clients and declarative content authors.
Native embedding has a separate admission gate.

Providers publish typed observations, source health and capability information.
The controller assigns provenance and limits demand. Manifests declare exact
identity, compatibility, architecture, permissions, quotas and content hashes.
Updates cannot silently expand permissions. Disabling drains work and leaves
truthful unavailable or retained observations.

Process separation contains some failures; a sandbox claim must name enforced
OS controls. Declarative scenes, themes and presets cannot execute code or grant
permissions. Unknown optional content is preserved inertly within bounds; unknown
required behaviour is rejected before activation.

The experimental C sketch uses caller-owned UTF-8 buffers. Result retrieval must
never repeat a mutation after an insufficient-buffer response. Export/calling
convention, allocator, threading and cancellation rules need real independent
consumer qualification before ABI stability. Only `source/api/` will own the
implemented public header after a recorded migration.

See [SDK](../../spec/contracts/sdk.md), [protocol](../../spec/contracts/protocol.md),
[versions](../../spec/contracts/versions.md) and
[content admission](../../spec/experience/presets.md).
