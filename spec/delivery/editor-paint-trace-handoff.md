---
type: "SysPane Work Record"
title: "Editor native paint attribution handoff"
description: "Independent call stacks confirm full rasterization during geometry-only editor work."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:57:04.923418+00:00"}
sp_id: "SP-EDITOR-PAINT-TRACE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-EDITOR-PAINT-TRACE", "SP-PREPARED-EDITOR-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Editor native paint attribution handoff

The [independent trace](checkpoints/editor-paint-trace.json) confirms that real
Pango text painting occurs during EditorForm construction and geometry refresh
inside recovery/history callbacks, as well as during GTK drawing. The experiment
uses the same product sources and exact binaries as the prepared-editor checkpoint.
No runtime behavior, release claim or production recovery gate changes here.

## Native evidence

Three source-bound attempts retain the unchanged seven-case GUI exercise. The
first exceeded its 64-frame diagnostic unwind bound and is invalid; preserve it.
The revised probe observes direct executable calls, permits at most 256 unwound
frames and retains at most 128 distinct stacks of 32 executable frames each.
Both subsequent traces completed without overflow. Every frontend lifetime has
a completed transcript, and every observed native child exited without forced
cleanup. Raw archives remain under ignored out/; their inventories and hashes are
linked by the checkpoint. The three archives preserve 413350686 uncompressed bytes.

The final trace records these pango_cairo_show_layout call counts:

| Case | Constructor geometry | Edit-callback geometry | GTK drawing |
|---|---:|---:|---:|
| MAX-WIDGETS | 258 | 514 | 17458 |
| MAX-SCENE | 4 | 6 | 58 |
| MAX-RECORD | 4 | 6 | 60 |
| MAX-COMMAND-REJECT | 2 | 0 | 30 |
| OVER-RECORD-REJECT | 2 | 0 | 10 |
| CLOSE-PREPARING | 2 | 0 | 6 |
| POLICY | 2 | 2 | 30 |

For MAX-WIDGETS, constructor geometry covers the original two-widget editor and
the later 256-widget saved editor: 258 calls. Recovery restoration, undo and redo
account for 256 + 2 + 256 = 514 callback geometry calls. Their resolved stacks pass
through SceneSurface::compose, SceneSurface::paint, EditorForm::resolve_nodes and
preview. Construction additionally reaches EditorForm's constructor; callback
geometry reaches changed/command. GTK painting instead reaches EditorForm::draw.
Separate surface-validation raster calls are retained in the checkpoint.

Counts are not durations. Dynamic drawing counts vary with scheduling. Probe
interposition and stack unwinding perturb execution; none of these runs qualifies
responsiveness. All three preserve failures in MAX-WIDGETS, MAX-SCENE, MAX-RECORD
and POLICY, with the three rejection/closing cases passing. Existing 100 ms timing
and 200 ms private-erasure limits remain unchanged.

The decoder's three test methods pass, including 15 malformed/overflow/truncated
transcript variants. Compiler, probe, symbolizer, analyzer, transcript and fixture
identities are recorded. Product sources and binaries are unchanged, so the prior
969 portable and 130 native case results remain prior evidence; they were not
rerun for this diagnostic-only increment.

Specification generation and validation pass for 667 inventory files,
51 schemas and 183 fixtures. Integrity sealing covers 666 files.
These are specification checks, separate from native product qualification.

## Next implementation boundary

Close initial-preview readiness before changing construction. An editor may defer
its first full composition to GTK drawing only if any earlier geometry-dependent
selection, click or key explicitly resolves current geometry first. Preserve exact
intrinsic metrics, conditional visibility, field hydration, policy withdrawal,
topology changes and native error/fallback behavior. Add independently expected
native cases that drive real controls before the first draw; run them against the
current behavior before implementing the change. Do not reuse a rendered frame
across changed authority, time, telemetry, resources or topology.

Then close asynchronous history/edit preparation with exact current-owner proofs.
Moving initial painting alone cannot resolve the remaining undo/redo validation
and composition delays. Preserve the original failures and rerun ordinary GUI
qualification after each functional repair. Native inspector, desktop/telemetry
integration, other platform adapters and all five complete 0.1.0 editions remain
required. W-11 stays in progress and production recovery remains disabled.
