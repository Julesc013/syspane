---
type: "SysPane Handoff"
title: "Initial editor preview readiness handoff"
description: "First composition now waits for drawing or guarded earlier input; fixed timing failures remain."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T07:25:48.890502+00:00"}
sp_id: "SP-INITIAL-PREVIEW-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-INITIAL-PREVIEW", "SP-EDITOR-PAINT-TRACE-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Initial editor preview readiness handoff

The Linux editor constructs its validated surface and controls without performing
the first full preview composition. GTK drawing resolves it; any earlier admitted
input first resolves the same current geometry through the existing renderer.
Semantic preparation, resource/layout/theme validation and later editing/drawing
remain unchanged. No worker, timer, frame cache or relaxed gate was added.

The [package](packages/w-11-initial-preview.md) fixes the behavior before the code
change. The [checkpoint](checkpoints/initial-preview.json) binds exact source,
artifacts, commands, archived native observations and retained failures.

## Independent behavior checks

Nine fixed cases passed on the original runtime, then passed unchanged after the
repair. They drive real GTK controls without realizing the canvas or iterating the
main loop: tree/pointer selection, immediate arrow input, both breakpoint selection
paths, reload before input, policy withdrawal, empty click, unselected key and native
text-capacity fallback. Successful input submits the exact independently expected
scene, changing only the active layout's x by one DIP. Withdrawal exposes no private
rows/fields; fallback exposes no editable geometry. Each owner closes normally.

The current run passes 323 selected Linux portable checks and two component checks
on each Windows development profile. It also passes 220 named native cases
across the checkpoint's 19 families, plus SCENE-IMAGE. Those include prepared-owner
admission, reply lifecycle, preview refresh, layout/arrange/group/snap/containers,
visibility/locks, installed recovery/editor/settings, recovery controls, standalone
editor/image erasure and phase-observer failures. Linux profile revision is 64;
Windows profile revisions remain 37 and 28. This Linux-only implementation change
does not claim a fresh 969-check cross-platform portable run or historical OS pass.

## Native cost and remaining qualification

Independent paint tracing now records zero constructor-geometry Pango calls in
every case; MAX-WIDGETS previously recorded 258. Edit-callback geometry remains
514 calls for MAX-WIDGETS and six each for MAX-SCENE/MAX-RECORD. Drawing counts vary
with scheduling. Instrumented call counts and timings are diagnosis only.

| Phase case | Prior editor construction (ms) | Current editor construction (ms) | Current full population (ms) |
|---|---:|---:|---:|
| MAX-WIDGETS | 104.509 | 57.528 | 73.799 |
| MAX-SCENE | 78.249 | 72.529 | 88.806 |
| MAX-RECORD | 78.333 | 72.412 | 88.267 |

The unchanged ordinary GUI exercise still fails four cases:

| Case | Maximum observed work (ms) | Maximum excess delay (ms) |
|---|---:|---:|
| MAX-WIDGETS | 76.261 | 166.800 |
| MAX-SCENE | 92.262 | 176.743 |
| MAX-RECORD | 91.964 | 173.549 |
| POLICY | 35.839 | 130.530 |

The fixed limit for each timing dimension remains 100 ms. All three rejection/
closing cases pass. POLICY private erasure takes 105.288 ms against the unchanged
200 ms bound. Every observed native child exits without forced cleanup. This run
removes the remaining over-limit measured tick work, but excess delays still fail;
it does not qualify overall responsiveness or enable production recovery.

Four earlier orchestration launches stopped before any test ran because an ignored
coordinator used an incorrect editor-exit artifact filename. Their errors are retained
separately; the corrected coordinator records each actual execution before accepting
an expected failing diagnostic. Original product failures and diagnostic overflow
remain in the preceding checkpoint chain. Raw archives and machine bindings stay
under ignored out/; the unchanged active workspace limit is 8 GiB and retained
evidence is reported separately.

Specification generation and validation pass for 670 inventory files,
51 schemas and 183 fixtures. Integrity sealing covers 669 files. These are
specification checks and do not replace native product qualification.

## Next boundary

Close current-owner asynchronous history/edit preparation, including first structural
submit eligibility and native preview handoff. Bind prepared results to exact current
draft, selection/history, resources, topology and policy; retain full validation and
existing no-op/error behavior. Preserve the independent expectations and repeat the
ordinary timing/erasure qualification after a functional repair. Native inspector,
telemetry/desktop integration and all five complete 0.1.0 editions remain required.
W-11 stays in progress and production recovery remains disabled.
