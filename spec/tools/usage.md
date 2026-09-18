---
type: "SysPane Guide"
title: "Specification tooling and validation scope"
description: "Run deterministic checks, context export and safe integration without AIDE."
tags: ["tools"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-TOOLS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-OKF", "SP-CONTEXT", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Specification tooling and validation scope

## Commands

From the repository root, use `python spec/tools/specctl.py`. An explicit `--root PATH` before the subcommand checks another spec bundle. Python 3.11+ is a development prerequisite; it is not shipped as the SysPane runtime.

| Subcommand | Actual operation |
|---|---|
| `validate` | strict JSON/frontmatter, IDs, references, local links, work DAG and catalog structure |
| `validate --schemas` | additionally run Draft 2020-12 validation and selected semantic invariants on paired fixtures |
| `generate` / `generate --check` | write/check deterministic indices, concept catalog and traceability |
| `verify-integrity` | compare delivered file bytes to the explicit SHA-256 inventory |
| `seal` / `seal --apply` | preview/write a new hash inventory after validation and regeneration |
| `context --topic NAME --max-chars N --out PATH` | export whole required files and a filtered acceptance slice, bounded by characters |
| `impact PATH_OR_ID` | conservative dependent spec/requirement/test/work candidates |
| `work --ready` | dependency-ready planned work, not an execution grant |
| `search WORD` | simple local concept search without embeddings or a server |
| `bootstrap --repo PATH` / `--apply` | preview/create only missing reviewed root integration files |

## Limitations

The frontmatter parser intentionally accepts JSON-flow YAML values only. It rejects YAML aliases/tags and duplicate fields; it is not a general OKF/YAML validator. Link checks cover ordinary inline Markdown links and supported heading slugs outside fenced blocks. Reference-style links, embedded HTML and sophisticated Markdown extensions are not claimed as fully parsed.

Schema validation requires the pinned development dependencies. Missing dependencies fail explicitly. Schema identifiers use a non-resolving example domain; references are registered from local files, with no network resolver. Structural JSON Schema and selected semantic fixtures do not prove the native runtime algorithms.

Context packet budgets count Unicode characters, not provider tokens. Mandatory material is never truncated; an insufficient budget fails. Optional documents are listed when omitted. The packet records Git state only when a real local checkout can be inspected. Do not place disposable context inside canonical `spec/`.

## Bootstrap safety

Use a trusted, quiescent directory controlled by the developer. Preview validates all destinations; apply refuses conflicting content, path escape and symlinked targets. Re-running is idempotent when files match. This is not a hardened boundary against hostile concurrent replacement of parent directories. It never runs Git, installs dependencies/services, modifies desktop settings or grants privileges.

The CI template is optional and requires review before copying/pushing it. It uses a pinned checkout identity and a hosted specification-only job; no privileged self-hosted/native lab or publication credentials are configured. Downloading dependencies is done only when that reviewed CI workflow runs, not by bootstrap.

## Updating the bundle

Edit canonical inputs, run `validate --schemas` and tooling tests, regenerate indices, inspect changes and explicitly reseal when publishing a new bundle. Resealing changes only hashes; it cannot update a native test outcome or fabricate human review. `generated/validation-report.json` describes the delivery test run and must not be silently presented as evidence for later modifications.
