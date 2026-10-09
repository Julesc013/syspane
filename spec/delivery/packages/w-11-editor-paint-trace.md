---
type: "SysPane Work Package"
title: "Independent editor paint call trace"
description: "Resolve whether geometry-only editor work performs native rasterization before choosing a repair."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T06:48:00+00:00"}
sp_id: "SP-W11-EDITOR-PAINT-TRACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-PREPARED-EDITOR", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent editor paint call trace

The prepared-editor checkpoint preserves four fixed GTK timing failures. Source
inspection suggests that resolve_nodes renders complete native text pixels before
GTK draws them again. This is a hypothesis requiring a native trace; it does not
authorize skipping current geometry, visibility, resource or policy validation.

## Experiment and ownership

Run the unchanged seven-case installed GUI exercise using its existing packaged
fixture and original acceptance limits. A test-only Linux preload library observes
direct executable calls to pango_cairo_show_layout, delegates every call unchanged and aggregates
only executable-relative call-stack offsets and counts. Resolve those offsets
after process exit against the exact unstripped fixture binary. Record source,
compiler, library, executable and transcript hashes. The driver alone supplies
LD_PRELOAD for this experiment; no product entry point, override, API or binary
changes. Native execution remains under the admitted non-root laboratory account.

The probe retains at most 128 distinct stacks, 32 executable frames per stack and
256 unwound frames per call. Storage is fixed, synchronized and contains no text,
authored values, policy data or filesystem paths. It records first/last sequence
numbers and call counts, with no I/O while GTK runs. At normal process exit it
writes a bounded numeric transcript to inherited stderr. Overflow, invalid counts,
missing/truncated completion, duplicate process identity or unresolved product
frames invalidate diagnostic evidence; they cannot turn a product failure into
a pass. Other inherited processes may emit empty transcripts, which are retained
but do not substitute for each observed frontend lifetime.

Interposition and unwinding perturb execution. Preserve the original timing and
semantic outcomes but make no latency qualification claim from this experiment.
The unchanged ordinary GUI run remains the qualification gate. No new product
worker, timer, scheduler, authority or acceptance limit is introduced. Compile
the probe into an owned ignored out/ directory and archive complete native runs
before pruning duplicate owned records under the existing workspace budget.

The first experiment's 64-frame unwind bound overflowed on real GTK call stacks;
its diagnostic output is invalid and preserved. The revised bound above remains
finite and the probe excludes Pango calls made directly by toolkit libraries.
This changes only the diagnostic capacity, not any product or acceptance limit.

## Decision and completion

Require call stacks proving whether real native text painting occurs inside
EditorForm construction, synchronous geometry resolution, recovery/history
callbacks and GTK drawing. Count calls by exact stack and show source locations;
do not infer CPU cost from call counts or aggregate overlapping stacks as time.
If geometry requires intrinsic text metrics, a repair must preserve those exact
metrics and layout/visibility/error outcomes. Caching a rendered frame across
changed policy, telemetry, time, resources or topology is not admitted here.

Completion requires the source-bound trace, preserved original outcomes, an
explicit supported conclusion and the next implementation boundary. This package
alone changes no product behavior. Production recovery, W-11 and all five complete
0.1.0 release editions remain open.
