---
type: "SysPane Work Package"
title: "Inspector chart continuity across coalesced delivery"
description: "Forward known skipped admission context without inventing samples or changing the bounded latest-state receiver."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-10T05:33:19.872295+00:00"}
sp_id: "SP-W11-INSPECTOR-DELIVERY-GAPS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-INSPECTOR-TELEMETRY", "SP-W11-SCENE-INSPECTOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Inspector chart continuity across coalesced delivery

Continue W-11 live semantic qualification with this correctness prerequisite.
The installed receiver permits latest-complete-frame replacement. ChartHistory
requires skipped admission context to produce a break. A replaced frame was
validated by the native receiver but never admitted to the scene history; do not
silently connect the surrounding displayed points or claim the missing point was
collected into that history. Preserve the bounded slot and original wire versions.

Give each newly accepted complete frame a receiver-local uint64 ordinal starting
at one. Duplicate wire publications do not advance it or replace the frame.
Snapshot generations are provenance, not this ordinal: a generation jump alone
does not prove a skipped native delivery. Preserve original receipt time/tick and
immutable payload. Overflow closes the receiver with capacity failure; never wrap.

Within one unchanged binding and delivery scope, the inspector compares the new
ordinal to its last admitted frame. A forward difference greater than one calls
the existing surface gap operation before admitting the new full state, in the
same synchronous presentation transaction. No extra paint exposes the intermediate
state. A non-increasing ordinal on a different frame is invalid: detach and admit
no new payload. Zero is not a valid delivered ordinal. First attachment accepts
only the latest frame and invents no preceding points. Attachment replacement,
policy, stale clocks and native leases retain their existing checks and erasure.

A repeated measurement after a skipped frame cannot heal the pending break;
the next new point begins a segment. Once that point is admitted, a subsequent
contiguous publication can join it. A duplicate wire frame is neither a new sample
nor evidence of loss. Keep every admitted scene publication's existing history
feed; do not infer gaps from sampling cadence or numeric generation differences.
This adds one bounded ordinal per transferred frame/receiver, not a payload queue,
worker, cache or chart policy grant.

Freeze `tests/scene/inspector-delivery-cases.json` before repair. Seven scenarios
give exact native GTK point rows and pending-break outcomes: contiguous generation
jump, coalesced success, coalesced failed acquisition, duplicate wire, duplicate
measurement preserving a break, first-latest attachment and repeated delivery.
Run them inside the existing native SCENE-INSPECTOR chart case before its original
independent AT-SPI/keyboard/erasure exercise. Preserve the failing baseline and
unchanged expectations. These are controlled synthetic measurements through the
real receiver, renderer and GTK model, not maximum-input performance, installed
native acquisition or human accessibility qualification.

The first repaired run exposed an invalid new duplicate-point stimulus: it moved
the measurement from 100 to 200 and back to 100, violating the model's established
measurement high-water rule before reaching chart history. Preserve that attempt
and its original input. Correct only the skipped second publication to a failed
acquisition retaining the first measurement/value (100/10). The expected rows and
pending-break assertions are unchanged; no model chronology rule is weakened.

After ordinary workspace preflight/configure/build, run
`ctest --preset linux-x64-gcc13 -R '^native[.]SCENE-INSPECTOR' --output-on-failure`.
Also run the original installed telemetry and network consumer cases, chart/scene,
receiver/data/telemetry and component checks on their applicable development
profiles. Record exact source, binary and oracle identities and failures; preserve
the five full-edition release gates. Then continue maximum live table/chart loads.
