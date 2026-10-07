---
type: "SysPane Work Package"
title: "Complete-scene command transport"
description: "Carry the full authored scene contract through negotiated commands, bounded admission and durable recovery."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T04:12:48Z"}
sp_id: "SP-W08-LARGE-COMMANDS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-NATIVE-CONTENT", "SP-W08-RESOURCES", "SP-W08-COMMAND-SESSIONS", "SP-W10-NATIVE-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Complete-scene command transport

Close the W-08/W-10 mismatch between 256 KiB local scenes and 16 KiB commands.
Keep the existing transaction, ledger, resource, publication and reconciliation
owners. This package admits command 0.5 and generation manifest 0.3; older command
schemas, accepted sizes, result identities and stored generations remain compatible.
No new mutation service, chunk-assembly protocol, import authority or activation claim.

## Exact command and negotiation contract

Command 0.5 retains the 0.4 operations, revision/policy/intent/request fields and
extensions, with optional `content`. Scene 0.2 may be resource-free. A command
replacing scene 0.3 requires complete package/preset pins; a resource-backed current
generation still cannot discard its closure through omission of `content`.
All individual scene/settings semantics, document size limits, role/capability
checks, duplicate-operation rules and current-policy commit permit remain in force.

The UTF-8 command body, including original whitespace, is at most 327,680 bytes
(320 KiB). The canonical command also fits that ceiling. The embedded scene remains
at most 262,144 canonical JSON bytes; settings remain at most 16,384. Local scene
validation still enforces the existing 16,384 JSON nodes and container depth below
32. Count nodes as containers, keys and non-container values, as in the existing
parser. Command 0.5 and its envelope permit at most 18,432 nodes and container depth
below 40, providing room around a valid maximal scene. Revalidate the extracted
scene independently so wrapping never relaxes its own constraints. Only the new
command profile uses those parser limits; other messages and old command versions
retain their original limits and malformed-input rejection.

Sending command 0.5 requires exact command 0.5 and result 0.1 document negotiation,
`configuration.transactions`, `configuration.large-commands`, and a negotiated
frame ceiling of at least 328,704 bytes (body plus 1 KiB envelope headroom). The
1 MiB global frame ceiling and five-second incomplete-frame deadline are unchanged.
The extra frame headroom covers maximum-length ASCII connection and producer IDs.
An owner advertises this capability only when it implements the complete command
and receipt path. Preview-only/health owners do not gain transaction authority.

Optional incompatible large-command capability is removed; a required incompatible
combination fails negotiation. Content still requires `configuration.content`;
scene 0.3 replacement additionally requires `configuration.scene-content`. Either
0.4 or 0.5 can satisfy that feature's document dependency. Unnegotiated 0.5 commands
return feature.unsupported before admission/preparation when the ordinary decoder
can read them; malformed/over-budget envelopes follow the existing connection-close
rules. A small negotiated frame must never silently truncate or split a mutation.

Native hosts explicitly pass negotiated large-command support into a draft. The
legacy default continues emitting 0.2/0.3/0.4 and rejecting oversized Apply with the
draft intact. An enabled draft emits 0.5, including for small commands, and preserves
that exact request through cancellation/disconnect/reconciliation. Reopening with a
different peer requires a fresh host capability choice; active requests are never
rewritten or blindly retried. Preset preview can opt into 0.5 through the same
explicit capability, retaining its exact resource selection.

## Admission, replay and durable identity

Keep 128 outstanding requests per connection, 128 retained records per principal,
16 principals, 1,024 total records, ten-minute terminal retention and the global
16 MiB ledger reservation. Charge original body bytes plus the existing 4 KiB
result allowance before execution. Fifty maximum-size 0.5 bodies fit; the next
does not. Return busy without an orphan job or preparation. Never evict an unexpired
result or raise these limits to make a larger command fit. Exact-body replay,
changed-byte conflicts, current-policy retrieval, cancellation and confirmed worker
stop semantics remain unchanged. These are accounted retained-data budgets, not
allocator/RSS guarantees; bounded job/parser copies remain explicitly separate.

Generation manifest 0.3 stores the original 0.5 command in `request.json`, privately
owned with the same no-follow/single-link file rules as other generation files.
Its identity has exactly principal, epoch, request and `body_sha256`; the SHA-256
binds the complete original body bytes. The manifest otherwise keeps revision,
settings/scene hashes and optional resource-index hash. `request.json` is at most
327,680 bytes. Manifest remains at most 65,536 bytes; no string-escaped large body
is embedded in it. Require exactly the expected generation files for the new format.

Write and flush request.json before publishing the manifest/selecting record. Read,
hash, parse, validate version 0.5, revision/intent/identity and resource selection as
one coherent generation. Reject missing, changed, oversized, linked or foreign
request files. Never mix a request from a previous generation into recovery. Old
manifest 0.1/0.2 identities retain their inline body and 16 KiB bound. Keep at most
the existing current/previous committed receipts and existing read-only fallback.
Downgrade to an older reader cannot claim that a new-format generation is supported.

## Fixed acceptance and execution

Preserve literal input/expected scene bytes and independently specified limits
before implementation. Cover full-size scene edits (including multibyte/escaped
content), exact body limit and one-byte overflow, near-limit node/depth wrapping,
legacy rejection, negotiation/feature/frame refusal and independent policy checks.
Exercise shared draft Apply, transactions, asynchronous admission/replay/cancel,
global ledger exhaustion/expiry and cross-epoch receipt reconciliation on the three
existing development toolchains. Do not derive expected output from the mutation.

Native Linux cases use the existing owned IPC, ext4 store, supervisor and GTK editor
fixtures. Verify real full-scene save/reopen, exact request-file hash and bytes,
lost acknowledgement/restart without duplicate revision, cancellation, revocation,
and interruptions before/after durable publication. Corrupt, missing or substituted
request files must not produce a mixed accepted generation. Retain a deliberate
wrong-stored-geometry control. Use ordinary workspace preflight/configure/build/test
commands and the declared non-root Linux cache. Preserve failed attempts and exact
source/binary/oracle/environment identities.

Completion closes the full-scene transport boundary, not W-08/W-10 or a complete
edition. Installed ownership/activation, full authoring/accessibility, other storage
and native adapters, historical target qualification and release gates remain open.
