---
type: "SysPane Handoff"
title: "Installed native scene editor"
description: "Real frontend authoring, authenticated persistence and shared verified helper ownership."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:00:18.819941+00:00"}
sp_id: "SP-INSTALLED-EDITOR-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-INSTALLED-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Installed native scene editor

The actual bin/syspane frontend now switches between native Settings and Edit scene.
It admits one active draft and uses its original authenticated controller/client,
request identity and reconciliation owners. Clean navigation reloads the coherent
saved profile, including after Apply; private fields, dirty scenes, modal editors,
held gestures and unresolved commands block navigation. Cancel session explicitly
discards the draft and returns to freshly loaded Settings.

The existing supervisor worker also owns LinuxEditorHelperOwner using the same
verified installation. GTK owns factory handles and the editor; verification and
native image/recovery execution remain on the supervisor worker. Closing continues
dispatch until controller, client, image and recovery work drain. There is no new
worker thread, alternate helper lookup or second request ledger.

DevelopmentFrontend now installs five files: bin/syspane, the configuration host,
image worker, recovery worker and share/syspane/helpers.json. The entry point embeds
helper record 0.2 expectations for the complete bundle. Substitution of any required
role refuses startup. Record 0.1 remains for its other explicit consumers.

GDK supplies real monitor bounds, work areas and scale. Monitor objects retain
session-local identities up to the existing package limits; these do not claim
persistent hardware identity. Invalid topology disables the active editor while
retaining its draft and keeping Quit available. A valid subsequent topology resumes
the same draft. The application fits its initial work area and scrolls forms so
navigation and Quit remain outside oversized editing controls.

Draft recovery is visibly unavailable. The downloaded profile does not yet carry
verified generation/session/recovery-directory authority. No revision-derived token
or unverified XDG path is substituted. Shipping the recovery helper grants no capture
authority. The scene uses its actual saved resources and reports missing telemetry;
it does not fabricate live values.

## Evidence and limits

The fixed INSTALLED-EDITOR cases run the actual frontend main and backend from
relocated production/fixture five-file payloads in an isolated X11/D-Bus laboratory.
The fixture configuration host supplies deterministic policy and held persistence;
production keeps protected-policy refusal. Native input drives the controls, while
an independent observer checks exact scene/settings/resource bytes and hashes,
controller identity/exit and runtime retirement. A deliberately wrong scene oracle
must fail. Final commands, source/artifact identities, results and preserved failures
are recorded in the [checkpoint](checkpoints/installed-editor.json).

The cases cover entry, properties, Apply/reopen, clean/dirty/private/pending navigation,
undo/redo, explicit cancellation/reload, lost acknowledgement without revision replay,
policy erasure, controller replacement, image-helper substitution and closing during
held persistence. The 45-second case, 600-second family and 200 ms post-observation
erasure bounds remain fixed. All 15 new cases and the existing settings, editor/form,
recovery and helper-worker regressions pass: six recorded native families contain
85 named cases, with an additional C++ SCENE-IMAGE check. All 64 selected shared
configuration/protocol checks and six component graph checks across Linux GCC13,
Windows GCC15 and Windows v141_xp pass. In the final installed run, erasure after
observed controller loss took 59.21 ms for policy revocation and 59.31 ms for replacement.
All application stderr records in that run are empty under fatal GTK criticals.

The first observer assumed Home would select the tree's initial cursor; explicit
End/Home with independently observed selected rows fixes that input assumption.
The second compared a formatted numeric field against integer text; it now compares
the parsed numeric value while preserving literal persisted-scene expectations.
Both failures remain archived. A screenshot exposed an oversized form on the small
laboratory display, prompting the bounded window and scrolling fix. No frozen package,
expected scene, existing test definition, product deadline or workspace quota changed.

## Next admitted boundary

W-11 remains in progress. Bind editor recovery to authenticated profile, session,
committed generation and verified native directory authority. Move or bound existing
synchronous recovery validation before whole-UI latency qualification. Add the native
inspector, real telemetry, desktop activation/visibility and independent escape/recovery,
then complete imports, accessibility, lifecycle, packages and native qualification.

All five Windows 9x, Windows NT, Linux X11, Wayland and Mac OS X release editions
remain required. The evidence here covers the pinned unprivileged Linux development
laboratory; Windows component graphs do not execute historical guests. Protected-policy
deployment and public release require their corresponding authority.
