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
updated: {"by": "codex", "at": "2026-10-08T00:34:15.101366+00:00", "scope": "Native conditional presentation contract and development admission"}
---

# Rendering, text, layout and display recovery

The [scalar scene surface package](../delivery/packages/w-09-scene-surface.md)
defines the initial text/value/status/group capability and its erasing owner.
Pinned resources, singleton bindings and readable geometry compose atomically;
unavailable capabilities produce a whole-scene alternative. Its owned native
window evidence does not qualify the full widget set or behind-icons activation.

The [native text package](../delivery/packages/w-09-native-text.md) closes the Linux
plain-text measurement/raster prerequisite. It preserves native logical/ink origins,
uses bounded wrapping and explicit semantic/contrast colors, and records actual
fallback fonts. Live scene composition and retained-policy cache erasure remain
separate integration gates; this adapter's raster output does not establish visibility.

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

The shared [layout implementation contract](../delivery/packages/w-09-layout.md)
defines exact 1/64 DIP allocation, viewport breakpoints, safe-region choice and
readable overflow for the existing scene grammar. Native adapters supply measured
minimum/preferred sizes and must handle alternative/degraded plans explicitly.
They cannot infer visible success from returned geometry alone.

Use [scene 0.2 layout](../experience/scene-bindings.md); resolved rectangles and native
font substitutions are derived output. Decode authored sRGB RRGGBBAA straight-alpha
tokens consistently before backend conversion. Missing fonts, high contrast and
reduced motion cannot hide mandatory states or rewrite source documents. Rendering
progress and producer/metric freshness have separate timers and evidence.

## Conditional native presentation

The [native visibility package](../delivery/packages/w-09-native-visibility.md)
closes masking, warning geometry and lifetime for the Linux development experiment.
Measure authorized content before evaluating conditions; hidden content retains its
layout node and may continue authorized bounded chart/image work. Consume shared
condition decisions within the same serialized erasure owner. Hidden payloads leave
no pixels, accessible values, table identities, chart points or image metadata.

Unresolved and mandatory source states replace hidden content with status-only text.
Relay group diagnostics to existing leaf bounds, promote them through hidden inspector
groups and paint warnings after ordinary content. Reject warning overflow or overlap
atomically as surface.visibility_layout. Policy denial erases the whole result.
Ordinary scene 0.5 refusal remains until private native controls and integration
checks pass; this experiment's explicit opt-in is not installed capability admission.
