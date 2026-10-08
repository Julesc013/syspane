---
type: "SysPane Work Record"
title: "Portable scene layout checkpoint"
description: "Exact authored geometry, safe display regions and explicit readable overflow across development toolchains."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T19:33:21Z"}
sp_id: "SP-LAYOUT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-LAYOUT", "SP-NATIVE-CONTENT-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Portable scene layout checkpoint

Source baseline: `29a87531c933639dc2268e4c91bb7df49836233e`. Git history identifies
the resulting commit. The [package](packages/w-09-layout.md) closes W-09's shared
geometry boundary while retaining every admitted scene/layout kind and the full
native desktop objective.

The engine resolves immutable scene 0.2 documents using explicit local display
identity/role maps, work areas, safe insets/exclusions and premeasured readable
leaf sizes. It computes the largest safe rectangle, selects display-width
breakpoints, measures hierarchy and allocates stack/grid/canvas/fixed/flow layouts.
Priority affects shrinking above readable minima and never removes an item.
All post-decode geometry uses integer 1/64 DIP units; only clipped output bounds
convert to pixels through each display's explicit rational scale and pixel origin.

Missing/ambiguous displays retain authored intent and use an explicit fallback.
Cross-display parentage is rejected. Invalid inputs yield no partial plan. Resource
bounds and diagnostics distinguish ordinary geometry, degraded placement and a
required alternative presentation. Off-screen/unreadable content remains represented;
it is never counted as successful visible activation. The engine performs no native
font lookup, collection, I/O or mutation of authored documents.

## Evidence

The first 26 input/expected-output cases were recorded before engine implementation.
Five additional cases cover exclusion order, native preferred metrics, nested
breakpoints and sub-DIP rounding. The dedicated executable also checks invalid/
maximum-size scenes and compares exclusion geometry against an independent exhaustive
cell-occupancy oracle for all 256 arrangements of eight obstacles. Every successful
fixed case checks enumeration invariance and authored-input preservation.

Full suites pass 203 Linux, 185 contemporary Windows and 172 historical-toolset
entries on the modern Windows host, including the same 33 scene checks. Eighteen
historical executables pass the PE/header/import and actual linker-input audit.
Specification checks and 56 tooling tests pass with two existing Windows symlink
skips. Historical native OS behavior and native rendering remain unqualified.

The initial compiler failure for three misleadingly indented statements is retained
with its exact source archive. Correcting statement layout does not change any
expected geometry. A workspace reservation stopped the historical configuration
before it began. Verified completed cached attempts were reclaimed only after
comparison against unchanged committed evidence; the unexpected empty attempt
remains untouched. The reservation then passed and the historical checks resumed.
Both reclamation audits and the original preflight stop are preserved.

Evidence is indexed in `out/evidence/w-09-layout-attempts.json`; the
machine handoff is `out/evidence/layout-handoff.json`. Final staged input
hashes bind all three full runs and the fixed expected cases to this checkpoint.

## Remaining boundary

W-09, W-08 and all five complete release tracks remain open. Connect native text
measurement and drawing to the immutable scene/resource generation and this plan,
with current-policy erasure, live bindings and actual activation/recovery. Then
native editing/settings can operate on the same resolved scene and common commands.
Installed ownership, media decoding, complete provider behavior, native labs and
package/lifecycle qualification remain required. Geometry tests do not establish
font shaping, accessibility, screenshots, behind-icons placement or visible health.
