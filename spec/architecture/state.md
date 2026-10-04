---
type: "SysPane Specification"
title: "State store, identity and observation semantics"
description: "Represent typed facts with orthogonal support, acquisition, freshness and presence."
tags: ["architecture"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-STATE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SCHEDULER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# State store, identity and observation semantics

## Entities and relationships

An entity identity is opaque and scoped to a producer plus lifetime. Retain stable source identifiers when trustworthy, but never merge entities solely because display name, IP address, drive letter or serial matches. Expose identity uncertainty. Use generation/tombstone records to prevent late results from a removed device being assigned to its replacement.

Relationships are typed edges, not a universal single-parent tree: volume extents can span disks; a dock can contain several classes of devices; virtual networking has lower-layer and membership relations. An inspector may project a tree without changing the graph.

## Observation dimensions

Store a typed value (or explicit absence), unit, origin (`observed`, `derived`, `configured`), support, latest acquisition result, freshness, presence, source, observed time, last-attempt time and generation. Retained values after failure must show the last successful observation time and the latest failure. `unsupported`, `access_denied`, `disabled`, `not_present`, `pending` and a measured zero are distinct.

No arbitrary numerical confidence score is assigned. Providers can include a documented accuracy or uncertainty measure when it has a physical or statistical meaning. Operator annotations do not become measured device facts.

Inventory freshness differs from sample freshness. A startup-read serial remains meaningful until an invalidation; a throughput rate needs an actual interval. A global “older than three seconds means stale” rule is incorrect. Each metric descriptor owns freshness and invalidation rules.

## Store publication

Stage source results, validate entity references and units, reconcile identities, calculate transitions, then publish an immutable generation. A reader sees a coherent application snapshot but must still see per-field observation times. A snapshot is not a simultaneous physical measurement of all devices.

Source generations are monotonically increasing within a producer epoch. Deltas declare base and target generation. A consumer missing a base rejects the delta and requests a snapshot. Duplicate delivery is idempotent when request/record IDs match; conflicting reuse of an ID is an error.

## Error semantics

Errors have stable project codes plus native domain/code and a bounded, sanitized explanation. Native raw text is not safe HTML/terminal markup. A failure does not erase useful historical values, but the UI cannot show them as current. A provider returning malformed data is disabled or quarantined according to policy; its error cannot crash the store.

A source transition timestamp is retained only when the source actually supplied it. Otherwise label the event as first observed at reconciliation. Current snapshots are coalescible; evidence history separately describes indications, transitions and gaps. See [history](../telemetry/history.md) for durability boundaries.

## Descriptor and binding boundary

[Metric descriptors](../telemetry/metric-registry.md) declare field units, denominator,
temporality, freshness, source coverage, sensitivity and cost. [Portable selectors](../experience/scene-bindings.md)
resolve saved intent separately from producer/epoch-scoped observation identity.
Ambiguous or missing pins cannot silently bind replacement hardware. Source liveness
does not renew each field's measurement freshness.
