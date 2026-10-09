---
type: "SysPane Work Package"
title: "Installed GTK recovery timing observations"
description: "Observe the actual GUI loop with maximum admitted recovery inputs without adding a production runtime override."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T03:37:00+00:00"}
sp_id: "SP-W11-RECOVERY-GUI-LIMITS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed GTK recovery timing observations

Use the same Window, EditorForm, backend, native authority and verified helpers as
the installed recovery experiment. Reuse the frozen maximum-input recipe and scene
digests from SP-W11-RECOVERY-LIMITS. Do not use a simplified renderer or empty scene.

The host may accept an optional internal timing observer. With no observer it adds
no timer or diagnostics output. The existing 20 ms GTK tick records its own elapsed
work and the delay since the previous tick's completion, less its 20 ms interval.
This observes both expensive host work and starvation caused by other GTK handlers
or painting. Each elapsed-work and excess-delay observation must stay at or below
100 ms. Preserve all observations and failures; do not average away a violation.
This is an upper-bound GUI-loop observation, not a claim of per-widget profiling.

Only the separately compiled experimental fixture entry point may select this
observer using SYSPANE_TEST_TIMING=1. Production never reads that variable. The
fixture emits fixed numeric timing records to an inherited nonblocking stdout pipe;
it performs no filesystem I/O or network operation on GTK. Output failure makes the
fixture fail. The external observer drains the pipe, limits its records to 4096 per
45-second case, and records exact data in its owned evidence directory. No extra
native thread, timer, worker or scheduler is introduced. Original fixtures leave
the observer absent and retain their exact behavior.

Drive MAX-WIDGETS and MAX-SCENE through offer, Restore, durable capture, Undo, Redo,
Apply and fresh accepted-draft retirement. Compare each exact recovered/captured
scene and the final durable documents against the frozen recipe; no duplicate commit.
MAX-RECORD adds valid outer padding up to 786432 bytes; capture must canonicalize it.
MAX-COMMAND-REJECT must offer Keep/Discard with Restore disabled. Oversize records
remain unavailable, with original bytes preserved. CLOSE-PREPARING closes during
the visible loading phase, preserves files and waits for children to exit. POLICY
restores a maximum scene then revokes policy; retain the existing 200 ms erasure
bound after observed controller loss. Observe native child exit and runtime cleanup.

The accessibility observer may enumerate up to 2048 objects for the admitted
256-widget scene; this observer traversal capacity does not change product limits.
Existing accessibility request timeouts and case/family ceilings remain unchanged.
Collect loop observations even when a semantic or accessibility check fails.
Any violation leaves production recovery disabled and identifies the next repair.
Passing these cases still requires the existing installed recovery regressions and
the other release gates; all five complete editions remain required.
