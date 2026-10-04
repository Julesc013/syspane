---
type: "SysPane Specification"
title: "Universal Setup consumer boundary"
description: "Keep provider qualification and maintenance authority outside normal startup."
tags: ["setup"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-SETUP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMPOSITION", "SP-RELEASE"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Universal Setup consumer boundary


SysPane owns product identity, selected components, payload manifests, native frontend
text, policy and recipes. Universal Setup (USK) supplies only its admitted public
ownership/transaction/verification/lifecycle operations through
`source/integrations/universal-setup/`. Do not copy its engine or repository structure
into SysPane. Link it only into the maintenance composition when needed.

The supplied reviews inspected USK README at
`2749a15b835a6c1c9968598a2b434d85809691ad` and describe an operator-acceptance/SDK
candidate. This is review provenance, not a live dependency pin, an API audit or
SysPane qualification. Before implementation, inspect the actual selected public
headers/schemas and bind exact source/artifact, SDK/contract versions and enabled
operation/platform evidence. Do not infer mutation readiness from SDK availability.

Read-only discovery and planning precede apply. Plans identify exact target identity,
component/dependency closure, payload/data/setup roots, changes, privileges, owner,
preconditions and recovery source. Apply rejects stale plans, changed targets or
unqualified provider operations. Native registry/shortcut/elevation/package-manager
integration remains unavailable until implemented and tested by the selected adapter.

Ordinary desktop, diagnostic, collector and saver launches work without USK. Setup
is never a side effect of viewing data or importing a preset. Public mutation stays
disabled until provider/profile/operation consumer tests pass in admitted disposable
roots. Product spec changes and this user-requested documentation sync grant no
installation, signing or provider activation authority.

Release work must instantiate a setup-binding schema from the actual inspected
upstream contract; inventing a provider-compatible API from README text is prohibited.
The pending executable binding and consumer harness are tracked in W-32.
