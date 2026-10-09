---
type: "SysPane Handoff"
title: "Detached editor request preparation handoff"
description: "Portable full command preparation and exact owner adoption, with native integration still required."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T11:37:14+00:00"}
sp_id: "SP-REQUEST-PREPARATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-REQUEST-PREPARATION", "SP-EDITOR-CALLBACK-TRACE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Detached editor request preparation handoff

The portable EditorDraft request boundary now separates full command preparation
from current-owner adoption. The [package](packages/w-11-request-preparation.md)
defines exact inputs, invalidation, resource limits and the remaining native gate.
The [checkpoint](checkpoints/request-preparation.json) records source archives,
artifact identities, fixed expectations and executed checks.

RequestWork captures a bounded detached settings base/draft and immutable resource
context. It executes ordinary begin validation and exact command serialization on
the test worker thread. Its local ticket is discarded. The opaque result carries
the command, serialized bytes and weak originating identity; it cannot publish or
authorize a request. Adoption requires the unchanged originating owner, epoch and
revision, rechecks current command/resource authority, and only then allocates the
next live ticket and installs the ordinary pending request. Throwing copies precede
publication; the final state transition uses moves, swaps and bounded cleanup.

Scene, selection, history and revision are unchanged by preparation/adoption. A
successful adoption clears clipboard state as synchronous begin does. Invalidating
operations, including failed edits and selection attempts, fence stale results.
Copy/move/assignment and destroyed or different origins cannot receive the proof.
Preview, cancellation, unknown outcomes, exact request identity and existing result
reconciliation retain the ordinary transaction path. No GTK object, live draft
pointer, history stack or pre-existing transaction result enters the worker input.

## Evidence and scope

The five common reference cases first passed through synchronous begin before
implementation. The unchanged test source then passed eight prepared cases, adding
invalidation, identity and one-shot guards. Literal expected commands, theme pins,
scenes, ticket/revision values and actual transaction writes are checked; agreement
between two implementations alone is not the oracle. Detached execution uses a
joined test thread and proves that the origin remains unchanged before adoption.

All three profiles were fully rebuilt: Linux GCC revision 72, Windows GCC 41 and
v141_xp 32. Each passed all 342 selected portable editor/settings/configuration/
scene/protocol/component checks. The two existing historical artifact checks pass.
These are development-host results, not historical OS or full edition qualification.

Six existing native families pass all 88 recorded cases: history worker/form,
recovery preparation, editor helper worker, installed recovery and installed editor.
These regressions exercise the rebuilt consumers; they do not exercise a native
RequestWork integration, which is still pending. All 24 build/test attempts in this
checkpoint exited successfully. Earlier failures in the preceding checkpoints
remain preserved and are not superseded by these component/regression results.

Specification validation passes with 51 schemas and 183 fixtures. The tooling
suite reports 62 tests: 60 passed and two Windows symlink-privilege skips. Generated
projections and the integrity seal are verified separately from product checks.

Complete native attempts were archived, byte-verified and pruned only after exit.
Two old diagnostic input directories and their copied executables were separately
preserved and verified, freeing 13953112 active bytes without discarding their data
or inferring an execution outcome. Shared build tooling remains under source/build;
raw evidence and machine bindings remain ignored out/ content.

The maximum-scene case contains 256 widgets and exactly 262144 serialized scene
bytes. The original synchronous Linux begin measurement was 102560 us. The final
prepared-path measurements were:

| Development profile | Capture (us) | Worker plus join (us) | Adoption (us) |
|---|---:|---:|---:|
| Linux GCC | 1460 | 117999 | 966 |
| Windows GCC | 1645 | 168103 | 734 |
| Windows v141_xp | 1050 | 32430 | 342 |

These are individual component observations. Worker duration includes thread
creation/join overhead and a second strict parse of the resulting wire command.
They do not establish a latency distribution, GUI responsiveness or equivalence of
timers across hosts. The earlier callback-trace CPU/wall discrepancy remains open.

## Native continuation

The installed form still calls synchronous begin. This checkpoint does not connect
RequestWork to a native task slot or claim the 90 ms Apply callback is repaired.
Close and implement one finite request-preparation slot on the existing editor
worker, ordered with recovery/history work. Verify held-work progress, cancellation
before/after computation, owner-only result transfer, exact stopped acknowledgement,
and shutdown while work is running. Then connect the form's pending/cancel/current-
policy state without adding another thread or timer. Preserve the current recovery
digest and distinguish preparation cancellation from unknown durable outcomes.

Isolate ready/recovery/command/backend costs in that integration and retain the
other measured restore/form-timer/paint work. Only then rerun the unchanged ordinary
seven-case GUI timing/erasure qualification. The prior MAX-RECORD delay failure
remains failed; production recovery/history admission stays disabled. W-11 and all
five full SysPane 0.1.0 release editions remain unfinished.
