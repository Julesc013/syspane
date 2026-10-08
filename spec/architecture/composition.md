---
type: "SysPane Specification"
title: "Roles and component composition"
description: "Define dependency direction and optional runtime roles without product forks."
tags: ["architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-COMPOSITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-ARCHITECTURE", "SP-REPOSITORY"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Roles and component composition


## Roles, targets and capabilities

A role describes an instance's job; a target describes its build/runtime floor;
a capability describes implemented, qualified, currently available and authorized
behaviour. Consumer, technician and enterprise workflows select presets and policy,
not separate semantic engines. Not every role requires another process.

| Role | Responsibilities | Excluded authority |
|---|---|---|
| Desktop | Passive wall, inspector, native settings/editor, local state | Installation or arbitrary OS mutation |
| Console/Collector | Local observation, optional recording and explicit export | Mandatory GUI, shell host or setup provider |
| Saver/preview | Read-only filtered scene under native host lifecycle | Credentials, editing while locked, elevation |
| Saver settings | Native unlocked configuration through common commands | Implicit full-screen launch or setup |
| Diagnostic | Bounded health/profile inspection and safe launch | Loading failed optional dependencies |
| Maintenance | Explicit lifecycle operations through the installation owner | Resident telemetry/presentation duties |

## Source and build ownership

Retain `source/application/` for composition roots and `source/desktop/` for shell
hosts, matching existing work outputs. The audits' alternative `apps/` and `hosts/`
names are not additional trees. `source/platform/` owns clocks, files, waits and IPC;
`source/collectors/` owns acquisition; `source/interfaces/` owns native interaction.
`source/integrations/universal-setup/` is the sole product-owned setup adapter.

The model has no platform, provider, GUI or renderer dependency. Runtime consumes
typed model and service interfaces. Collectors publish model observations; commands
own authored changes; projection consumes accepted state; hosts own placement.
Composition roots select concrete adapters. Use in-memory typed structures inside a
process; serialize only at interchange boundaries. Private headers stay with owners.

Before source targets are admitted, a component manifest under `source/build/`
records ID, source owner, public/private interfaces, allowed dependencies, target
requirements, role membership and installed-file owner. Explicit CMake targets and
dependency checks enforce the graph. This is build metadata, not another build system.
Do not create empty source slots or permanent platform source forks.

## Compositions and closure

Windows retains controller and isolated surface binaries. Potentially hanging
providers and separately authorized privileged collection have their own bounded
lifecycle. A Linux shell bridge keeps blocking work outside the compositor. Other
platforms preserve contracts without copying the Windows process count.

The diagnostic composition must prove its smaller dependency closure. Desktop,
collector and saver launch cannot depend on USK, AIDE or a model service. Normal
endpoint packages omit test runners, build tools and unused optional roles.
Public C header ownership moves from the experimental sketch to `source/api/`
only with an explicit migration; installed SDK copies are generated artifacts.
