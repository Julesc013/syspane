---
type: "SysPane Risk register"
title: "Open decisions, risks and resolving experiments"
description: "Keep unresolved choices discoverable without blocking unrelated work."
tags: ["delivery"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-RISKS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-ROADMAP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Open decisions, risks and resolving experiments

## Mandatory unresolved admissions

| ID | Question or risk | Resolving evidence | Blocks |
|---|---|---|---|
| R-01 | XP/7 wallpaper-preserving behind-icon host | native temporal/input tests of actual candidates | XP/7 Desktop claim |
| R-02 | Current Explorer tree/private host drift | exact-build host diagnostics and external reveal tests | affected Windows Desktop profile |
| R-03 | GNOME/Wayland/Plasma layering and bridge rules | protocol/extension review and native host experiment | affected Linux Desktop profile |
| R-04 | Older OS X toolchain/dependency floor | pinned build/import/run evidence | claimed older OS X minimum |
| R-05 | XP-compatible shared C++ subset | build/link/runtime proof with pinned compiler/CRT | shared binary composition on XP |
| R-06 | Windows RT authorized execution | legitimate deployment feasibility review | any RT native product claim |
| R-07 | License and contribution/IP policy | owner decision, dependency review | public code licensing/distribution |
| R-08 | Durable journal backend/flush policy | corruption/crash and write-load tests | durable-history guarantees |
| R-09 | AIDE contract integration | pinned schema inspection, consumer adapter conformance | live AIDE operation claims |
| R-10 | Exact performance/resource thresholds | baseline measurements on named lab profiles | performance marketing and release budget |
| R-11 | Native package signing/notarization availability | authorized pipeline and credentials policy | signed public distribution |
| R-12 | UI/property coverage and native accessibility | generated coverage plus executed accessibility tasks | complete native-GUI claim |
| R-13 | Field-specific notification gaps | real changes incl DNS/protocol-unbound NICs | one-second freshness for affected fields |

## Handling

Each resolving experiment is a work unit with bounded resources and an oracle. Record the exact failed candidate, changed assumption and follow-up. Do not invent a compiler flag, shell API, capability or future provider because a table has a blank cell.

Known uncertainty is not a reason to remove the user's requirement. A platform can remain a planned profile while useful native inspector/collector work proceeds. Record feature-specific status instead of cancelling the whole product or pretending a conventional window passes.

## Review cadence

Revisit a risk when its dependency changes: OS update, new toolchain, new AIDE contract, new provider or observed failure. Avoid arbitrary recurring full re-research. Source references contain dates and scope; mark stale source facts without changing stable product intent automatically.
