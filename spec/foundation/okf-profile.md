---
type: "SysPane Specification"
title: "OKF and the SysPane specification profile"
description: "Use upstream OKF without inventing a new universal knowledge format."
tags: ["foundation"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-OKF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-OKF", "SRC-AIDE"]
sources: [{"id": "SRC-OKF", "resource": "https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md", "title": "Open Knowledge Format v0.2"}, {"id": "SRC-AIDE", "resource": "https://github.com/Julesc013/aide/blob/aec53b1d3675f02e2fdd17cc718fdcff6cd4e9f3/README.md", "title": "AIDE README and OKF decision"}]
---

# OKF and the SysPane specification profile

## Selected format

The upstream specification inspected for this bundle is **OKF v0.2**, commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`. Its basic Markdown/type/frontmatter shape remains readable by the v0.1-style AIDE knowledge conventions inspected separately. This is not a claim that an AIDE v0.1 consumer implements the new provenance families.[^SRC-OKF]

Every concept is UTF-8 Markdown with YAML frontmatter. This project's stricter authoring profile uses one top-level key per line and JSON flow values, a subset of YAML, to enable small deterministic tooling without accepting executable tags, aliases or arbitrary YAML features. A general OKF reader may accept more YAML; `specctl` is a **SysPane profile checker**, not a complete general-purpose OKF validator.

`index.md` and `log.md` are reserved and are not concepts. Index files have no frontmatter except the bundle-root `okf_version` declaration. Logs have date headings, newest first. Regular relative links are used for GitHub rendering; OKF bundle-absolute links beginning `/` would be interpreted differently by GitHub's repository browser.

## Profile fields

| Field | Meaning |
|---|---|
| `type`, `title`, `description`, `tags` | Upstream metadata; human routing |
| `status` | OKF lifecycle, initially `draft` |
| `generated` | Producing actor and observed preparation timestamp |
| `sources` | Optional upstream provenance entries with `resource` and stable source IDs |
| `sp_id` | Stable project identity, independent of the OKF path-based concept identity |
| `sp_profile` | `syspane-spec/0.1.0` |
| `sp_authority` | `normative-proposal`, `informative`, `generated`, or `template` |
| `sp_requires` | Project IDs whose meanings must also be understood |
| `sp_review` | `unreviewed` until an accountable reviewer acts |
| `sp_sources` | IDs in the compact source register |

A file move changes its OKF concept path; retain its `sp_id`, update links and record old-to-new paths in `foundation/path-aliases.json`. Internal IDs are not invented public resolvable URLs. Do not put an unowned domain into `$id` fields; the schemas use versioned URNs and an offline registry.

## Prose and structured records

Use Markdown for reasoning, contracts, examples and runbooks. Use JSON for queryable registries, schemas, commands and bounded evidence records. Use NDJSON for append-oriented event interchange. Runtime TOML import is an optional human-facing representation of typed settings, never the only interface and never an alternative authority.

Do not put a second hand-maintained requirement catalog inside frontmatter. Do not encode the entire specification as JSON. The human and machine views must complement rather than transcribe each other.

## Extension and migration

Unknown OKF metadata is retained. The project checker may impose stricter local rules than OKF; label that distinction. No data-movement pipeline or cloud service is required to read this bundle. Migration to future OKF versions is a tracked change with compatibility fixtures and an updated pin, not an implicit upgrade when upstream `main` moves.

[^SRC-OKF]: [Pinned upstream OKF specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md), inspected 2026-09-17.
