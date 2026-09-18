---
type: "SysPane Decision"
title: "Treat AIDE as a replaceable development control plane"
description: "Decision proposal: Pin real upstream contracts before admitting a consumer adapter."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-008"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AIDE", "SP-AGENTS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Treat AIDE as a replaceable development control plane

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Pin real upstream contracts before admitting a consumer adapter.

## Context

The future orchestration design is not the same as existing schema/runtime support.

## Consequences and verification

Preserve ordinary build commands, explicit grants, provider limits and durable evidence.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
