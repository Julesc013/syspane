---
type: "SysPane Work Record"
title: "Composition-scoped native text handoff"
description: "Exact standalone/session rendering evidence, lower paint cost and remaining recovery qualification."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:56:50.472455+00:00"}
sp_id: "SP-TEXT-SESSION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-TEXT-SESSION", "SP-RECOVERY-HOTPATHS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Composition-scoped native text handoff

Linux composition now owns one stack TextSession and lazily creates one native
font map. Plain text, semantic blocks, tables, chart labels and visibility diagnostics
borrow it only for synchronous calls. Every request still validates its inputs and
owns a fresh context, font description and layout. Image rasters keep their existing
path. The session retains no request/theme/text/layout/raster and is destroyed on
success or exception before frame publication. There is no process/thread-local
session, extra production worker or changed policy/erasure path.

TextSession is noncopyable, nonmovable and confined to its creating thread. A
wrong-thread call fails with text.owner before touching native state. Standalone
render_text creates its own independent session. Native/allocation errors keep
their original mapping; invalid requests cannot contaminate later valid results.

## Independent evidence

Before the backend changed, 30 requests (20 accepted, 10 rejected) ran through the
original standalone TextProbe. The repository's
`tests/scene/text-session-expectations.json` pins original metadata, exact pixel
digests, errors, executable/source identity, recipe and font runtime. Raw pixels,
inputs, outputs, binary and source archives are retained locally through the
[checkpoint](checkpoints/text-session.json). A fresh checkout uses the compact
expectations and declared font runtime; historical archives are not test dependencies.

The candidate matches all 30 standalone results and three shared-session orders,
each with a seed request followed by wrong-thread refusal and same-thread reuse:
123 exact result comparisons in total. Rejections produce no partial output file.
This test supplements the unchanged independent native text and typography oracles
(27 and 11 named cases), which passed before composition integration. The integrated
build uses the same tested TextProbe binary. The test-only thread is joined inside
that probe; the product adds no scheduler or thread.

After integration, all 12 native scene/role/visibility/table/chart/image and erasure
checks pass. Seven recovery families pass all 83 named cases. All 320 selected
portable checks pass on each of Linux GCC 13, Windows GCC 15 and v141_xp, and both
historical PE checks pass. Linux profile revision is 59; Windows revisions remain
35 and 26 because their component inputs are unchanged. This Linux backend work
does not establish historical runtime compatibility or any complete release edition.

## Measured result and open gate

With other builds/tests finished, MAX-WIDGETS first paint measures 52.939 ms,
compared with 301.165 ms at the preceding compiled-schema checkpoint. Resource
preparation, binding validation and surface construction measure 38.052, 19.330
and 45.817 ms. This is one observed run, not a cross-machine guarantee or proof of
the whole GUI loop. The maximum-text scene still returns its existing alternative
preview; a short failing-layout paint does not mean all text fits that display.

The full unchanged GTK family records 3 passing and 4 failing cases.
Production recovery remains disabled. Every tick-work and excess-gap sample still
has a 100 ms bound; inputs, renderer expectations and deadlines were not weakened.

| Case | Outcome | Maximum tick work (ms) | Maximum excess gap (ms) |
|---|---|---:|---:|
| MAX-WIDGETS | fail | 209.8 | 224.2 |
| MAX-SCENE | fail | 238.1 | 250.5 |
| MAX-RECORD | fail | 218.8 | 226.6 |
| MAX-COMMAND-REJECT | pass | 31.5 | 8.0 |
| OVER-RECORD-REJECT | pass | 32.2 | 7.8 |
| CLOSE-PREPARING | pass | 32.1 | 3.1 |
| POLICY | fail | 38.3 | 220.0 |

The following cases completed exact Restore, capture, Undo, Redo, Apply and
accepted-draft retirement: MAX-WIDGETS, MAX-SCENE, MAX-RECORD.
POLICY recorded 123.374 ms for erasure against its unchanged 200 ms limit.

All 30 observed native children exited without forced native-child cleanup.
Failed observers may terminate their owned frontend; this is not a clean-close
claim for failed cases. Earlier transient insensitive Apply, controller replacement
and native timeout failures remain preserved; later success does not explain them.

## Next admitted boundary

Measure the remaining synchronous large-scene preview reconstruction, validation
and native-control work. Close the ownership and invalidation contract before
reusing validated resources or moving work across owners. Preserve current-policy
checks, exact pixels/layout, atomic outcomes, resource bounds and all fixed GUI
oracles. Only complete qualification and production/fixture checks permit recovery
enablement. Native inspector, full desktop/provider/lifecycle integration, remaining
OS adapters and all five complete 0.1.0 editions remain required.
