---
type: "SysPane Work Package"
title: "Coherent native recovery admission snapshot"
description: "Pair accepted documents with verified profile-directory identity and current retention permission."
tags: ["delivery", "configuration", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:10:00+00:00"}
sp_id: "SP-W08-RECOVERY-CONTEXT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-WORKER", "SP-W08-PROFILE-OWNER", "SP-W10-RECOVERY-DRAFT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Coherent native recovery admission snapshot

Installed recovery needs one coherent native source of accepted state, generation
and directory provenance. Existing separate load, generation-token and path calls
must not become an inferred grant in the frontend. Extend the current profile owner,
store and serialized worker; retain their locks, current policy checks and fail-closed
invalidation. Do not introduce another storage owner, transaction ledger or thread.

## Snapshot and lifetime

LinuxProfileStore exposes a trusted in-process recovery snapshot containing one
Committed value and optional recovery admission. LinuxProfileWorker executes the
whole operation in one existing worker call. No other call can interleave within
that snapshot. Shared immutable package allocations remain shared. All ordinary
store, transaction and profile-projection behavior remains unchanged.

Admission contains the profile ID, exact accepted-generation token, native recovery
directory, state-root and recovery-child device/inode identity, owning uid, policy
revision and erase permission. Read/retention permission is represented by presence
of the admission. The generation is the existing SHA-256 of verified selector bytes;
never derive it from a revision or recovery record. A commit changes it, reopening
the same accepted generation preserves it. Recovered/damaged selectors expose the
coherent recovered documents but no recovery admission.

The profile owner obtains directory identity from its held descriptors and existing
path/marker/lease verification. Recheck policy and all directory bindings before
returning the snapshot. A replaced state/recovery directory, changed marker, denied
profile policy or policy revision change fails and preserves the existing invalidation
latch. Ordinary recovery-permission denial does not invalidate a valid profile.

## Permission and trust

Admission requires explicit local editor.recovery capability, an authenticated
native-granted console role, available unchanged policy, permission for editor.recovery
and sensitive history disclosure. Denying editor.recovery.erase removes only the
erase permission; omission follows the existing denied-capability policy model.
All EditorDraft editing/resource/version checks remain independently mandatory.
This native snapshot neither grants mutation rights nor bypasses UI disclosure rules.

The method is for trusted native controller workers, like load(); it is not an
external projection. Its paths and node identities are observations held under the
profile owner's lifetime, not transferable authority by themselves. Do not add them
to the existing profile image or wire version, enable the installed recovery factory,
or infer a client session here. The following authenticated-transfer package must
bind them to exact peer/epoch/profile/session and revalidate directory identity before
helper work. Revocation/publication guards, lost-result retirement and GUI validation
latency still need that installed composition and its independent tests.

## Frozen evidence

Freeze this package and recovery-context-cases.json before production edits. Native
cases independently compare saved documents to the existing startup/commit fixtures,
the generation to selector-byte SHA-256, and directory identities to fstat/lstat
observations. Cover exact startup, reopen, commit, missing capability, denied retention,
denied erase, ungranted/wrong role, policy change/regrant, directory replacement,
damaged-selector recovery, wrong store thread and serialized worker execution. A
deliberately wrong generation oracle must fail. Observe actual owned-process exit.

Keep the existing owner/startup/worker/controller checks, Linux component build and
all three component graphs. Each new native case has a 15-second ceiling and the
family has a 180-second ceiling. Existing resource, helper, workspace and product
acceptance limits remain unchanged. Record exact source/artifact/environment identity,
preserve failures, update the campaign handoff and leave all five release editions open.
