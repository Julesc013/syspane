---
type: "SysPane Specification"
title: "Maintenance, recovery and update trust"
description: "Define repair and interruption outcomes before enabling managed mutations."
tags: ["setup"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-SETUP-LIFECYCLE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-INSTALL-OWNERSHIP", "SP-ARTIFACTS"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Maintenance, recovery and update trust


## Lifecycle

Discovery and plan are read-only. An installation-scoped lock serializes apply and
binds the plan to source/target identities and current ownership. Quiesce affected
components, stage and verify the full replacement closure, record recovery state,
then commit through the designated owner. Expose planned, applying, committed,
recovering, failed and partially-applied states with exact effects; return code alone
does not prove file/process/permission invariants. Do not leave the ordinary UI elevated.

Repair restores owned payload for an identified release from a verified intact
source. It does not upgrade, migrate data irreversibly, change policy or erase user
content. Upgrade/downgrade includes document compatibility planning, staged verification
and a tested rollback path. Uninstall removes owned components while preserving
unknown/modified resources and user data. Purge and relocation each need their own
explicit plan and authority.

A damaged executable cannot be its only repair source. Use an independent maintenance
composition and offline recovery payload. Self-maintenance hands off before replacing
running code; provider support and native file-lock behaviour must be tested. On
interruption, inspect the journal and observed effects before resuming/reversing;
never assume all-or-nothing effects without evidence.

Tests interrupt every phase, change files between plan/apply, overlap install attempts,
exhaust disk, revoke privilege and remove portable media. Inspect exact owned files,
retained data, permissions, processes and current policy afterward. One operation's
qualification does not enable every other operation or target.

## Acquisition and trust

Start with verified offline packages. Automatic downloading/updating remains disabled
until channels, trusted metadata roles/keys, signature thresholds, rotation/revocation,
expiry, target binding, anti-rollback and freeze handling are specified and tested.
Evaluate a pinned established update framework as a design candidate; no framework
or signing key is adopted by this document. A matching checksum alone is insufficient.

Offline import reports which origin/freshness checks were possible and cannot silently
disable freshness checks while claiming live-update equivalence. Code, document
migrations, presets and providers are distinct operations. Preserve a last-supported
historical artifact with source/provenance where licensing allows; do not imply an
obsolete OS security warranty. Public release still needs explicit license/IP,
security intake, supported-version and authorized publication decisions.
