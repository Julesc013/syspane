---
type: "SysPane Decision"
title: "Share meaning and operations, not every binary or pixel"
description: "Decision proposal: Portable C++17 engine with native platform adapters and reduced profiles where justified."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-004"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ARCHITECTURE", "SP-PLATFORMS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Share meaning and operations, not every binary or pixel

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Portable C++17 engine with native platform adapters and reduced profiles where justified.

## Context

Current and historical platforms differ in API, toolkit, security and deployment.

## Consequences and verification

Qualify separate build/runtime/profile evidence and avoid duplicated modern/legacy implementations.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
