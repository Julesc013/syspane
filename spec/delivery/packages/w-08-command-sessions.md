---
type: "SysPane Work Package"
title: "Asynchronous authored command sessions"
description: "Join authenticated sessions to one bounded transaction owner without blocking control traffic."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T16:49:14Z"}
sp_id: "SP-W08-COMMAND-SESSIONS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-AUTHORED", "SP-W24-PACKAGE", "SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Asynchronous authored command sessions

Continue W-08 in the existing configuration, protocol and native application
components. Add the optional `configuration.transactions` handshake feature to
command 0.2/result 0.1 sessions backed by the authored transaction owner. It admits
existing scene/settings preview and commit operations for authenticated writer
roles. It requires both document versions and an 8192-byte negotiated frame floor;
an unmet required feature fails negotiation, an optional feature is removed. The
same frame floor applies to settings previews on this asynchronous composition.
Sessions without that owner retain their preview-only behavior. With an owner,
legacy settings previews also use its single ledger; feature negotiation cannot
multiply principal admission or replay capacity. Original-epoch wire reconciliation
is a separate pending boundary; current-epoch result.get never invents that scope.

## Ownership, states and bounds

The session loop alone owns admission, the existing request ledger, connection
lifetimes and result delivery. One worker exclusively executes authored validation,
resource preparation and native store access. Native composition supplies actual
thread/process execution and confirms termination before releasing the worker slot.
A returned callback or a cancellation request alone does not release it. Worker
inputs are immutable copies. No received JSON supplies native authority or policy.

States are queued, running/preparing, commit-permitted, stopped/terminal. Admission
reserves one ledger record and one original-connection reply. At most 128 queued,
running or undelivered completion records exist globally, one executing worker, and
eight reserved asynchronous replies per connection. Retain ledger limits of 128
records per principal, 1024 globally, 16 principals, 16 MiB body/result reservations,
16 KiB body, 4 KiB result and ten minutes terminal retention. Each reply reservation
holds 5120 payload bytes plus its four-byte prefix inside the existing 16-frame,
64 KiB control queue. Ordinary control traffic uses remaining capacity. Saturation
returns busy before admission if an ordinary reply fits; otherwise close the peer.
These bounds cap command body copies below 2 MiB beyond the ledger. There is one
current/prepared authored bundle, bounded by the authored package; no growing
completion stream or scene-copy queue is admitted. Private decomposition is delegated.

Cancellation before the commit permit sets a flag; the worker checks before/after
preparation and in the native publication guard. The guard serializes latest policy
and cancellation under the owner lock, reauthorizes the original command and grants
the permit immediately before the native selecting-record operation. Later cancel
does not undo the permit or claim cancellation. Before confirmed worker stop,
duplicate/query/cancel replies say unknown with `request.pending` and null storage
facts. At termination report the actual cancelled, failed, unknown or committed
result. Native publication failure after a permit still reports its actual result.
Policy replacement before the permit rejects publication; after it, publication may
finish but current policy governs disclosure and all subsequent work.

Disconnect discards connection queues/reservations, not admitted work or results.
Reconnect under the same authenticated principal can retrieve/replay the outcome.
A monotonically allocated connection lifetime prevents delivery to a reused ID.
Policy replacement clears queued results and reservations before any fallible check;
the owner is updated before delivery resumes. Query and completion delivery recheck
current authorization for the original operations. A policy-hidden result uses
`unknown` with `policy.denied` (or `policy.forced`) and null storage facts: result
0.1 permits null facts only for unknown outcomes. This does not assert that a
previously admitted mutation failed to commit. Expired/absent results are unknown.
A clock regression or invalid policy revision invalidates admission and
pre-permit publication permanently; it cannot be repaired by a later timestamp.
Shutdown invalidates the owner and requests cooperative cancellation. Hung native
preparation requires an independently supervised executor before installed use;
this finite laboratory must bound every injected wait and join its owned worker.

## Verification and handoff

Use ordinary configure/build/test presets after workspace preflight. Shared cases
must cover committed facts, previews, exact-byte replay/conflict, cancellation on
both sides of the permit, policy changes, held worker slots, connection reuse,
reply saturation and heartbeat responsiveness. Run those cases on all three
development toolsets. A native Linux experiment uses the existing OS-authenticated
local IPC adapter and private ext4 generation store with synthetic resource inputs.
An independent client observes responsive heartbeat/query/cancel during resource
preparation, joins actual exit evidence and verifies stored documents independently.
Preserve failed attempts and exact source/artifact/environment identity.

This checkpoint does not complete W-08: installed controller and protected-policy
ownership, bounded worker supervision, full asset closure, original-epoch wire
reconciliation, native settings/editor controls, undo/external edits/migrations and
visible activation remain required. Historical runtime and non-Linux persistence
qualification remain separate. Public release and privileged actions stay reserved.
