---
type: "SysPane Guide"
title: "Implementation readiness and gates"
description: "Distinguish implemented specification checks from pending native and release work."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00"}
sp_id: "SP-READINESS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CURRENT"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied October 2026 audit inputs", "title": "October review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Implementation readiness and gates


The October revision closes bounded contract and documentation gaps. It does not
implement the native product. Existing stable identities remain; new meanings have
new versioned schemas or explicit work-scope refinement.

| Gate | Present as specification/checks | Pending implementation/evidence |
|---|---|---|
| Initial authoring | Rich initial settings descriptors, scene/binding/layout 0.2, result and handshake shapes | Runtime merge/resolution, migration, transport framing, persistence and native controls |
| Recovery/security | Independent diagnostic, lease, policy/disclosure and quota contracts | Fault harness, native peer authorization, revocation, measured budgets |
| Native profiles | Typed target/capability metadata and independent work units | Exact compiler/dependency profiles, component manifest, native builds and external desktop oracle |
| Content/SDK | Preset/package/extension metadata and buffer-result sketch | Bounded importer, dependency closure, extended theme/AST, installed SDK/ABI consumers |
| Saver | Role/lifecycle/privacy/ownership contracts | Native host adapters and preview/fullscreen/configuration qualification |
| Packages/setup | Names, paths, one-owner and recovery contracts | Actual release/component/setup manifests bound to inspected provider, offline packages and lifecycle tests |
| Public release | Provenance and qualification rules | Owner license/IP/support choices, native evidence, authorized signing/publication |
| Online update | Trust/admission requirements | Pinned metadata design, implementation and expiry/revocation/rollback qualification |

Do not block independent host probes on every future schema. Do not enable a feature
before its own unresolved boundary is closed. The [work graph](work-units.json) and
[risks](open-questions.md) name the resolving work. AIDE remains inactive; README-level
upstream observations are not consumer acceptance.
