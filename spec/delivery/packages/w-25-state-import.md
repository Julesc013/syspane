---
type: "SysPane Work Package Boundary"
title: "W-25 complete remote state import"
description: "Connect bounded telemetry documents to the revocable model owner without reinterpreting reported state as a local acquisition."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:30:29+11:00"}
sp_id: "SP-W25-STATE-IMPORT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-TELEMETRY-WIRE", "SP-W25-DATA-VIEW", "SP-STATE", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 complete remote state import

Own the conversion in `source/diagnostics/`, alongside the existing data owner;
extend the shared model only with explicit reported-state admission and preserved
metadata. The model still has no JSON dependency. The existing three profiles may
build this component. This closes the in-process receive boundary, not the native
subscription/demand scheduler or a real collector/renderer.

## Binding and lifetime

`DataView::attach_wire` receives a locally established telemetry binding after
authentication/negotiation, fixes its connection, producer/epoch, subscription,
policy revision, channel/classification and producer-to-consumer direction, and
requires the existing current policy/authority checks. Never derive this binding
from a received document. The binding's policy revision and scope must equal the
owner's current values. Prepare the binding before changing lease state.

`receive` takes the local attachment token and admitted revision separately from
payload bytes. Check them before parsing, copying data or advancing successor time.
Then validate the whole envelope against the stored binding using the telemetry
codec. A malformed or incorrectly bound document disconnects the attachment while
retaining prior coherent data. The native caller must also close its stream; this
component does not own native handles. Model/domain invalidity and capacity failures
retain data and require resynchronization. No received frame renews the lease.
Wire-bound attachments accept data only through `receive`; typed publication calls
cannot bypass the stored binding or reported-state mode.

Policy replacement drops the binding with all owned payload/replay history and
invalidates the token, including under clock failure. A renewed grant needs a new
authenticated attachment/full snapshot. Same-policy/epoch reconnect retains the
store's replay and retired-identity reservations. Validate the connection envelope
against the new local binding. Changed subscription/body fields change replay body
bytes; a producer uses a new record ID for a fresh full confirmation with changed
body bytes. A connection-envelope change alone does not change body replay identity.

## Complete state, acquisition and coverage

Add `Store::import_state` for already decoded, coherent complete reported state.
Keep `publish`/`resynchronize` acquisition semantics unchanged. The first accepted
publication fixes each store as acquisition or reported-state mode; mixing modes
fails without changing it. Only a new legitimate producer/epoch or policy lifetime
creates a fresh store; mode/capacity failure cannot reset history automatically.

A complete full snapshot may establish state or confirm identical current state;
a delta is a complete replacement with the exact accepted base and increasing
generation. Replays retain the existing ordering/capacity behavior and additionally
compare original delivery body bytes. A full confirmation's normalized model and
preserved document must equal current state. Unknown annotation or metadata changes
therefore require a new generation; they cannot silently change a confirmed view.

`partial` and `gap` documents request resynchronization and preserve the entire prior
model; they admit no record ID, remove no entity and clear no existing gap. Supporting
incremental partial coverage needs an explicit future coverage/merge contract.
Only a valid complete full snapshot may clear a gap, including after reconnect.

Reported observations retain their supplied value, source, acquisition/error, origin,
observation/attempt times and sample interval; never fill them from older local data.
A retained non-null failed/denied/pending/disabled observation requires supported
status, an observation time and stale freshness. A null value requires null observed
time and no measured tick; unsuccessful supported/unknown null state has unknown
freshness. Unsupported state requires null value, non-success acquisition and
not-applicable freshness. Successful state still requires supported status, a value,
observation time and no error. Absent non-null state must already be stale. Retention
is an assertion from the authenticated producer, not independently verified source
history or newly successful acquisition. Descriptor unit/type, graph, ID, error and
size checks remain mandatory before atomic publication.

## Metadata and time mapping

Preserve entity identity maps, snapshot capture time and per-observation generation
as typed model fields. Preserve the entire snapshot document as bounded opaque JSON
text in the model for identity/extension/original-time round trips; the adapter owns
its validation. The model does not interpret or execute that text. The received
body's exact bytes remain part of the publication replay record. Presentation uses
the existing synchronous policy-checked borrow, so these fields share payload lifetime
and classification. Labels and annotations still need the eventual UI's escaping.

Convert valid offset-bearing calendar timestamps to UTC seconds/nanoseconds without
the machine timezone or locale. Retain fractional digits beyond nanoseconds in a
canonical digit suffix (at most 34 digits, no trailing zero); retain original offset
and fractional spelling in the opaque document/replay bytes. Timestamp normalization
does not invent producer-monotonic time. Observation 0.1 has no measured tick: imported
observations keep it absent. Existing TTL evaluation therefore cannot label them
locally fresh merely from receipt, wall time, heartbeats or remote `current` status.
Producer-clock provenance/mapping remains required before that freshness claim.

Identity maps have at most 64 entries, 256-byte keys and 2,048-byte values. Original
body and preserved document each have the 1 MiB ceiling and are charged to existing
8 MiB candidate/64 MiB replay-storage limits. Count metadata strings and time suffixes
as well as typed records; no unaccounted side cache or secondary replay ledger.
Speculative admission shares immutable historical records and commits model, replay,
tombstones and lease together. These remain admission rather than allocator/RSS bounds.

## Fixed acceptance and execution

| Family | Required observations |
|---|---|
| IMPORT-STATE | Import the canonical full snapshot through the wire-bound data owner; expose exact typed values/identity/generation/capture metadata and preserved document. |
| IMPORT-RETAIN | Initial retained-denied state is valid; a remote retained value newer than local data is preserved; inconsistent retention/status/type fails atomically. |
| IMPORT-COVERAGE | Partial/gap cannot delete prior entities or advance generation; deltas cannot clear a gap; complete full recovery and removal retain retired-ID protection. |
| IMPORT-REPLAY | Exact body replay is a no-op; changed whitespace under a reused ID conflicts; same-generation full confirmation consumes capacity without dropping history; reconnect preserves reservations. |
| IMPORT-TIME | Offset conversion, pre-epoch/leap dates and subnanosecond suffix match fixed expected outputs; source strings survive; no measured tick or fabricated local TTL freshness. |
| IMPORT-LIFETIME | Wrong binding/mode, old token/revision, unavailable/replaced policy, bad clocks and capacity fail with prior-state/removal guarantees; callback borrowing retains existing protections. |

Run ordinary configure/build/CTest commands on all three profiles and preserve source,
artifact, fixture and failure identities. Existing acquisition and native regression
oracles remain. No native telemetry, historical guest, renderer or desktop qualification
follows; next connect native demand/policy lifetimes and explicit producer-clock data.
