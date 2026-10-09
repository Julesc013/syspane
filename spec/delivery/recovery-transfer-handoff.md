---
type: "SysPane Handoff"
title: "Authenticated coherent recovery context transfer"
description: "Negotiated profile transfer binds saved generations and native recovery observations to the authenticated editor session."
tags: ["delivery", "configuration", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:48:00+00:00"}
sp_id: "SP-RECOVERY-TRANSFER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-RECOVERY-TRANSFER"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authenticated coherent recovery context transfer

The existing native controller now serves explicitly negotiated profile-request,
profile-result and ProfileImage 0.2. Its context carries recovery observations bound
to the exact connection, producer epoch, requested profile/editor session, transfer
ID, document revision and policy revision. The native provider pairs these with
the accepted generation and held directory identities before image preparation.
Replacement images publish only after the command worker joins; an older transfer
keeps its original documents and generation through a later commit.

The portable receiver validates the complete profile/resource closure and every
recovery identity before exposing a typed view. Retention denial or absent native
admission yields null recovery; erase denial clears only erase permission. Role,
history disclosure and local recovery capability remain mandatory. Legacy 0.1
requests, parts and resource capability headers retain their original bytes. The
native recovery capability is admitted separately by the recovery provider.

The [frozen package](packages/w-08-recovery-transfer.md) records message shapes,
version/feature negotiation, native directory format and unchanged limits. The
[checkpoint](checkpoints/recovery-transfer.json) binds literal fixtures, exact
source/artifact identities, executed commands, native archives and preserved
failures. The native observer reuses the existing authenticated controller harness;
its exact 0.1 oracle remains active alongside the new independent 0.2 oracle.

## Evidence and limits

Nine new portable families cover exact/legacy bytes, permission, negotiation,
version lifetime, malformed scope/directory data, provider failure, worker join,
pinned generations and receiver invalidation. Native cases independently compare
the transmitted generation to selecting-record bytes and directory identities to
lstat/fstat observations. They cover real commit, a pinned old transfer, reconnect,
replacement epoch, retention/erase denial and current-policy withdrawal. A wrong
generation oracle fails; owned child exits are observed. Shared checks run on all
three development profiles, with the native cases on the pinned Linux laboratory.

All three builds pass, with 73 selected shared checks per profile (219 total) and
six component graph checks. The six new native cases and 54 recovery-context,
profile-projection, controller and worker regression cases pass. Specification
validation accepts 51 schemas and 183 fixtures; tooling reports 60 passed and two
Windows symlink-privilege skips. These are scoped development results, not native
release qualification.

The first Linux build stopped on test-code indentation warnings. The new schemas'
initial URIs also failed the repository identity convention. Both were corrected
without changing the frozen behavior or original 0.1 schemas. An owned temporary
test directory inherited the parent checkout's Git identity; GIT_CEILING_DIRECTORIES
now isolates that test run while preserving its no-repository assertion. Two budget
inspections encountered concurrent temporary-file cleanup and stopped before their
next commands. The remaining checks resumed after the tooling process exited.
These records remain preserved; no quota, product deadline or acceptance oracle
was relaxed.

## Next admitted boundary

W-08 remains in progress. Installed recovery is still visibly unavailable. The
received context describes authenticated remote observations; it does not confer
native filesystem authority. Connect it to the installed helper worker only after
matching the active peer/epoch/profile/editor session, independently holding and
revalidating the expected state/recovery directory nodes, and enforcing current
revocation/publication guards. Preserve exact-generation draft retirement and
lost-result reconciliation. Address synchronous recovery validation cost before
whole-UI responsiveness qualification, then enable and test the real recovery flow.

Native inspector, telemetry, desktop activation/visibility, independent escape,
imports, accessibility, lifecycle and complete packages remain required. Windows
9x, Windows NT, Linux X11, Wayland and Mac OS X are all still required complete
editions. Windows host/toolset checks do not qualify historical guests; protected
policy deployment and public releases require their corresponding authority.
