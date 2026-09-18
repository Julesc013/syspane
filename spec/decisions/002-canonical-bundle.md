---
type: "SysPane Decision"
title: "Keep spec, docs and source distinct"
description: "Decision proposal: Root spec/ owns intent/contracts; docs/ owns audience-oriented explanation; source/ owns implementation."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-002"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-REPOSITORY", "SP-DOCS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Keep spec, docs and source distinct

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Root spec/ owns intent/contracts; docs/ owns audience-oriented explanation; source/ owns implementation.

## Context

Multiple hand-maintained copies create drift and context waste.

## Consequences and verification

Generated indices and docs maps retain hashes and links; schemas have one canonical location.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
