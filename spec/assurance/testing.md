---
type: "SysPane Specification"
title: "Testing and evidence model"
description: "Distinguish planned tests, executed checks and release acceptance."
tags: ["assurance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-TESTING"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AUTHORITY", "SP-PROTOCOL"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-05T19:48:29+11:00", "scope": "Implementation closure review; no native execution or human review attested"}
---

# Testing and evidence model

## Test layers

Use deterministic unit tests for model/scheduling/transactions/layout, contract tests for schemas/protocols, replay tests for event histories, fault tests for failures and fuzz tests for parsers. Native integration tests exercise actual OS APIs. Desktop tests observe pixels and input externally. Accessibility and usability require their own evidence.

The catalog in `assurance/tests.json` is a plan. Its `execution` fields initially say `not_run`. The Python tests shipped here validate the specification tooling, graph and example contracts, not the SysPane native application. These scopes must remain explicit in every status page.

## Evidence envelope

A result identifies test ID and oracle version, source/build artifact, toolchain and dependencies, environment profile, configuration, stimulus, observed result, timestamps/duration, logs/artifact hashes and limitations. Outcomes include pass, fail, not_run, blocked and inconclusive. Missing hardware or capture is not a pass.

Bind evidence to the exact integrated candidate when claiming release readiness. Reusing component evidence requires matching relevant dependency inputs and an explicit justification. A documentation-only change need not invalidate unrelated native tests; a host/driver/oracle change may do so even when collector code is unchanged.

## Independence

A test runner must not trust an application's self-reported visibility or performance alone. Independent oracles can inspect window trees, native APIs and external capture. A review agent cannot edit the oracle/threshold and then call the same candidate independently verified. Test changes receive their own review and version.

## Determinism

Inject clocks, sources and failures. Use explicit seeds and retain failing minimized cases. Repeat synthetic tests on portable core builds with different compilers. Pixel tests have platform-specific tolerances; compare state/geometry invariants across native text engines. Timing tests distinguish source latency, notification delay, collection delay and visible presentation.

## Completion policy

A package reaches the implemented gate when its required outputs exist and mandatory executable implementation checks ran and passed, with source-bound evidence and an authorized integration decision. A blocked mandatory implementation check leaves that gate incomplete. Missing native qualification can remain separately blocked while code is implemented on an identified development profile. A release additionally requires all mandatory profile gates. Untested future profiles remain unqualified; they do not block unrelated development but cannot appear in the release support claim.

[Work-package closure](../delivery/work-packages.md) distinguishes investigation,
implementation, qualification and release gates. Parent test families remain plans;
completed packages link concrete case bindings and actual results. The initial
[acceptance traces](acceptance-traces.md) specify model, request-budget, persistence
and cold-start cases. None is an executed native result in this revision.

## October acceptance expansion

The catalogs add scene/selector semantics, descriptor consistency, resolution,
persistence, leases/recovery, role privacy, target/artifact identity, setup ownership,
screensaver lifecycle and result-buffer retrieval. Tool tests and fixtures execute
only specification logic; catalogued product tests remain `not_run`.

Evidence keys include source/generated inputs, dependencies, test code and oracle,
toolchain, platform/driver/display/session, policy and package bytes. Reuse only
unchanged relevant inputs or a recorded reviewed equivalence; never edit old evidence
to promote a new artifact. Qualify the final selected package independently. Missing
labs block affected claims, not unrelated deterministic work or another native profile.
