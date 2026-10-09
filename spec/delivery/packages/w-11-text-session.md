---
type: "SysPane Work Package"
title: "Composition-scoped native font setup"
description: "Reuse Linux font setup within one synchronous composition while preserving exact rendering and erasure."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:42:00+00:00"}
sp_id: "SP-W11-TEXT-SESSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-HOTPATHS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Composition-scoped native font setup

The measured 256-widget first paint still takes about 301 ms after compiled schema
navigation. Implement the admitted native-text session in `source/rendering/`;
keep the existing 100 ms GUI, 200 ms erasure, scene, glyph and pixel limits.
No production recovery enablement, native target qualification or new scheduler.

An internal, noncopyable and nonmovable TextSession owns one lazily created Linux
Pango font map. It is confined to its creating thread; rendering on another thread
fails with `text.owner` before touching native state. Existing standalone
render_text creates an independent session. A nullable explicit helper argument
may select a session for synchronous calls; no request or retained object stores
that borrowed argument. TextSession owns no request, theme, text, layout or raster.

Each request retains its original validation order, context, font description,
language, role, scale, wrapping, colors and independent layout. Reuse only the font
map at its original 96 dpi. Existing native/allocation error mapping remains.
Rejected requests cannot poison later valid calls. No process-wide or thread-local
session, authored cache, deferred request or shared concurrent native state.

SceneSurface::compose owns a stack session. Propagate it through plain text,
semantic blocks, tables, chart labels and conditional-visibility diagnostics.
Successful image rasters retain their existing image path. Destroy the session
on every return or exception, before publishing the frame or invoking its sink.
Existing policy withdrawal, clear-before-paint and accessibility erasure remain.
Standalone helper callers may omit the session and retain their existing behavior.
The session adds no product request limit: existing composition bounds govern it.

## Frozen verification

Before changing the native backend, generate the fixed sequence in
`tests/scene/text_session_cases.py` and capture the existing standalone TextProbe's
metadata, exact RGBA bytes and errors. Pin the source, executable, recipe and font
runtime identities. Retain raw inputs/results locally; compact hashes are sufficient
for the shared expectation record. This baseline supplements independent TEXT-RASTER,
THEME-TYPOGRAPHY, scene/table/chart/visibility/role composition and erasure oracles.
Do not regenerate expectations from the candidate.

A test-only TextProbe session mode accepts at most 64 requests and 32768 input
bytes. Compare standalone and shared-session results in forward, reverse and
alternating order, with invalid requests between valid ones. Each invocation has
the original 10-second native text deadline; the family has a 90-second ceiling.
Compare dimensions, all rectangles, preferred size, baseline, lines, glyph failures,
font lists, theme immutability, every RGBA byte and exact errors. Observe no partial
file on rejection. Retain the normal one-request interface and its fault witnesses.
Also exercise wrong-thread refusal and same-thread reuse after that refusal.

First verify the session and independent text oracles before connecting it to
SceneSurface. Then rerun scene composition, role typography, table/chart/image and
visibility checks plus all corresponding native erasure cases. Run the original
83 recovery regression cases and fixed maximum GUI qualification, measure the same
preview stages, and retain every failure. Preserve all three portable-profile
regressions and historical PE checks. A missing target laboratory remains blocked
qualification; all five complete desktop editions remain required.
