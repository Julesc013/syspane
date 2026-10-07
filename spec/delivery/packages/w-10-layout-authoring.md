---
type: "SysPane Work Package"
title: "Native layout and responsive variant authoring"
description: "Author every existing layout kind, ordered breakpoint, display intent and active fixed variant through the shared draft."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T09:40:30.790394+00:00"}
sp_id: "SP-W10-LAYOUT-AUTHORING"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-EDITOR", "SP-W09-LAYOUT", "SP-W10-NATIVE-EDITOR", "SP-W10-NATIVE-OBSERVATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native layout and responsive variant authoring

Continue W-10 through the existing EditorDraft, validator, renderer and transaction
owners. Keep scene 0.2/0.3, layout 0.1 and wire identities unchanged. Implement
portable bounded input projection and a native Layout panel for one selected widget.
This closes authoring of the existing layout grammar; it does not invent locking,
conditional visibility or typography storage. Flow/container group conversion,
clipboard, recovery drafts, installed ownership and complete editions remain required.

## Private input and atomic adoption

Expose leaf fixed/flow and group fixed/canvas/stack/grid choices. Every variant has
its own field buffer, including inactive kind fields. Populate existing authored
values exactly; round-trip without changing the document. Default fields for a newly
chosen kind are fixed x/y 0, width 180, height 80; flow widths 32/180/32768 and heights
16/80/32768, anchor start; canvas 180/80 and diagnose; stack vertical, gap 8 and
diagnose; grid two columns, gap 8 and diagnose. Defaults supply explicit UI input;
they do not replace existing authored fields without Set layout.

The panel selects Base or one of up to eight breakpoint rows. Add copies the selected
variant into a new last row with an empty threshold requiring explicit input. Remove
is available only for a breakpoint. Keep row order; reject duplicate/decreasing
thresholds rather than sorting them. Switching rows/kinds preserves private invalid
text. Validate all selected variant kinds on Set, ignore inactive kind fields, and
preserve an originally present empty breakpoints array on no-op round-trip. Thresholds
retain the existing display-safe-width semantics and bounds, including equality.

Numbers use the existing bounded locale-independent content-number grammar (64
characters, optional sign/fraction/exponent, finite results only). Columns and sibling
position use canonical unsigned integer syntax. Enforce every existing layout bound,
ordered min/preferred/max triple, kind applicability and eight-breakpoint ceiling.
No clamp or conversion from resolved pixels. Invalid input stays visible and leaves
scene, selection, history and active request unchanged. Show a native error.

Expose selected-widget priority and zero-based sibling position in the same private
input. Reordering retains parentage and all relative order of other siblings; moving
to the current index is a no-op. Group children retain identity and content.

Expose local display ID versus portable role and its exact identifier. Explain that
a changed assignment applies to the selected object's entire top-level subtree.
Resolve the root by authored ownership, never by topology or enumeration index. A
typed RootDisplayEdit updates that root and all descendants in one operation, allowing
the maximum 256-node scene without widening the existing 128-operation batch bound.
Require an actual root ID for this operation. An unchanged display input leaves all
existing assignments intact, including equivalent role/local aliases. Missing or
ambiguous displays retain authored intent and use the existing renderer fallback.

Set layout submits complete-layout, priority, optional root-display and sibling-order
edits as one existing atomic EditorDraft history entry. It does not save. Cancel/Escape
discards input. While open, block other editor mutation/selection/Apply paths. Close,
policy/owner change, reload and topology replacement erase the panel and all row/kind
buffers; regrant alone cannot restore them. Held native references retain the existing
200-ms erasure requirement. Use the existing restricted private text control.

## Active fixed variants

Extend typed move, resize, align and distribute with explicit optional variant indices:
base is -1; breakpoint indices are 0..7 and must exist. Default omission preserves
all previous base-only callers. A move/arrange vector must match target count exactly.
Reject invalid indices, nonfixed selected variants, overlapping target sets and
ordinary bounds atomically. Modify only the named variants; never a base selected by
accident. History, policy, exact rounding and scope rules remain unchanged.

Native direct operations capture each node's resolved variant index and geometry.
Pointer and keyboard use the same typed operations; snaps keep their current captured
projection. Topology/focus/policy changes cancel held gestures. Numeric geometry fields
show the active fixed variant, with its identity in accessible guidance; buffered
geometry rejects if that variant changed before Set properties. Revert refreshes it.
Align/distribute operate on active fixed variants with existing native size-expansion
and sibling/display checks. Flow nodes remain selectable; their ordering/constraints
are edited through Layout, with no implicit destructive conversion to fixed pixels.

## Execution, evidence and remaining work

Freeze complete authored scenes, expected edits, order, breakpoint choices and exact
geometry examples before implementation. Cover every kind, all anchors/axes/overflow
values, decimal bounds, invalid triples/order/index/kind, no-op/Undo/Redo, 256-node
display propagation, current policy and exact submitted scenes. Include inactive
variant preservation and mixed base/breakpoint selections in direct transforms.

Use ordinary workspace preflight/configure/build and all three development profiles.
Run affected editor/settings/configuration/composition/protocol tests. The owned Linux
ext4/Xvfb/D-Bus matrix must operate actual controls, observe pixels and active variant
geometry, compare stored scenes/resources, reopen and exercise invalid/cancel/history,
topology, policy erasure and lost-acknowledgement recovery. Calibrate wrong-layout,
retained-field and frozen-preview faults with positive distinguishing evidence.
Rerun the existing native editor matrices and observation calibration when their
shared owner changes. Preserve every attempt and exact source/oracle/binary identities.

Routine implementation details are delegated. Existing contract meaning, release
scope, privilege and user-desktop boundaries are fixed. This component is not full
native or historical qualification. Continue remaining responsive/flow group
transformations, lock/visibility/typography, recovery/clipboard, installed ownership
and all five complete-edition release gates after this package.
