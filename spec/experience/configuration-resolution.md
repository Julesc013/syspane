---
type: "SysPane Specification"
title: "Configuration resolution and provenance"
description: "Define deterministic precedence, reset semantics and mandatory policy constraints."
tags: ["experience"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-CONFIG-RESOLUTION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SETTINGS", "SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Configuration resolution and provenance


## Resolution order

Resolve built-in defaults, admitted installation defaults, selected preset,
user overrides, then explicit session overrides. Role-specific selections are
named documents in those layers, not hidden extra precedence. Apply current
mandatory policy as constraints/forced values after resolution and recheck at
prepare, commit and activation. A rejected request reports why; policy never
silently turns a prohibited request into an authorized side effect.

Each effective value exposes requested value, effective value, originating layer,
document revision, policy generation, locked/unavailable reason and activation
scope. Protected administrative sources are distinct from user-writable defaults.
Portable flags, TOML imports and native preference backends cannot bypass them.

## Merge and edit rules

Absent means inherit. Scalars replace lower-layer values. `null` is a value only
where the relevant schema permits it, never an implicit reset or deletion.
`reset` removes the current layer's override. Ordered scalar lists replace as a
whole; they are never implicitly concatenated. Scene objects merge only through
stable-ID operations. `remove` creates an explicit inherited-object tombstone;
resetting that operation restores inheritance. Reordering uses explicit ID order,
not array-index identity. Reject duplicate or dangling object references.

Presets form a bounded acyclic single-parent chain with pinned versions/digests,
maximum eight levels. Includes resolve only within admitted package closure, never
through automatic URLs or arbitrary filesystem searches. Updates use a three-way
comparison of old base, user changes and new base, with conflicts previewed before
one authored-state transaction.

One typed runtime store is canonical. TOML is an authoring/import route. Registry,
GSettings or KConfig integration must not become another independently writable
settings engine. Structured edits preserve comments/order or write a clearly named
generated override. External edits use digest/revision conflicts.

## Theme and motion precedence

`display.theme_id` is the application default. Scene 0.2 `theme_id: null` inherits
that default; an explicit scene theme selects an override. Scene 0.1 always carries
an explicit theme and migration preserves it. Native high contrast and mandatory
status indicators constrain the selected theme without rewriting source content.
Effective motion is the most restrictive of theme preference, user reduced-motion,
OS accessibility and policy. A theme cannot re-enable animation disabled elsewhere.

Tests compare GUI, CLI, imports and preset operations on canonical authored state,
check reset/remove/list rules, current policy changes and external-edit conflicts.
