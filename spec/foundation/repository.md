---
type: "SysPane Specification"
title: "Repository architecture and ownership"
description: "Keep product source, specification, publication and control-plane records distinct."
tags: ["foundation"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-REPOSITORY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Repository architecture and ownership

## Root responsibilities

```text
syspane/
  README.md              Product homepage; stable user-facing identity
  AGENTS.md              Short cross-tool work router, not the full specification
  CLAUDE.md              Imports AGENTS.md; no copied policy wall
  spec/                  This canonical design/contract bundle and spec tooling
  docs/                  Authored publication-ready guides and generated reference pages
  source/                One implementation tree
  tests/                 Product test implementations and fixtures
  resources/             Native resources and translations
  configuration/         Shipped product scenes, themes and profiles
  sdk/                   Consumer examples and packaging, not duplicate implementations
  packaging/             Portable and managed packaging
  tools/                 Product developer utilities, only when needed
  .aide/                 Admitted control records/binding; not a copied AIDE engine
  .github/               Repository/CI integrations
```

All canonical machine contracts live in `spec/contracts/` at this stage. Do **not** also create root `schemas/`, `docs/specifications/`, or `.aide/schemas/` copies. A build can package or generate a copy, with provenance and a regeneration check. `source/api/` owns the eventual public C header; the supplied experimental header is a design fixture that must be moved through a recorded ownership migration when implemented.

## Source decomposition

Use cohesive build targets for `model`, `runtime`, `commands`, `configuration`, `history`, `scene`, `presentation`, `protocol`, `diagnostics`, platform adapters, collectors and native interfaces. Platform services supply clocks, waits, files, IPC and handles; they do not own product semantics. Native GUI and shell adapters can use the platform's language/toolkit while sharing operation semantics.

Do not mirror private headers into `include/`. Do not split all code into arbitrary `modern/legacy` directories. Compile target profiles from reusable components and small capability-specific adapters. Avoid every-file-per-trivial-class fragmentation and giant utility modules: split by independent responsibility, test boundary and reason to change.

## Build outputs and assets

Ignore `out/`, local caches, `.aide.local/`, private recordings and `dist/`; do not commit release binaries. Tests needing a large artifact record a digest and retrieval method, not a volatile machine path. Imported assets need provenance and redistribution review. Do not copy font files into this specification archive.

Shared build scripts, dependency locks, component manifests and target profiles live
under `source/build/`. The user retired the root build-support directory on
2026-10-08; it must not return to the remote tree. Machine bindings belong in
`out/campaign/workspace.json`, populated from the versioned example. Generated logs,
source snapshots, native recordings and archived evidence belong in ignored
`out/evidence/` or other owned `out/` subtrees, never in the source tree.

Keep compact checkpoint summaries, test commands and limitations in `spec/delivery/`.
Historical evidence locators describe local archives, not portable repository links.
A fresh checkout must build and run deterministic tests without those archives;
native qualification produces its own source-bound prerequisite records. Preserve
existing failures locally when relocating records. The active workspace allowance
continues to exclude archived evidence, as it did before the location change;
report retained archive bytes separately rather than silently enlarging the quota.

## Branches and history

Proposed roles: `main` for integrated accepted state, `dev` for active integration, `task/<work-id>-<slug>` for bounded changes; release/hotfix branches only when operationally needed. The baseline was imported on `main` at `91e10b8b7a8a5da5ab2d93e8cdcbaade6aa0fbd9`. A `dev` branch is optional and has not been adopted by this documentation update; the user explicitly requested committing and syncing these amendments to `main`. Tooling supplied here does not create branches or commits.

Path identity must survive refactoring through aliases, release notes and compatibility tests. AIDE may plan a reorganization but cannot move a tree merely to match a fashionable template. Preserve authored README structure and keep volatile implementation progress elsewhere.

## October ownership decisions

Root `README.md` is the product homepage; `TODO.md` routes pending work rather than
duplicating the machine work graph. Keep `source/application/` and `source/desktop/`
as the established composition/host paths. [Composition](../architecture/composition.md)
defines dependency direction and the planned component manifest.

Use explicit checkout, build, cache and task roots with ownership markers, quotas,
retention and cleanup obligations. No recursive repository copies, unowned worktree
farms or invented drive-root output directories. Cleanup resolves and checks its
owned targets first. Builds and checks remain usable without AIDE.
