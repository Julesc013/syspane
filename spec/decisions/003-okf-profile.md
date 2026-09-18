---
type: "SysPane Decision"
title: "Use pinned OKF v0.2 with a local authoring profile"
description: "Decision proposal: Use Markdown, YAML-frontmatter JSON-flow values and stable sp_id metadata."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-003"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-OKF", "SP-AIDE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Use pinned OKF v0.2 with a local authoring profile

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Use Markdown, YAML-frontmatter JSON-flow values and stable sp_id metadata.

## Context

A vendor-neutral readable bundle avoids a required database while preserving strict local linting.

## Consequences and verification

The checker is not a universal YAML/OKF implementation; AIDE v0.2 consumption is not presumed.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
