---
type: "SysPane Work Package"
title: "Semantic typography in scene composition"
description: "Bounded role composition with preserved diagnostics and legacy pixels."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T03:00:00Z"}
sp_id: "SP-W09-ROLE-COMPOSITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-TYPOGRAPHY", "SP-W09-SCENE-SURFACE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Semantic typography in scene composition

Continue W-09's existing SceneSurface, table, chart, image and visibility owners.
Theme 0.1 must keep the existing single-layout path and exact native pixels.
No authored schema, command identity, content pin or telemetry meaning changes.
Theme 0.2 requires current resource authorization AND an explicit trusted
SurfaceConfig experimental_typography admission. Default refusal, including a
disabled display, remains surface.typography_unavailable. Ordinary capability
advertisement alone does not enable it. Native theme authoring and its trusted
editor admission are the next package; installed and release qualification remain open.

## Roles and observable composition

For admitted theme 0.2, retain typed owned text blocks at semantic construction,
never infer roles by splitting user strings, searching keywords or reading markup.
Plain and accessibility strings retain their existing spelling, order and content.
An embedded newline stays in its originating block. Empty titles retain one label
block. Groups have no ordinary visual title; their existing accessible title remains.

| Content | Ordered blocks / roles |
| --- | --- |
| Text widget | Its complete body (legacy scene title fallback): body |
| Value or status | Complete title: label; formatted value plus unit: value; complete state/provenance line, including Current: diagnostic |
| Unmatched scalar binding | Title: label; existing Waiting/Unsupported/etc. message: diagnostic; no invented value |
| Chart | Scalar blocks above, followed by sample/segment line: label unless capacity/gap/fault then diagnostic; range/unit/clipped line: value unless unavailable/clipped then diagnostic; window/interpolation line: label |
| Table | Title and column headers: label; summary/count/truncation line: diagnostic; each cell: value and diagnostic blocks as for a scalar, omitting its synthetic empty title; unmatched cell: diagnostic only |
| Image | Existing bitmap, loading/failure markers and accessible alt/state; no new visual text |
| Conditional warning | Complete existing inherited/own diagnostic text: diagnostic, including warnings promoted from hidden groups |

A block uses the exact role resolver, native family fallback, language, foreground,
contrast and scale already specified. For multi-block scalar/chart/cell text, raster
each block independently on transparent background, align left at x=0, and stack in
order with ceil(4 * scale) device pixels between complete padded rasters. Keep empty
blocks and each raster's native padding. Composite width is maximum part width;
height is sum of heights plus gaps. Apply the chosen background exactly once over
that rectangle, then premultiplied OVER each part. One block uses the original
native raster directly. This is a visual composition buffer, not a shaped text line;
do not expose invented combined native baseline/ink metrics.

Table column maxima, row maxima and existing 8-DIP horizontal/4-DIP vertical gaps
remain. Chart plot geometry, history, sampling, border and 4-DIP text-to-plot gap
remain. Use the role-composed dimensions for the existing layout resolver. Conditional
visibility keeps the same unconditioned layout and wraps warnings with the existing
width rule. If a diagnostic cannot fit or would overlap another diagnostic, reject
the whole presentation as surface.visibility_layout; never shrink, omit or clip it.

## Bounds, ownership and failure

Every block string counts toward the existing 256-KiB derived text budget, including
cell blocks and role names. At most 16 blocks per scalar composite, 4096 combined
text bytes and 1024 combined native lines; existing individual text limits also
apply. Construction counts all simultaneously retained part pixels plus output
pixels against its supplied remaining scene budget, as table/chart composition does.
Each raster stays at most 2048 by 2048 and 4,194,304 pixels; scene/display/history/
image bounds remain. Missing glyphs or exceeded capacity reject the whole frame.
No partial pixels or accessible payload is published.

Blocks belong to the existing frame/cell objects, never another cache. Hidden payload
reset, replace, policy loss, failed native clear and shutdown erase them alongside
existing derived content. Inspector hidden-payload validation must reject retained
blocks. Policy denial takes precedence over typography admission. Authored documents
remain immutable; resolved fonts never overwrite the theme. No new privileged action.

## Frozen verification and execution

Freeze this package, literal fonts/semantic examples and independent expected-pixel
composition before production edits. Verify scalar current/pending/failed/stale,
status, embedded newlines, body, table headers/cells/summary, chart metadata, hidden
diagnostics and group propagation. Build expected rasters from literal complete base
fonts, without using production block composition or its chosen roles. Check exact
raw RGBA, table cell rectangles, chart text/plot boundary, scale, translucent background
and contrast. Deliberate all-body selection must differ in positive observed pixels.
Verify limits, default/capability/policy refusal, replacement/regrant and block erasure.
Preserve failed attempts and source/artifact/runtime identities.

Use ordinary CMake/CTest commands for linux-x64-gcc13, windows-x64-gcc15 and
windows-x86-v141-xp; run full portable suites, new native.ROLE-COMPOSITION and existing
text, scene, visibility, editor and erasure regressions on the pinned non-root Linux
laboratory. Historical toolset checks run on the contemporary host, not historical
qualification. Stay within the existing 7-GiB workspace; delete only verified committed
duplicates under owned roots. Then connect native theme authoring through the existing
draft/resource/persistence owners. This boundary does not complete W-09 or W-10.
