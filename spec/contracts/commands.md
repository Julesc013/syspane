---
type: "SysPane Specification"
title: "Commands, transactions and activation"
description: "Unify editing, native settings, CLI and policy through validated operations."
tags: ["contracts"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-COMMANDS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-STATE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Commands, transactions and activation

## Command envelope

A request carries a request ID, expected document revision, relevant policy generation and typed operations. Each operation identifies a stable target and typed arguments. Initial operations include setting a property, adding/removing/moving/resizing a widget, binding a field, applying a theme and changing a display assignment.

The controller resolves authorization from the authenticated caller and policy, never from a caller-supplied `approved: true`. A request can ask for preview or commit, but neither mode bypasses schema/semantic validation. Exports and diagnostics use separate read operations.

## Transaction stages

`parse → normalize → schema validation → semantic validation → policy evaluation → resource preparation → revision compare → durable commit → activation`. Preparation failures leave the accepted document unchanged. Where activation cannot be atomic across providers, report per-component activation state and retain a coherent accepted generation with explicit pending/degraded outcomes.

Define the commit boundary and recovery journal so crash after persistence but before activation is reconcilable. Do not conflate “stored”, “activated”, “visible” and “durable”. A configuration transaction does not claim simultaneous physical state across hardware sources.

## Conflicts and idempotency

An expected revision mismatch returns a conflict with bounded changed-path metadata. No blind last-writer-wins default. Reusing a request ID with identical payload returns its recorded result within a bounded deduplication window; reusing it with different payload is rejected. Expired deduplication state is explicit in the protocol.

Undo records reversible authored changes and their required base revision. A restrictive policy update may prevent reapplying an old state. Undo never runs an inverse hardware action, uninstalls software, or purports to reverse historical observations.

## Semantic validators

Validate target existence, graph cycles, resource and widget limits, references, supported operation types, units, monitor assignments, extension capabilities and policy. JSON Schema describes structure but cannot substitute for these rules. A valid JSON payload may still be inadmissible.

## Evolution

The provided 0.1 schemas and fixtures are experimental contracts. Publish a compatibility table and migration fixtures before stabilizing a public version. Unknown optional annotation fields can be preserved; unknown required operations fail with a precise error. Do not reuse an operation name with changed meaning under the same version.

## Acceptance

Exercise concurrent editor/CLI edits, malformed input, unknown operations, denied changes, partial activation, duplicate requests, restart after commit, rollback/undo and policy changes during a draft. Operation-equivalence tests compare canonical authored state, not the order in which native controls happened to fire callbacks.
