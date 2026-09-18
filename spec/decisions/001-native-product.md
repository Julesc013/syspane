---
type: "SysPane Decision"
title: "Own the complete native vertical stack"
description: "Decision proposal: No Desktop Info or other display engine is a required component."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-001"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-CHARTER", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Own the complete native vertical stack

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

No Desktop Info or other display engine is a required component.

## Context

The user rejects disappearing desktop overlays and requires native control over collection, hosting, editing and recovery.

## Consequences and verification

Build the first working native pane and independently test reveal persistence before promising broader support.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
