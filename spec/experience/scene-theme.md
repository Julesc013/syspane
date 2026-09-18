---
type: "SysPane Specification"
title: "Scene, theme and binding model"
description: "Keep visual customization portable, bounded and independent from collection."
tags: ["experience"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-SCENE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-RENDERING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Scene, theme and binding model

## Scene structure

A scene document owns stable object IDs, display assignments, containers, widgets, bindings and authored constraints. Widgets reference telemetry fields/entities through a bounded binding language, not arbitrary code. Repeating collections preserve stable row identity and configured sorting; user-priority ordering does not jitter with every traffic change.

The initial built-in primitives are labelled text/value, table, chart, status, group and image. A section is a container, not a separate telemetry subsystem. Adding a second rendering of a field shares acquisition demand. Removing a widget does not remove a separately enabled history request.

## Themes

Theme documents own typography, spacing, density, colour tokens, borders, alpha, chart styles and optional motion. They are versioned separately from scenes and settings. Native adapters can substitute available fonts and high-contrast values without rewriting source documents. Themes cannot suppress mandatory source-failure, replay or host-degradation labels.

Images and other assets are packaged by manifest with size/hash/media-type checks. Reject path traversal, external auto-fetch URLs, executable payloads and decompression bombs. A signed theme is attributable, not proof it is safe. Core trust badges cannot be overridden by a custom style.

## Binding and expressions

Use explicit entity selectors, field paths, unit-aware formatting, predicates and bounded derived expressions. No file access, network, shell, dynamic imports or privileged API from a binding. Cap expression depth, operations, collection cardinality and emitted text. A missing binding exposes unavailable state rather than a blank or zero.

Unit conversion distinguishes decimal and binary sizes, bits and bytes, cumulative counts and interval rates. Expression error and source error remain distinct. Format dates by locale for display but keep export timestamps unambiguous. Sorting is stable with explicit tie-breakers.

## Interchange and downgrade

Preserve unknown optional extension data during round trips. Reject unknown mandatory behaviour and explain unavailable widget capabilities. Moving a scene to an older profile uses a preview of adaptations; it does not silently delete sections. Retain source schema version and a reversible migration record where feasible.

## Acceptance

Fixtures cover shared bindings, invalid fields, unknown widgets, unit mismatch, expression limits, malicious asset paths, missing fonts, high contrast, responsive reflow and downgrade loss reports. Native screenshots can differ; the authored document and state meaning remain consistent.
