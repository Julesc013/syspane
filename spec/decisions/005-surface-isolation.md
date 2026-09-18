---
type: "SysPane Decision"
title: "Isolate the Windows surface process"
description: "Decision proposal: Controller state/history/inspector survive a failed desktop host or renderer."
tags: ["decisions"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ADR-005"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROCESSES", "SP-WINDOWS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Isolate the Windows surface process

## Status

Proposed baseline decision. User-established constraints are preserved; newly authored implementation detail awaits review. This is not a human approval record.

## Decision

Controller state/history/inspector survive a failed desktop host or renderer.

## Context

Private shell lifecycle and documented cross-process DPI consequences require containment.

## Consequences and verification

More than one process is acceptable inside a standalone native application package.

A change to this decision requires an impact review of the referenced concepts, requirements, contracts, tests and publication mappings. Keep this record and add a superseding decision rather than rewriting history to hide the earlier choice.
