---
type: "SysPane Specification"
title: "System architecture and dependency contracts"
description: "Compose a portable semantic engine with native collection, interfaces and desktop hosts."
tags: ["architecture"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-ARCHITECTURE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-CHARTER", "SP-AUTHORITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# System architecture and dependency contracts

## System context

SysPane consumes local operating-system state and, when explicitly allowed, registered workshop endpoints. It produces a passive operational wall, a diagnostic inspector, history and structured exports. Native UI commands change settings and scenes, not the observed operating system. AIDE is outside this runtime boundary.

```text
OS/provider indications + scheduled measurements
                     |
             bounded acquisition planner
                     |
           semantic store and reconciliation
              /                 \
     evidence/history        presentation projection
                                   |
                       layout -> renderer -> native host

Native settings / desktop editor / CLI / local API
                     |
        command validation + policy + transaction store
                     |
       settings / scenes / themes / consumer demand
```

## Component contracts

| Component | Owns | Forbidden dependencies |
|---|---|---|
| Model | Identity, typed values, relationships, generation semantics | OS handles, fonts, windows, provider SDK objects |
| Runtime | Demand aggregation, scheduling, reconciliation, source health | Rendering, GUI control state |
| Commands | Validation, revision checks, transaction records | Direct hardware manipulation |
| Configuration | Typed persistence, policy merge, migrations | Independent UI-specific setting truth |
| History | Bounded records, rotation, checkpoints, replay | Invented events or implicit remote export |
| Presentation | Projection, layout and rendering contracts | Direct collector queries |
| Desktop adapter | Window/shell placement and recovery | Telemetry interpretation |
| Native interfaces | Platform controls and accessibility | Bypassing the command/policy system |
| Providers | Native acquisition and provenance | Assigning their own privileged trust level |

CMake target dependencies enforce these boundaries. Unit tests use fake clocks, sources, stores, process hosts and rendering sinks. Global mutable singletons are not a substitute for lifecycle ownership. Prefer explicit composition and scoped instances.

## Four documents, two control contracts

Telemetry, settings, scene and theme have separate revisions and serialization contracts. Commands and capabilities/policy govern operations. A telemetry generation does not increment a scene revision. Moving a widget does not restart an unrelated collector. The same CLI and GUI operation receives the same policy and validation result.

## Scope and scale

Each producer has an identity and boot/session generation. Local host, container/guest, remote asset and application session scopes remain distinguishable. Names, drive letters, interface indexes, serial strings and IP addresses are attributes, not universal durable IDs.

Initial components can be libraries linked into native binaries. An internal module boundary does not require a DLL or microservice. Introduce a process boundary for measurable failure, permission, threading or platform-awareness isolation, not for every class.

## Portability acceptance

A second platform should exercise the semantic contracts early. Keep source acquisition and shell-host facts native. Do not encode Windows NCSI as a portable truth about Internet access or impose Windows processor-group semantics on every OS. Exporters may map to external standards through versioned adapters without surrendering internal meaning.

## Completed boundary definitions

The observation/presentation path, authored-state transaction path and installation
path have separate authority. [Roles and composition](composition.md) define selected
components; [recovery](recovery.md) keeps a minimal diagnostic path independent;
[persistence](persistence.md) binds document generations without mixed recovery.

Settings, scenes, themes, presets, policy and extension manifests are separately
versioned. [Configuration resolution](../experience/configuration-resolution.md)
owns precedence. [USK](../setup/contract.md) is a maintenance-only provider binding;
ordinary controller, surface, collector and saver startup must not depend on it.
