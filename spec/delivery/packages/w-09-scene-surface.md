---
type: "SysPane Work Package"
title: "Policy-owned native scalar scene surface"
description: "Compose authored scenes, pinned resources, scalar bindings and native text under one erasing presentation owner."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T21:05:00Z"}
sp_id: "SP-W09-SCENE-SURFACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-NATIVE-TEXT", "SP-W09-BINDINGS", "SP-W09-LAYOUT", "SP-W25-NATIVE-NETWORK-CACHE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-owned native scalar scene surface

Continue W-09 by composing existing scene 0.2, bindings, immutable resources and
native text. This package admits an initial scalar presentation capability, not a
complete edition. Preserve valid unsupported documents. Tables, charts, images,
collection-valued widgets and richer text content require their missing contracts
and implementations; return an explicit whole-scene alternative, never silently
omit them or invent content in extensions.

## Authored meaning and readable output

Within this capability, text renders its literal title and has no bindings. Value
and status each render title, one singleton binding's value/unit, and a mandatory
status line. Direct/persistent/unresolved pins are singleton; selector mode must be
singleton. Groups retain ordered children and use their title as an accessibility
group name; they have no painted header or implicit padding, as required by the
existing geometry contract. Extra bindings on groups/text and every unsupported
combination produce surface.unsupported. These are capability limits, not new
validation rules or changes to authored content.

Format uint64 exactly in decimal, bool as true/false, strings literally and finite
binary64 with the existing JSON library's round-trip decimal encoding. No unit
conversion or locale-dependent numeric rounding is introduced. Null is an em dash,
never zero. Append the reported unit with one space unless it is empty or 1.
Selection outcomes use Waiting, No matching entity, Restricted, Unsupported field,
Ambiguous selection, Invalid source or Capacity exceeded. Never append old values
to those outcomes. Binding denial makes the entire scene restricted with no payload.

For a matched row, status uses this ordered list, joined with ' | ': Retained
when the producer presentation is retained; Stale or Freshness unknown when
applicable; Pending, Access denied, Source failed or Disabled for acquisition;
Absent or Presence unknown; Unsupported or Support unknown; Derived or Configured
for origin. Use Current only when that list is empty. Include only a safe error
code after Source failed (in parentheses); no provider error message. The label,
value/unit and status are separate LF-delimited lines. Accessibility text preserves
the same content plus explicit support/acquisition/presence/freshness/origin/lease
axes and age in integer nanoseconds or unknown. These are initial English labels;
localization and full native accessibility navigation remain subsequent gates.

Shape the complete visible block with the native adapter. Initial minimum and
preferred metrics are its unwrapped readable raster extent, including the raster's
guard pixels converted upward to 1/64 DIP. Do not use wrapping or clipping to hide
overflow. Resolve the shared layout with those metrics. Any alternative layout,
missing glyph, unsupported widget or text/resource capacity failure clears the
candidate atomically and returns an alternative, with one public stable reason.
Degraded but fully readable layouts retain their existing diagnostics.

Paint leaves in layout preorder at their resolved pixel positions. Each leaf's
native raster supplies its theme background once; display buffers otherwise remain
transparent. Group bounds are not extra paint layers. Preserve straight-to-
premultiplied conversion and compose premultiplied RGBA with integer OVER, rounding
each destination contribution as (channel * (255-alpha) + 127) / 255. A pixel may
not be copied outside its resolved display. Each display is at most 2048 pixels per
axis; total retained pixels at most 4,194,304 and text at most 262144 UTF-8 bytes.
Check total raster/temporary pixel accounting too: display buffers plus leaf
rasters share an 8,388,608-pixel construction ceiling. Limits are logical payload
budgets, not a whole-process RSS guarantee for native font libraries.

## One serialized owner

SceneSurface owns the immutable authored generation and ResourceSnapshot, complete
trusted provider declarations, all DataViews, current policy, and at most one final
frame. Validate resource binding and current required capabilities before painting.
The fixed declaration set has at most sixteen unique producers; each declares scope,
types, fields/TTLs, metrics and explicit pin mappings. Native provider discovery and
mapping persistence remain caller integration requirements; names/indexes cannot
create mappings. No DataView pointer escapes the owner.

All access occurs on one serialized event loop. Attach/receive/heartbeat/gap/
disconnect, policy replacement, scene replacement and close first discard the
cached frame and invoke the native clear callback. Clear empties copied native
accessibility text and schedules blank painting before accepting another frame.
It returns success only after reachable native payload references are removed;
it does not assert display-server presentation. Failure/exception permanently
closes the owner, removes its data views and prohibits further payload callbacks.
This is application-state erasure, not forensic memory sanitization.

Policy changes erase before checking revision, including grants. Available policy
must strictly advance the highest accepted revision; duplicate/regressed policy
leaves the owner denied. Unavailable policy does not reset that revision. Regrant
cannot restore an old DataView: fresh attach and full state are required. Both
desktop and accessibility operational disclosure, telemetry.subscribe and the
resource capabilities must remain allowed. Denial cannot retain scene labels,
counts, identities, values or pixels in a published frame.

Each paint request supplies current producer-qualified measurement ticks and
recomputes bindings/metrics/layout while current. It erases the previous frame,
then publishes one atomic frame via a synchronous borrow. No asynchronous prepared
frame can be submitted. The sink must not retain frame/model pointers or export
payload. The native adapter may copy only the accessibility text covered by its
registered clear callback. Drawing references exist only during the borrow.
Every mutating call, paint and status access rejects reentry during a borrow or
clear callback. A thrown sink exception releases the borrow without a second call.
Caller owns the surface for the entire call. Public status contains only code,
cached widget/pixel counts and stable reason, never payload identities.

Time is monotonic milliseconds supplied by the serialized native owner. Regression
closes and erases; no wrap/rebase. Native drawing obtains a new tick at execution
time, not queue time. The owned GTK laboratory repaints at 50 ms cadence so source
expiry becomes visible; installed scheduling/suspend recovery remain unqualified.
Owner close and destruction clear before native widget teardown. No history, disk
cache, clipboard, export or operational-value logging is enabled.

## Native experiment and acceptance

Archive exact expected cases before implementation. Component cases cover pinned
theme/scene identity, scalar zero/null/exact integers, status axes, group ordering,
overflow/unsupported atomicity, source disconnect/restart, stale/regranted policy,
old callbacks, both-channel denial, native clear failure and reentry/exception.
Use actual DataView wire admission and the shared binding/layout/native text code.

Run an owned authenticated Xvfb/GTK experiment with public synthetic telemetry and
one authored value widget. The independent Python observer constructs expected text
from fixed values and compares root pixels with separately rendered TextProbe
rasters. Assert real GTK accessible names and their erasure through the native
accessibility boundary. Exercise value replacement, revoke, stale delivery, grant
without data, fresh reattachment and source loss. Policy clear must remove old
pixels within 200 ms and keep them absent until explicitly fresh data is accepted.
Retain negative controls that leave old pixels or accessibility names; the observer
must reject them. A normal test window does not qualify behind-icons placement.

Use ordinary preflight/configure/build/test commands. Run existing suites on all
three development profiles and preserve exact source/oracle/native artifact and
runtime identities, failures and handoff. Keep W-09 and every full edition open.
Next integrate installed source/catalog/policy ownership, full widget content,
native accessibility structure/editing and independently verified host activation.
