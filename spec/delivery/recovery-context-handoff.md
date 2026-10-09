---
type: "SysPane Handoff"
title: "Coherent native recovery admission snapshot"
description: "Accepted saved state paired with held directory identity and current retention permission."
tags: ["delivery", "configuration", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:21:00+00:00"}
sp_id: "SP-RECOVERY-CONTEXT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-RECOVERY-CONTEXT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Coherent native recovery admission snapshot

LinuxProfileStore now returns one trusted native snapshot of committed documents,
shared immutable resources and optional recovery admission. LinuxProfileWorker
performs the complete operation on its existing storage thread. The admission
pairs the exact accepted selector-byte digest with the profile ID, recovery path,
held state/recovery device and inode identities, owning uid, policy revision and
erase permission. It uses the existing profile locks and invalidation latch.

Admission requires the explicit local editor.recovery capability, an authenticated
native-granted console role and current sensitive-history permission. Denied
retention returns the committed state without admission; denied erase removes only
erase permission. Recovered damaged selectors likewise expose the coherent saved
documents without admitting recovery. Policy changes and replaced directories or
markers invalidate the owner, including after the previous policy/path is restored.
Policy and all directory bindings are checked again before returning the snapshot.

## Executable evidence

The [frozen package](packages/w-08-recovery-context.md) retains its original cases,
limits and startup/commit fixtures. Independent Python observations compare exact
documents and resources, the SHA-256 of the saved selecting record, and lstat/fstat
directory identities. Checks cover reopen, commit, capabilities, roles, retention,
erase denial, revocation/regrant, late policy change, replaced roots/children/markers,
damaged-selector fallback, store-thread rejection and serialized worker calls.
The worker case holds the final verification, observes concurrent-call refusal and
then verifies the completed snapshot. A deliberately wrong generation fails the
oracle; every new probe process exits normally under observation.

All 14 new cases pass within their fixed 15-second case and 180-second family
limits. The four existing native owner/startup/worker/controller families also pass,
for 224 named native cases in total. The Linux build, 64 selected shared checks and
six component graph checks across Linux GCC13, Windows GCC15 and Windows v141_xp
pass. Exact source, artifacts, commands, native archives and validation records are
bound in the [checkpoint](checkpoints/recovery-context.json). Raw evidence remains
local under ignored out/evidence. The 8 GiB active-output allowance is unchanged.

## Next admitted boundary

W-08 remains in progress. This API is an in-process observation for trusted native
workers; it is not a wire projection or a transferable grant. Installed recovery
remains unavailable. Bind a coherent profile/recovery transfer to the authenticated
peer, connection, producer epoch, profile and editor session. Revalidate directory
identity before helper operations and close admission on authority loss. Preserve
current-policy publication guards, exact-generation reconciliation, lost-result
retirement and all independent EditorDraft editing/resource checks. Address the
existing synchronous recovery validation cost before whole-UI qualification.

Then complete native inspector, telemetry, desktop hosting/visibility, independent
escape/recovery, lifecycle and packages. Windows 9x, Windows NT, Linux X11, Wayland
and Mac OS X remain required complete editions. This Linux component evidence and
the Windows graph checks do not qualify those releases or historical/native guests.
