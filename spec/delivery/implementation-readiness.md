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
sp_sources: ["SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied October 2026 audit inputs", "title": "October review inputs"}]
updated: {"by": "codex", "at": "2026-10-06T00:26:58+11:00", "scope": "Portable W-24 implementation checkpoint; native IPC authentication and desktop qualification pending"}
---

# Implementation readiness and gates


The October revision closes bounded contract and documentation gaps. It does not
implement the native product. Existing stable identities remain; new meanings have
new versioned schemas or explicit work-scope refinement.

| Gate | Present as specification/checks | Pending implementation/evidence |
|---|---|---|
| Initial authoring | Setting descriptors, scene/binding/layout 0.2, portable frame/handshake/preview checks | Runtime merge/resolution, migration, native transport integration, persistence and native controls |
| Recovery/security | Diagnostic/lease contracts and portable policy/disclosure/revocation/queue checks | Fault harness, native peer authorization, actual data-path revocation, measured budgets |
| Native profiles | Windows/Linux model and portable protocol build profiles, component ownership and executable checks | External desktop oracle, native transport/recovery, desktop builds and target qualification |
| Content/SDK | Preset/package/extension metadata and buffer-result sketch | Bounded importer, dependency closure, extended theme/AST, installed SDK/ABI consumers |
| Saver | Role/lifecycle/privacy/ownership contracts | Native host adapters and preview/fullscreen/configuration qualification |
| Packages/setup | Names, paths, one-owner and recovery contracts | Actual release/component/setup manifests bound to inspected provider, offline packages and lifecycle tests |
| Public release | Provenance and qualification rules | Owner license/IP/support choices, native evidence, authorized signing/publication |
| Online update | Trust/admission requirements | Pinned metadata design, implementation and expiry/revocation/rollback qualification |

Do not block independent host probes on every future schema. Do not enable a feature
before its own unresolved boundary is closed. The [work graph](work-units.json) and
[risks](open-questions.md) name the resolving work. AIDE remains inactive; README-level
upstream observations are not consumer acceptance.

## Repository-only implementation

The current baseline is sufficient to begin an admitted foundation/investigation
campaign. It is not a complete executable contract for unattended implementation
and release of every edition. Close the relevant package before implementing it;
retain engineering choices and native experiments where evidence is required.

[Work-package closure](work-packages.md) defines the required scope, interfaces,
failure/resource rules, decision authority, commands and completion evidence.
[W-01](packages/w-01-foundation.md) is the first detailed package, with concrete
model cases. Its runtime scope is now admitted and both development builds passed
their foundation cases; see [the handoff](foundation-handoff.md).
[Acceptance traces](../assurance/acceptance-traces.md) keep the original expectations;
only linked executed cases are claimed. [W-24's portable checkpoint](transport-handoff.md)
adds request-budget and protocol/policy cases. Native stream runners remain pending.

For W-24, finish native peer authentication, bounded I/O and real client/server
integration under its [package](packages/w-24-transport.md). The portable preview
slice closes role/state/ownership, queue and reservation limits; disabled features
still require their own closure before advertisement. For W-08/W-09/W-33, add exact merge, scene/layout, selector, preset and
recovery examples as those boundaries are admitted. Existing framing, persistence
and architecture decisions remain the starting point.

Use the proposed cold-start exercise to detect missing observable contracts.
Private implementation differences are permissible. Missing laboratories remain
blocked qualification. A finite release scope must identify exact profiles,
capabilities, packages, document versions, mandatory tests and deferred work before
claiming completion; the full product direction remains in the campaign.
