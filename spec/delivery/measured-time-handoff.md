---
type: "SysPane Work Record"
title: "Measured telemetry and freshness checkpoint"
description: "Bind versioned measurement times to consumer clock scope, replay history and native delayed-delivery evidence."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:04:00+11:00"}
sp_id: "SP-MEASURED-TIME-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-MEASURED-TIME", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Measured telemetry and freshness checkpoint

From base `1106f1b369eafcb4ff183f9f16344308ce5559b2`, W-25 implements the
[measured-time package](packages/w-25-measured-time.md) in the existing model,
codec, session owner, native stream and data view. The native data remains synthetic;
actual collectors and renderers remain required.

## Implemented boundary

Experimental observation/snapshot/telemetry 0.2 adds an explicit measurement domain
and nullable original measurement count. Exact document/feature negotiation is
required; 0.1 schemas, fixtures and inventory admission keep their meaning. Native
scope stays local to the consumer and never becomes a wire-supplied authority.

The consumer requires a qualified local reading, rejects future remote measurements,
and preserves measurement time through duplicate/full confirmation and reconnect.
Local clock mismatch/regression latches a fault; policy still removes payload when
the clock is bad. Same-epoch reattach cannot change version/domain/scope or clear
history. A new producer epoch requires complete state before replacing the retained
model. Obsolete callbacks are rejected before clock processing.

Finite-TTL freshness uses matching epoch/domain/local scope and integer age. Exact
expiry, zero TTL, absent mappings and mismatches are stale. Positive rate intervals
require strictly increasing compatible counts. A bounded per-field high-water mark
also survives temporary field absence/null measurement, preventing later timestamp
rollback. Its key storage is charged to retained memory and limited by the existing
observation ceiling. Queue, frame, graph, replay and policy limits remain unchanged.

Measured projection provides a checked local tick alongside the borrowed model and
independent lease presentation. Callers must respect retained/disconnected state;
a small measurement age alone cannot make a lost producer live.

## Executed checks and preserved failure

Five portable families cover codec/version/domain rejection, exact age/rate bounds,
replay/high-water capacity, reconnect/epoch/policy lifetime and session negotiation.
Three native Windows/Linux cases independently compare the sender's original count
with received wire bytes and consumer output: immediate delivery is current under
a 1 s TTL; delivery delayed 200 ms is stale under a 100 ms TTL; a count 60 s in the
future is rejected without importing payload. The preceding inventory and native
clock cases remain unchanged.

Final suites pass 88 Windows, 89 Linux and 81 historical-toolset host checks.
Historical PE/import audits cover ten executables; the native clock/IPC adapters
remain disabled in that profile. Current profile revisions are Windows x64 15,
Linux x64 16 and historical x86 8. Fresh relocated model-only smoke archives pass
on all three profiles; they are not distribution packages for these probes.

The first modern runs failed one newly written codec assertion. It compared whole
serialized envelopes, although the established contract guarantees exact **body**
bytes and equivalent envelope content. Source/contract review corrected the test
to check both, including a deliberately formatted body. No codec behavior or
acceptance requirement changed. `measured-time-oracle-review.json` and the adjacent
`first-failure.ctest.txt` files preserve the original assertion, reasoning and runs;
original source archives remain in owned output. This is agent review, not a claim
of independent human approval.

Records in `build-support/evidence/w-25-measured-time-<profile>.json` bind final
artifacts, exact cases and native process output. The attempts/verification records
and machine `measured-time-handoff.json` supply the resumption evidence. Specification
checks now cover 29 schemas and 85 fixtures, including eleven new measured examples.
The combined campaign workspace stays within its current 2 GiB allocation.

## Next admitted work

Close a real native source's identity, acquisition/counter, error, cancellation,
bounded demand and evidence-disclosure contracts, then connect it to independent
supervision and this measured receive path. Preserve source failure and retained
value semantics while testing actual data production. Continue other native-host
tracks independently in their admitted laboratories.

Native suspend/resume, namespace mismatch/change/denial, read/query/range/regression
fault injection and historical guest execution remain unqualified. Product demand
aggregation, installed policy/distribution, failure retention, real rendering,
cross-component erasure and external visible/editor recovery remain open. W-25 and
the campaign are incomplete; no privileged action, release or AIDE activation is
attested.
