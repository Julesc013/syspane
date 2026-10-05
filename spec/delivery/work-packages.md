---
type: "SysPane Specification"
title: "Implementation work-package closure"
description: "Make each admitted package implementable, verifiable and resumable from the repository."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T19:48:29+11:00"}
sp_id: "SP-WORK-PACKAGES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AUTHORITY", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-READINESS-2026-10-05", "resource": "User-supplied readiness review, 2026-10-05", "title": "Implementation closure review"}]
---

# Implementation work-package closure

The repository must let a fresh implementer identify the next admitted package,
build it, check observable behaviour and leave a source-bound handoff. Document
length is not the acceptance criterion. No specification can pre-qualify code or
replace the native experiments that determine whether a platform adapter works.

[work-units.json](work-units.json) remains the campaign index and dependency graph.
A row may link a detailed package through `package`, a path relative to `spec/`.
Such a document refines that row; it is not a second roadmap or live scheduler.
The first detailed package is [W-01](packages/w-01-foundation.md).

## Required package contents

| Element | Required information before the relevant implementation begins |
|---|---|
| Scope | Work ID, objective, externally observable result, non-goals, owned source paths and prerequisite evidence |
| Inputs | Exact contract versions, required capabilities, target/profile identity and dependency identities |
| Interfaces | Typed inputs/outputs; mutable-state owner; sender/receiver roles where relevant; error and lifetime rules |
| Behaviour | Normal, invalid, interrupted, shutdown and recovery cases with exact expected results |
| Limits | Relevant size, concurrency, storage, timing, retry and resource exhaustion rules; distinguish fixed limits from measured budgets |
| Decisions | Established requirements, delegated implementation choices, experiments and decisions reserved to the owner |
| Execution | Commands from a stated working directory, required tools/environment, expected artifacts and exit semantics |
| Completion | Mandatory case IDs, runnable bindings, evidence identity, remaining limitations and next dependency-ready step |

A missing item blocks only the implementation that depends on it. A bounded
experiment can precede interface closure when it has a question, method, inputs,
limits, failure recovery and decision criterion. Record its result before selecting
the dependent design. Do not conceal uncertainty behind an invented build profile.

## Decision authority

| Class | Implementer action |
|---|---|
| Established product contract | Preserve its observable meaning; report a conflict before changing the affected behaviour |
| Delegated engineering choice | Choose private decomposition, algorithms and test organisation within the contract; record material rationale and continue |
| Experiment-dependent choice | Run the admitted bounded experiment, preserve failure evidence, then select or propose the dependent contract change |
| Reserved authority | Obtain the missing product, license, privileged-operation, signing or publication decision before that action |

An explicit user instruction can admit a bounded implementation package without
an AIDE grant. Do not request the same authority again or invent an AIDE prerequisite.
Record the actual instruction and scope; quoted recommendations alone do not grant
execution authority. A new ambiguity in private code organisation is normally a
delegated choice, not a reason to stop the campaign.

## Distinct gates

| Gate | Evidence required |
|---|---|
| Ready to investigate | Bounded question, method, environment, recovery and decision criterion; applicable authority present |
| Ready to implement | Relevant behaviour, interfaces, failures, limits and acceptance closed; prerequisite evidence and applicable authority present |
| Implemented | Required code/artifacts exist; mandatory executable implementation checks ran and passed on the named development profile |
| Qualified | All mandatory capability tests passed on the named target with identified artifact and independent oracles where required |
| Releasable | Qualified payload plus package/lifecycle evidence, license/support decisions and applicable release authority |

The gates are facts recorded in the work handoff, not interchangeable labels. A
missing lab can leave code implemented and target qualification blocked. A skipped,
failed, blocked or null-runner mandatory implementation check prevents the
implemented gate. A completed investigation may have a failed candidate as its
useful result; it must not become an implemented or qualified claim.

Campaign `status` is scheduling information only. Before treating a prerequisite
as satisfied, identify the required gate and linked evidence for its actual
outputs. If only part of a unit is delivered, record that boundary and keep the
remaining work visible; do not use `complete` to release dependent work on absent
outputs. The current `work --ready` command checks graph status, not these gates.

## Acceptance and handoff

Keep existing test IDs as parent families. Give concrete cases stable child IDs,
fixed inputs and expected results, then bind them to test source and a command.
Family definitions in [tests.json](../assurance/tests.json) remain plans; their
`execution: not_run` is not the mutable result of the latest run. A completed
package supplies non-null executable bindings for every mandatory executable case
in its linked handoff/evidence. A future family may retain a null command while
its implementation remains pending.

Use the [handoff envelope](../contracts/handoff.schema.json) for the summary and
link a detailed record when it cannot express case bindings, gate states or
provenance. Record source commit plus any dirty input manifest, generated-input
hashes, test/oracle revision, tool/dependency identities, artifact hashes,
environment, exact command, exit code, actual outcome and logs. Preserve original
failures. A corrected oracle is a separately identified contract change; rerunning
against a convenient new expectation does not retroactively erase the failure.

Include delegated choices, unresolved conflicts, blocked claims, authority used
and the next step. Store evidence through the existing repository/AIDE ownership
rules; do not start a second execution database. Keep ordinary commands usable
without AIDE. Validate resumption using the [cold-start exercise](../assurance/acceptance-traces.md#cold-start-exercise).

## Finite release closure

Before release integration, populate a release scope record with the exact edition,
target profile revisions, required capabilities, supported document versions,
package forms, mandatory case bindings, lifecycle/support owners and explicit
deferrals linked to work IDs. An empty or family-wide profile is not a finish line.
Changing scope requires a recorded decision; it must not happen by dropping a
failing test or relabelling a conventional window as a persistent desktop host.

The first complete desktop edition includes real telemetry, native settings,
direct editing, persistence and recovery, plus the external desktop oracle.
Experimental console/model smoke artifacts are useful development results and
must retain that narrower description. Other platforms and future features stay
in the product direction without making each individual release unbounded.
