---
type: "SysPane Work Package"
title: "Installation-relative helper identity and immutable launch"
description: "Bind private helper execution to the running application's compiled payload closure."
tags: ["delivery", "setup", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T19:28:59+00:00"}
sp_id: "SP-W26-HELPER-IDENTITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W26-PACKAGE", "SP-W08-PROFILE-SUPERVISOR", "SP-INSTALL-OWNERSHIP", "SP-ARTIFACTS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installation-relative helper identity and immutable launch

Continue W-26's local development packaging and W-08's native supervisor boundary.
Implement LinuxInstallation under source/platform, compiled helper-closure generation
under source/build, and a LinuxProfileSupervisor constructor consuming this owner.
The existing independently admitted native-path constructor remains usable for
bounded composition tests; installed frontend code must use verified installation
lookup. Do not infer policy, persistent-data mode or release qualification from it.

## Fixed layout and trust anchor

For this initial Linux development payload, the application is bin/syspane, the
configuration helper is libexec/syspane/syspane-configuration-host, and the helper
closure is share/syspane/helpers.json, all relative to one payload prefix. Discover
that prefix from the kernel's /proc/self/exe identity and exact bin/syspane suffix.
Never use argv[0], cwd, PATH, environment-selected program roots or a session field.
Portable relocation before startup is supported. This lookup writes no payload,
setup receipt, user data or autostart resource and adopts no maintenance ownership.

The build first produces the actual configuration-host ELF. A generator verifies
its x86-64 ELF identity, fixed interpreter and declared OS imports, rejects RPATH/
RUNPATH and origin-dependent/private loader closure, then writes one canonical
helpers.json and a private generated C++ expectation header. Both derive from those
same helper bytes. The application embeds the expected record digest, helper digest
and helper byte count. The record has exactly format=SysPane.Helpers,
schema_version=0.1.0, target_profile=linux-x64-gcc13, product_version=0.0.1 and
configuration_host={path,sha256,bytes,imports}; bytes is a positive decimal string,
path is the fixed relative helper path and imports is the sorted admitted list.
Its identity changes when helper bytes change; no timestamp or absolute build path
enters it. The record does not contain its consumer executable hash, avoiding a
circular build dependency. A later full release manifest owns complete package
closure, source/toolchain identities, licensing and frontend hashes.

The compiled expectation is rooted in the already executing application. A manifest
and helper that agree with each other but differ from that expectation must fail.
This protects helper selection and byte identity; it does not authenticate the
application's original acquisition, replace package signatures, enable online updates
or authorize a privileged installation. Existing acquisition/release gates remain.

## Native admission and immutable bytes

Use one serialized worker outside GUI callbacks. Admit only the existing unprivileged
context. Bound the discovered executable path to 512 bytes and the ancestor walk to
64 components. Walk from / using held no-follow directory descriptors. Ancestors
must be owned by root or the current uid with no group/other write or special mode
bits; files/directories beneath the payload prefix must have the prefix's owner.
The initial qualified payload filesystem is ext4 or tmpfs. Other filesystems and
platforms require their own native evidence; this is not a new universal floor.

Hold identities for the ancestor chain, bin/libexec/share subdirectories, current
executable, helper and record. Named and held current-executable identities must
match /proc/self/exe. Payload files must be regular single-link files with no group/
other write or special bits; executables require executable bits, the record does
not. Refuse symlinks, aliases, deleted/replaced current executables and unknown
record fields. Bound the record to 65536 bytes and the helper to 64 MiB, matching
the compiled positive byte count before allocation. Read exactly that length with
bounded EINTR retries and verify stable identity/size/mtime/ctime and current path
bindings before and after hashing. The existing document/content digest ceilings
remain 1 MiB/16 MiB; add a separate 64 MiB payload-digest entry using the same SHA-256
algorithm. Independent Python hashes must agree for the real multi-megabyte ELF.

Copy the verified bytes into an executable memfd, then require WRITE, SHRINK, GROW
and SEAL seals. Release the transient input buffer after sealing. Retain at most
one 64 MiB immutable image per installation owner, plus a transient input buffer
of at most 64 MiB during verification. Refuse systems that cannot provide the
required executable sealed image. Before each launch revalidate named/held roots
and payload file metadata; any detected change permanently invalidates this owner.
A new owner may inspect a new coherent installation; it cannot adopt another build
while the running application's compiled expectation still names the old one.

Expose a verified borrowed sealed-helper descriptor only to trusted native callers.
It remains valid while the installation owner lives. Add Child::launch_sealed for
this descriptor: validate the required seals and native ELF, retain existing exact
pidfd/reaper ownership, inherited stdio, clean environment and close-from behavior.
Execute the held descriptor without reopening a pathname. A change after validation
can therefore result in the original admitted bytes executing or a refusal, never
execution of substituted disk bytes. The helper still arms exact parent lifetime
and authenticates the existing bootstrap. Keep original path-launch behavior for
its existing independently admitted users; do not silently change their environment.

## Packaging, fixed acceptance and handoff

Freeze this package and helper-identity-cases.json before implementation. Build a
development-only installation probe embedding the generated expectation. The native
oracle places it at bin/syspane alongside the real production configuration helper
and generated record. Label that executable as a test application, not a desktop
edition. Preserve a deterministic local ZIP of these exact bytes and its readme;
extract only its fixed four-file set. Execute the relocated probe from an unrelated
directory with hostile argv[0]/PATH/helper variables and no injected loader path.
This extends the local smoke campaign; it is not a release or a replacement for
the complete native settings/editor frontend.

Verify exact helper hashes, actual /proc child executable identity and kernel seals,
refused post-seal writes, guarded constructor integration with LinuxProfileSupervisor,
default-policy refusal and native child exit. Negative cases cover missing/modified
helper or record, self-consistent forged closure, wrong target, symlink/hardlink,
unsafe modes/ancestors, replaced current executable, replaced files after admission,
changed root, mutable-descriptor launch, wrong-thread use and parent death. After
admission, replace the disk helper and launch the already borrowed sealed descriptor:
only the original production startup diagnostic/exit is permitted, never the test
substitute's deliberately different output. Preserve failed attempts and exact
native metadata. Reuse one owned test image per attempt where practical; retain
the baseline package, mutation definitions, observed hashes and any failing image.

Run native.HELPER-IDENTITY, PROFILE-SUPERVISOR, PROFILE-CONTROLLER and RECOVERY-QUEUE,
the affected portable digest/command tests, and component graphs on all three
profiles. Keep source/artifact/expected-record identities and workspace reservations.
Next wire the verified installation owner and independently scheduled supervisor
into the real frontend with policy-filtered profile projection and native UI.
Protected-policy deployment, complete packaging/lifecycle, non-Linux adapters and
all five release editions remain required.
