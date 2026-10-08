---
type: "SysPane Work Record"
title: "Authenticated session demand checkpoint"
description: "Bind controller-selected acquisition plans to authoritative subscription lifetimes and preserve native restart timing evidence."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T15:31:11Z"}
sp_id: "SP-SESSION-DEMAND-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W07-SESSION-DEMAND", "SP-DEMAND-EXECUTOR-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authenticated session demand checkpoint

Source baseline: `e567a018d334506e42332dc7f44f9c911ac1d362`. Git history identifies
the resulting commit. Every build/test attempt retains exact input hashes and a
source archive, including the failed initial native run.

The shared DemandSessions adapter owns the existing session and demand components.
The controller supplies a bounded immutable field/entity/age/priority request at
connection creation; the peer cannot replace it. Only an admitted subscription
creates a lease, using its actual negotiated role and authenticated grants. Existing
0.1/0.2 wire bodies are unchanged. General consumer-selected wire demand remains
an explicit future boundary, and collection selection does not narrow a complete
snapshot's disclosure contract.

Accepted new heartbeats renew demand. Duplicates, data, polling and repeated
subscribe do not. Decreasing heartbeat sequences close only that peer. Identical
resubscription rotates the callback ticket without renewing the lease or cancelling
compatible work. Old tickets are rejected before examining callback time or data.
Independent peers merge compatible requests and retain demand when another leaves.
Policy and clock faults clear session queues and cancel jobs; cancelled jobs occupy
their slots until the native owner confirms stop. Regrant cannot revive old peers.

The Linux collector now consumes this composition instead of manually decoding
heartbeats and mirroring leases. Its held acquisition thread, real measurement
times, source retirement and join-before-completion rules remain intact. Five new
portable families pass on all three development toolsets. Full suites pass **130
Linux, 119 contemporary Windows and 108 historical-toolset entries**. The latter
execute on the modern Windows host only. Fifteen historical executables pass the
PE32/header/mandatory-import audit and actual pinned SDK/static-CRT input checks;
no XP, Windows 9x or older NT runtime qualification follows.

The initial targeted Linux run passed 39 of 40 entries. Its collector hang case
observed only 999 ms between the reported fault and restart: the gate's original
clock was sampled just before the fault event timestamp. The native supervisor
now enforces the same required backoff from that exact reported timestamp as well.
The original source and failed public report remain preserved. The final full run
passes all eight collector, five demand-executor and five consumer-continuity cases
with their original oracle files unchanged.

`out/evidence/w-07-session-demand-attempts.json` indexes attempts, archives,
artifact identities, public native reports and the historical audit. Specification
checks are in `out/evidence/w-07-session-demand-verification.json`; the
machine handoff is `out/evidence/session-demand-handoff.json`. Operational
continuity journals remain ignored; public projections retain outcomes/counts and
the original private record hashes. No real-user desktop, VM or protected policy
was changed, and no release was published.

W-07/W-25 remain in progress. Next close general consumer wire selection, bounded
invalidation/coalescing and installed controller/policy ownership, and implement
the W-08 scene-command/persistence boundary using its existing contract identities.
The full [0.1.0 release](release-0.1.0.md) across all five required families remains
open, including native settings/editing, providers, packages and native qualification.
Historical version/architecture floors and designated historical/Mac labs remain
unresolved; this component checkpoint supplies no replacement support claims.
