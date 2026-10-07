---
type: "SysPane Work Record"
title: "Conditional visibility evaluator checkpoint"
description: "Exact policy-bound comparison with explicit unresolved states and open native admission."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T22:51:02.675487+00:00"}
sp_id: "SP-VISIBILITY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-VISIBILITY", "SP-RUNTIME-OBSERVATION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Conditional visibility evaluator checkpoint

Source baseline: `10dd7f9c51208fa7c863200f7ced19f964c4e3b3`. The
[package](packages/w-09-visibility.md), new standalone schema, 38 comparison
examples, 21 state examples and test runner were frozen before production changes.
Existing scene/command schemas and their original fixture bytes remain unchanged.

## Implemented boundary

`scene::project_visibility` evaluates one bounded singleton binding and typed
comparison through the existing policy-bound borrow. It distinguishes shown/hidden
from pending, empty, denied, unsupported, ambiguous, invalid, capacity, lost lease,
unavailable, stale, unit mismatch and type mismatch. A false comparison is the only
way a valid rule returns hidden. Missing or failed input cannot conceal itself by
being treated as false, and ne does not turn a type mismatch into true.

The existing exact numeric comparator is shared privately with binding selection;
its arithmetic is unchanged. Examples distinguish adjacent integers above 2^53,
the uint64 ceiling, signed minima, finite binary64 extremes, fractions and negative
zero. Units match exactly. Text equality does not normalize or fold case. No raw
value or identifier is returned; the derived decision remains operational data
under the synchronous borrow. Revocation, regrant, fresh attachment, producer epoch
replacement, unknown clock and active/retained lease states use existing owners.

The canonical visibility 0.1 schema is embedded through the current authored schema
generator and exposed through validate_visibility_document. One singleton selector,
direct pin, persistent pin or unresolved legacy pin is allowed. Collections, unknown
properties, nonfinite literals, coercion, text ordering and unsupported unit syntax
reject before projection. The existing binding budgets remain authoritative.

## Executed checks and preserved failures

All 24 affected visibility/binding/composition checks pass on Linux GCC13, Windows
GCC15 and v141_xp. Complete non-native suites pass 317, 314 and 311 respectively,
including the new checks. This is execution on development hosts; v141_xp does not
establish XP or other historical Windows qualification.

All fifteen existing native rendering checks pass, covering settings, inspector,
text, images, charts, tables and disclosure erasure. These regressions do not
exercise conditional native widgets, which remain unimplemented.

Original attempts are retained. The first Linux build omitted the schema-generator
registration; the next rejected a misleadingly indented test statement. v141_xp
rejected reused local variable names, then exposed an implicit JSON initializer
producing an object where the test fixture needed an array. Explicit array creation
repairs that fixture construction. The original fixed schema, comparison/state
inputs and expected outcomes remain unchanged. Test-runner changes are limited to
the line split and explicit container construction. The package's provisional
generated timestamp was corrected to its actual preimplementation freeze time;
the frozen original and correction record are retained, with no contract-body change.

Records: `build-support/evidence/w-09-visibility-attempts.json`,
`w-09-visibility-native-index.json`, `w-09-visibility-verification.json`,
`w-09-visibility-staging.json` and `build-support/evidence/visibility-handoff.json`.
They bind original inputs, exact source archives, commands, logs and artifact
identities. The workspace maximum is unchanged. Cleanup verified twelve duplicate
native folders against the prior commit before reclaiming 345,440,527 file bytes.
The native rendering launch reserves its separately measured 400 MiB growth.

## Required continuation

Admit rules through a new scene version and explicitly negotiated command/capability
without changing old schemas. Cover content selection, coherent persistence,
replay/reconciliation, scene promotion, lock protection and atomic editor history.
Then implement native private condition input and renderer ownership, including
retained layout space, hidden group/child composition, unresolved diagnostics,
mandatory status outside conditions, and policy-driven pixel/accessibility erasure.
Prepare independent expected scenes and pixels before that implementation.

This checkpoint implements a shared prerequisite. Existing scenes cannot enable
conditional visibility, and the existing native tests are regression evidence only.
W-09/W-10, typography, clipboard/recovery drafts, installed ownership, other adapters,
historical laboratories and all five complete editions remain open. Historical
accessibility timeout causes are still unexplained. No release or privileged
operation is authorized by this checkpoint.
