---
type: "SysPane Work Record"
title: "Independent recent-failure metadata checkpoint"
description: "Bind bounded native fault records, private file handling and policy-gated diagnostic projection to current evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:55:00+11:00"}
sp_id: "SP-FAILURE-METADATA-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-FAILURE-METADATA", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent recent-failure metadata checkpoint

From base `a67d5a4c1bd73031afa8df5c68233a46c811d827`, W-25 now records bounded
advisory failure metadata and reads it through the independent diagnostic entry.
The [boundary](packages/w-25-failure-metadata.md) owns exact fields, interrupted
input, private-file access, disclosure and acceptance. The campaign and W-25
remain in progress.

## Implemented behavior

The same portable codec runs on all three build profiles. It accepts only sixteen
fixed-shape records within 8 KiB, requires consecutive sequence numbers and
nondecreasing elapsed time, and rejects arbitrary fields/text. Truncation at every
byte of a two-record fixture preserves only completed lines; malformed completed
input invalidates the entire projection. Recorded stop facts never become live
health or permission to control a process.

The modern native adapter exclusively creates private files, retains one handle,
requests flushes and latches recording failures without replacing existing files.
It validates same-user ownership, file type, link count, permission and bounded
read consistency. Windows uses native Unicode arguments and file APIs; Linux uses
no-follow/nonblocking file access. Parent directories remain caller-selected;
hostile same-user replacement and power-loss durability are not qualified.

The actual recovery probe's nine existing owned-process scenarios now produce
journals whose count/reason/role/stop facts match their process observations. The
original timing, quarantine, restart and independent child-exit criteria still pass.
Optional journal writes follow confirmed failed-child cleanup and retain the
original fault snapshot. Journal failure cannot grant a restart or suppress a guard decision.

`--report --failures <absolute-path>` and the native inspector equivalent select a
file explicitly. Existing default behavior remains independent of optional input.
Failure details require current operational permission for the relevant export or
inspector/accessibility channels. Denial replaces previous details and prevents
reader invocation. Native tests observed unavailable-policy reporting and hidden
Close; typed read-spy fixtures prove permitted projection and revocation. No installed
protected policy was changed, so positive native policy deployment stays unqualified.

## Verification and preserved failures

Windows profile revision 8 passes 57 CTest entries; Linux revision 9 passes 58.
Historical profile revision 2 passes 54 host entries, including the unchanged PE/
import closure and the three new portable metadata cases. Its native file adapter
is disabled; XP/7 guest runtime remains unexecuted. The relocated historical model
smoke still uses its original literal oracle; it is not a diagnostic product package.

Each modern native file family executes ten cases: Unicode round-trip, exclusive
creation, capacity, regression/failure latch, reading beside an open writer,
interrupted/invalid input, oversize, hard links, path/type rejection and platform
permission checks. Linux also exercises symlink/FIFO rejection. Windows broadens
only an owned fixture's DACL to verify rejection; symlink creation fails for lack
of privilege and that reparse case remains explicitly unexecuted.

The first Windows build failed on a duplicate `NOMINMAX` definition under warnings
as errors. An include guard corrected it without relaxing flags. The first Windows
diagnostic run failed in the Python harness while printing a Unicode path under
the console encoding; ASCII-escaped invocation logging corrected that observer
failure. Both original failures, their commands/source snapshots and later complete
runs are retained. No acceptance oracle changed to turn either failure into a pass.

Records use `out/evidence/w-25-failure-<profile>.json`, with adjacent
native reports/CTest logs. `w-25-failure-attempts.json` retains build/test attempts;
source archives remain in the bounded owned campaign cache. The original failed
diagnostic report is stored separately. `w-25-failure-verification.json` records
specification generation, schema/tool checks and integrity. The machine handoff is
`out/evidence/failure-metadata-handoff.json`.

## Remaining work

Close and implement explicit configuration preservation, including native user
selection, unchanged source bytes, permissions, interruption, current policy and
no-overwrite behavior. Connect real telemetry/full-snapshot and renderer recovery,
policy-driven payload removal and independent editor exit before completing W-25.
This optional probe journal is not a product data-root/retention design.

Continue independent host tracks. Existing guest VMs still await scope/usability
clarification; no guest was started or changed. No Windows or historical desktop
profile became qualified, and the Linux composition failure remains open.
