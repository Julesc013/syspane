---
type: "SysPane Decision"
title: "Use one validated operation system"
description: "Decision proposal: GUI, desktop editor, CLI and API submit the same typed revisioned transactions."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-006"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMMANDS", "SP-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Use one validated operation system

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

GUI, desktop editor, CLI and API submit the same typed revisioned transactions.

## Context

File-format equivalence alone does not prevent validation drift or concurrent edit loss.

## Consequences and verification

Implement preview/conflict/commit/activation separately and test GUI/CLI semantic equality.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
