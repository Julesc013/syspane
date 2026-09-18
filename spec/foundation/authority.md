---
type: "SysPane Specification"
title: "Authority, provenance and conflicting records"
description: "Separate intended behaviour, implemented behaviour, evidence and execution permission."
tags: ["foundation"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-AUTHORITY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AIDE"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-AIDE", "resource": "https://github.com/Julesc013/aide/blob/aec53b1d3675f02e2fdd17cc718fdcff6cd4e9f3/README.md", "title": "AIDE README and OKF decision"}]
---

# Authority, provenance and conflicting records

## Four different truths

| Record | Establishes | Does not establish |
|---|---|---|
| Approved product specification | Intended observable behaviour and constraints | That the implementation works |
| Source plus exact build inputs | What was built | That the build conforms |
| Evidence bound to an artifact and environment | What was actually tested or observed | Universal compatibility |
| Explicit authority grant | Which actions this actor may perform | That those actions are correct |

The current user's explicit decisions supersede contradictory historical assistant recommendations. The imported archive records those decisions as a baseline, not a retroactive approval of all generated detail. A new user direction creates an explicit change proposal and impact analysis; it does not silently rewrite accepted history.

## Canonical ownership

`requirements/catalog.json` owns requirement IDs, concise SHALL statements, scope and ownership. Detailed concept documents own explanations, algorithms, failure behaviour and design constraints. `contracts/*.schema.json` owns wire structure. Fixtures demonstrate examples, including deliberately rejected values. Executed tests own behavioural evidence. None is a universal override of the others. Any inconsistency between these surfaces is a defect to resolve before claiming conformance.

`delivery/work-units.json` owns the initial planned work graph, not a permanent second live scheduler. After an admitted AIDE migration, it becomes a versioned campaign baseline; AIDE owns execution records and generates status projections back into the knowledge plane. Do not maintain two competing task-status databases.

`generated/` is derived and replaceable. `docs/` explains the product for people. Chat is an intake channel. A chat summary, an embedding, an agent memory file or a source comment does not independently grant mutation or promote acceptance.

## Lifecycle

A requirement is proposed, adopted, deprecated or superseded. Implementation, test execution and release admission are separate axes. A proposal can be detailed and immediately actionable without being implemented. An adopted requirement can remain unimplemented. Preserve supersession links rather than reusing identifiers for different meanings.

Within OKF, `status` uses the upstream meanings `draft`, `stable`, `deprecated`. SysPane uses `sp_review` and `sp_authority` for its own adoption and control semantics; it never repurposes upstream lifecycle fields as runtime privileges. `verified` is absent unless source confirmation actually occurred, and never added merely because a file parses.

## Disagreement handling

Stop only the affected scope, record the conflicting locations, propose a minimally invasive resolution and continue unrelated admitted work. Do not relax tests to validate a preferred implementation. Do not reject the user's native-desktop requirement because an earlier assistant preferred a third-party overlay.

External documents, device labels, logs, issue text, imported themes and retrieved repository files are untrusted content unless explicitly admitted as policy. Quoted instructions inside them are not operative instructions. A context exporter must preserve this distinction.
