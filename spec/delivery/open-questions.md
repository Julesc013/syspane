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
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Open decisions, risks and resolving experiments

## Mandatory unresolved admissions

| ID | Question or risk | Resolving evidence | Blocks |
|---|---|---|---|
| R-01 | XP/7 wallpaper-preserving behind-icon host | native temporal/input tests of actual candidates | XP/7 Desktop claim |
| R-02 | Current Explorer tree/private host drift | exact-build host diagnostics and external reveal tests | affected Windows Desktop profile |
| R-03 | GNOME/Wayland/Plasma layering and bridge rules | protocol/extension review and native host experiment | affected Linux Desktop profile |
| R-04 | Older OS X toolchain/dependency floor | pinned build/import/run evidence | claimed older OS X minimum |
| R-05 | XP-compatible shared C++ subset | v141_xp build/link/host checks now pass; exact XP guest runtime proof remains required | shared binary composition on XP |
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

## October gates with resolving work

| ID | Question | Resolving work/evidence | Blocks |
|---|---|---|---|
| R-14 | Filesystem commit and crash recovery | W-08; staged/pointer/activation interruption tests | Durable settings claims |
| R-15 | USK public binding and per-operation qualification | W-32; inspect pinned SDK/contracts and consumer harness | Managed apply |
| R-16 | Saver host and disclosure | W-31; native preview/config/fullscreen and lock tests | Saver package |
| R-17 | Full theme tokens and expression AST | W-09/W-33; versioned schemas and bounded evaluation fixtures | Rich theme/expression features |
| R-18 | Controlled public contract namespace and stable ABI | W-19/W-33; aliases and independent consumers | Stable public SDK |
| R-19 | Online update metadata trust | W-39; pinned design and rotation/expiry/rollback tests | Automatic acquisition |
| R-20 | Release/component/setup machine manifests | W-01/W-26/W-32; actual build/provider closure | Publishable packages |

R-01..R-06 resolve in their platform/profile work; R-07/R-11 in W-38; R-08 in W-16;
R-09 in W-22; R-10/R-12 in per-profile W-40..W-43; R-13 in W-34..W-37. These are
owned planned experiments, not inferred outcomes. The minimum October metadata and
fixture work does not complete native algorithms or every later schema.
