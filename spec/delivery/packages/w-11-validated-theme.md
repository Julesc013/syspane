---
type: "SysPane Work Package"
title: "Exact validated theme reuse during composition"
description: "Remove repeated theme schema walks without changing request validation, typography or pixel output."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T06:35:00+00:00"}
sp_id: "SP-W11-VALIDATED-THEME"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSPECTOR-ATTRIBUTION", "SP-W11-TEXT-SESSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Exact validated theme reuse during composition

The complete attribution run separates admission (24–40 ms), non-presentation
painting (37–54 ms) and GTK presentation (21–24 ms) on slow populated-table ticks.
MAX-CELLS and POLICY still fail the original whole-tick bound. Painting is a
material repair boundary. Native text currently calls theme_font for every cell,
and that function validates the entire theme on every call.

Add an immutable ValidatedTheme value in the existing configuration component.
Its constructor validates the whole supplied theme before taking an owned copy.
Only exact structural equality, including JSON numeric representation/type, may
reuse this proof. Ordinary JSON equality or rounded numeric comparison is not
proof of equal validation behavior. Compare keys, types and leaf values, with a
bounded walk; a mismatch uses the original full validation path. A caller-mutated
theme, invalid token outside font data or changed role font cannot inherit a prior
proof. Invalid role rejection retains its original precedence.

The original theme_font remains the standalone entry. Font selection, owned
return values, fallbacks and validation errors remain identical. Add only an
optional borrowed proof to the internal TextRequest; no schema or runtime flag.
TextSession continues to own only native font setup, never theme/request data.
SceneSurface owns one stack proof per composition. Tables and semantic blocks
may own one additional proof each for their derived contrast/background theme,
reusing a matching caller proof. At most three owned proof copies coexist along this path, in addition to the
existing request values; no per-cell retained map or cross-composition cache is admitted.
Composition proofs die before frame publication and native sink invocation. Current
policy/resource authorization, frame bytes, raster allocation and erasure rules
remain unchanged.

Use existing literal typography cases for exact/mismatched proof resolution and
invalid themes. Verify ownership after mutating the original JSON and explicitly
check that changing integer representation cannot match a proof. Invalid requests
must not poison later use of a valid proof.

The TextProbe may accept an experiment-only prepared_theme input. Compare exact
and deliberately mismatched valid proofs against all 30 already frozen standalone
metadata/pixel/error outcomes; retain the original input, process and family
bounds, issuing individual bounded requests as necessary. Do not regenerate
expected pixels. Run native text/typography, scene/table/chart/visibility and
erasure regressions, the ordinary table family and complete phase diagnostic.
Shared configuration code requires development-profile builds and typography
checks on Windows GCC, v141_xp and Linux GCC; historical import checks remain.

This repair does not imply qualification until the unchanged ordinary timing
oracle passes. Preserve every failed attempt and use the resulting attribution
to select any further repair. All five complete native editions remain open.
