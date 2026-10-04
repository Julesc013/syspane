# Deployment and maintenance design

No downloadable payload or qualified installer exists. Release selection will
offer only exact qualified target profiles, with normal desktop, portable and
optional component choices. CPU/ABI and runtime floors belong in package
identity; ordinary executable names stay stable.

Installations have one mutation owner: unmanaged portable, Universal Setup
(USK) managed, or a native package manager. USK cannot independently overwrite
MSI, PKG, DEB or RPM-owned resources. Ordinary SysPane startup must work without
initializing USK. Provider integration remains unqualified until its exact source,
artifact, platform and operation have consumer evidence.

Keep payload, user content, machine policy, local history, disposable cache,
session IPC and setup state separate. Portable mode selects a data root
explicitly. Read-only media must report session-only changes or request a
deliberately chosen save location; it must not silently scatter files elsewhere.

Repair restores an identified release's owned payload. Upgrade plans document
compatibility and rollback. Uninstall preserves user data and reports modified
or foreign files. Purge is a separate destructive operation. Saver-only removal
must preserve content shared with the desktop application.

Offline packages precede automatic updating. Public releases need license and
notice decisions, exact dependency closure, native evidence and authorized
signing/publication. Signing transformations and reproducible unsigned payloads
have separate hashes. Future online updating needs trusted metadata, key
rotation/revocation, expiry and rollback/freeze protections before enablement.

Contracts: [artifacts](../../spec/delivery/artifacts.md),
[paths and ownership](../../spec/setup/ownership.md),
[provider binding](../../spec/setup/contract.md) and
[lifecycle/recovery](../../spec/setup/lifecycle.md).
