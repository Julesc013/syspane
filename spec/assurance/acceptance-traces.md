---
type: "SysPane Specification"
title: "Concrete implementation acceptance traces"
description: "Specify independent expected outcomes for the first model, request and recovery cases."
tags: ["assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T19:48:29+11:00"}
sp_id: "SP-ACCEPTANCE-TRACES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-TRANSPORT", "SP-PERSISTENCE", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-READINESS-2026-10-05", "resource": "User-supplied readiness review, 2026-10-05", "title": "Implementation closure review"}]
---

# Concrete implementation acceptance traces

These are versioned expected behaviours, **not executed product tests**. They refine
existing families in [tests.json](tests.json); they do not replace the families or
create a second result register. Each implementing package binds its mandatory
cases to real test code/commands and records outcomes separately. Case IDs below
are child IDs within their stated parent families. Retain the input/oracle revision
when changing a case.

## Model foundation cases

Common notation: `P` is one producer, `E1` and `E2` are distinct epochs, generation
numbers are unsigned integers, and identities `A1`/`A2` denote different entity
lifetimes even when their labels match. Each row begins from its stated initial
snapshot. An error means no partial publication. The harness supplies exact typed
values without making native API calls.

| Case / parent | Input and stimulus | Required observable outcome |
|---|---|---|
| STATE-01 / T-STATE | Current `(P,E1,7)` has A1. Submit candidate generation 8 containing A1 twice with values 10 and 20. | Reject duplicate identity; current remains generation 7, including its original A1 value. |
| STATE-02 / T-STATE | Current `(P,E1,7)` has A1 named `Ethernet`. Generation 8 removes A1. Generation 9 adds A2 also named `Ethernet`. Deliver a late A1 observation with value 99 after generation 9. | A1 stays retired. A2 receives no value from A1. Generation 9 is unchanged by the rejected late result. |
| STATE-03 / T-STATE | Current generation 7. Receive delta base 6, target 8. | Reject missing base, retain generation 7 and request a coherent full snapshot. Do not apply individual operations from the delta. |
| STATE-04 / T-STATE | Apply record ID R in E1 producing generation 8 and A1 value 10. Deliver R with identical content, then R with value 11. | Identical duplicate leaves generation 8/value 10; conflicting duplicate is an error and also leaves generation 8/value 10. No generation 9 appears. |
| STATE-05 / T-STATE | Hold reader snapshot `(P,E1,7)` with A1 value 10. Publish valid generation 8 with A1 value 20. Then submit generation 9 with an edge to missing A2. | Existing reader still sees generation 7/value 10. A new reader sees generation 8/value 20. Reject generation 9 as a whole; new readers continue to see generation 8. |
| VALIDITY-01 / T-VALIDITY | At UTC `2026-10-05T00:00:00Z`, A1 reports observed value 42 B/s, support supported, acquisition success, freshness current, presence present. At +1 s acquisition fails with source error `fixture.unavailable`. | Value remains 42 B/s; observed time remains 00:00:00Z; attempted time becomes 00:00:01Z; acquisition failed, freshness stale, presence present and error retained. No successful zero is synthesized. |
| VALIDITY-02 / T-VALIDITY | Compare a successful measured value 0 with an unsupported field whose value is null, a supported pending field with null, and the retained value from VALIDITY-01 after A1 removal. | Measured zero remains success/present. Unsupported/null and pending/null stay distinct. Removed A1 exposes absent presence and cannot present its retained value as a current measurement or transfer it to A2. |
| CLOCK-01 / T-CLOCK | In E1, counter rises from 100 to 300 over monotonic 1,000,000,000 to 3,000,000,000 ns. UTC moves backward by one hour. | Interval is 2,000,000,000 ns; rate, if derived for this descriptor, is 100 units/s. UTC change does not alter the interval or create a negative rate. |
| CLOCK-02 / T-CLOCK | First counter sample is `(E1,100,3,000,000,000 ns)`. Next is `(E2,300,1,000,000,000 ns)`. | No cross-epoch interval/rate is computed. Record a reset/gap; wait for another valid E2 sample before deriving a rate. |

Native resume/suspend clock semantics still require profile-specific T-CLOCK
cases. These synthetic examples do not prove the operating system's clock adapter.
W-01 may test interval eligibility without implementing the later rate collector.

## Request budget cases

Use the experimental limits in [transport](../contracts/transport.md), one
authenticated principal/installation/epoch, an injected monotonic clock and a
valid changing mutation for each new ID. Disable unrelated background traffic.
These cases belong to T-IPC and T-PROTOCOL in W-24/W-08.

| Case | Stimulus | Required observable outcome |
|---|---|---|
| IPC-BUDGET-01 | Admit 128 distinct requests and hold them before terminal outcome. Submit request 129. | Request 129 is busy before execution. Existing reservations remain intact; cancellation and health control traffic can still make progress. |
| IPC-BUDGET-02 | Finish all 128 admitted mutations at clock t=0. Submit another at t=599 s, then at t=600 s after reclamation. | No active mutations remain, but retention reservations still make the first submission busy. At t=600 expired entries can be reclaimed and the new request admitted if other checks pass. |
| IPC-BUDGET-03 | Disconnect/reconnect after IPC-BUDGET-02 at t=599 s; submit a new mutation, then retrieve an earlier result. | Reconnection does not reset principal-scoped retention capacity. New mutation stays busy; authorized result retrieval returns the retained result without executing a mutation. |
| IPC-BUDGET-04 | Resend an identical retained request, then reuse its ID with a changed body. | Identical replay returns its existing result without another reservation or revision. Changed body returns conflict; retained record and authored revision are unchanged. |

Exact role/connection-state message schemas, controller-wide memory/connection
limits and reserved control queue budgets remain W-24 closure items. These cases
do not claim complete wire conformance or establish production throughput.

## Committed change with lost acknowledgement

PERSIST-01 belongs to T-PERSISTENCE and T-TRANSACTION. W-08 supplies the coordinator
and storage fault harness; the platform adapter supplies the actual durable-write
experiment. The starting scene is valid at revision 40 with a widget property
`x=10`. A valid scene replacement changes it to `x=20`; all other authored content
is identical. The request R includes expected revision 40 and admitted policy.

| Step | Stimulus | Required observable outcome |
|---|---|---|
| 1 | Start controller in epoch E1 from the committed revision 40 bundle. | Client/controller agree on revision 40 and x=10. |
| 2 | Submit R once. | Authenticate, validate and compare expected revisions before publication. |
| 3 | Persist revision 41 and R's committed identity; inject a crash after the storage profile's durable boundary but before acknowledgement or activation. | Fault evidence names the transition. Revision 41 and its manifest/request identity are recoverable as one coherent bundle. |
| 4 | Restart in distinct epoch E2. | Recover revision 41, x=20; no mixed generation or new revision 42. |
| 5 | Reconnect and reconcile the original E1 request against the committed journal/revision. | Report the recovered commit. Do not submit a fresh mutation merely because the E1 reply was lost. |
| 6 | Resume activation with current policy. | Report pending, active or degraded accurately. Durability alone cannot report visible. |
| 7 | Read committed state and command history. | Exactly one authored change, revision 41, x=20. Reconciliation created no revision 42. |

W-08 must bind the test to a concrete versioned command/document fixture and
W-24's result/reconciliation messages before execution. This trace defines the
required observation; it is not a second wire format.

| Variant / parent | Changed stimulus | Required observable outcome |
|---|---|---|
| PERSIST-02 / T-PERSISTENCE | Revoke relevant disclosure policy before E2 starts. | Recover the same authored revision but apply current policy before disclosure; no replay/undo restores the revoked permission. |
| PERSIST-03 / T-PERSISTENCE | Remove/full-fail media before pointer publication and durable acknowledgement. | No durable-success result. Current selected bundle remains coherent revision 40; any draft remains explicitly unsaved and is not silently replayed. |
| PERSIST-04 / T-PERSISTENCE | Corrupt current selecting record after revision 41; provide a separately verified last committed record for revision 40. | Recover revision 40 with diagnostic. Do not choose revision 41 by directory time. Preserve corruption evidence. |
| PERSIST-05 / T-PERSISTENCE | Renderer remains unavailable after E2 recovery. | Committed revision remains 41; activation stays pending/degraded and visibility unproven. The independent diagnostic remains usable. |
| PERSIST-06 / T-PERSISTENCE | Reconnect after ordinary terminal-result retention expired, while the selected committed manifest still records R. | Result-cache expiry is explicit; reconcile R to revision 41 from the journal/manifest without another mutation. |
| PERSIST-07 / T-PERSISTENCE | Both ordinary result and any journal identity for an old request have been legitimately pruned. | Outcome is unknown, never fabricated success/failure. Retrieve current authored state; do not automatically retry the old mutation with a new ID or assume it never committed. |

## Cold-start exercise

This proposed exercise evaluates repository sufficiency; it has not run. It does
not instruct the current agent to launch other agents. When separately admitted,
give a fresh session only a pinned checkout, the root README, a bounded work ID
and its actual authority/environment. Keep the conversation and previous private
reasoning out of the exercise input.

The implementer must find the contracts, identify prerequisites, perform the
package and run its declared checks. Prepare expected observable results
independently before inspecting the implementation. Compare outputs, not private
class organisation. Record every consequential assumption as a missing contract,
delegated choice, missing environment capability or implementation error.

The exercise passes only when the package's required checks pass, the handoff is
source-bound, and no unresolved missing contract changes observable acceptance.
Blocked environment capability is a blocked exercise, not a specification failure
or a pass. Preserve discrepancies before any oracle amendment. A second implementer
may derive expected outcomes independently when that work is explicitly assigned.
