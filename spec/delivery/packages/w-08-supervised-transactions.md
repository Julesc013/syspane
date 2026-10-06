---
type: "SysPane Work Package"
title: "Independent transaction deadlines and controller recovery"
description: "Bound uncooperative transaction work without killing threads or replaying uncertain mutations."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T17:23:18Z"}
sp_id: "SP-W08-SUPERVISION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-RECONCILIATION", "SP-W08-COMMAND-SESSIONS", "SP-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Independent transaction deadlines and controller recovery

Continue W-08 using the existing transaction owner, native child owner, health
channel and restart gate. One controller process owns its transaction thread,
store lock and authenticated client sessions. An independent supervisor owns the
exact controller process and never opens that store while the controller lives.
Terminate the process to stop uncooperative work; never terminate a C++ thread,
pretend cancellation proves stop, or retain its in-memory store after failure.

## Admission and deadlines

Extend HealthLink with an explicitly selected `recovery.transaction` feature and
`transaction-watch` 0.1 document, alongside recovery-health 0.1. Both endpoints
require this profile; existing health/render links retain their original behavior.
Use existing native peer/PID authentication, console controller role, framing,
4096-byte frames, 16-event/16-frame/64 KiB bounds and five-second handshake/partial
frame deadlines. Client command sessions do not admit supervision messages.

| Message | Direction | Exact body and state |
|---|---|---|
| `transaction.started` | controller to supervisor | One `ticket`: nonzero canonical uint64 decimal string. Connected, no active ticket, greater than the last completed ticket. |
| `transaction.armed` | supervisor to controller | Same ticket, once, after the independent deadline is armed. The controller cannot start its worker before receiving it. |
| `transaction.finished` | controller to supervisor | Same armed ticket, only after actual worker join and owner completion. No durable/activation facts or mutation authority are conveyed. |

The supervisor's serialized monotonic clock starts an absolute 5000 ms operation
deadline when it receives started. At elapsed >=5000, fault wins over a queued
finish. Heartbeats, duplicate/mismatched events and replacement start messages
cannot renew it. Deadline, malformed order, disconnect or clock regression latches
failure for that controller lifetime. A new watch is created only for a new child.
The existing independent health lease remains three missed one-second heartbeats.

On fault, first quarantine the existing restart gate with unconfirmed stop, request
termination of the exact held child, then supply confirmed stop only after native
wait proves exit. Missing stop proof prevents replacement. Reuse the existing
1/2/4 second bounded backoff and three-restarts-per-60-second circuit. Do not reset
the budget after a successful handshake or transaction. Replacements open storage
afresh and use distinct producer epochs and endpoint lifetimes.

The controller monitors the supervisor health lease independently of its worker.
Supervisor loss/expiry causes process exit without waiting for an uncooperative
thread; native parent-death handling covers abrupt supervisor death. Such exit
does not assert cancellation or non-commit. Supervisor signals grant no command,
policy or storage authority. Current policy is still enforced at the commit permit
and disclosure boundary. Existing clients reconnect and reconcile their original
epoch/request; recovery never resubmits a mutation automatically.

## Native experiment and acceptance

Extend the Linux command composition, preserving ordinary command/reconciliation
tests. The supervisor launches only its own executable through the existing Child
owner, uses private owned runtime endpoints, and bounds the whole fixture to 90 s.
The test client supplies synthetic store/resources and explicit laboratory policy;
installed policy distribution and persistent installation identity remain open.

Portable tests check exact deadline edges, late finish, ticket order, latched clock
faults and link direction/negotiation/order. Native tests must independently observe
real additional worker tasks, responsive command heartbeats while work hangs,
the old process's exit before replacement, and unchanged/recovered authored state.
Cover normal completion; preparation hang (revision 40 stays); post-durable hang
(revision 41 recovers); frozen controller; supervisor death and supervisor freeze;
and repeated faults opening the existing restart circuit. No client mutation replay
is part of recovery. Verify files and result schemas independently of probe claims.

Run ordinary preflight/configure/build/test on all three existing development
toolsets. Native supervision qualification here is Linux IPC/ext4 only; portable
guards on historical-toolset host builds are not historical native support. Preserve
source-bound failures and results. Installed lifecycle, full resource closure,
native settings/direct editing, activation, non-Linux storage/supervision and every
complete desktop release remain required.
