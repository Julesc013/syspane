---
type: "SysPane Specification"
title: "Progressive context and chat-mode continuity"
description: "Retrieve the smallest complete task context and keep results tied to repository state."
tags: ["governance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-CONTEXT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AGENTS", "SP-OKF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Progressive context and chat-mode continuity

## Navigation model

Read `README.md`, `delivery/current-state.md` and the relevant topic route before implementation. Directory indexes summarize nearby concepts. `generated/catalog.json` resolves stable IDs to paths and hashes; `generated/traceability.json` connects requirements, specs, tests and planned work. Neither generated file is an independent authority.

`tools/routes.json` defines a mandatory shared nucleus and topic-specific required/optional files. `specctl context` includes whole files, reports omissions, and fails when the required set does not fit the character budget. It never silently truncates a mandatory requirement or claims an exact tokenizer count. Larger text budgets can be selected explicitly when needed.

## Packet identity

Each packet identifies bundle version, source files and hashes, generation time, actual Git ref/dirty state when available, and omitted optional files. Outside a Git checkout it states that no commit was observed. A packet is a reproducible projection of particular bytes, not an evergreen memory dump.

Stable prefixes can reduce repeated prompt material, but provider cache behavior is not controlled by this repository. Measure accepted-work cost and latency rather than promising zero repeated input. Do not scatter volatile timestamps through every canonical file or regenerate the whole corpus for an unrelated edit.

## Chat read workflow

Supply the repository plus a commit/ref and the intended task. A connected GitHub reader resolves the actual ref, reads the start/current-state/route files, then fetches only the related specs and evidence. A URL alone does not preload the repository into ChatGPT. When tools are unavailable, upload the relevant packet or selected files with their manifest.

## Chat write/execute workflow

A read-capable connector does not imply write or execution capability. With an admitted write/runner adapter, submit a bounded patch/work unit and collect its actual result. Otherwise produce a unified diff or replacement bundle with explicit target ref, file list and validation instructions; a human or coding agent applies it. Never say a change was committed or a test ran when only a patch was drafted.

## Durable results

Accepted new design belongs in `spec/` with a decision/change record. Implementation belongs in `source/`. User guidance belongs in `docs/`. Execution/evidence belongs in the admitted control/evidence store. A chat handoff points to those records instead of becoming a competing task database.

Use `specctl impact PATH` for conservative impact candidates. It is a graph aid, not a compiler dependency proof and not permission to skip native tests. Scope decisions and cache validity remain explicit.
