---
type: "SysPane Work Package"
title: "Installed native scene editor"
description: "Connect native scene authoring to the actual frontend, verified helpers and authenticated commands."
tags: ["delivery", "experience", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T23:38:00+00:00"}
sp_id: "SP-W11-INSTALLED-EDITOR"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSTALLED-SETTINGS", "SP-W11-EDITOR-HELPER-WORKER", "SP-W10-RECOVERY-CONTROLS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed native scene editor

Compose the existing EditorForm in the real bin/syspane frontend. This package
adds native scene authoring, rendering and durable Apply to that application.
The complete edition still requires telemetry, behind-icons hosting, inspector
integration, independent escape/recovery and installed draft recovery. Current
profile transfer lacks verified committed-generation and recovery-directory
authority. Do not infer those from revision numbers or XDG strings, enable capture
without them, or count this package as completion of those requirements.

## Application and native ownership

Use the existing frontend supervisor/client workers. Construct EditorHelperClient
on GTK and its LinuxEditorHelperOwner beside LinuxProfileSupervisor on the existing
supervisor worker with the same verified installation. Pump both every 10 ms during
ordinary scheduling. Never introduce a second installation owner or an additional
helper worker thread. GTK receives trusted image factories; helper verification,
launch and native polling remain outside its callbacks and all shared mutexes.

Advance DevelopmentFrontend to the existing five-file helper record 0.2 bundle:
bin/syspane, configuration host, image worker, recovery worker and helpers.json.
The main embeds the bundle expectation. Missing or substituted roles refuse startup;
there is no configuration-only fallback in this installed edition. This supersedes
the three-file payload choice in SP-W11-INSTALLED-SETTINGS; record 0.1 remains valid
for its other explicit consumers. Package the fixture frontend with its separate
configuration helper and the same production image/recovery helpers. Preserve
protected-policy refusal; no new environment/CLI authority switches in production.

Closing erases both active forms, stops factory admission and keeps GTK dispatching
until controller/client/helper owners and the form's child work have drained.
Destroy helpers/supervisor on their native worker before runtime retirement. The
backend cannot report stopped while image or recovery work remains. Policy loss,
disconnect and replacement erase the active editor's private fields, resources,
preview and accessible data using its existing invalidation paths.

## One active draft and navigation

Start in Settings. Add native Settings and Edit scene actions with stable accessible
identities. Only one form owns an editable draft. Navigation is enabled only with
a current coherent profile, no unresolved request, no authored changes, no invalid
setting/private property text, no held gesture and no open modal editor. Expose a
read-only can_leave query on each form; checking it must not mutate or validate a
document again. Search text and selection alone do not block navigation.

When navigation is admitted, close the previous form and request a fresh coherent
profile. Await native image/recovery closure before destroying an editor or creating
its replacement. Never reuse the frontend's older cached scene after a successful
commit. Disable repeated navigation while loading. The editor's explicit Cancel
session action discards its local draft through its existing semantics, then returns
to freshly loaded Settings. Quit retains the existing explicit close semantics.

Editor actions share the backend's original request identity, one-command admission,
cancel, result/reconciliation and reload owners. Widget IDs use the controller's
fresh process epoch plus a monotonic GUI counter, never reuse a deleted ID in that
process, and are checked against the scene by the existing editor. Do not create a
second request ledger. Route replies to the active form only. Preserve unresolved
identity through loss; reconstitute a fresh editor after reconciliation and a fresh
coherent download, never replay an edit automatically.

## Native scene context

Read actual GDK monitor geometry, work areas and scale on GTK. Bound active displays
to sixteen and retained session monitor identities to sixty-four. Assign one local
ID per held native monitor object, without reusing IDs after removal. Publish the
primary role and fallback, with DIP/device-pixel conversion through existing scene
types. Refresh on native monitor/work-area/scale change; preserve authored values.
These are session-local identities, not persistent hardware binding claims. Missing
or inadmissible topology gives an unavailable editor and leaves Quit responsive.

Use the exact downloaded scene, resources, policy and negotiated capabilities.
Keep current property, layout, content, undo/redo, fonts and Apply semantics. Supply
the verified image factory. Unconnected telemetry remains an explicit missing source;
never substitute synthetic live values. Draft recovery remains disabled until its
separate authority boundary closes. Display a concise recovery-unavailable notice
so users understand that an unapplied draft is not promised across a crash.

## Frozen acceptance

Freeze this package, installed-editor cases and literal expected scenes before
production edits. Native observers run relocated production/fixture five-file
payloads on an isolated X11/D-Bus laboratory. Drive real GTK controls and inspect
stored scenes/settings/resources independently. Cover entry, properties, Apply and
reopen, clean/dirty/private/pending navigation, undo/redo, explicit draft cancellation,
reload, lost acknowledgement/reconciliation without duplicate revision, policy erasure,
controller replacement, helper substitution and closing during held persistence.
A deliberately wrong scene oracle must fail. Observe controller exit and runtime
retirement; preserve all failures and exact source/artifact identities.

New cases have 45-second ceilings and a 600-second family ceiling; existing cases,
product deadlines, task bounds, erasure bounds and workspace reservations remain.
Run unchanged installed-settings cases against the updated five-file packaging,
editor/form and helper-worker regressions, relevant command/profile checks and all
three component graphs. Record synchronous consumer work and other qualification
limits honestly; this package does not grant whole-editor performance, recovery,
desktop hosting or any of the five complete release editions.
