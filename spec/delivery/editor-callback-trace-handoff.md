---
type: "SysPane Handoff"
title: "Editor callback timing handoff"
description: "Source-resolved GTK action and timer spans with preserved ordinary qualification failure."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T11:16:16+00:00"}
sp_id: "SP-EDITOR-CALLBACK-TRACE-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-EDITOR-CALLBACK-TRACE", "SP-VALIDATED-AUTHORED-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Editor callback timing handoff

The [bounded callback experiment](packages/w-11-editor-callback-trace.md) now
observes executable-owned GTK signal handlers and GLib timers without modifying
product binaries. All seven instrumented GUI cases pass; they do not supersede the
ordinary MAX-RECORD failure recorded in the [preceding handoff](validated-authored-handoff.md).
Production recovery/history admission remains disabled. W-11 and all five complete
SysPane 0.1.0 release editions remain unfinished.

The [checkpoint](checkpoints/editor-callback-trace.json) records exact source
archives, compiler/probe/runtime identities, artifacts, original outcomes and
callback/gap summaries. All 52 recorded product artifacts equal those in the prior
failed ordinary GUI attempt. Product source, original seven case definitions,
recipe, exact document checks and 100 ms/200 ms limits are unchanged.

## Diagnostic validity

A standalone GObject/timer fixture first compares normal and instrumented behavior
against two fixed output lines and literal assertions. Its 17 callbacks include
four nested emissions and five timer invocations. Argument/return values, swapped
and after order, block/unblock, function/data disconnection, self-disconnection,
timer priority, continue/remove/cancel and exactly-once destruction agree.

Four decoder checks cover valid and empty helper transcripts, malformed/bounded
records, parent/ordinal/lifetime consistency, interval union, timer-stream coverage
and independent clock disagreement. Two initial decoder development failures and
one clock-assumption preflight rejection remain preserved. The latter failed
before native cases began; only one instrumented seven-case campaign was run.

That campaign produced 2798 complete callback records across fourteen observed
frontend lifetimes. The 20 ms timer ordinals correspond one-to-one with the original
per-process timing streams. All executable callback offsets resolve against the
unchanged fixture. Nested spans are unioned when accounting for gaps. Uncovered
time remains explicit; toolkit-owned registrations and OS scheduling are outside
the probe's coverage, as are registrations through g_signal_connect_object or
pre-created closures. Current source uses timer-ID lookup/removal; the wrapper
does not preserve GLib data-based source lookup, which these consumers do not use.
Interposition also changes marshalling overhead, so these
measurements are diagnostic only.

Thread CPU exceeded wall time in 2476 records. The initial short fixture disagreement
was 9500 ns CPU versus 9180 ns wall; larger callbacks also disagree materially.
Both raw clocks are retained with an explicit discrepancy field. Do not derive CPU
utilization, blocked duration or a scheduling cause from their difference in this
laboratory. The root cause of that clock disagreement has not been established.

## Observed work

These are individual instrumented observations, not a latency distribution or a
reproduction of the preceding ordinary failure.

| Case and callback | Wall time (ms) | Source boundary |
|---|---:|---|
| MAX-WIDGETS recovery restore | 73.446 | editor button handler, line 455 |
| MAX-WIDGETS editor timer | 68.501 | 40 ms form callback, line 520 |
| MAX-WIDGETS native draw | 45.530 | canvas draw handler, line 502 |
| MAX-SCENE Apply | 83.552 | editor button handler, line 455 |
| MAX-RECORD Apply | 90.053 | editor button handler, line 455 |
| MAX-RECORD recovery restore | 74.564 | editor button handler, line 455 |

These locations refer to source/interfaces/editor_form_linux.cpp in source base
8826789e3baa1b75fd33d575f235427e916ecd7f. Action names come from a fixed whitelist
of the existing editor-action identifiers, not an inference from callback address.

MAX-RECORD's longest gap spans 110.798280 ms between frontend timer wrappers.
Apply occupies 90.053100 ms within it. The union of all observed callbacks in that
gap occupies 92.021850 ms, leaving 18.776430 ms outside observed callbacks. The
original observer reports 90800 us excess delay and 263 us work on the next tick;
the wrapper-derived excess differs by 1720 ns because the wrapper also surrounds
observer overhead. This identifies actual long synchronous Apply work. It does
not establish the cause of the earlier 143870 us failure, which was not reproduced.

The instrumented policy case observed erasure after 67.039 ms. Retain its result
without using it to replace ordinary erasure qualification or any earlier failure.

## Next boundary

Close asynchronous Apply preparation through the existing worker and current-owner
adoption. First isolate the measured handler's ready/recovery submission, command
construction/full validation and backend enqueue costs so the repair targets the
actual work. Preserve current policy, request/revision identity, full command and
resource validation, durable acknowledgement and unknown-outcome reconciliation.
Keep restore, 40 ms adoption/preview work and drawing visible when evaluating the
repair. Rerun ordinary GUI qualification only after a measured implementation change.

The complete native attempt was archived and every file verified before its owned
duplicate directory was pruned. Raw traces, source archives and all five probe
build/self-test records remain in ignored out/evidence/. Earlier failed self-test
Python source digests were recorded without complete source snapshots; the two
campaign attempts have full source archives. Shared diagnostics live in tests/;
no new root directory, product override or release authority is introduced.

Specification validation passes for 692 files, 362 concepts, 131 requirements,
61 planned acceptance definitions and 49 work units. All 51 schemas/183 fixtures
pass; generated projections and 691 sealed entries agree. The specification-tool
suite reports 62 tests: 60 passed and two skipped for Windows symlink privileges.
All four decoder checks also pass on Windows. These checks do not qualify product
behavior or replace the native observations above.
