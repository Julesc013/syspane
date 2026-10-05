---
type: "SysPane Work Record"
title: "Explicit private preservation checkpoint"
description: "Bind opaque configuration copies, native controls and interrupted publication to measured development evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:35:07+11:00"}
sp_id: "SP-PRESERVATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-PRESERVATION", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Explicit private preservation checkpoint

From base `ee2ac9617ded2959efc9bf0499b72ccd8be1e6ee`, W-25 adds an explicit private
copy operation to the independent diagnostic entry. The [package](packages/w-25-preservation.md)
owns its exact behavior. W-25 and the campaign remain in progress.

## Implemented behavior

The operator selects absolute source/destination paths in native Win32/GTK text
controls or supplies `--preserve <source> <destination>`. The adapter never parses,
repairs, activates or restores the file. It accepts at most 8 MiB from a same-user,
single-link regular file without other non-administrative writers. Selected parent
directories are trusted; arbitrary hostile same-user replacement is not qualified.

A current available policy must permit preservation and the relevant acknowledgement
or native path-display channels. Revision, capability and disclosure are rechecked
through the operation. Destination/staging creation is exclusive. Transfer chunks
are at most 64 KiB; the adapter requests a file flush, verifies staged bytes, rereads
the held original and publishes with no-replace rename. Copies have owner-private
permissions. Existing names survive. Failed/interrupted attempts retain their own
private partial rather than deleting data. No directory flush/power-loss guarantee
is claimed; the fixed acknowledgement always reports `durable:false`.

The native inspector admits one worker, disables path editing during a copy and
keeps Cancel/Close usable. Revocation clears selected paths and replaces status.
Close cancels without joining blocked I/O; the entry's process lifetime bounds the
worker. Tests deliberately block only their typed policy fixture to demonstrate
that native Close still exits. There is no product policy override.

## Verification and failures

Windows development revision 9 passes 59 CTest entries; Linux revision 10 passes 60.
The native preservation family executes 17 Windows and 18 Linux cases, including
opaque binary/empty/Unicode copies, exact destination names, private permissions,
size boundaries, existing/racing names, source changes/sharing, links, cancellation,
external termination and four native control scenarios. Windows symlink creation
is unavailable under this account, so that additional leaf-link case remains
unexecuted. Foreign-owner and unsupported-filesystem execution need separate labs.

Native UI cases activate the actual compiled controls programmatically with a
typed positive-policy reader. They prove copy binding, busy admission, cancellation,
revocation clearing and Close during blocked work. They do not qualify external
keyboard/pointer input, accessibility or installed protected policy. The actual CLI
was exercised under unavailable mandatory policy and denied without creating copy
or partial files. Existing hidden native Close and all prior regressions still pass.

Historical-toolset revision 3 passes 55 host checks, unchanged PE/import closure and
relocated model smoke. Only the portable policy predicate is added to that profile;
native preservation remains excluded and XP/7 guest runtime remains unexecuted.

Preserved failures include a Linux fixture's missing aggregate initializer, the
Windows source adapter rejecting the verified owner's OWNER RIGHTS ACE, and a
Windows rename buffer without a terminating wide NUL. The collision oracle caught
the last defect because the copy received an unintended suffix. The racing file
was retained. The buffer now includes its terminator, and exact-name checks cover
eight different lengths. Expectations, no-overwrite rules and compiler warnings
were not weakened. Original native reports and source-bound build/test attempts
remain distinct from the final passing checkpoint.

Records are `build-support/evidence/w-25-preservation-<profile>.json` and adjacent
native reports/CTest logs. `w-25-preservation-attempts.json` binds preserved attempts
and failures. `w-25-preservation-verification.json` records spec/tool/integrity checks;
`preservation-handoff.json` is the machine-readable handoff. Ignored source archives
and synthetic fixtures remain under the campaign's bounded owned output roots.

## Next work

Close product failure-log ownership/retention and full-snapshot/data recovery before
enabling them. Connect actual telemetry/renderer recovery, policy-driven payload
removal and independent editor exit. Qualify positive protected-policy deployment
and the outstanding preservation environments separately. Continue independently
available host tracks; the Linux desktop composition failure and Windows/macOS
capture gates remain open. Existing guest VMs have not been started or changed
while their test scope is pending. No public release or privileged action occurred.
