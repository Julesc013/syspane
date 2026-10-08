---
type: "SysPane Handoff"
title: "Coherent authored profile and resource projection"
description: "Bounded authenticated reads connect the native command controller to a typed frontend receiver."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T20:30:41+00:00"}
sp_id: "SP-PROFILE-PROJECTION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-PROJECTION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Coherent authored profile and resource projection

The native configuration controller now serves configuration.profile through its
existing authenticated Sessions and independently watched policy sampler. The
command worker prepares immutable ProfileImage instances from the actual saved
documents and resource closure. AsyncCommands publishes a replacement only after
actual worker join; indeterminate storage or invalid authority withdraws it.

One controller-wide transfer pins one coherent revision while later commands may
commit. Each bounded response carries exact part identity, size, digest and cursor.
Package bytes remain immutable shared allocations. Reads do no filesystem work or
media hashing on the session loop. Existing control capacity is checked before
admission, and disconnect, expiry or policy loss drops the transfer and queued data.
Complete authoring data requires operational and sensitive inspector/accessibility
disclosure; mutation denial alone does not prevent an otherwise admitted read.

ProfileDownload validates envelopes, correlation, cursor progression, byte limits,
hashes, document/resource contracts and the selected package closure. It exposes no
partial UI state. Its effective policy contains only the console's disclosure rules,
forced values and capability restrictions; it is not native policy provenance.
The caller must invalidate the receiver and clear UI-held state on policy, producer
or connection loss. The saved revision remains separate from activation/visibility.

## Evidence

The fixed portable cases cover exact startup documents/packages, read-only and
forced policy, disclosure denial, negotiation/frame floors, one-slot contention,
foreign/expired cursors, queue pressure, revocation, pinned versus current revision,
actual-join admission and unknown storage outcomes. Receiver cases cover binary
content exceeding one frame, empty assets, corruption, wrong envelope/query/hash,
invalidation and a malformed header with a deliberately recomputed valid hash.

The independent Python native oracle reads real controller traffic and verifies
literal startup documents, every resource byte and on-disk generations. It proves
that an existing read stays at revision zero while a command commits revision one,
that a new read sees revision one, and that reconnect cannot adopt an old transfer.
Policy revocation and same-revision drift stop disclosure; a held policy read is
terminated by the independent absolute transaction watch.

All three development profiles configure/build, pass 47 portable checks (including
the sixteen new projection cases) and both component graph checks. The seven new
native cases and five existing controller/supervisor/command/recovery families pass
62 distinct cases in total. Specification validation covers 48 schemas and 166
fixtures; tooling reports 60 passing tests and two Windows symlink skips.

The [checkpoint](checkpoints/profile-projection.json) binds all executed checks,
source snapshots, native artifacts, archives and limitations. The first Linux build
stopped on a warning treated as an error; formatting was corrected. A coordinator
attempt then stopped before testing because its artifact list named a nonexistent
generated header. The list was corrected, and the original source archive and
coordinator failure remain preserved. Review tightened receiver capability ordering
and exact package-closure checks before final validation. Fixed package/case bytes
were unchanged. No failed attempt is replaced with a passing claim.

## Continue toward the native edition

W-08 remains in progress. Compose the actual controller/inspector frontend from the
verified installation owner, independently scheduled supervisor, authenticated client
and ProfileDownload. Resolve deployment/data/runtime ownership, retain the other
private helpers' exact installation closure, and connect native settings/editor,
telemetry, activation, import catalogs and recovery context. Preserve original
request identities across replacement and use reconciliation before retrying edits.

These native transfers exercise the shipped profile in the admitted ext4 laboratory;
maximum-size native transfer throughput is not qualified here. Larger/binary resource
assembly has portable checks, not a complete installed UI claim. Positive native
policy remains a dedicated test fixture; protected-policy deployment is unqualified.
Windows shared builds do not qualify historical OS behavior. All five complete
desktop editions, package/lifecycle evidence and original release gates remain open.
