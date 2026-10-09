---
type: "SysPane Work Package"
title: "Detached editor request preparation"
description: "Move full Apply command preparation off the GUI while retaining exact current-owner publication."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T11:25:16.359970+00:00"}
sp_id: "SP-W11-REQUEST-PREPARATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-EDITOR-CALLBACK-TRACE", "SP-W11-HISTORY-PREPARATION", "SP-W11-RECOVERY-SUBMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Detached editor request preparation

The callback trace measures MAX-RECORD Apply at 90.0531 ms. Source inspection locates
command construction, full authored/theme validation and serialization in begin,
before the existing backend enqueues a request. First measure ordinary begin on
bounded large inputs, then preserve its exact observable results through detached
preparation and current-owner adoption. The original synchronous API remains.

## Preparation and authority

The serialized EditorDraft owner requests work with the final intent and request
identifier. Every attempt invalidates preceding history, recovery and request
preparations, including invalid intent/identifier and clean no-op attempts. Check
ordinary editable state and argument validity; clean drafts return no work. Capture
only the bounded settings base/draft, epoch, immutable resource context and policy
needed for the ordinary begin checks. Copy no history, selection, clipboard, active
request, ticket counter or result. No live owner pointer or native object crosses
the worker boundary. One work item is consumed by one run, including failed runs.

Run the original full begin validation on detached state, including command schema,
authored coherence, limits, resource and theme preparation. Serialize the exact
final request identity, epoch, expected revision, policy generation and intent.
The result is opaque and grants no authority. Retain the validated command and its
exact serialized bytes, plus weak owner/mutation identity. Worker preparation must
not allocate a live request ticket, send IPC, change the origin or publish storage.

Adoption consumes the result once. Require the originating live draft identity and
unchanged mutation generation, current editable state, epoch and base revision.
Reauthorize the exact command and current resources under the live policy. Reuse
only full structural proof for those unchanged inputs. No caller-created proof,
mutable prepared document, changed request identifier or unchecked skip flag exists.
Then allocate the next live ticket and install the ordinary pending request with
the exact prepared body. Clear clipboard as ordinary begin does. Do not modify
scene, selection, history or revision. Prepare any throwing copies before changing
the active request, ticket or state. Refusal preserves those observable values and
invalidates other pending preparations. Existing complete/cancel/disconnect/result
reconciliation behavior applies unchanged after adoption.

Every existing recovery-invalidating operation, and every selection attempt,
invalidates request work even if rejected or visually unchanged. Copies, moves,
assignment, destruction and cross-draft use cannot transfer adoption identity.
Starting new request/history work invalidates previous results. Policy changes
invalidate even across denial followed by regrant. Worker completion after any of
these events is allowed, but stale results cannot become pending requests.

Storage is bounded by one detached base/draft pair per admitted work and one
command plus serialized wire body per completed result, under existing authored,
resource and wire limits. Resource snapshots remain immutable. No unbounded cache,
retry loop, new scheduler or enlarged document limit is authorized.

## Native integration gate

Portable preparation is a required implementation stage, not a completed GUI repair.
Before connecting it, close one finite request slot on the existing editor worker,
ordered with recovery/history preparation, cancellation before/after computation,
closure acknowledgement and stopped-result ownership. Disable conflicting authoring
while preparation is pending; retain navigation/close cancellation and current
policy erasure. The live GUI alone adopts and submits. Recovery digest selection
must still describe the current retained draft; pending preparation is not a durable
request and cancellation must not fabricate an unknown storage outcome.

No additional worker thread or timer is authorized. Topology change, reload,
withdrawal, disconnect and close cancel pending work; late results must not revive
a closed/replaced form. Record exact ready/recovery/command/backend stage costs
before selecting the integration boundary. Native qualification requires held-work
cancellation/current-policy cases and the original seven GUI timing/erasure cases
after integration. Keep other measured restore/form-timer/paint work visible.

## Fixed verification

Freeze literal command/scene/theme/revision/ticket expectations and run the common
trace, theme, transaction and envelope cases first through ordinary synchronous
begin. Run the same unchanged expectations through prepared adoption. Also test
detached execution on a joined test thread, no origin mutation before adoption,
stale/cross-owner/copied/moved/destroyed origins, repeated/failed run and adoption,
policy denial/regrant, cancellation, preview then commit, conflict, unknown result
and exact original-request reconciliation. Invalid results must not spend a ticket
or alter scene/history/selection. Measure capture/run/adopt independently; do not
substitute their sum or a microbenchmark for GUI responsiveness qualification.

Use existing component/test targets on all three development profiles, preserving
source ownership and dependency declarations. Rebuild affected dependents, run
portable editor/settings/configuration/scene/protocol/component checks and legacy
artifact checks, then native consumers as appropriate. Archive source-bound results
and failed attempts under ignored out/. Production recovery and all five full
0.1.0 editions remain unqualified until their complete gates pass.
