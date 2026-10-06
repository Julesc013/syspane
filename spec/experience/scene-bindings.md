---
type: "SysPane Specification"
title: "Portable scene structure and binding"
description: "Separate authored hierarchy and selectors from resolved geometry and live identity."
tags: ["experience"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-BINDINGS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SCENE", "SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Portable scene structure and binding

The executable [layout package](../delivery/packages/w-09-layout.md) closes the
initial geometry algorithms, explicit monitor fallback, native readable metric
inputs, clipping/overflow diagnostics and pixel conversion. It preserves the
authored schema and does not qualify native text, drawing or activation.

## Versioned scene grammar

Keep the delivered [scene 0.1 schema](../contracts/scene.schema.json) and fixtures
as migration inputs. New authoring uses [scene 0.2](../contracts/scene-v0.2.schema.json).
Its ordered roots and ordered group children own each widget exactly once. IDs are
unique within a scene; parentage is acyclic, depth is at most 16 and widgets at most
256. Only groups have children. Visual parentage is separate from entity relationships.

Layout authoring supports canvas, stack and grid containers; leaf placement supports
fixed rectangles or flow with readable min/preferred/max sizes and anchors. Breakpoint
alternatives are ordered by increasing minimum width; the highest applicable one
wins, within the schema's bounded count. Resolved pixel rectangles are derived state.
Over-constrained layouts return diagnostics and a readable fallback, not silent loss.
Absolute positioning remains supported. The editor moves groups without changing
child identity and freezes selected-item placement during live inventory changes.
A fixed group is a positioned bounded canvas; its rectangle is preserved when
migrating an old absolute group. Other container layouts resolve placement from
the display region or their parent container.

Portable monitor roles resolve through a host-local map. Missing displays retain
their assignment and temporarily map to an admitted readable fallback with a warning.
Do not rewrite user intent when DPI, fonts or display topology changes.

## Binding grammar

[Binding descriptors](../contracts/binding.schema.json) select an entity type and
scope, bounded predicates, singleton/collection mode, stable sort and a maximum
result count. Scope is explicitly local host, current session or a registered asset.
Collection ordering ends with scoped entity identity as a deterministic tie-breaker;
rows retain that identity across refreshes. Collection truncation is visible.

Direct pins bind producer/epoch/entity identity and are local. A persistent pin
uses a provider-defined durable key and namespace plus a local mapping. Names,
drive letters and reused interface indexes never silently substitute new hardware.
Portable packages use selectors or explicit unresolved mapping prompts.
An `unresolved_pin` preserves a legacy entity/field without inventing a producer
epoch. It stays inert until an explicit local rebinding transaction resolves it.

Resolution yields matched, pending, empty, denied, unsupported or ambiguous.
Singleton multi-match is ambiguous; it never chooses the first record arbitrarily.
Missing/error input remains missing/error, not zero. Unit conversion is explicit.
The first grammar supports selection and formatting only; general expression AST
evaluation stays unavailable until versioned bounds and conformance fixtures exist.
No file, network, process or arbitrary native calls are binding operations.

## Migration and acceptance

Migration copies 0.1 widgets as ordered roots, preserves rectangles/theme and moves
literal display/entity assignments to local bindings; it cannot infer portability.
Preview any missing producer context and retain the original document. Downgrade
reports unsupported hierarchy/selectors and never flattens destructively in place.
Unknown optional extensions survive inertly within parse bounds.

Fixtures cover hierarchy cycles, multiple parents, dangling/deep graphs, constraints,
selector bounds and migration. Native tests use two host inventories and display
topologies, removal/replacement, ambiguous pins and save/reload equivalence.
