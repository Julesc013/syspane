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
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
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

## Initial executable contract scope

The [table surface contract](../delivery/packages/w-09-table-surface.md) defines
ordered collection columns using existing bindings, exact scoped row joins,
explicit truncation/missing cells and native grid metrics. The
[scene 0.3 content contract](../delivery/packages/w-09-scene-content.md) adds plain
text bodies, column labels, bounded chart settings and exact image package/asset
references. Native text and label presentation are connected; chart sampling,
image decoding/rendering and richer formatting remain separate enablement gates.

[Scene/binding 0.2](scene-bindings.md) supplies ordered container membership, bounded
layout variants, monitor roles and portable selectors. The 0.1 rectangle schema is
retained for migration, not silently reinterpreted. General expression evaluation
remains gated until a typed AST, units and resource fixtures are specified.

Authored colors are sRGB `#RRGGBBAA` with straight alpha; backend premultiplication
is a deliberate conversion. [Resolution](configuration-resolution.md) defines default
versus scene theme and most-restrictive motion/accessibility precedence. The current
theme 0.1 schema represents five semantic colors, one font and motion. The
[theme 0.2 typography contract](../delivery/packages/w-09-typography.md) adds complete
font weight/style and named body, label, value and diagnostic roles. Absent roles
use the base font; theme 0.1 retains normal weight/style for every role. Family
names are literal data, native fallback preserves the authored name, and resource
admission requires theme.typography under current policy. The
[checkpoint](../delivery/typography-handoff.md) records native text evidence.

The [role-composition contract](../delivery/packages/w-09-role-composition.md)
assigns semantic roles and preserves mandatory diagnostics with bounded native
composition. Theme 0.2 requires explicit trusted development admission in addition
to current resource authority; direct consumers still refuse by default. Native theme
authoring and trusted editor integration remain the following boundary. Spacing/density, chart styles and contrast variants still require versioned
contracts and native tests; none is hidden in optional extensions.


The [theme-authoring input/artifact contract](../delivery/packages/w-10-theme-authoring.md)
preserves exact no-ops and authors complete base/role fonts without mutating an
installed package. Generated identity binds the source license and edited content.
The durable command boundary below now publishes versioned overrides. Atomic editor
history and native controls remain required before native theme editing is enabled.


The [bounded theme override contract](../delivery/packages/w-10-theme-overrides.md)
defines exact resource selection 0.2 and immutable replacement/reset beside the
original preset closure. The explicit component API preserves image references. The
[durable theme command](../delivery/packages/w-08-theme-commands.md) now admits exact
source-bound font intent through command 0.8 and Linux generation 0.4 recovery. It
retains the original closure and one canonical override, including reset and exact
request reconciliation. The [theme-history contract](../delivery/packages/w-10-theme-history.md) now connects
atomic editor resources and Apply/reload. Native authoring still requires font controls,
independent pixels/save/reopen and policy-loss erasure evidence.
