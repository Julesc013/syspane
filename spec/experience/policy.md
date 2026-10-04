---
type: "SysPane Specification"
title: "Policy and information disclosure"
description: "Constrain collection, retention and every presentation channel independently."
tags: ["experience"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-POLICY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-SECURITY", "SP-CONFIG-RESOLUTION"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Policy and information disclosure


## Authority and field classification

Protected machine/organization policy is authenticated by its native adapter,
not by a boolean in a caller document. The
[policy document](../contracts/policy.schema.json) is experimental data, not a grant.
It has a revision, scope, forced values/limits and role/channel disclosure rules.
User/session/portable preferences cannot weaken it. Missing required policy disables
restricted operations while preserving non-sensitive diagnostics.

Metric descriptors classify public, operational, sensitive or secret fields.
Unknown fields default to sensitive for unattended/export surfaces. Credentials
never belong in telemetry, presets or diagnostic bundles. Native peer/session
identity and destination are policy inputs, independent from compiled capability.

## Disclosure channels

Evaluate collection, retention and projection separately for desktop pixels,
inspector, saver/preview, accessibility, tooltips, clipboard, history, logs, support
bundles, extensions and explicit remote/export destinations. Filter before sending
data to a less-trusted consumer; hiding pixels after delivery is insufficient.
Saver defaults expose only public fields. Support bundles use consistent synthetic
identifiers when joins are useful and show the redaction preview before export.

Lock, session switch and live revocation stop prohibited collection/subscriptions,
clear affected in-memory projections and prevent new exports. Existing retained
records follow explicit retain/restrict/purge policy with an auditable outcome;
masking a display does not erase an old log. Purge requires its own authority.
An old accepted configuration never revives a revoked permission.

## Defaults and deployment

No default external listener, cloud traffic, remote scan, autostart, executable
extension or privileged helper. Probes and exports require explicit scope and
enablement; opening a native inspector is distinct from modifying OS state. Future
management actions need separate preview, authorization and recovery contracts.

Offline enterprise deployment uses the same policy and authored-state validation.
Test policy changes during draft/commit/activation, saver coexistence, tooltips and
assistive access, redacted exports and cross-session denial. Process separation alone
is not a sandbox or proof of information-flow enforcement.
