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
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
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

## Concrete initial 0.2 operations

Command 0.1 is preserved. [Command 0.2](command-v0.2.schema.json) supports the same
descriptor-generated `settings.set` operations and `scene.replace` carrying a scene
0.2 draft at the expected revision. Replacing a scene is atomic authored-state work;
it does not replace telemetry or bypass policy. Fine-grained hierarchy/binding/reset
operations require a future versioned contract; GUI prototypes may produce the same
validated whole-scene replacement.

The transaction coordinator owns the expected generation for affected settings and
scene documents; drafts carry that base revision, then successful commit assigns a
new revision. Only one scene replacement per request is admitted. Validate the
complete candidate, including hierarchy and policy, before publication.

[Command 0.3](command-v0.3.schema.json) additionally selects the exact resource
closure. [Command 0.4](command-v0.4.schema.json) retains that envelope and accepts
scene 0.2 or 0.3 replacement. The [content package](../delivery/packages/w-09-scene-content.md)
defines typed widget content, validation and explicit migration. Older commands
cannot carry new scene replacements; a resource-bound settings-only command 0.3
preserves an existing scene 0.3. No command version implies visible activation.

[Persistence](../architecture/persistence.md) owns generation recovery;
[transport](transport.md) and [command results](command-result.schema.json) distinguish
accepted/stored/durable/activated/visible, cancellation and result retrieval.

Settings defaults and overlapping command constraints derive from the initial
registry. Check current policy during prepare, commit and activation. Tightening
policy revokes prohibited work/disclosure independently of slow cosmetic activation.
