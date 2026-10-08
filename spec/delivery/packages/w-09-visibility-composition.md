---
type: "SysPane Work Package"
title: "Borrowed visibility composition"
description: "Compose bounded condition trees without nested reads or retained decisions."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T23:44:03.167528+00:00"}
sp_id: "SP-W09-VISIBILITY-COMPOSITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W09-VISIBILITY", "SP-W10-VISIBILITY-ADMISSION", "SP-W09-BINDINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Borrowed visibility composition

Continue W-09's native integration by closing the shared read and hierarchy
boundary first. Parent, child and content queries may use the same DataView.
Nesting existing project_binding calls would reenter that view; collecting and
retaining independent visibility results would violate their borrowed lifetime.
This package adds a single bounded batch borrow and a scene visibility projection.
It does not remove SceneSurface's conditional-scene refusal gate. Native geometry,
diagnostic placement, resource/history ownership, controls, accessibility and
independent pixel/erasure evidence remain required before enabling that renderer.

## Batch ownership and limits

project_bindings accepts an ordered array of 0..512 existing binding documents,
at most 262144 canonical UTF-8 JSON bytes in total, the existing trusted input
catalog, time, sink and BindingLimits. Validate all grammar/context and the sink
before touching a view or delivering a result. Duplicate queries are allowed.
Each successful batch contains one BindingFrame per query in input order.

Route each query exactly as project_binding does. Denial precedes pending, which
precedes unsupported fields. Missing producers, unresolved pins, field errors,
empty results and ambiguity are per-query outcomes; an unrelated unavailable
producer cannot suppress a successful query. Borrow the union of usable routed
views once in catalog order. Resolve queries and invoke the single batch callback
while every contributing borrow remains alive. A failed measured borrow makes only
queries using that view pending; do not fall back to an unmeasured read. A callback
cannot reenter any contributing view, retain/export payload, or retain the batch.
No demand, attachment or native cache is created. Sink exceptions propagate once.

The existing maxima remain: 16 inputs, 8 MiB query index space, 4194304 total
resolver work steps and 4 MiB total accounted output. Output accounts 128 bytes
per frame plus existing accounted row bytes. Work accumulates across queries;
query scratch indexes are released between resolutions. Caller limits may lower
these maxima, including to zero. Empty batches need no output/work budget.
Any index/work/output exhaustion or allocation failure during projection produces
one whole-batch capacity result with no frames. Invalid grammar/context throws
before delivery. A sink allocation failure is a sink exception, not a second
capacity callback. Earlier single-query API behavior remains unchanged.

## Hierarchy projection

project_scene_visibility accepts one valid scene 0.2..0.5 and the same catalog,
time, sink and limits. It validates authored structure before reading telemetry.
Missing visibility is shown. Evaluate every own rule exactly once, including
rules beneath hidden or unresolved ancestors; never suspend their input demand.
Use one batch for the own rules and preserve the single-rule comparison semantics.

Return nodes in authored root/child preorder, independent of widgets-array order.
Each node has its authored ID/parent, own outcome, show_content and blocker.
show_content is true only when every own/ancestor outcome is shown. blocker is
the first non-shown node's ID on the root-to-node path, or empty. These are
operational derived decisions and exist only inside the protected callback.
Never change the scene, layout, selection or any rule to apply inheritance.

Separately return every unresolved own outcome in preorder as an ID/code
diagnostic. Shown/hidden have no diagnostic. In particular, a false ancestor
cannot remove a child's unresolved diagnostic. This separation defines content
gating; it does not authorize hiding core source-failure, replay, lease, host or
policy status. Native consumers must render those outside authored predicates.

Any denied own condition makes the whole projection restricted, with no nodes or
diagnostics. Batch capacity makes it capacity, with no nodes or diagnostics.
Otherwise state is ready, even when content is hidden or diagnostic entries exist.
This state is evaluation readiness, not native activation or release qualification.
Policy revocation followed by regrant cannot recover old decisions without fresh
attachment/full state. No decisions survive a call. Native presentation may only
consume these results under a separately admitted policy/erasure owner.

## Frozen verification and continuation

Freeze this package and tests/scene/visibility-composition-cases.json before
production edits. Exact cases cover parent/child false, unresolved beneath false,
ordered diagnostics, independent roots, storage-order permutation, denial and
capacity. Exercise same-view duplicate queries, multiple producers, unavailable
and denied isolation, clock/lease/restart/regrant, all limits, invalid late queries,
all contributing borrow guards and a throwing sink. Preserve existing comparison,
binding, layout, authored-admission and native refusal expectations.

Run all three development profiles with source/artifact-bound evidence in the
existing bounded workspaces. Historical toolset execution is not historical OS
qualification. Keep failures and original oracles. The next boundary is the
native retained-layout/diagnostic/accessibility owner and private rule controls;
W-09/W-10 and all five complete release editions remain open.
