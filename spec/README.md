---
type: "SysPane Guide"
title: "SysPane specification bundle"
description: "Start here to adopt, validate and use this repository-native specification."
tags: ["README.md"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-START"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: []
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-05T23:39:47+11:00", "scope": "Admitted model foundation; executed development checks, no desktop qualification or human review attested"}
---

# SysPane specification bundle

**SysPane — System Panel** is a native operational-desktop product family. Its flagship Windows surface remains visible behind desktop icons when the ordinary desktop is revealed, without changing the configured wallpaper. Native Linux and macOS/OS X editions, and early Windows XP/7 investigations, are part of the first implementation campaign.

This is an **experimental design and implementation baseline**. The repository now builds a typed model and development smoke program on identified Windows/Linux toolchains. It includes runnable specification tooling and synthetic contract fixtures. No usable desktop edition, historical operating-system compatibility, performance, security certification or upstream AIDE integration has been qualified.

## Adoption

This bundle is already imported at `Julesc013/syspane/spec/`. The October 0.2.0 amendment retains the 0.1.0 authoring profile and old document fixtures; see [audit disposition](delivery/audit-2026-10-04.md). Do not nest it under `docs/`, and do not copy the specification bodies into another canonical tree. Start with [the navigation index](index.md), [current state](delivery/current-state.md), [the reading routes](governance/context.md) and [the implementation campaign](delivery/roadmap.md).

From the repository root, run:

```sh
python spec/tools/specctl.py validate
python spec/tools/specctl.py generate --check
python spec/tools/specctl.py verify-integrity
python -m unittest discover -s spec/tools/tests -v
```

For complete JSON Schema fixture validation, install the reviewed development-only dependencies in an isolated environment and run:

```sh
python -m pip install -r spec/tools/requirements.txt
python spec/tools/specctl.py validate --schemas
```

Python is a **development tool**, not an endpoint runtime requirement. `python` means an available Python 3.11+ interpreter; `python3` or `py -3` may be the appropriate launcher. The reports under `generated/` identify their actual specification-tool execution environments. Windows tooling execution is not native SysPane or desktop qualification.

## Root integration without overwriting files

```sh
python spec/tools/specctl.py bootstrap --repo .
python spec/tools/specctl.py bootstrap --repo . --apply
```

The first command is a plan. The second creates missing, reviewed root integration files from `bootstrap/files.json`, refuses conflicting existing files, and never commits, pushes, installs a service, signs, deploys or changes repository settings. Inspect the plan before applying. Review the templates as executable supply-chain inputs before trusting any tooling in a newly received archive.

## Working on one task

```sh
python spec/tools/specctl.py work --ready
python spec/tools/specctl.py context --topic network --max-chars 42000 --out /tmp/syspane-network-context.md
python spec/tools/specctl.py impact spec/telemetry/network.md
```

On Windows choose a suitable writable output path instead of `/tmp`. Context output is an explicitly bounded projection with file hashes and omitted-file notices; it is not a new source of truth. Never instruct every subagent to read the entire bundle.

## Authority and review

Existing user decisions are preserved as design constraints. New implementation choices are **normative proposals** pending adoption and review. Every concept is marked draft; no human review or execution grant is fabricated. A maintainer can admit a bounded work unit without claiming every future platform contract is frozen. Normative proposal means “implement this once adopted”, not “already implemented”.

The bundled registry statements, detailed specifications, schemas and fixtures have different responsibilities; contradictions block integration rather than silently choosing one. See [authority](foundation/authority.md). Open questions are explicit, with the experiment needed to resolve them. The first campaign does not wait for all future standards to be finalized.

## Publishing and continuity

`docs/` is for polished, audience-specific documentation. `source/` is implementation. This `spec/` is the canonical design and contract bundle. `.aide/` will carry admitted development-control records after an actual AIDE binding is verified; it does not replace product truth. The wiki is a generated navigation surface, never a competing specification.

The [source register](references/sources.json) records the supplied materials and verification boundaries. Original transcripts are not bulk-copied into the public repository: they contain obsolete guidance, unnecessary private workshop context and non-authoritative assistant text. The [disposition register](references/disposition.md) preserves why those alternatives are not current.

## October implementation boundaries

New contracts cover composition, configuration resolution, portable scene/binding
0.2, persistence/recovery, policy, screensavers, target identity and setup ownership.
Descriptor-derived constraints and new synthetic fixtures are executable spec checks.
[Readiness](delivery/implementation-readiness.md) and the work graph identify what
still needs runtime implementation, native evidence or an owner decision.
