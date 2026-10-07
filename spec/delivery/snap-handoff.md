---
type: "SysPane Work Record"
title: "Native grid and alignment-guide checkpoint"
description: "Bounded shared snapping with independently observed native gesture feedback and persistence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T06:10:20.794700+00:00"}
sp_id: "SP-SNAP-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-SNAP", "SP-GROUP-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native grid and alignment-guide checkpoint

Source baseline: `01bea41e2123f69b1d71285b5ab944122efeace7`. The
[package](packages/w-10-snap.md) closes deterministic grid/alignment-guide snapping
for the existing native editor's fixed-base pointer moves and resizes. W-10 remains
in progress; this component checkpoint does not complete an installed edition.

The shared projection accepts captured geometry in signed 1/64-DIP units and
returns deltas plus guide facts. It validates bounds before arithmetic, resolves
axes independently and chooses candidates by exact distance/source/coordinate/ID/
anchor order. Grid ties go away from its origin; zero-motion axes stay unchanged.
Sibling and parent/work-area guides use leading, center and trailing anchors.
Resize changes only trailing edges. Bypass returns the raw quantized delta.
The projection cannot mutate a scene; release still uses MoveWidgets/ResizeWidget
through the existing atomic draft and resource-aware transaction owner.

The native form captures selection, siblings, parent/work area, display origin,
scale and options at press. Live telemetry cannot retarget a drag. Native toggles
enable snapping and grid display independently; spacing cycles through 4/8/16/32 DIP.
Preferences stay local to the session and do not enter authored history or storage.
Snapped outlines, magenta guide lines and accessible coordinates agree while held.
Ctrl at release bypasses snapping; arrows/numeric fields remain precise alternatives.
Grid painting is bounded to 512 lines. Cancellation, focus/topology/policy changes
and close erase transient feedback; disclosure regrant cannot revive geometry.

## Verification

The package and 17 literal input/output cases were archived before production
changes. Four portable families cover coordinates and threshold ties, resize,
union movement, guide priority/order, bypass, integer extremes, invalid inputs,
capacity, atomic history, exact submission and policy rejection/erasure.
All 105 affected CTest entries pass on Linux GCC 13, Windows GCC 15 and v141_xp
on contemporary Windows.

Thirteen private Linux native cases exercise real check buttons and spacing,
held-gesture pixels and accessible guides, grid/sibling snapping, resize,
multi-selection, release-time bypass, precise keyboard movement, Escape, option
changes, cancellation, policy erasure, durable save/reopen and lost-result restart.
The deliberate altered-commit and frozen-preview controls are positively detected.
The unchanged grouping (11), arrangement (14), editor (20) and complete-scene/
storage/IPC (24) matrices also pass: 82 native cases across five final matrices.

The first native observer moved focus before GTK finished activating a check
button. It now awaits the externally observed checked state before dragging.
The second failure was fault calibration: freezing the native preview prevents
held guide lines from appearing, before the later moved-pixel check. The observer
now identifies that specific earlier failure only when live accessible coordinates
are correct, independently sampled original pixels remain exact and durable
documents remain unchanged. Both original failures and observers are archived;
neither correction changes the frozen geometry or product implementation.

Repository evidence paths (outside the standalone specification bundle):
`build-support/evidence/w-10-snap-attempts.json`,
`build-support/evidence/w-10-snap-native-index.json`,
`build-support/evidence/w-10-snap-verification.json`,
`build-support/evidence/w-10-snap-staging.json` and
`build-support/evidence/snap-handoff.json`.

## Next admitted boundary

Close remaining binding/content/theme, lock/visibility/typography properties and
responsive/flow transforms. Complete clipboard authority and recovery drafts, then
installed controller/catalog/policy ownership and scene-aligned entry/restoration
with independent escape before mapping. Continue other adapters and historical
native qualification independently.

These owned ext4/Xvfb/DBus checks do not qualify installed desktop behavior, physical
power-loss durability, historical Windows, full accessibility/performance or a
complete edition. Two existing Windows symlink tooling assertions remain skipped.
The Windows 9x, Windows NT, X11, Wayland and Mac OS X release scope is unchanged.
