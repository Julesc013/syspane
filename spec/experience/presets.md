---
type: "SysPane Specification"
title: "Preset and content admission"
description: "Compose versioned documents without granting authority or losing local edits."
tags: ["experience"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-PRESETS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-CONFIG-RESOLUTION", "SP-SDK"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Preset and content admission

The bounded [content resolution package](../delivery/packages/w-08-content-resolution.md)
defines exact manifest/document pin semantics, entry names, closure bounds and
preset composition for the first executable preview. Its implementation does not
qualify archive import, durable resource installation or rendering.


Presets reference versioned scenes, themes and permitted setting defaults by
identity and digest. Shipped presets are immutable; edits produce a user derivative
or override. Their pinned single-parent inheritance follows
[configuration resolution](configuration-resolution.md). Local binding maps, histories,
credentials, observations, installation receipts and runtime selection are excluded
from default portable export.

The [preset](../contracts/preset.schema.json) and
[content package](../contracts/content-package.schema.json) contracts describe identity,
versions, required/optional capabilities, dependencies, asset closure and hashes.
Import first validates bounded size, depth, paths, media types, decompressed size,
case collisions and dependency cycles. Package-relative paths cannot escape the
admitted root, follow symlinks or resolve absolute/remote assets. Undeclared executable
content is rejected. A digest proves identity, not publisher trust.

Preview additions, overrides, unavailable optional content, required-capability
refusals, privacy effects and any migration loss. Missing optional widgets remain
inert placeholders with authored data retained. Required unknown behaviour blocks
activation. No import enables probes, export, code, elevation, helper installation
or autostart; feature intent is not a grant. Existing policy constrains all content.

Executable providers use a separate
[extension manifest](../contracts/extension-manifest.schema.json) and explicit admission.
Requested permissions, target/contract compatibility, resource quotas, source and
artifact identity, update/revocation policy and actual isolation are checked before
execution. Signatures do not confer built-in provenance or extra rights. Updates
requiring more authority need a new admission; disable/revoke drains demand and
publishes truthful source status. No arbitrary in-process third-party libraries in
the first stable runtime.

Initial package schemas define metadata and limits, not a working archive importer
or installed SDK. Native decode/path/permission/update tests remain release gates.
