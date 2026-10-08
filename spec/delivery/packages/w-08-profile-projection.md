---
type: "SysPane Work Package"
title: "Coherent profile projection over authenticated local sessions"
description: "Deliver saved authoring data and exact resources to the native frontend with bounded disclosure."
tags: ["delivery", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T20:09:57+00:00"}
sp_id: "SP-W08-PROFILE-PROJECTION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-CONTROLLER", "SP-W08-COMMAND-SESSIONS", "SP-POLICY", "SP-TRANSPORT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Coherent profile projection over authenticated local sessions

Connect W-08's real command owner to frontend reads. Preserve one transaction owner,
the existing command ledger and exact persisted documents. Add an immutable shared
ProfileImage prepared during controller startup or on its supervised command worker.
Publish its replacement only after the worker has actually joined. An open transfer
pins one committed image even while a later command commits. It never claims that
the image is activated or visible. Native reads, package hashing and image preparation
must not occur inside Sessions or GUI callbacks. An indeterminate store or invalid
owner exposes no new image. Legacy command owners need not implement this feature.

## Admission and disclosure

Negotiate configuration.profile, profile-request 0.1.0 and profile-result 0.1.0 with
a minimum frame ceiling of 12288 bytes. Missing required support fails handshake;
optional unsupported support is removed. No command version or write permission is
needed for a read. Only an authenticated native-granted console role may receive
the complete authored profile in this initial adapter. Require available policy,
profile.open and profile.read permission, and both operational and sensitive
disclosure on inspector and accessibility. Arbitrary titles, selector identities,
extensions and package bytes are treated as sensitive; do not redact them into an
apparently editable but incomplete scene. Resource capabilities must remain admitted.
Read-only policy may deny mutations while still allowing this projection.

The current native policy sampler still runs before dispatch and disclosure; the
new feature cannot bypass its independent watch. Policy replacement clears pending
projection bytes and closes an active transfer before any further disclosure.
Disconnect, malformed sequence, monotonic regression and transfer expiry release
the pinned image and queued bytes. Receiver-side partial data must also be discarded
on transport/policy/epoch loss. Previously received bytes are not retroactively
revoked by hiding a window; existing UI erasure contracts still apply.

## Messages and transfer lifecycle

Use profile.read requests and profile.chunk responses within the existing exact
connection/producer-epoch envelope. Their bodies use the linked machine schemas.
Every request has schema_version=0.1.0 and an identifier query_id. An open has only
op=open. A read additionally has transfer_id, part and offset, all canonical uint64
decimal strings, with a positive transfer ID. A close has its positive transfer ID
and no part/offset. A query ID correlates one exchange; it is not a mutation receipt.

One transfer exists across all connections in a Sessions owner. A second open
returns busy without replacing it. IDs monotonically increase and never wrap within
the producer epoch. Open returns the first chunk of part zero. Subsequent reads
must name the exact next part/offset; no seeking, duplicate chunk replay or transfer
adoption by another connection/lifetime. An invalid sequence closes that connection.
Close releases an owned transfer and returns closed. A complete final chunk releases
the slot; the receiver needs no subsequent close. Other transfer IDs are invalid.

Each chunk returns the pinned revision, policy_generation, positive transfer ID,
part/offset, total part count, total bytes for this part, lowercase SHA-256 of the
whole part, at most 4096 raw bytes encoded as lowercase hexadecimal, and complete.
complete is true only on the last chunk of the last part. An empty part uses empty
hex at offset zero and still has the SHA-256 of empty bytes. A denied, busy or
unavailable response contains only schema_version, query_id and outcome; no revision,
transfer ID, policy contents or existence detail. Closed adds only transfer_id.
Malformed documents and wrong envelope/direction follow existing session closure.

Transfers expire at 5000 ms without an accepted read or 60000 ms from open,
whichever comes first; equality expires. Heartbeats and rejected requests do not
extend either deadline. Expiry closes the owner connection and drops queued data.
Use the existing 16-frame/64-KiB control queue, reserving 12288 bytes before each
response. Queue exhaustion closes the connection and releases the transfer. Clients
should await each response. Do not enlarge command/result or telemetry queues.

## Exact parts and bounds

The image has at most 1092 parts and 70 MiB total decoded part bytes including the
effective policy view. Existing 64-package, 1024-asset, 64-MiB total asset and 16-MiB
individual asset ceilings remain. At most one historical image can be pinned by the
session transfer, in addition to the command owner's current and worker-prepared
images. Package allocations are immutable and shared; do not copy all media per
connection or chunk. Chunk encoding adds only the bounded response allocation.

Part 0 is canonical compact JSON with exactly format=SysPane.ProfileImage,
schema_version=0.1.0, revision, selection, theme, capabilities and packages. Selection
and theme are exact existing resource pins; capabilities is the sorted trusted
provider set. Packages are sorted by manifest SHA-256. Each entry has manifest
(decimal part index) and assets (ordered objects with path and decimal part index).
Asset paths are lexicographically sorted. No filesystem paths or request receipts
are sent. Header size is at most 1 MiB with the ordinary parser bounds.

Parts 1 and 2 are canonical exact saved settings and scene JSON, retaining their
existing document/version limits. Part 3 is the effective policy view: exactly
revision, forced_settings, denied_capabilities and disclosure. Forced rows have path
and value; disclosure rows have channel and allow_classifications, restricted to the
authenticated console's rules. Other roles, policy IDs, scope and retention metadata
are not projected. Bound this view to 65536 bytes. It describes UI constraints; it
is not native policy provenance and cannot authorize a controller operation.

Parts 4 onward contain each package's exact manifest then its exact assets in the
header order. Manifest and asset hashes remain independently verifiable through
ContentCatalog. Each part hash/size is stable throughout its transfer. Canonical
JSON applies to the generated header/documents/view; retained package bytes must
not be normalized or rewritten.

## Receiver and verification

Provide a portable serialized ProfileDownload for an already authenticated native
connection, fixed producer epoch and locally admitted capabilities. It correlates
each query, enforces every bound/order/hash/identity and releases partial data on
any error or explicit invalidation. It hands no partial documents to a UI. After
all parts arrive, validate the authored pair, complete ContentCatalog, exact resource
selection/theme and current projected constraints. Return the typed authored state,
immutable resource snapshot and effective UI policy. Local capabilities intersect
the advertised set and must admit the actual closure. Never write received paths to
disk or accept wire data as a native Authority. Caller invalidation is mandatory on
connection, producer or policy loss, including after a complete download.

Freeze this package and profile-projection-cases.json before production changes.
Use literal existing startup documents/packages as the independent oracle. Cover
exact bytes, forced/read-only policy, denied/same-revision revocation, optional and
required negotiation, cross-connection access, busy/close, expiry/deadline equality,
malformed sequence, queue pressure, current versus pinned revision, native reconnect,
worker join/unknown outcomes, large/binary/empty parts, corrupt bytes, wrong epoch/
query/digest and receiver invalidation. Native Python observes real child/session
traffic and stored files independently; fixture policy is never called protected
policy qualification. Preserve failures and source/artifact identities.

Run portable projection and command/reconciliation tests on all three development
profiles, native projection/controller/supervisor regressions, component graphs and
specification checks. Next compose the actual native frontend with verified helper
lookup, independent scheduling, deployment/runtime ownership and these profile reads;
connect settings/editor, telemetry, activation and recovery. All five complete
editions, protected-policy qualification and original release gates remain required.
