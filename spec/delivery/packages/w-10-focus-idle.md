---
type: "SysPane Work Package"
title: "Native editor focus and refresh fairness"
description: "Explain preserved focus failures without weakening native interaction or erasure checks."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T13:07:07Z"}
sp_id: "SP-W10-FOCUS-IDLE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-EDIT-LOCKS", "SP-EDIT-LOCKS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native editor focus and refresh fairness

Investigate the preserved large-scene Apply/Undo focus failures at 9c1757d.
Keep the existing three-second focused-state deadline, focus plus keyboard
activation, exact authored scenes, visible pixels, durable results and 200 ms
disclosure-erasure bound. A successful retry does not explain a failure.

## Bounded investigation

Distinguish actual GTK/window focus loss from delayed accessibility focus state.
Observe actual widget focus, exported ATK focused state, normal-idle progress and
periodic drawing in the same owned non-root Xvfb/D-Bus laboratory. Instrumentation
may record state; it must not force focus or retry mutations. Preserve original
failure records, the diagnostic sources, binary identities and raw observations.

The initial hypothesis is that repeated expensive preview drawing prevents GTK's
normal-idle accessibility focus work from running. Compare unchanged scheduling
against a diagnostic change to the priority of the editor's existing 40 ms refresh
source. Use the same bounded drawing workload and existing focus/activation checks
in both arms. A forced load is a diagnostic condition, not historical evidence.
Identify the actual refresh source and keep input, policy and shutdown callbacks
unchanged. If the observations do not support this hypothesis, retain them and
investigate the next supported cause rather than changing the acceptance oracle.

## Implementation and verification

The editor's own optional periodic refresh must allow pending normal-idle GTK work
to progress even when a paint takes longer than the requested refresh interval.
Input-driven drawing and immediate policy erasure retain their existing semantics.
Do not solve this by reporting focus from a success return, extending deadlines,
forcing focus repeatedly, skipping controls or suppressing preview rendering.

Scheduling priority and private callback organization are delegated choices.
Any new regression must independently demonstrate the failure on the old schedule
and the required focused state and real keyboard activation on the corrected one.
Retain the full scene, history, pixels, persistence/reconciliation and disclosure
checks. Verify bounded load and continued drawing rather than accepting a frozen
preview. Keep diagnostic injection outside ordinary product behavior.

Run the affected Linux native matrices, including the 24-case large-command
matrix, and appropriate shared checks using existing presets and workspace bounds.
Bind all claims to exact source, oracle, executable and environment identities.
Do not claim unrelated earlier focus/interface causes, all accessibility or full
performance qualification from this boundary. W-10 and all five complete editions
remain in progress; publication and privileged operations are not admitted.
