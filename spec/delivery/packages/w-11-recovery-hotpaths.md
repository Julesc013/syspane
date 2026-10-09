---
type: "SysPane Work Package"
title: "Recovery preview validation and text setup costs"
description: "Reduce measured GUI work without relaxing validation, private-data lifetime or the frozen maximum-input oracle."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:15:00+00:00"}
sp_id: "SP-W11-RECOVERY-HOTPATHS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Recovery preview validation and text setup costs

The recorded maximum-input GTK failures remain the admission criterion. Keep the
same scenes, command/record bytes, exact results, render/layout oracles, 100 ms
samples, 200 ms erasure and native deadlines. Production recovery stays disabled
until complete qualification passes. No additional timer, worker or scheduler.

## Trusted schema compilation

The implementation may precompute navigation of the finite compiled-in schema set:
resolved references, type alternatives, property/required names, scalar bounds and
combinators. Build one immutable graph with owned stable nodes. Complete its
construction before publishing it to any validator; shared initialization is thread
safe. Reference cycles remain bounded by the existing 64-level evaluation limit.
No authored document, text, command, authority, policy, validation result or digest
is cached. Authored inputs cannot create graph nodes or regex entries.

Preserve all current matching rules and structural/semantic checks, including JSON
encoding round trips, original byte ceilings, numeric integrality and finiteness,
Unicode scalar lengths, regex-search semantics, extension names, unique items,
oneOf/anyOf/allOf, conditional branches and nested reference roots. Keep error codes
and schema identities. This is an internal representation change, not a new schema
language or a permission to skip repeated validation of a changed input.

Before replacing the evaluator, run a frozen corpus through the existing public
validation APIs and preserve the exact accepted/error results and binary identity.
The corpus includes unchanged valid/invalid repository fixtures and deterministic
missing-property, wrong-type, extra-property, boundary and nested mutations. Compare
candidate results exactly. This equivalence check supplements the independent
fixture/schema and existing transaction/editor/layout expectations; it cannot
override them. An oracle discrepancy is a contract investigation, not a changed
expected value to obtain a pass. Keep the original executable source in the evidence
archive, not as a second production evaluator or a second source tree.

The deterministic corpus is `tests/configuration/schema_equivalence.py`: supported
catalog fixtures, plus the first 32 paths of each valid document with fixed type,
missing-property, extra-property, string and numeric mutations. The streaming
test adapter admits at most 12000 cases, 1 MiB per line and 128 MiB per run; the
runner has a 180-second deadline. Freeze corpus bytes, recipe and baseline source/
binary hashes before the evaluator change. Record exact output digests by fixture
in `schema-equivalence.json`; retain full input/output locally for diagnosis.
The ordinary test command compares only; it cannot regenerate expectations.

## Optional native text setup reuse

If measurement still identifies native font setup as material, one synchronous
composition may own a native text session and reuse its font map across its text
requests. Each request still gets independent text/layout/context state, current
theme/language/scale and original pixel/glyph/size checks. Requests cannot retain a
borrowed pointer. Destroy all session state at the end of composition, including
exceptions, before returning a frame. No global/thread-local authored-text or pixel
cache, retained native layout, asynchronous delivery or policy bypass is admitted.
Keep standalone render_text behavior and compare exact pixels, extents, fonts and
diagnostics with independent existing native oracles before using the session in
the installed editor. Any broader caching or scheduling change needs its own
ownership, invalidation and erasure contract first.

## Verification and handoff

Measure the same preview stages and complete GTK loop after each material change.
Run selected schema/configuration/editor/settings/scene/protocol/component tests on
all three profiles; preserve v141 PE import/rejection checks. Run installed recovery,
editor/settings, frontend recovery, preparation and recovery controls. For text
changes also run native text/typography/scene composition and erasure oracles.
Preserve every failed attempt, transient Apply state and controller restart rather
than equating later success with an explanation. Keep generated outputs in owned
ignored roots and archive completed evidence before reclaiming duplicates.
The complete five-platform 0.1.0 release, native inspector and remaining desktop,
provider and lifecycle work remain required.
