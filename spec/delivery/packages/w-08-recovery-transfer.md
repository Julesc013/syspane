---
type: "SysPane Work Package"
title: "Authenticated coherent recovery context transfer"
description: "Extend the existing profile transfer with explicitly negotiated recovery observations and exact session binding."
tags: ["delivery", "configuration", "contracts", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:30:00+00:00"}
sp_id: "SP-W08-RECOVERY-TRANSFER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-RECOVERY-CONTEXT", "SP-W08-PROFILE-PROJECTION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authenticated coherent recovery context transfer

Extend the existing profile projection and native controller. Preserve all 0.1
requests, results and image bytes. No second endpoint, transfer slot, storage owner,
request ledger or scheduler. Native observation and profile-image preparation stay
on startup/command workers; no filesystem work enters the session loop or GUI.

## Negotiation and messages

Add optional configuration.recovery-context with profile-request 0.2.0 and
profile-result 0.2.0. It requires configuration.profile, both new document versions
and the unchanged 12288-byte frame floor. Missing required support fails handshake;
missing optional support removes the feature. A 0.2 request without all support
closes the connection. 0.1 requests remain usable when both versions are admitted.

Version 0.2 keeps the existing body shapes and numeric/size rules, except that open
requires exactly two additional identifier strings: profile and editor_session.
Read and close retain their existing members. Results retain the existing members
and use the request's version. The active slot pins its version; changing version
during reads/close fails. All connection-lifetime, cursor, denial/busy/unavailable,
queue, deadline and image-count bounds remain unchanged. Denial responses reveal
no profile, generation, session or directory detail.

## Coherent image and context

ProfileImage 0.2 has the same exact header members and ordered parts as 0.1; only
its declared version changes. Prepare/cache both header encodings and their hashes
on the worker. Parts 1, 2 and 4 onward retain the existing exact bytes. Part 3 is
exactly {policy, recovery}: policy is the existing effective console policy view;
recovery is null or the following object. The complete part retains the 65536-byte
ceiling and counts against the original total-byte limit.

The recovery object contains exactly connection_id, producer_epoch, profile,
editor_session, transfer_id, revision, policy_generation, generation, directory and
erase. Identity strings obey ordinary identifier bounds. Revision, policy generation
and positive transfer ID use canonical uint64 decimal strings. Generation is the
64-character lowercase SHA-256 of the verified accepted selecting record. Erase is
a boolean. The directory object contains exactly kind="linux-profile/0.1", path,
uid, state_device, state_inode, recovery_device and recovery_inode. Its path is a
canonical absolute POSIX path ending in /recovery, at most 4096 bytes, with no NUL,
empty/dot/dot-dot components or trailing slash. Numeric fields are canonical uint64
strings; uid fits uint32, inode identities are positive, and devices are equal.
This initial native format is explicitly Linux-only; other adapters need their own
declared directory identity format rather than invented Linux identities.

The existing AsyncCommands worker receives an optional trusted recovery provider.
It prepares the image's immutable recovery observations from the same Committed
value used for the documents. Linux composition obtains one recovery_snapshot and
checks exact authored documents and shared resource identity against that value.
Provider failure must not expose a mismatched image or manufacture an unsaved result;
the existing uncertain-storage/reconciliation path applies. Replacement images,
including metadata, publish only after actual worker join. An older active transfer
keeps its original documents and generation while a newer command commits.

Project a non-null recovery object only when the native snapshot admits it, the
requested profile matches, editor.recovery is explicitly locally supported, and
the authenticated native-granted console still has sensitive-history permission.
Require its policy revision to equal the transfer's current policy revision; deny
editor.recovery.erase by clearing erase. Missing permission/observation produces a
null recovery field while ordinary profile disclosure rules still apply. Do not
construct authority from the requested profile/session or from a pathname.

## Receiver and lifetime

ProfileDownload takes an optional explicit expected profile/editor-session scope.
That mode sends 0.2 and requires 0.2 result/header/context. Ordinary mode sends and
requires 0.1. It validates the whole profile/resource closure before exposing data,
then validates all context identities against its authenticated connection, fixed
epoch, requested scope, transfer ID, document revision and projected policy.
Reject unadmitted editor.recovery, denied history, inconsistent erase, malformed
directory/generation and unknown/extra fields. Null recovery is valid and grants
nothing. Any error or disconnect/policy/epoch invalidation discards the view.

The returned context is bound remote observation, not protected native policy or a
filesystem capability. The installed helper owner must independently match the
profile/directory and active connection/session before operations, revalidate node
identity, enforce current revocation/publication guards, and retire only the exact
matching applied draft after reconciliation. This package does not enable installed
recovery or remove the existing consumer-validation latency gate.

## Fixed verification

Freeze this package, recovery-transfer-cases.json and its literal expected context
before production changes. Portable checks cover exact 0.1 preservation and 0.2
context, null/denied permission, optional/required negotiation, version switching,
connection/epoch/profile/session/transfer/revision/policy mismatch, malformed native
identity, provider failure, worker join, pinned old/new generations and invalidation.
Use literal expected fields and existing startup/commit fixtures, not a production
encoder as an oracle. Native checks independently observe real authenticated
controller traffic, selector-byte digests, filesystem identities, commit/reconnect,
retention/erase denial and current-policy withdrawal with actual child exit.
Deliberately wrong generation expectations must fail.

Run new portable checks and existing profile/command/protocol regressions on all
three development profiles, Linux native recovery transfer/context/projection/
controller/worker checks, component graphs and schema/integrity validation. Keep
fixed product, transfer and workspace limits, preserve failures and source/artifact
identities, update the handoff and sync main. All five full release editions remain
required; graphs and component tests do not qualify historical/native guests.
