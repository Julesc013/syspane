---
type: "SysPane Work Package"
title: "Prepared initial editor ownership"
description: "Move validated draft construction off GTK while preserving current profile ownership and native rendering checks."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:11:32+00:00"}
sp_id: "SP-W11-PREPARED-EDITOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-FRONTEND-PHASES", "SP-W11-FRONTEND-RECOVERY", "SP-W11-INSTALLED-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Prepared initial editor ownership

The preceding checkpoint measures fresh GTK EditorForm construction at 156–195 ms.
The existing preview-cost experiment independently measures large EditorDraft
construction at roughly 54–79 ms. Draft construction owns no GTK object or native
thread binding. Move that same complete validation to the existing frontend client
worker, then transfer exclusive ownership to GTK. Do not skip validation, raise
limits, add a scheduler, or enable production recovery.

## Prepared value and adoption

An opaque PreparedEditor owns one freshly constructed EditorDraft plus the exact
authority, policy, settings, capabilities and large-command admission used by the
form. Construction runs the ordinary EditorDraft/SettingsDraft validation, resource
resolution and disclosure checks. The value exposes no mutable draft, JSON or
resource handle and cannot be copied. A unique owner may transfer it across a
thread boundary only after construction ends; no two threads may access it.

EditorForm consumes that unique owner as its sole initial semantic state. It does
not accept competing authored documents, policy or resource arguments on this
path. A null owner is an error before native setup. The traditional constructor
prepares and consumes the same value synchronously for existing callers. Form
construction, native controls, topology, text/layout, SceneSurface binding checks,
image callbacks and subsequent mutations remain confined to the GTK owner.
Prepared state conveys no authority beyond its original snapshot. Destruction of
an unconsumed value releases its private state without GTK or helper operations.

## Backend ownership and invalidation

The existing serialized client worker prepares one candidate after a complete
authenticated profile download and resource closure. Preparation runs outside the
backend mutex. Existing heartbeat, profile and result deadlines remain in force
and are checked after construction. Before publication, recheck supervisor
generation/readiness, shutdown, pending request and superseding reload intent.
Discard a superseded candidate and let the existing coalesced reload path run;
never publish it briefly as ready. The current profile and its prepared owner are
published together under the existing mutex. There is at most one stored prepared
value and one worker-local candidate; reload/submission releases the stored value.

take_editor accepts the exact current shared FrontendProfile identity. Under the
same mutex it refuses a foreign/copied/stale profile, loading, pending request,
withdrawal, shutdown or non-ready supervisor. It moves the prepared owner once;
a repeated request returns empty. Serial/epoch/revision/policy/capability/resource
binding follows the unmodifiable current profile identity, not caller-supplied
copies of those fields. Reload, submission, withdrawal and close discard the slot.
The GTK caller treats an empty result as a changed/unavailable snapshot and waits
for current state instead of using a synchronous fallback.

Experimental recovery admission is a constructor choice made by the existing
compiled entry point. The worker adds the recovery capability under exactly the
previous experimental-profile condition. This does not authorize recovery helpers;
the separate live native admission and exact receipt retirement remain required.
No new command-line/environment override or wire/document version is introduced.
Policy withdrawal after transfer is still handled by the existing GTK withdrawal
path and its unchanged erasure deadline. Native qualification must prove that the
remaining synchronous work does not prevent that boundary.

## Independent checks and limits

Run native component cases that construct the opaque value on another joined
thread, mutate original input copies, then adopt and drive the actual form controls.
Retain the original direct/reconciled/default/non-accepted/stale/invalid/withdrawn
reply expectations. Verify null-owner refusal. These cases do not themselves prove
backend currentness or native process ownership.

An independent backend extension verifies one consumption, copied identity refusal,
stale identity after reload/restart, pending submission, policy withdrawal and
shutdown. Refusal must not consume the current slot. Existing stored-document,
scope, process-exit and operation-deadline observers remain unchanged. Preserve a
bounded repeated-reload case so superseded work cannot publish an old ready state.

Use the pinned development profiles and ordinary configure/build/test commands.
Run affected portable suites on all three toolchains because the prepared value is
shared code. Run installed recovery/editor/settings, frontend backend, standalone
editor/recovery and scene/image/erasure checks. Repeat phase attribution and the
unchanged ordinary seven-case GUI oracle with its 100 ms work/delay and 200 ms
erasure limits. Maximum-input backend qualification retains its existing deadlines.
Preserve source/artifact identities and all failures in owned ignored output roots.
Preparation timing improvements are evidence, not permission to enable recovery.

This package implements preparation/adoption only. Remaining first-admission,
history/edit callbacks, native inspector, telemetry/desktop integration and all
five complete 0.1.0 editions remain required. Ordinary reversible implementation
choices are delegated by campaign admission; public releases and privileged
operations remain outside this package.
