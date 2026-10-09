---
type: "SysPane Work Package"
title: "Immutable authored validation for native composition"
description: "Remove repeated structural validation while retaining current geometry, resource and policy checks."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T10:23:48+00:00"}
sp_id: "SP-W11-VALIDATED-AUTHORED"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-ADMISSION-INVESTIGATION", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Immutable authored validation for native composition

The retained phase diagnostic reproduces a 100665 us between-callback delay while
that callback performs only 206 us of work. It does not identify the delayed work.
The preview diagnostic measures structural/resource binding at 17532/25325 us and
surface construction at 42514/58228 us for MAX-WIDGETS/MAX-SCENE. The latter scene's
paint returns an alternative; its short paint duration is not a rendering success.
Source inspection shows duplicate scene validation during surface construction and
another full validation on every paint. Address that measured repeated work without
claiming it explains every retained failure.

## Ownership and behavior

Add configuration::ValidatedAuthored, an opaque owner of an actual const Authored
allocation. Construction deep-copies the supplied pair and runs the unchanged full
validate_authored against that owned copy. Neither an lvalue, a moved argument nor
an outstanding reference into the caller's JSON may mutate the snapshot. Copies
share only that immutable allocation; moves transfer it. There is no default or
caller-supplied trusted/skip-validation constructor. documents() returns const data
while an owner lives; access through a moved-from owner throws authored.snapshot.
It proves document structure, semantics and coherent revision, not authorization.

Add overloads of scene::resolve and validate_resource_binding accepting that owner.
The raw JSON/Authored overloads retain full validation and their original error
order. The snapshot layout overload still validates every current topology and
metrics input, then runs the same complete geometry algorithm. Resource binding
still checks theme identity, required contracts, manifests and image references.
authorize_resources and all surface policy, forced-theme, capability, visibility,
source lease, text, image, pixel, erasure and lifetime checks remain unchanged.

SceneSurface construction/replacement creates one snapshot, uses it for initial
binding/layout checks and retains it for later layout. Each paint still obtains
fresh measurements, telemetry, images and text and composes fresh pixels. Retain
only the current snapshot, no revision-indexed cache. Replacement validates before
adopting the new config/snapshot together; rejection retains the previous authored
configuration and proof, with the existing clear/history invalidation behavior.
Close or failed native clearing releases the snapshot as well as current state.

## Limits and authority

Existing 16384-byte settings, 262144-byte scene, 256-widget and all geometry/render
budgets remain fixed. Each live surface adds at most one deep copy of this bounded
authored pair (JSON heap overhead is additional); replacement can temporarily hold
the previous and candidate snapshots. Copies of the proof share storage. No frame,
telemetry, policy decision or resource permission is cached by this mechanism.
Private allocation and helper organization are delegated engineering choices.
No protocol/document version changes or production recovery admission are authorized
by this repair. Keep the existing admission gate closed pending its own checks.

## Fixed verification and completion

Freeze tests/scene/validated_authored_tests.cpp before product changes. First run its
reference adapter against existing full-validation APIs; then enable only the test
adapter definition to exercise the new owner. Literal existing geometry fixtures
remain the independent expected outputs. Cover copy/move and retained mutable input
references, malformed/mixed/oversize input, current topology/metrics refusal, changed
theme binding and current policy denial. Do not derive expected geometry from either
implementation. No existing acceptance expectation or timing limit may change.

Use ordinary configure/build commands on linux-x64-gcc13, windows-x64-gcc15 and
windows-x86-v141-xp. Run scene.AUTHORED-SNAPSHOT and all configuration, scene, editor,
settings, protocol and composition checks on those profiles, plus legacy artifact
checks. Run native surface/content/pixel/erasure, editor geometry/refresh/history,
recovery ownership/preparation/backend/limits, installed settings/editor/recovery
and admitted-entry regressions. Run the existing preview-cost diagnostic once for
comparison, then one unchanged ordinary RECOVERY-GUI-LIMITS attempt. A failure is
retained and requires evidence-led repair, not unchanged retries until success.

Record commands, source archive, artifact/environment identities and full failures
under owned ignored out/ roots within the current active-output budget. Completion
of this repair requires behavioral regressions to pass and measured removal of the
repeated validation cost. GUI qualification and ordinary production admission remain
separate gates. All five complete desktop editions remain the release objective.
