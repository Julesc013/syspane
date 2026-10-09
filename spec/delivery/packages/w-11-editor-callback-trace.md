---
type: "SysPane Work Package"
title: "Independent editor callback timing trace"
description: "Attribute work outside the frontend timer without changing product behavior or acceptance limits."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T11:07:24+00:00"}
sp_id: "SP-W11-EDITOR-CALLBACK-TRACE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-VALIDATED-AUTHORED", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent editor callback timing trace

The immutable-authored checkpoint preserves MAX-RECORD's 143870 us excess delay
between frontend timer callbacks. Its surrounding callbacks take less than 600 us.
The cause remains unproven. Before another repair, observe executable-owned GTK
signal callbacks and GLib timers, including Apply, recovery, history and drawing.

## Bounded experiment

Use a test-only Linux preload library with the unchanged seven-case installed GUI
exercise, packaged fixture and original semantic, erasure and timing oracles.
Intercept only direct executable registrations whose callback is also in that
executable through g_signal_connect_data, g_timeout_add or g_timeout_add_full.
Other registration APIs, including g_signal_connect_object and pre-created closures,
remain outside coverage. Timer source-ID lookup/removal remains valid; data-based
source lookup is not supported by this diagnostic wrapper and is absent from the
current consumer source. Review that constraint before reusing it with new consumers.
Signal closures retain their original callback, data, marshaller,
arguments, return value, swapped/after flags and destroy notifier. Public closure
marshal guards measure entry/exit. Timer wrappers retain interval, priority,
callback result and exactly-once destroy notification. Block/disconnect matching,
recursive emission and self-disconnection must retain their observable behavior.

Before native diagnosis, compare an uninstrumented and instrumented standalone
GObject/timer fixture with fixed literal expectations. Test decoder rejection of
truncated, overflowing, duplicate, inconsistent and invalid nested transcripts.
Failure of these checks prevents using the probe to attribute product behavior.

The probe owns fixed storage: 2048 concurrent registrations, 32768 invocation
records and 64 nested entries per thread. Record numeric PID/TID, registration and
invocation identities, parent invocation, callback ELF offset, bounded signal/action
enums, timer interval/priority, monotonic start/end nanoseconds and thread CPU time.
Do not record authored strings, object/data addresses, policy data or paths. No
transcript I/O occurs during callbacks; emit a complete transcript at normal exit.
Overflow or unfinished entries invalidate diagnosis while original calls continue.
Inherited helper processes may emit empty transcripts. Every observed frontend
lifetime requires a complete nonempty trace. Missing/forced-exit traces remain a
diagnostic failure, never an invented pass.

Compile only into owned ignored out/campaign/editor-callback-trace. Record source,
compiler, probe, fixture, symbolizer and runtime identities. Resolve exact callback
entry offsets after exit. Preserve original failed outcomes and source-bound raw
evidence. Archive and verify complete native attempts before duplicate cleanup.
No product binary, entry point, capability, scheduler or acceptance limit changes.

## Attribution and decision

Correlate each frontend timer registration's ordinal with the existing per-process
timing stream, requiring complete one-to-one coverage. Timer wrapper intervals
include observer overhead, so do not equate them to the narrower product work
measurement. Report wall and thread CPU time separately; wall-minus-CPU cannot
distinguish scheduling from blocking. Account for nested spans by interval union,
never by summing inclusive callback times. Report uncovered gaps explicitly.

The initial laboratory fixture returned 9500 ns thread CPU across 9180 ns wall.
Preserve this clock disagreement and the rejected diagnostic attempt. The decoder
must report CPU-over-wall discrepancies explicitly rather than assume independently
read clocks always satisfy CPU <= wall. This corrects the diagnostic's clock
assumption; fixture behavior and all product acceptance limits remain unchanged.

Run one initial diagnostic campaign after the fixture checks. Instrumentation can
perturb timings: it cannot qualify latency or replace the ordinary GUI gate.
Require source-resolved evidence before attributing a delay to an action. If a
long callback is found, identify its implementation boundary and preserve its
current authority, validation, persistence, erasure and lifetime contracts in the
repair package. If gaps remain outside observed callbacks, record that limitation
and choose a bounded scheduling/toolkit investigation rather than guessing.

Completion is the validated diagnostic, actual evidence, supported conclusion and
next implementation boundary. Production recovery, W-11 and all five complete
SysPane 0.1.0 editions remain open.
