---
type: "SysPane Work Package"
title: "Policy-bound authored scene bindings"
description: "Resolve existing selectors and pins against scoped immutable producer views without name-based rebinding."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T19:53:39Z"}
sp_id: "SP-W09-BINDINGS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-BINDINGS", "SP-W09-LAYOUT", "SP-W25-NETWORK-PRESENTATION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Policy-bound authored scene bindings

Implement the existing binding 0.1 grammar in the shared scene component. This is
the value-selection input to native measurement/drawing, not a second telemetry
store or a replacement for the existing measured network view. Keep authored
bindings unchanged. General expressions, implicit unit conversion and arbitrary
I/O remain unavailable. Native rendering, cache erasure and editing remain W-09
integration requirements.

## Trusted routing and lifetime

The serialized controller owner supplies at most sixteen distinct DataViews, each
with its expected producer, one explicit scope (local_host, current_session or a
named registered_asset), supported entity types, declared observation fields/TTLs
and explicit persistent-pin mappings. This context is trusted local routing, never
inferred from names, source labels or a client's document. Standalone descriptor
validation retains the existing 262144-byte authored scene ceiling, including
maximal Unicode predicates; it must not impose a smaller ASCII-only allowance.
All candidate producers
for the requested scope/type must be present; an incomplete provider catalog cannot
claim a complete selection. A producer and a DataView appear at most once.

Each entry has at most 256 types, 256 fields and 256 pin mappings. Field TTL is
absent for non-expiring inventory or positive nanoseconds. A pin mapping explicitly
names namespace/key, entity type, producer epoch and entity ID. A key has at most
512 Unicode scalars (2048 UTF-8 bytes), is valid UTF-8 and nonempty. Duplicate exact
mappings are invalid; different candidates for one key remain ambiguous. No
automatic mapping is created from display name, index, identity metadata or a
previously selected row. Mapping persistence/authorization belongs to its owner.

Route direct pins by producer; selectors/persistent pins by exact scope and type.
No routed view means unsupported. An unresolved legacy pin remains pending without
reading a view. Validate grammar/context before access. Check every routed view's
current permission before payload availability: any denial returns denied with
no rows/counts/identity/value. A missing payload in any routed view returns pending;
do not disclose a partial collection as complete. Missing declared fields return
unsupported only after permission checks. These outcomes do not expose producer
metadata. Snapshot producer mismatch returns invalid without payload.

Borrow all routed views synchronously, nesting distinct views so the final sink
runs while every contributing borrow is alive. No payload/model pointer escapes,
cache persists, or acquisition occurs. The sink must not retain/copy/export payload
or reenter a view; a native retained cache needs its own admitted erasure owner.
Exactly one sink call occurs for valid invocation, including no-payload outcomes;
sink exceptions propagate once and release all borrows. Invalid grammar/context
throws before the callback. Internal budget/allocation exhaustion returns capacity
without partial payload. Caller supplies a sink and immutable context for the call.

An entry normally supplies a qualified current measurement Tick and uses
DataView::project_measured. An absent Tick is admitted only for explicitly retained
presentation via DataView::project; every retained non-null value is then stale
and has no age. Never fall back from a failed measured borrow to an unqualified
borrow. An unavailable measured borrow returns pending with no old payload.

## Selection and comparison

Selector predicates are ANDed. Reserved fields entity.id, entity.kind and
entity.display_name select snapshot metadata; all other fields name observations.
There is no implicit identity-map lookup. Observation fields are indexed by entity
and field. Existing wire admission rejects duplicate entity/field pairs,
including different sources; preserve that stronger invariant. The resolver also
defensively diagnoses multiple sources as ambiguous, never choosing the first.
A missing, denied, unsupported, failed, stale, null or not-present
predicate value is unknown, not true for ne. A known false predicate excludes the
entity even when another predicate is unknown. Otherwise any uncertain candidate
prevents a complete selection: denied beats ambiguous, unsupported, then pending.
Do not disclose counts/rows from that incomplete selection.

Predicates use exact typed equality. Boolean and string types never coerce. Numeric
types compare by mathematical value: uint64 values are never first rounded to
binary64, including 2^53+1 and UINT64_MAX. Strings compare their UTF-8 bytes, with
no locale/case/Unicode normalization. eq and ne complement each other only for a
known value. All numeric values must already be finite in accepted state/grammar.

For sorting, available values precede unavailable values in either direction.
Available categories ascend as boolean, number, string; values within a category
use false before true, numeric order or UTF-8 byte order. Descending reverses
available ordering only. Requested keys are compared in order, then ascending
(producer, epoch, entity ID), regardless of sort direction. Stale/error/missing
sort fields are unavailable; their condition does not invent a predicate match.
Every row retains the exact scoped identity and snapshot generation.

Singleton selection with more than one candidate is ambiguous even when limit=1.
Collection applies its 1..256 limit after ordering and reports total matched count
and truncation explicitly. Empty complete selection returns empty. Direct pins
require exact producer/epoch/entity; restart, removal or name/index reuse cannot
rebind them. Persistent pins require explicit matching mappings; none is pending,
multiple live targets ambiguous, stale/dangling mappings empty. A selector may
select a replacement that satisfies its predicates; its row identity must change.

## Projected fields and bounds

Matched rows contain selected field, typed value and unit, all observation status
axes, safe error code (never free-form error message), observed/attempted/measured
times and interval. Preserve null separately from numeric zero. Metadata output
is a configured string with unit 1 and an explicit metadata flag; observation
timestamps do not apply to that synthetic field. Missing declared observations give a pending
row; multiple sources an ambiguous row, without either value. Resolution matched
describes entity selection, not acquisition success. Consumers must show row state
and observation axes. Freshness uses the declared TTL and model freshness rules;
age exists only for compatible nondecreasing epoch/clock/scope. Producer lease
presentation/reason remain distinct from metric freshness. No formatting or unit
conversion is performed in this component.

Defaults/ceilings per call are 4 MiB accounted output, 8 MiB temporary field index
and 4,194,304 work steps. Callers may lower but not raise them. Account 256 bytes
per output row plus every copied string, including value/time/identity strings;
account 128 bytes plus entity/field bytes for each indexed observation. Charge a
step per scanned observation/entity, pin mapping, predicate and sort-key comparison. Keep at
most limit candidate references (one for singleton, while counting all matches)
using a bounded heap. Build one producer's field index at a time. These are
deterministic admission limits, not allocator/RSS guarantees. Any exceeded budget
returns capacity with no payload; internal storage never grows with all matches.

## Independent acceptance and completion

Before implementation, record exact cases for direct pin restart/replacement,
selector ambiguity, scope isolation, stable multi-producer ordering, collection
truncation, uint64/binary64 boundaries, false-versus-unknown predicates, missing and
multi-source fields, stale/retained state, unresolved/persistent pins, denial,
reentry, sink exceptions and all budgets. Reverse provider/entity/observation
enumeration and retain expected identities. Exercise the real DataView wire
admission and current-policy erasure, not just fabricated resolver inputs.

Run the shared tests on all three development profiles, full regression suites,
historical artifact audit and specification checks. Preserve original failures,
exact source/oracle inputs and a next-step handoff. This prerequisite does not
complete W-09 or any full platform edition.
