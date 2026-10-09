---
type: "SysPane Handoff"
title: "Native request preparation handoff"
description: "One finite request slot on the existing worker, with owner-only adoption and form integration still required."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T12:01:53.593797+00:00"}
sp_id: "SP-REQUEST-WORKER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-REQUEST-WORKER", "SP-REQUEST-PREPARATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native request preparation handoff

The [request worker package](packages/w-11-request-worker.md) now has an
implementation in the existing Linux helper owner. One independent request slot
shares the checked admission sequence with history and recovery preparation. Each
poll services existing native I/O and then executes the oldest eligible pure work.
Computation and running-input destruction happen outside the channel mutex.

RequestPreparationTask provides GUI-owned status, cancellation and one-shot result
transfer. A completed handle retains its reservation until released. Running
cancellation immediately prevents delivery, but stopped acknowledges completion
and input destruction; dropping a running handle cannot prematurely free its slot.
Channel closure includes request work in its drain condition. The frontend backend
exposes the factory for the next form integration. No new thread or timer exists.

The worker cannot submit a request or allocate a live ticket. Its opaque result
still requires unchanged-origin adoption under current policy. A taken result is
owned by the caller; cancelling the former task does not revoke that result. The
form must invalidate the originating proof when its context changes.

## Evidence

The [checkpoint](checkpoints/request-worker.json) records exact source archives,
artifact identities, commands and fixed expectations. Build commands succeed for
Linux GCC revision 73, Windows GCC 42 and v141_xp 33. All 19 selected portable
request/history/component checks pass on each profile, as do the two historical
artifact checks. These are development-host results, not historical OS qualification.

All 14 fixed native request cases pass in 28 probe runs. They verify exact commit
and preview commands, request/epoch/ticket identity, unchanged originating state,
capacity, null/consumed input, owner refusal, cancellation/drop/close, stale policy,
and all six admission orders across the three computation types. Three running
cases observe the worker stopped by the kernel before cancellation, drop or close.
Every probe exits cleanly and no child helper is launched for pure computation.
The oracle rejects an intentionally wrong expected revision.

All seven native families pass 97 cases: request worker, history worker, recovery
preparation, helper worker, recovery admission, installed recovery and installed
editor. Complete recordings were archived, byte-verified and pruned after process
exit, preserving 1001133346 raw bytes without enlarging the active workspace budget.

Specification validation passes with 51 schemas and 183 fixtures. Its tooling
suite reports 62 tests: 60 passed and two existing Windows symlink-privilege skips.
Generated projections and the integrity inventory are checked separately from
native product evidence.

Observed maximum request-interface durations are 778 us for capture, 90 us for
task creation, 37 us for status, 19 us for take, 75 us for adoption, 742 us for
destruction and 75 us for cancellation. These individual probe observations are
below the fixed 100-ms task bound. They are not installed GUI qualification or a
performance distribution.

The first Linux build failed because the frontend factory declaration omitted the
new task header. That failed source/archive/log remains preserved. Adding the
include repaired the build without changing the frozen contract or expectations.
Shared build files remain in source/build; raw attempts and byte-verified native
archives remain local ignored out/ content.

## Next boundary

Installed Apply still uses synchronous begin. Connect the request factory to the
form's existing timer, disable conflicting authoring while preparing, and retain
navigation/close cancellation and current-policy erasure. Only the live GUI may
adopt and submit the exact prepared request once. Preparation cancellation has no
durable outcome and must not be reported as an unknown storage transaction.

The current recovery session refuses submitting while capture is paused. Resolve
that interaction explicitly: retain an exact current-draft recovery digest without
resuming capture in a way that invalidates pending request work. Clear pre-submit
state on cancellation and preserve unknown-outcome reconciliation after actual
submission. Recheck policy, topology, reload, disconnect and closed-form ownership
before consuming a late result. Observe ready/recovery/adoption/backend callback
costs, then execute held form cases and the original seven GUI timing/erasure cases.

The prior ordinary MAX-RECORD delay failure remains failed. Production recovery
and history admission stay disabled. W-11 and the complete Windows 9x, Windows NT,
Linux X11, Wayland and Mac OS X release editions remain unfinished.
