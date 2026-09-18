---
type: "SysPane Provenance"
title: "Source disposition and superseded guidance"
description: "Preserve design lineage without reintroducing rejected assumptions."
tags: ["references"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-DISPOSITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-AUTHORITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
---

# Source disposition and superseded guidance

## Source hierarchy

The current user's explicit decisions control the project direction. Earlier assistant documents are historical inputs. They contain useful telemetry and recovery concepts, but also proposals the user expressly rejected and unsupported claims. The source register retains attachment names and SHA-256 hashes; originals are not bulk-published into this public bundle.

## Dispositions

| Historical idea | Current disposition | Reason |
|---|---|---|
| Desktop Info initial renderer/collector dependency | rejected | user requires a greenfield owned persistent surface |
| Workshop-fleet-only identity; local host unimportant | rejected | user explicitly needs rich local operational awareness |
| GPO wallpaper change or stamped bitmap | rejected | preserve configured corporate wallpaper |
| One raw Win32 binary automatically covers every Windows | rejected | API, runtime, shell and deployment qualification differ |
| Zero CPU/energy or universal tiny memory claims | rejected | no measurements support them |
| Every metric can use zero polling | rejected | rates require interval sampling; events require reconciliation |
| Sixteen adapters and one address per family | superseded | bounded dynamic collections, graph identity and complete addresses |
| One enum for all validity; commit equals pagefile usage | superseded | orthogonal observation state and distinct memory quantities |
| WorkerW call once guarantees persistence | superseded | host lifecycle and external temporal acceptance |
| GDI alone solves XP/7 transparency | unverified candidate | older host/presentation investigation required |
| One universal top-level parent for every entity | superseded | typed relationships and projections |
| Delay GUI/editor and XP/7/Linux/macOS until much later | rejected | initial parallel native and unified-editing campaign |
| Arbitrary in-process plugin framework | deferred/restricted | declarative and isolated extensions first |
| AIDE has only two commits/two-line README | not supported by inspection | pinned main contains substantial protocol/knowledge work |
| AIDE future runtime already does every requested action | unverified | actual consumer binding and evidence required |
| `src/` or many competing top-level implementation trees | rejected | user chooses one `source/` tree |
| Wiki/chat as independent requirements store | rejected | repo-native canonical specs with projections |

## Retained concepts

Typed observations, separate state/history, explicit unavailable/stale values, event-first network collection, hardware scope, source provenance, offline use and isolated optional privilege are retained and refined. WYSIWYG editing, native GUI completeness, portable scenes/commands and early platform breadth derive from the later conversation rather than the original attachments.

## Added design proposals

The precise directory map, SysPane metadata profile, requirement/test IDs, JSON schema shapes, fixture choices and Python tooling are newly authored implementation proposals in this delivery. They are not quoted user decisions or existing AIDE contracts. Review can refine them without erasing the accepted product constraints.

Public technical facts were checked against the sources listed in `sources.json` where used. Platform-specific details not reverified here are framed as candidates/experiments rather than shipping support statements. Do not copy unsupported numerical estimates or legal conclusions from the historical files into the product documentation.
