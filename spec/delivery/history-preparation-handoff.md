---
type: "SysPane Handoff"
title: "Prepared history transition handoff"
description: "Detached undo/redo validation and current-owner adoption are implemented; native scheduling remains next."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T07:57:06.259246+00:00"}
sp_id: "SP-HISTORY-PREPARATION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-HISTORY-PREPARATION", "SP-INITIAL-PREVIEW-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared history transition handoff

EditorDraft now supplies detached, one-shot undo/redo validation and opaque
current-owner adoption. The [package](packages/w-11-history-preparation.md) defines
the boundary. The [checkpoint](checkpoints/history-preparation.json) identifies
executed source, artifacts, commands, native archives and preserved failures.

history_work(false) selects Undo; true selects Redo. Empty history returns no work.
The work owns the selected target and detached settings context, sharing immutable
resources. It contains no live draft pointer, history stacks, clipboard, request
tickets or result payload. run() performs the existing full scene/resource checks
and primes only structural submit hints. Failed and successful work are one-shot.

adopt_history() accepts only its exact unchanged origin and rechecks current preview
and resource authority. It restores the target selection and transfers one entry
between the existing stacks, preserving request numbering, resources and history
accounting. Ordinary begin still fully validates commands and resources. Every
mutation attempt fences prior work; selection fences history without invalidating
recovery proofs. Copy/assignment/move, policy regrant and origin destruction cannot
transfer or revive a preparation identity.

## Executed verification

Five independent synchronous trace families passed before product changes: exact
scenes/selections, versioned themes, the 64-entry boundary, a valid local scene too
large for the legacy command envelope, and preview/commit request continuity.
Those expectations then passed through prepared transitions on all three profiles.
Preparation runs on a separate joined test thread and must leave its origin unchanged.

Nine prepared families include 36 invalidation combinations, identity/lifetime,
policy and supplemental failed/replayed-work guards. The guards were added only to
the prepared compilation branch; the synchronous test source with prepared branches excluded is
byte-identical to the successful baseline, preserving all five observable traces. No expectation was
derived from the prepared implementation's output.

All 332 selected portable checks pass on each profile: 996 total. Both legacy PE
checks pass. Native regressions pass 113 named cases in the checkpoint's
10 families, plus SCENE-IMAGE. They cover existing prepared-editor/reply
lifecycle, initial input, recovery preparation/controls, installed recovery/editor
and standalone editor/image erasure. The profile revisions are Linux 65, Windows
GCC 38 and Windows v141_xp 29. Host execution and import checks are not historical
guest or complete desktop qualification.

Two baseline failures remain preserved: warning-as-error formatting stopped the
first test build, then an invalid oversized single-widget text input was rejected by
the unchanged authored schema. The corrected baseline uses 70 individually valid
widgets to exceed the old wire envelope. Both corrections preceded product changes;
the successful baseline and every subsequent attempt retain source hashes.

The workspace allowance remains 8 GiB. After the completed Windows GCC build/tests,
12 reconstructible compiler object files were removed from their verified owned
build directory, freeing 178947572 bytes. The tested executable digest stayed exact.
Raw observations and cleanup records remain in ignored out/; no retired root or
generated archive is tracked.

Specification generation and validation pass for 673 inventory files,
51 schemas and 183 fixtures. Integrity sealing covers 672 files.
These checks do not qualify native behavior or complete a release.

## Native integration still required

The installed frontend still calls synchronous undo/redo. This portable checkpoint
does not claim improved GTK timings, whole-package completion or production recovery
enablement. The four GUI delay failures remain prior evidence in the initial-preview
checkpoint; no new GUI-limit run is claimed here.

Next close a bounded history-task slot on the existing editor worker, including
coexistence with recovery preparation, cancellation and acknowledged closure. Connect
current-form adoption, conflicting-action refusal and native preview rebuilding;
test held worker progress, stale completion, reload/topology/policy/close and exact
undo/redo before enabling that path. Then rerun the original ordinary GUI limits.
General asynchronous authoring and native preview handoff remain required, as do the
native inspector, telemetry/desktop integration and all five full 0.1.0 editions.
W-11 stays in progress and production recovery remains disabled.
