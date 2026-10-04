---
type: "SysPane Specification"
title: "Rendering, text, layout and display recovery"
description: "Render only necessary changes and keep authored intent separate from pixels."
tags: ["desktop"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-RENDERING"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-DESKTOP", "SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Rendering, text, layout and display recovery

## Pipeline

Accepted telemetry and scene revisions produce a display projection. The layout engine resolves authored constraints using display geometry and native text metrics. The renderer draws supported primitives and reports frame generation/presentation health. The host places those surfaces. No stage queries hardware while painting.

Use logical units with one explicit conversion at the backend boundary. Keep source units, formatted labels, font metrics and pixels distinct. Font fallback, script shaping, bidirectional text, localized numbers and high-contrast substitutions are real layout inputs. Do not preserve a fixed screenshot by clipping translated values.

## Primitives and caching

Start with text, labelled values, tables, separators, status markers, time-series charts, containers and images. Cache immutable text/layout and geometry by the inputs that actually affect them. An observation that is unchanged does not dirty unrelated widgets. A theme colour change need not rerun collection or entity reconciliation.

The wall uses demand-driven rendering. Animation is bounded and optional. The editor may redraw at an interactive cadence while dragging, then returns to idle behaviour. A constantly updating “0.1 seconds ago” label has an explicit cost; coarsen age formatting when detailed transition feedback ends.

## Responsive rules

Resolve stack/grid/flow and bounded absolute positioning first. Widgets declare minimum readable size, preferred size, constraints, priority and compact alternatives. Below a breakpoint, hide low-priority columns or move details to inspector/pages rather than shrinking all fonts. Critical failure indicators cannot be silently clipped by a theme.

Display identity is best-effort with persistent user assignment and confidence/ambiguity diagnostics. Never identify every monitor only by transient index. A removed monitor changes resolved geometry, not authored ownership. Logo exclusions, system-reserved regions and user-safe margins are first-class.

## Resource and failure limits

Cap surfaces, image dimensions, decoded image memory, vertices, text length, chart points and retained layout caches. On low memory, reduce optional detail and report degradation; do not allocate endlessly while retrying device creation. Failed graphics resources are recreated from a retained projection without replaying hardware I/O.

A backend must state alpha format, blending, text antialiasing and transfer costs. Screen-space bounds and damage rectangles are performance tools, not correctness proofs. Full-surface update APIs may still transfer the full window even when only one data row changed.

## Acceptance

Golden synthetic scenes cover multilingual text, malformed labels, long identifiers, high contrast, themes, empty/error/stale states, 1024×768 through large/multi-display profiles and DPI changes. Assert semantic layout invariants across platforms; use per-platform images for raster comparison. Independently measure visible generation and resource costs.

## Authored versus resolved state

Use [scene 0.2 layout](../experience/scene-bindings.md); resolved rectangles and native
font substitutions are derived output. Decode authored sRGB RRGGBBAA straight-alpha
tokens consistently before backend conversion. Missing fonts, high contrast and
reduced motion cannot hide mandatory states or rewrite source documents. Rendering
progress and producer/metric freshness have separate timers and evidence.
