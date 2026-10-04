---
type: "SysPane Specification"
title: "Configuration persistence and recovery"
description: "Make accepted, durable and activated configuration generations distinct."
tags: ["architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-PERSISTENCE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMMANDS", "SP-SETTINGS"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Configuration persistence and recovery


## Experimental storage contract

Use bounded immutable generation directories for settings, scene and referenced
theme/preset identities. A manifest binds each document's version, revision, digest
and transaction/request identity. One current-generation record selects the bundle;
readers must never assemble documents from unrelated generations. The storage adapter
reports whether its filesystem profile can establish durable replacement.

Write a staging generation, validate hashes/closure and current authorization,
flush documents and manifest where supported, then compare expected document and
policy revisions under the writer lock. Publish the generation pointer using the
profile's tested replace/flush sequence. Report `durable` only after all required
storage acknowledgements. Otherwise expose accepted/unsaved state explicitly.
Do not silently fall back to a weaker filesystem guarantee.

## Recovery and activation

At startup select the last complete validated committed generation. Incomplete
staging is never current. A corrupt pointer uses the last verified committed record
with a diagnostic; do not guess the newest directory by modification time. Retain
the previous generation through activation and recovery according to a bounded
policy; never prune the only recoverable accepted state.

Crash after persistence but before activation resumes reconciliation against that
generation and today's policy. Resource preparation may fail without replacing the
old active presentation. Per-component activated/pending/degraded states remain
visible. Restrictive policy stops prohibited work and disclosure before cosmetic
activation finishes; rollback/undo cannot restore revoked authorization.

External text edits compare the original document digest and revision. Preserve
comments or write a scoped override; conflicts do not silently overwrite either
writer. Full/read-only/removed media leave a useful inspector and explicit unsaved
state. Configuration commit records, telemetry journals, setup receipts and AIDE
evidence are different stores with different retention.

The exact filesystem primitive sequence remains a per-target experiment. Inject
interruption at every transition, including after pointer publication and before
activation. Accept only an old or new coherent bundle, never a mixed one. This
document specifies recovery behaviour, not a proven fsync implementation.
