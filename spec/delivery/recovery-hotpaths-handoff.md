---
type: "SysPane Work Record"
title: "Compiled authored-schema validation handoff"
description: "Frozen pre-change equivalence, reduced schema navigation cost and remaining GTK qualification failures."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:35:52.762922+00:00"}
sp_id: "SP-RECOVERY-HOTPATHS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-RECOVERY-HOTPATHS", "SP-RECOVERY-LIMITS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Compiled authored-schema validation handoff

The validator now compiles navigation of the finite trusted schema set into one
immutable graph. Stable owned nodes resolve references, property names, bounds,
types and combinators before publication. Thread-safe initialization precedes use;
the original evaluation depth bound remains. Constant and regex references point
only into immutable trusted schemas. No authored value, policy, authority, digest
or validation result is retained. JSON round trips, byte limits, matching order,
structural/semantic checks and error codes remain required.

Before replacing the evaluator, the fixed corpus exercised the original public
APIs on Linux GCC 13, Windows GCC 15 and v141_xp. All three produced identical
results for 5823 cases across 81 fixture groups. Expected results in the repository's
`tests/configuration/schema-equivalence.json` identify the original source and binary
hashes. Full input/output, executables and
source archives are preserved locally through the [checkpoint](checkpoints/recovery-hotpaths.json).
The ordinary runner only compares results; it cannot regenerate expectations.
Equivalence supplements independent fixtures and semantic acceptance tests. It does
not prove correctness by itself or turn a partial document API into full product validation.

All 320 selected checks pass on each of the three toolchains (960 total), including
the frozen equivalence corpus on each. Seven Linux native families pass all 83
named cases: maximum backend inputs, installed recovery/editor/settings, frontend
recovery, preparation and recovery controls. Both historical PE checks pass.
The initial warning-as-error build failure is retained with its enum typing fix.
Profile revisions are Linux 58, Windows GCC 35 and v141_xp 26. These development
results do not qualify historical native runtimes or any complete desktop edition.

## Remaining GUI gate

The unchanged installed GTK qualification records 3 passing and 4 failing
cases. Production recovery remains disabled. The per-sample limit is still 100 ms;
no input, rendering expectation, erasure rule or deadline was relaxed.

| Case | Outcome | Maximum tick work (ms) | Maximum excess gap (ms) |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 532.5 | 584.5 |
| MAX-SCENE | fail | 237.9 | 232.2 |
| MAX-RECORD | fail | 245.7 | 223.8 |
| MAX-COMMAND-REJECT | pass | 34.2 | 6.7 |
| OVER-RECORD-REJECT | pass | 32.5 | 7.5 |
| CLOSE-PREPARING | pass | 33.6 | 4.3 |
| POLICY | fail | 40.2 | 190.7 |

MAX-WIDGETS, MAX-SCENE and MAX-RECORD completed the exact Restore, capture, Undo,
Redo, Apply and accepted-draft retirement assertions before failing timing. POLICY
erased in about 130 ms within the 200 ms bound, then failed ordinary loop timing.
The transient insensitive Apply button was not reproduced in this run; its earlier
failure remains unexplained and preserved.

All 28 observed native children exited without forced native-child teardown.
Failed observers may terminate their owned frontend during cleanup; this is not
a clean-close claim for failed cases. Preserve the earlier controller replacement,
transient Apply state and timeout observations. A later successful semantic trace
does not explain those failures.

With other builds finished, the stage diagnostic measures MAX-WIDGETS resource
construction at 37.329 ms, binding validation at 18.504 ms, surface construction at
44.844 ms and first paint at 301.165 ms. The preceding pattern-only checkpoint
measured 93.831, 53.713, 114.137 and 364.914 ms respectively. These are individual
observations, not portable performance guarantees. The earlier diagnostic in this
change overlapped Windows build/test work and is retained separately. The maximum
text scene still returns the existing alternative-preview state; its short paint
does not prove that all text fits the display.

## Next admitted work

Implement and independently verify the bounded synchronous native text session
described by [the package](packages/w-11-recovery-hotpaths.md). Reuse font setup
only within a composition, retain exact text/pixel/layout oracles and destroy native
state before returning. Further validation or scheduling changes need explicit
ownership and invalidation contracts; do not skip validation to meet a timing limit.
Investigate the Apply/controller observations, then rerun all seven fixed GTK cases
and the original regressions. Production enablement requires complete qualification
and its own production/fixture checks. Native inspector, telemetry/desktop/provider/
lifecycle work, remaining OS adapters and all five full 0.1.0 editions remain open.
