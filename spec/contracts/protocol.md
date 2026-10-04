---
type: "SysPane Specification"
title: "Protocol, schema ownership and wire rules"
description: "Define bounded language-independent records without forcing a runtime dependency."
tags: ["contracts"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-PROTOCOL"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE", "SP-COMMANDS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-JSON", "SRC-SCHEMA", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-SCHEMA", "resource": "https://json-schema.org/draft/2020-12", "title": "JSON Schema Draft 2020-12"}, {"id": "SRC-JSON", "resource": "https://www.rfc-editor.org/rfc/rfc8259", "title": "RFC 8259 JSON"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Protocol, schema ownership and wire rules

## Contract ownership

All canonical JSON schemas live in this directory. Do not create another manually maintained `schemas/` root with copies. SDK packages and docs may project these files, carrying input digests. Product implementation reads the same versioned contracts or generated bindings.

The fixture schemas cover observation, snapshot, event, settings, scene, theme, command, capability, evidence and handoff records. They are experimental contracts, not proof of a complete native vertical slice. Scene/command/capability 0.2 coexist with preserved 0.1 migration inputs; [version policy](versions.md) identifies their separate compatibility obligations. Domain-specific additions require registry/fixture updates and compatibility review.

## Numeric and text rules

UTF-8 is the interchange encoding. Reject duplicate JSON keys and non-finite numbers. Encode uint64 counters, nanosecond times and other precision-critical large integers as canonical non-negative decimal strings, without leading zeros except `0`. Small bounded layout values can be JSON numbers. RFC 8259 explains the interoperable precision limits of common JSON numeric implementations.[^SRC-JSON]

Timestamps use explicit UTC offsets and durations specify units. Monotonic times are meaningful only inside their producer epoch. Identifiers are opaque and case-sensitive unless their contract explicitly says otherwise. Never compare them through locale-specific casing.

## Framing and limits

The experimental [local transport](transport.md) fixes four-byte big-endian length framing, a 1 MiB hard payload ceiling, handshake/version rules, authenticated roles, deadlines and bounded request retention. NDJSON export uses one JSON record per line, UTF-8, LF, and a maximum line length. An incomplete final line is not a valid event. Large exports page or stream bounded chunks rather than allocate the entire history.

An initial full snapshot plus deltas includes producer epoch and sequence/generation. On gaps, epoch changes or failed validation, request resynchronization. Unknown optional additions do not mean a client can execute an unknown command. Consumers reject unsupported mandatory feature versions.

## Error semantics

Return a stable error code, safe human explanation, operation/source identity and retryability classification. Do not expose secrets, raw internal paths or unbounded device strings in protocol errors. Missing data has a status, not a synthesized zero. Partial responses identify omitted scopes.

## Validation scope

Draft 2020-12 schemas provide shape validation; the bundled tooling validates positive/negative examples offline with the declared validator dependency.[^SRC-SCHEMA] Native protocol implementations must additionally pass semantic and adversarial conformance tests. The Python check is not an endpoint library and is not shipped with SysPane.

[^SRC-JSON]: RFC 8259, JSON interoperability and numeric precision.
[^SRC-SCHEMA]: JSON Schema Draft 2020-12, selected dialect.

## Strict local checking

The checker enforces offset-bearing date-time values even when optional format
packages are absent. This profile accepts seconds 00 through 59; leap seconds must
be normalized with source provenance before interchange. Unknown schema references
fail locally. Transport/runtime conformance remains separate from JSON fixtures.
