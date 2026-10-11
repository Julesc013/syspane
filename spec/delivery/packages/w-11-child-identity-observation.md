---
type: "SysPane Work Package Boundary"
title: "Consistent native child identity observation"
description: "Resample incomplete identity without weakening native acceptance."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-11T19:23:38.227441+00:00"}
sp_id: "SP-W11-CHILD-IDENTITY-OBSERVATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-BACKGROUND-INSPECTOR", "SP-W11-INSPECTOR-ASSETS", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Consistent native child identity observation

W-11 remains in progress. The [preceding checkpoint](../checkpoints/inspector-image-adoption.json)
preserves HELD-CLOSE failure with a verified image executable and empty argv.
A controlled replay of the actual pump reproduces permanently cached incomplete
identity despite subsequent correct argv. Preserve its harness hash and label
it as a model trace, not native execution. The kernel's
[procfs implementation](https://github.com/torvalds/linux/blob/v6.18/fs/proc/base.c)
allows an early empty command-line read; this does not prove the historical failure's
kernel timing. Review the correction as an oracle collection revision.

Product binaries, cases, expected rows, installation/seal checks, exact image
arguments, real SIGSTOP and exit, all 62-second/160-second deadlines, GUI/erasure
limits and wrong-value controls remain. This is not a new runtime/work graph.

## Interface, ownership and limits

The observer samples only children of the current frontend. It owns each pidfd.
One attempt reads complete NUL-terminated argv before and after executable
observation; samples must be identical and nonempty. The exact pidfd must be live
at both boundaries. Admit at most 4096 argv bytes; current helper invocations fit.
There is no internal retry loop, delay or deadline extension.

Empty/truncated/changed argv, disappearance and exit are unqualified. Close that
attempt fd and resample through the existing pump/deadline; never cache incomplete
identity. Keep bounded reason counters, not event queues. Required-child absence
still fails the held case. Accessible sealed helpers retain exact observed SHA-256.
Image helpers require exactly syspane-image-worker, an existing media type and
current frontend PID. Executable PermissionError allows the existing sandboxed
classification only with both identical complete argv and that exact tuple; claim
no directly observed hash. Wrong parent/media/role/count is an error. Exit or an
unrelated executable supplies no qualifying identity. Release every fd on error.

Held tests still verify parent-held seals/hash, literal loading, actual stopped
state and pidfd exit before navigation/close completion. Teardown checks actual
observed-child exit and reports forced cleanup. No privileged action is admitted.

## Sources, executable closure and next step

Tests own tests/configuration/child_identity.py, its portable trace suite, native
sealed-worker probe and integration in native_installed_editor.py. Bind
configuration.CHILD-IDENTITY and Linux native.CHILD-IDENTITY in existing CMake
testing. After workspace preflight and ordinary configure/build, run both through
ctest --preset linux-x64-gcc13, then native.INSTALLED-INSPECTOR-ASSETS.

Literal traces cover empty then complete argv, verified/sandboxed identity,
changed/truncated/oversized argv, disappearance at each read, exit at each boundary,
wrong image tuple and unrelated executable. Replay the actual pump to prove
resampling instead of caching. The native probe seals the existing pinned image
worker, observes live argv, decodes literal fixture pixels and proves actual exit.
It cannot qualify the installed GUI. Preserve the old harness and failed record.

Rerun installed image/topology, inspector, editor, recovery, telemetry, authored,
ordinary/complete-phase tables, phase-refusal and GUI/erasure families affected by
the shared harness. Preserve source/artifact/oracle/environment identity and every
failure; byte/type/inventory/process-verify quiescent archives before cleanup.
Then continue maximum GTK chart/mixed histories, human accessibility and all five
complete native editions and their release evidence.
