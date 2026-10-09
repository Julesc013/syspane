---
type: "SysPane Work Package"
title: "Initial editor preview readiness"
description: "Defer the first composition while preserving geometry-dependent input before GTK draws."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T07:02:00+00:00"}
sp_id: "SP-W11-INITIAL-PREVIEW"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-EDITOR-PAINT-TRACE", "SP-W11-PREPARED-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Initial editor preview readiness

The independent native trace confirms a full preview composition inside the form
constructor, followed by composition in GTK draw. Initial semantic preparation,
SceneSurface construction and its resource/layout/theme validation remain required.
Only the first full composition may move to the first draw or an earlier admitted
editing action. This is not permission to reuse old frames or skip native checks.

## State and behavior

The GTK-owned form starts with initial geometry unresolved. Construction creates
and validates the surface, populates the authored object list and ordinary controls,
and queues drawing. It makes no claim of resolved or visible preview content.
Before an admitted action can inspect geometry, selection variants, hit targets or
editable coordinates, resolve using the same current SceneSurface paint path.
The ordinary editing/request/policy/property-field guards run first. Completion of
either that resolution or a normal draw ends initial pending state, including a
defined alternative/empty outcome. Native failures retain ordinary error/fallback
handling. No failed or restricted frame may provide editable geometry.

Initial selection must hydrate the correct fields; a pointer hit must select the
same object; an immediately following arrow key must edit the same active layout.
Reload/topology/policy paths retain their existing invalidation and resolution.
Withdrawal before first input erases authored rows and private fields and prevents
editing. Closing before first drawing still erases native state and retires helpers.
Later changed/resolve/draw behavior stays as specified, including current telemetry,
conditional visibility and queued input following edits. No new worker, timer,
scheduler, public override, cache, authority or acceptance limit is introduced.

## Independent acceptance

Before changing product code, run a native component fixture with real GTK controls
but no realized canvas and no GTK main-loop iteration. Freeze the tests and bind
their source hashes. Cases cover tree selection, pointer selection, queued key,
topology breakpoint changes through both selection paths, reload before input,
policy withdrawal, empty-click/no-selection recovery and native text fallback.
Successful movement must submit the exact independently edited scene: only the
active layout's x increases by one DIP. Preserve all other authored content.
Withdrawal submits nothing and exposes no private rows/fields; fallback exposes
no editable geometry. Run exactly those expectations after the implementation.

Use ordinary profile configure/build commands. Run Linux portable checks, both
Windows component checks, existing standalone editor/preview-refresh, prepared
ownership, reply lifecycle, installed editor/settings/recovery, recovery controls,
layout/arrange/group/snap/container/visibility/lock and native image/erasure checks.
Keep native archives under ignored owned output roots and the existing budget.
Repeat bounded phase attribution, independent paint tracing and the unchanged
ordinary GUI limits. The trace should show no constructor geometry rasterization;
only the ordinary GUI observer can qualify latency. Preserve all remaining failures.

This closes initial composition scheduling only. Current-owner asynchronous
history/edit preparation, native inspector, telemetry/desktop integration and all
five complete release editions remain required. Production recovery stays disabled
until its original complete scheduling and responsiveness gates pass.
