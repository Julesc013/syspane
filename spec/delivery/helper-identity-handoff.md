---
type: "SysPane Handoff"
title: "Verified installation-relative helper execution"
description: "Compiled helper closure, immutable native execution and relocated development-package evidence."
tags: ["delivery", "setup", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T19:54:49+00:00"}
sp_id: "SP-HELPER-IDENTITY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W26-HELPER-IDENTITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Verified installation-relative helper execution

LinuxInstallation now discovers the payload prefix from the running kernel
executable identity and verifies its fixed bin/libexec/share layout. Its expectation
is compiled into the consumer from the built configuration helper, including exact
helper and closure-record digests. A forged record cannot approve another helper.
No cwd, argv[0], environment-selected helper or preference supplies that identity.

The native owner walks held no-follow directories, checks native ownership,
permissions, filesystem and current executable identity, and verifies stable file
metadata around exact hashing. Kernel executable-access checks cover the calling
user's effective permission. The verified image is copied into a sealed executable
memfd. Child::launch_sealed executes that descriptor with the existing clean
environment, descriptor closure and exact pidfd ownership; it never reopens the
helper pathname. Detected installation changes invalidate the owner permanently.

LinuxProfileSupervisor accepts this installation owner and revalidates it before
each launch. Already borrowed immutable bytes remain unchanged if a disk path is
substituted after verification. Existing native path callers retain their separately
admitted behavior. A dedicated 64 MiB payload digest uses the existing SHA-256
algorithm; document/content ceilings remain 1 MiB/16 MiB.

## Evidence and preserved failure

Twenty-one fixed helper-identity cases pass in the admitted non-root Linux/ext4
laboratory. The independent oracle creates and relocates a deterministic four-file
development ZIP containing the real configuration helper, compiled-expectation test
application, closure record and explicit development readme. The test application's
bin/syspane name exercises the intended layout; it is not the product frontend.

Python observes actual child executable bytes through /proc and native pidfds,
checks seals and failed writes, and verifies the production startup diagnostic and
exit. It covers hostile cwd/argv/PATH, manifest and payload forgery, wrong target,
links, unsafe modes and effective execution permission, current-executable/root/
file replacement, latched invalidation, wrong-thread use, mutable-descriptor refusal,
supervisor integration and parent death. Replacing the disk helper with a distinct
test executable still runs the original sealed production bytes. The substitute's
deliberately different diagnostic and exit are never accepted.

The first run failed because the generator added a trailing newline that the
existing strict parser rejects. The generator now emits canonical record bytes
without that newline; the parser and frozen acceptance definitions were unchanged.
That failed run and its exact original package remain preserved. Native input-image
inventories retain file identities, modes and hashes before each mutation/control
step. Baseline bytes live in the package; unique modified bytes have compressed
blobs, so restoring the reusable test image does not erase failed or rejected inputs.

PROFILE-SUPERVISOR, PROFILE-CONTROLLER and RECOVERY-QUEUE regressions also pass:
88 distinct cases across four native families. All three development profiles
configure/build, run 14 affected shared digest/command/reconciliation cases and
pass both component graph checks. The [checkpoint](checkpoints/helper-identity.json)
binds exact source, helper/probe/header/record artifacts, successful and failed
executions, archives and specification checks. Generated data and raw evidence
remain in ignored owned output roots; no archive was pruned.

## Next admitted boundary

W-26 and W-08 remain in progress. Wire the generated helper expectation,
LinuxInstallation and the independently scheduled supervisor into the real native
controller/inspector. Close its deployment/data/runtime ownership admission and
policy-filtered profile/resource projection, then connect native settings/editor,
telemetry, activation, recovery context, imports and package/lifecycle operations.

This helper identity is rooted in the already executing application. It does not
authenticate the application's original acquisition or replace release signatures,
complete dependency/notices closure or a native package manager's ownership. The
current verified loader closure uses only the named Linux OS libraries; private
origin-relative dependencies need another admitted closure. Tmpfs acceptance is
implemented but the payload-tree evidence here is ext4. Protected-policy deployment
remains unqualified: the production helper refuses unavailable policy. Windows
shared checks do not implement this adapter or qualify historical platforms. All
five complete desktop editions and the original release gates remain required.
