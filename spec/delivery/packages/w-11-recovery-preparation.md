---
type: "SysPane Work Package"
title: "Asynchronous editor recovery preparation"
description: "Move recovery reconstruction to the existing worker without granting stale prepared results authority."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T01:30:00+00:00"}
sp_id: "SP-W11-RECOVERY-PREPARATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-ADMISSION", "SP-W11-EDITOR-HELPER-WORKER", "SP-W10-RECOVERY-DRAFT", "SP-W10-RECOVERY-CONTROLS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Asynchronous editor recovery preparation

Move expensive capture/reconstruction off the GUI through the existing editor
helper worker. Keep the original literal recovery bytes, complete semantic/resource
validation, generation checks, single history and normal Apply transaction. Existing
synchronous APIs remain available for explicit non-GUI consumers and legacy tests.

## Portable work and prepared results

EditorDraft creates a bounded, detached work input containing only its current/base
authored documents, immutable shared resources/catalog, policy/authority, capabilities,
epoch and trusted recovery identity. Do not copy selection, undo/redo, clipboard,
private input, request history or native authority. Capture and restoration preparation
run the existing full checks on this detached value without touching the live draft.
The work input owns its state; it cannot borrow a destroyed or changing GUI object.

A prepared result is opaque and move-only. Only the recovery preparation engine
can construct it. Bind it to a unique live-draft validity token and the exact trusted
profile/generation. Changing authored state, policy, connection, baseline, request
state or lifetime invalidates existing work/results, including no-op or rejected
mutation attempts. Selection alone may change; a restore records its current value
for Undo. An invalidated token never becomes current again. Copies of a draft cannot
gain another draft's prepared result.

Consumption rechecks current recovery permission, editable/pristine state as relevant,
identity and token. It may reuse the opaque proof that those exact immutable inputs
passed semantic validation. This refines the repeated-check rule in SP-W10-RECOVERY-DRAFT:
no parsed bytes, caller-supplied candidate or stale inspection is a proof. Restore
adopts the prepared candidate through the existing bounded history path without
repeating semantic/resource reconstruction on GTK. Preserve no-op behavior, one Undo
step, exact resources and current selection restoration. Capture returns the original
canonical bytes or clean no-record result; consumption never commits or writes files.

Recovery availability and consumption use bounded policy/capability checks against
already validated authored state. Structural validation still runs at ordinary
authoring/reload boundaries and on the preparation worker. Do not weaken command,
scene, resource, font, metadata or policy checks to meet a timing target.

## Worker and session ownership

Add one retained preparation task slot to the existing editor helper channel.
Factories and task handles perform bounded memory/state work on the GUI. The same
serialized native worker acquires an input, runs it outside the shared mutex, then
publishes only if cancellation/closure has not won the channel lock. It creates no
thread pool, additional native worker, second history or request scheduler. Releasing
an active handle reserves its slot until the worker acknowledges completion.

Cancel/close synchronously remove queued inputs and deliverable results. An acquired
pure computation may finish before cancellation is observed, but its result must be
discarded and its buffers released before closure is acknowledged. Native helper and
supervisor scheduling during this bounded computation still require installed-loop
qualification; this package does not claim whole-frontend responsiveness.

The asynchronous EditorRecoverySession keeps at most one active preparation and one
latest pending input. Replacing pending capture cancels obsolete work and suppresses
its result. Count prepared offers within the existing single offer and bounded scene
state; share immutable package/media allocations. No unbounded result queue exists.
All existing byte limits remain: 786432-byte record, 327680-byte command and bounded
authored scenes/resources. These object-count/serialized limits are not RSS claims.

Keep editing blocked during initial recovery inspection. A valid prepared result
offers Restore; malformed/stale input offers Discard and Keep without leaking raw
untrusted text. Restore consumes the exact prepared result. Capture remains pending
through preparation and durable storage completion; Apply waits for that final fact.
Keep, discard, cancellation, policy/connection loss, reload and close drop prepared
results and stop old work. Late results cannot resurrect offers or captured records.
Preserve matching retirement, unknown-result reconciliation and unchanged storage
guards. No installed recovery enablement occurs before its live session composition,
exact applied-draft retirement and complete scheduling/latency qualification.

## Fixed verification

Freeze this package and case list before implementation. Reuse original literal
record, scene and font fixtures. Compare synchronous and prepared results to those
independent expectations, not merely to each other. Cover exact capture/clean result,
inspect/restore/Undo/Redo, no-op, font resources, malformed input, policy and every
draft invalidation boundary, cross-draft rejection and wrong identity. Preparation
must not mutate its origin; a destroyed origin cannot be revived.

On the native helper consumer, hold worker pumping while GUI methods continue; then
verify exact offer, restored scene, capture bytes, coalescing, cancellation and late
result erasure with actual helper exit. Measure GUI preparation/task/consumption
operations under the existing 100 ms development task bound, keeping full consumer
and worker timings separate. A wrong expected record/scene must fail. New native
cases have 30-second limits and a 300-second family limit. Preserve all older failures,
fixed oracles and product/workspace limits. Run affected portable tests on all three
profiles, native consumer/storage/helper regressions and all component graphs.
