---
type: "SysPane Handoff"
title: "Native history worker handoff"
description: "Bounded native history computation is verified; current-form integration remains next."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T08:31:00.479108+00:00"}
sp_id: "SP-HISTORY-WORKER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-HISTORY-WORKER", "SP-HISTORY-PREPARATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native history worker handoff

EditorHelperClient now exposes history_preparations(): GUI-owned bounded task
handles for the existing native worker. The [package](packages/w-11-history-worker.md)
defines admission, states, cancellation and coexistence. The
[checkpoint](checkpoints/history-worker.json) binds executions to source archives,
artifact digests, independent native observations and preserved failures.

One history slot and one recovery-preparation slot coexist. Each poll services
existing native I/O and runs at most the oldest eligible pure computation. Work
runs outside the channel mutex. A successful result transfers once; current-draft
adoption and current authority checks remain mandatory. The bridge creates no
thread, timer, child process or additional work queue.

Queued cancellation erases input immediately. Running cancellation withdraws
delivery while retaining the reservation until computation and input destruction
finish. Releasing a running handle cannot admit replacement work prematurely.
Completed handles reserve capacity until release. Channel close and native-owner
destruction cancel both preparation types and acknowledge orderly closure.

## Executed verification

All 13 fixed native history cases pass through the relocated verified helper probe.
They include exact Undo/Redo scenes and selection, held progress, consumed/null
inputs, capacity, one-shot take, owner checks, stale adoption, queued/completed/
running cancellation and release, worker/channel close and both orders of recovery
coexistence. Three witnesses observed a running computation and stopped that worker
in the kernel before cancellation, release or close. No product test hook or delay
was added. All 21 probe processes exited normally. The maximum observed task call
was 1479 microseconds against the unchanged 100-ms bound.
This establishes task-interface behavior, not complete GUI responsiveness.

The 8 native families pass 111 named cases, including original helper-worker,
recovery preparation/admission, frontend recovery, installed recovery/editor and
standalone recovery controls. All nine unchanged portable history checks and both
component checks pass on each of the Linux GCC, Windows GCC and v141_xp development
profiles: 27 portable history checks and six component checks. Native changes were
rebuilt on Linux; the unchanged portable binaries were rerun on all profiles.
Profile revisions are Linux 66, Windows GCC 38 and v141_xp 29. This does not qualify
historical guests, complete platform editions or deployment.

Two initial native failures are retained. The large fixture first exceeded the
128-edit batch limit, then the authored scene byte limit. Its builder now uses
valid batches and 256 widgets with bounded bodies. The fixed case outcomes and
timing limits did not change. Before native execution, one invented recovery error
spelling in the oracle was corrected to the existing recovery.prepared_stale code;
the original file, source comparison and review remain preserved. A local runner
also stopped before testing when a copied executable name did not exist. Its
record remains alongside the corrected successful execution.

Completed native attempts were archived, verified against complete byte inventories
and removed only from their owned duplicate output directories. The 8-GiB active
workspace allowance and action reservations are unchanged; retained local archives
are reported separately. No generated recordings or machine bindings are tracked.

## Next current-form boundary

The installed editor still uses synchronous Undo/Redo. Connect the new factory to
EditorForm through its existing worker and poll timer only after freezing native
form cases. A history request invalidates old recovery proofs: cancel/suspend that
capture while history is pending, then resume from the final authoritative draft.
Do not consume obsolete capture as a new recovery failure or preserve old permission.

Disable conflicting edits and Apply while a task is pending. Reload, policy/session
withdrawal, topology replacement and close must cancel it; retain the handle until
stopped and never apply a late result to a replaced form. On success, adopt against
the exact current draft and rebuild the native preview with current topology,
telemetry and policy. A prepared authored scene does not prove a native frame.

Test held progress, refused conflicting input, exact Undo/Redo, failed preparation,
capture coexistence and cancellation/replacement before and after completion. Then
rerun the unchanged ordinary GUI timing and erasure gates before enabling this path
in production. The initial-preview checkpoint's four delay failures remain prior
evidence; this checkpoint runs no new GUI-limit qualification. Production recovery
stays disabled. General asynchronous authoring, native inspector, telemetry/desktop
integration, lifecycle, other adapters and all five full 0.1.0 editions remain open.
W-11 remains in progress.
