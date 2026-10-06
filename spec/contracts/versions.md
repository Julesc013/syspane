---
type: "SysPane Specification"
title: "Contract versions and migration"
description: "Keep bundle, documents, wire, ABI, content and provider identities independent."
tags: ["contracts"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-VERSIONS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROTOCOL", "SP-CHANGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Contract versions and migration


The October documentation bundle is 0.2.0. The OKF authoring profile remains
`syspane-spec/0.1.0`; that profile identifies frontmatter conventions, not runtime
compatibility. Product releases, settings/scene/theme documents, wire protocol,
embedding ABI, content packages, target revisions and upstream providers each have
their own version and compatibility obligations.

Existing 0.1 document schemas/fixtures retain their identities. Scene and command
0.2 add hierarchy, portable binding and whole-scene transactions without silently
changing 0.1 acceptance. Versioned schema filename suffixes identify their document
version; unsuffixed schemas retain 0.1.0 IDs. Command 0.3 adds immutable resource
selection. [Scene content](../delivery/packages/w-09-scene-content.md) adds scene
0.3 and command 0.4 without changing older schemas or their accepted payloads.
The reserved
`https://schemas.example.invalid/syspane/` namespace is deliberately non-resolving,
with a local-only registry. It is not a claimed owned web domain or a URN. Select a
controlled stable public namespace and migration aliases before SDK stabilization.

Unknown optional extension fields survive round trips inertly within bounded bytes,
depth and cardinality. Unknown required features, operations, document major versions
or executable permissions fail before activation. Optional does not mean executable.

Migrate by copying, validating and previewing the candidate with a loss/remapping
report, then committing through the common operation path. Keep the original and
source schema version. Do not treat repair as consent to irreversible data migration.
Downgrade checks both binary and document compatibility; retaining an old executable
alone is not rollback. Policy is always re-evaluated at the destination.

Publish old/new fixtures, compatibility tables and independent consumer results
before claiming stable contracts. Experimental schemas do not imply installed SDK
support or native implementation. Schema validation and native acceptance evidence
remain separate.

Experimental [measured telemetry](../delivery/packages/w-25-measured-time.md) adds
observation/snapshot/telemetry 0.2 as one explicitly selected triple plus the
`telemetry.measured-time` feature. It carries original measurement counts in a
qualified shared native domain; consumer-local scope is never serialized. Version
changes cannot silently discard same-epoch replay/tombstone history. Existing 0.1
documents remain inventory-capable and do not acquire implicit measurement times.
