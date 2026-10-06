---
type: "SysPane Work Package"
title: "Committed request reconciliation across producer epochs"
description: "Recover durable outcomes through authenticated read-only IPC without resubmitting mutations."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T16:58:11Z"}
sp_id: "SP-W08-RECONCILIATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-COMMAND-SESSIONS", "SP-PERSISTENCE", "SP-ACCEPTANCE-TRACES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Committed request reconciliation across producer epochs

Continue W-08 in the existing protocol/configuration/native storage owners. Admit
the optional `result.reconcile` feature with `reconciliation-request` 0.1,
`reconciliation-result` 0.1 and command-result 0.1. Retain wire major 0/minor 1 and
the asynchronous profile's 8192-byte frame floor. Missing required documents or
frame capacity reject a required feature and remove an optional feature. Only a
session composed with the transaction owner advertises it. It does not require
permission to submit a fresh mutation or enable an unrelated feature.

The client sends `result.reconcile` with exactly `schema_version`, `query_id`,
`original_producer_epoch` and `request_id`. All three identifiers follow existing
256-byte ID syntax; maximum body is 2048 bytes. The authenticated native principal
and installation/session come from the connection, never the body. The envelope
uses the current connection and producer epoch. The response is `result.reconciled`
with those four echoed fields plus `result` (command-result 0.1). Its nested request
ID matches the requested ID and its producer epoch matches the current envelope.
Clients match the entire connection/current epoch/query/original epoch/request tuple
before consuming the result. Query IDs correlate observations, do not create mutation
identities, and may be reused only when the client can disambiguate that tuple.

## Read-only ownership and results

The native store supplies at most two committed receipts from its validated current
and previous selecting records. Each receipt contains the original native principal,
producer epoch, request ID, exact command bytes and committed revision. Validate ID
and body bounds, command shape, commit intent and expected revision plus one; reject
conflicting duplicate identities. Bootstrap has no receipt. Fallback may return the
same verified record twice; collapse identical receipts. No staging directory or
unselected orphan becomes a committed receipt. This interface is an internal trusted
store contract and never returns command bodies or principal keys on the wire.

The session loop owns an immutable receipt snapshot. Populate it before serving
connections and replace it only after the one transaction worker has actually
stopped. Refresh it in that worker; never call the native store on the connection
loop. Keep the existing two-receipt retention bound (under 34 KiB of body/identity
bytes per snapshot). A native/receipt-validation fault clears external receipt
availability and requires reopening; it cannot fabricate successful recovery.

Reconciliation performs no resource preparation, publication, revision increment,
request-ledger admission, expiry renewal or automatic retry. A matched committed
identity reports accepted, its original committed revision, stored/durable true,
visible false and pending presentation activation. This proves historical commitment,
not that its generation is still selected or currently active. A client must obtain
current authored state before applying subsequent edits or requesting activation.

Absent/expired/pruned identity is unknown with `request.reconcile` and null facts.
A current-epoch request still running is unknown with `request.pending`. Do not
map an absent journal record to an unsaved/cancelled result. Current result.get and
cancel retain their existing current-epoch scope. Reusing R in E2 does not change
reconciliation of E1/R. A same-epoch expired ordinary result can still reconcile from
the retained receipt. Reads neither extend journal retention nor recreate pruned IDs.

Current authenticated console/desktop/saver_settings authority and available policy
are required, with `result.reconcile` capability permitted. For a matched receipt,
authorize its original operations under the latest policy before disclosure. A
policy-hidden receipt or pending request reports unknown with policy.denied/forced and null facts;
forced values and role changes apply even after restart. Queued replies are erased
by the existing policy replacement path. No old-epoch permission is restored.

The result is bounded to 4096 bytes, its wrapper to 5632 and the complete envelope
to 6144. Check control capacity before lookup; disconnect on exhausted control
capacity. Use existing 16-frame/64 KiB queues, eight reserved mutation replies and
16 connections. Lookup allocates no separate queue, journal or request ledger and
cannot bypass those limits. Repeated observations are bounded by the same queues.

## Fixed verification and remaining gates

Run ordinary preflight/configure/build/test on all three development toolsets.
Portable tests cover current/previous/pruned receipts, E1/R versus E2/R collisions,
policy/role changes, cache expiry, malformed/cross-wired responses, negotiation,
invalid receipt rejection and lookup while a transaction worker owns the store.
Assert no store calls or writes occur during session lookup, and no ledger growth.

The Linux native experiment binds PERSIST-01 to a scene whose x changes 10 to 20
at revision 40 to 41. Submit R over authenticated IPC, stop the exact controller
after its durable transition and before its reply, observe stop and SIGKILL, then
restart E2 on the same owned private ext4 store. Reconcile E1/R over IPC and inspect
stored documents independently: revision 41, x=20, no revision 42 from lookup.
Exercise revoked policy, missing/pruned identity, coherent fallback and the before-
publication interruption control. Keep existing stored/durable/activation/visibility
distinctions. Preserve every failed attempt with source and artifact identity.

This closes only the reconciliation portion of PERSIST-01 and related variants.
Actual renderer activation, independent diagnostic availability, installed storage/
policy ownership, supervised workers, assets, native settings/direct editing,
non-Linux persistence and all full desktop releases remain required. The experiment
does not operate on installed user configuration, a user desktop or unrelated VMs.
