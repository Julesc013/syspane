---
type: "SysPane Work Package"
title: "Verified editor helper bundle"
description: "Extend installation-bound sealed execution to the existing image and recovery owners."
tags: ["delivery", "setup", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T22:15:00+00:00"}
sp_id: "SP-W26-EDITOR-HELPERS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W26-HELPER-IDENTITY", "SP-W11-INSTALLED-SETTINGS", "SP-W10-RECOVERY-CONTROLS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Verified editor helper bundle

Extend the existing LinuxInstallation, helper-identity generator, ImageJob and
LinuxRecoveryQueue. Keep the configuration-only record 0.1 and its compiled
expectation/API working unchanged. Its installed settings payload and historical
qualification remain valid. Introduce an explicitly selected bundle record 0.2 for
the future installed editor; do not infer its availability from filenames or silently
reinterpret 0.1. Do not add a second runtime, filesystem admission implementation,
work scheduler or user-selected helper path to installed mode.

## Bundle and ownership

The exact 0.2 top-level members are format=SysPane.Helpers, schema_version=0.2.0,
target_profile=linux-x64-gcc13, product_version=0.0.1 and helpers. helpers has exactly
configuration_host, image_worker and recovery_worker. Each entry has the existing
path, sha256, bytes and imports members. The respective fixed relative paths are:

- libexec/syspane/syspane-configuration-host
- libexec/syspane/syspane-image-worker
- libexec/syspane/syspane-recovery-worker

The record stays at share/syspane/helpers.json, rooted by the actual running
bin/syspane. The compiled bundle expectation contains the record digest and the
three ordered helper digest/size pairs. Neither a mutable manifest nor an external
string chooses a role. Use a native enum with exactly configuration, image and
recovery; invalid roles and missing legacy roles fail. A legacy expectation cannot
admit 0.2 and a bundle expectation cannot admit 0.1. Unknown/omitted/extra fields,
role substitutions and self-consistent forged records fail closed.

Use the existing fixed ELF64/x86-64/interpreter checks and no RPATH/RUNPATH rule.
Configuration and recovery direct imports remain libc.so.6, libgcc_s.so.1,
libm.so.6 and libstdc++.so.6. The image worker's direct imports are libc.so.6,
libgcc_s.so.1, libgdk_pixbuf-2.0.so.0, libglib-2.0.so.0, libgobject-2.0.so.0 and
libstdc++.so.6. The existing pinned image runtime owns its transitive libraries,
loader modules and containment dependencies; this bundle does not make them portable
or qualify a new OS floor. Preserve exact canonical 0.1 generator bytes when called
without the two additional helper inputs. Supplying only one extra helper is invalid.

One serialized native owner admits the entire bundle before exposing any image.
Reuse the existing held no-follow ancestor/file identities, ownership, filesystem,
execution-permission and compiled-digest checks. Each helper is at most 64 MiB;
retain at most three sealed images (192 MiB total) and one 64 MiB transient input
buffer while sealing them in sequence. The record remains at most 65536 bytes.
No GUI callback may construct or revalidate this owner. Keep its existing strict
thread affinity and permanent invalidation after detected installation change.

Every verified-helper request revalidates all current bundle path bindings and
file metadata, including executable permission for all three roles. No admitted
image is reopened by pathname for execution. Previously borrowed sealed bytes may
execute their original content if disk changes after validation; substituted bytes
must never execute. Existing acquisition, same-uid race and dynamic-library limits
remain; the compiled expectation is anchored in an already acquired application.

## Existing image and recovery owners

Add explicit overloads consuming a non-null shared LinuxInstallation owner. ImageJob
requests only the image role; LinuxRecoveryQueue requests only recovery. The configuration
supervisor's existing accessor selects configuration. Retain the installation owner
through use and launch via the existing Child::launch_sealed, including its clean
environment, exact pidfd/reaper ownership, inherited descriptors and parent lifetime.

Do not provide a pathname fallback after verification fails. Image constructor
failure launches no child. Recovery launch failure reports the existing unavailable
queue outcome without claiming successful storage. Revalidate for every recovery
operation, not just the first load. Keep all image decoding/containment/output bounds,
recovery guards/deadlines, cancellation and reaping behavior unchanged. In verified
mode, construct and poll these owners on the installation's serialized native worker;
the existing UI-oriented path experiment remains distinct. Installed UI composition
must later enqueue work and receive results without performing this filesystem work
on GTK. This package does not itself enable editor UI or recovery retention authority.

## Fixed verification and continuation

Freeze this package, editor-helper-bundle-cases.json and the referenced literal image
and recovery fixtures before implementation. Build a dedicated native test consumer
with the generated bundle expectation, using the actual existing three production
helpers. Its relocated five-file payload is an explicit development experiment,
not a complete desktop edition. Preserve exact package bytes and source/toolchain IDs.

Independently verify record/import/hash identities, each sealed descriptor and refused
writes. Exercise real image decoding against literal PNG/JPEG/SVG expected results,
invalid input and sandbox checks. Exercise recovery load/replace/reload/retire against
exact files and expected digests, including cancellation. Observe actual child images
through /proc and hold independent pidfds until exit. No controller self-report alone
proves identity, child death or disk contents.

Cover each missing, modified, swapped, linked and unsafe-mode role; altered manifest,
wrong version and forged hashes; invalid role, legacy role refusal and wrong-thread
access; mutation of one role invalidating another; attempted image/recovery launch
after change; immutable borrowed image after substitution; and verified-helper parent
loss. Calibrate a deliberately wrong pixel/file oracle. Preserve original failures.
Use one owned reusable payload with archived baseline bytes and exact mutation/node
snapshots, never unbounded payload copies. Bound each case to twenty seconds and
the whole native family to three minutes.

Run existing helper identity, image job, recovery queue and installed settings
regressions and all three component graphs. Advance the real editor only after this
verified launch boundary passes. Native worker/UI bridging, policy-bound recovery
directory/session selection, inspector/editor integration, telemetry, desktop
activation/escape, full lifecycle and all five complete release editions remain required.
