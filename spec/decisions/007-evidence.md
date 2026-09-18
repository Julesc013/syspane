---
type: "SysPane Decision"
title: "Separate specification success from product qualification"
description: "Decision proposal: Planning and schema checks never produce a native compatibility pass."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-007"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-TESTING", "SP-ORACLE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Separate specification success from product qualification

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Planning and schema checks never produce a native compatibility pass.

## Context

Internal visibility flags and fabricated test results can falsely satisfy the core requirement.

## Consequences and verification

Use external temporal desktop evidence and exact source/environment identities.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
