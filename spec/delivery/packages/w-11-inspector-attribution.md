---
type: "SysPane Work Package"
title: "Inspector admission, painting and presentation attribution"
description: "Separate nested native inspector costs before selecting the remaining maximum-table repair."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T06:25:00+00:00"}
sp_id: "SP-W11-INSPECTOR-ATTRIBUTION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSPECTOR-LIVE-TABLES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector admission, painting and presentation attribution

The current maximum-table candidate fails ordinary navigation at 109.450 ms and
the complete phase run reaches 183.445 ms. Continue W-11 with the same frozen
seven cases, profile, binaries built with the ordinary Debug profile, 100-ms GUI
and 200-ms erasure bounds. No acceptance or resource limit changes.

## Bounded experiment

Question: how much synchronous time is spent admitting delivery, painting the
SceneSurface and projecting/reconciling its native GTK rows? Add an optional
per-call observer to SceneInspector deliver/refresh, borrowed only until that
synchronous operation returns. It receives phase, monotonic microseconds and
completion; it receives no payload and retains no callback. All work still runs
on the owning GTK thread, with the original batching and error handling.

Admission wraps the existing action (attachment/full/heartbeat for delivery).
Painting wraps SceneSurface::paint including its sink. Presentation wraps that
sink's entire native presentation, including semantic-row projection and GTK
reconciliation. Thus painting includes presentation; they must not be summed.
The difference estimates non-presentation painting, including measurement overhead.
The whole frontend inspector span still includes admission, painting and teardown.
Do not interpret these wall durations as CPU utilization.

The ordinary frontend passes no observer. The existing compiled diagnostic
composition forwards spans only for the one periodic inspector deliver/refresh
inside its existing outer phase. Construction, topology replacement and policy
operations keep their current outer spans; they must not create duplicate
phase IDs within a tick. Append IDs 14 admission, 15 paint and 16 presentation to
the current journal, preserving IDs 1..13, its 8192-record bound, complete lifetime
matching and refusal behavior. Keep the invalid-ID decoder witness at 17 and
positively verify the added names.

An observer refusing or throwing disables further observation for that operation,
fails with inspector.phase_observer and performs normal inspector closure/erasure.
Nested exception unwinding must not invoke the failed observer again. Forwarding
failure also disables the frontend phase observer and triggers its existing
supervised shutdown. No environment handling is added to product code.

Before attributing performance, test native successful span ordering/containment,
per-call lifetime, and refusal/throw at every span after a populated tree. Require
the original information, explicit closed status and empty native payload after
failure. Run the existing decoder and native inspector cases with those assertions.
Then run the unchanged live-table phase family and preserve its whole-tick result,
including any failure. Record complete journals, exact sources, artifacts and
environment. Missing/incomplete journals are failed diagnostics, never estimates.

The largest measured contribution selects the next repair boundary. Before any
asynchronous composition, close current policy/profile/topology adoption,
clear-before-paint, chart continuity, cancellation, queue/memory limits and shutdown
ownership. This experiment alone does not qualify maximum tables, mixed charts,
human usability, desktop visibility or any complete release edition.
