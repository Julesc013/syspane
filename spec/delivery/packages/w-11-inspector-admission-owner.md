---
type: "SysPane Work Package Boundary"
title: "Inspector admission ownership before background rendering"
description: "Separate the existing delivery state machine from GTK without changing its observable decisions."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T02:00:00+11:00"}
sp_id: "SP-W11-INSPECTOR-ADMISSION-OWNER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSPECTOR-TELEMETRY", "SP-W11-INSPECTOR-DELIVERY-GAPS", "SP-W11-TABLE-RASTER-REUSE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector admission ownership before background rendering

Continue W-11 through a prerequisite for the measured admission/painting repair.
The existing synchronous SceneInspector owns delivery state inside its GTK
implementation. Extract that state machine into one private InspectorAdmission
owner in the same component. The current presenter must use it, so a later
background renderer can use the same implementation rather than a second set of
lease, clock and chart-continuity rules. This package does not enable asynchronous
presentation or claim to fix the preserved 100-ms GUI failures.

## Scope and ownership

InspectorAdmission borrows one SceneSurface whose lifetime encloses it. Construct,
use, reset and destroy both on one execution owner. Construct a future worker's
objects on that worker; do not move a GTK-created surface, native image handle,
Pango session or captured GTK clear callback across threads. Methods reject a
different thread or recursive admission before touching the borrowed surface.
The caller owns clear-before-presentation, current policy/resources/topology,
surface replacement, close and image-job drainage. Admission owns only its last
binding, frame, scope, heartbeat, attachment token and local absolute lease.

No queue, worker, cache, contract version, producer capability or installed helper
is added here. Binding/frame handles retain the existing bounded immutable
TelemetryDelivery; original wire bytes, receipts and receiver ordinals remain
unchanged. The returned clock map is owned by the caller for one paint. No sink,
phase observer, borrowed frame pointer or GTK object is retained by admission.

## Fixed transitions

Check profile compatibility before the synchronous presenter starts its observed
transaction. Missing current profile or a different previously selected profile
closes and erases that inspector. A delivery scope has the exact current profile
and supervisor generation; an old transferred scope grants no retention authority.

Within the transaction, check TelemetryDelivery.deliverable against the supplied
current scope and actual event-loop time. Native lease expiry, disconnected peer,
missing/zero ordinal, stale native clock (more than 250 ms), a clock from the
future or a frame receipt from the future disconnects the prior local attachment
and supplies no measurement tick. Paint retains only the existing surface's
permitted prior data with retained lease and unknown age. Never admit an unseen
queued value through that path. An expired or changed local binding/generation
requires a new attachment; native data does not renew the native lease.

For a changed frame under an unchanged attachment, a non-increasing ordinal
disconnects without importing the candidate. A forward skip calls gap before
receive, with no intervening paint. First attachment admits only the latest
frame. Repeated immutable frame handles do not feed history again. Only accepted
or duplicate receive/heartbeat outcomes continue; only an accepted heartbeat
renews the existing 3000-ms local lease. Native absolute deadline remains the
outer gate. Preserve the existing current-tick validation at receive.

Reset releases binding/frame/heartbeat/token state but retains the established
profile identity. It does not grant a new profile, policy or resource authority,
perform I/O, disconnect a different surface, or replace the caller's erasure.
Policy, replacement, close and unsuccessful presentation retain their current
clear ordering. Preserve synchronous method outcomes, per-call phase ordering,
observer lifetime and fail-closed behavior in the GTK wrapper.

## Executable completion

Add native.INSPECTOR-ADMISSION-OWNER to the existing inspector fixture executable.
Without initializing GTK, exercise the real renderer and receiver on the main
owner and on a fresh worker owner. Assert exact scalar text/lease/age, every
existing literal chart point and pending-gap outcome, refusal of future/stale
clocks and receipts, expired leases, zero/backward ordinals and wrong generations,
profile closure, reset after policy erasure and rejection of cross-thread use.
Transfer only owned semantic output from the worker; no borrowed native frame
escapes its synchronous sink. Destroy all objects on their constructing thread.
This is ownership/conformance evidence, not asynchronous GUI qualification.

Run ordinary budget preflight, configure/build and the new native test. Retain
SCENE-INSPECTOR-MODEL, all seven native SCENE-INSPECTOR cases (including the
unchanged scalar, chart and phase assertions), installed telemetry and the 146
selected shared regressions. Run original table/frame/role/erasure checks as
appropriate. Preserve source, binary, environment, commands and every failure.
Record the result in the existing W-11 work row and linked checkpoint/handoff.

## Next boundary remains gated

Before enabling a background renderer, its linked package must close one in-flight
job, bounded latest pending input and completed-result ownership; exact current
profile/policy/resource/topology adoption; sampled-clock age and absolute lease
expiry during computation; frame coalescing and chart gaps; immediate GUI erasure;
cancellation and destruction acknowledgement; image-child ownership/drainage;
and independent supervision while native composition is running. Do not place
native composition on the service-supervision thread. A thread that has not
stopped cannot be detached or counted as reaped, and a stuck native operation
cannot become a claimed bounded shutdown through a timeout flag.

No async callback may retain the existing synchronous phase observer. Worker
elapsed time and GUI work must be distinguished without changing the ordinary
100-ms GUI/200-ms policy-erasure oracles. Qualification still requires the
unchanged ordinary/phase maximum-table families, maximum GTK chart/mixed and real
installed histories, human usability, desktop/lifecycle and all five full editions.
