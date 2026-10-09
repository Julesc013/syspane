---
type: "SysPane Handoff"
title: "Native recovery helper admission"
description: "Bind helper work to current authenticated scope and independently held directory identities."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T01:20:00+00:00"}
sp_id: "SP-RECOVERY-ADMISSION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W11-RECOVERY-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native recovery helper admission

The existing verified helper worker now accepts LinuxRecoveryAdmission through a
trusted factory. It compares a received view with the host's current connection,
epoch, profile, editor session, saved revision and policy revision. Retention and
erase remain current permissions. It derives the expected path locally and holds
the exact state/recovery nodes without acquiring the controller's profile leases.
Replacement, permission changes or authority loss permanently withdraw the admission.

The parent checks admission before dispatch, at native polling and storage guards,
and before delivering results. Withdrawal erases retained results and closes the
exact child. The worker request carries an explicit directory-identity extension;
the sealed child verifies it before creating its writer file and through the existing
store publication sequence. Legacy private requests keep their exact old shape.
These operations stay on the existing worker and outside shared mutexes.

The [frozen package](packages/w-11-recovery-admission.md) and
[checkpoint](checkpoints/recovery-admission.json) bind contracts, source, artifacts,
commands and independently observed native results. The twelve new case families
cover exact load/capture/retire, all session dimensions, forged task parameters,
retention/erase denial, directory identities and replacements, native permissions,
symlinks, held-child withdrawal, result erasure and non-revival. The observer holds
a sealed child at its actual exec stop, changes the directory after the parent sent
the request, and lets the child refuse it before pumping the parent again. Neither
the replacement directory nor the held original receives a new writer file. A
deliberately wrong record expectation fails its oracle.

The withdrawal case also waits for the exact replacement bytes to appear in the
pending file, then revokes authority before the next parent pump. The original draft
remains exact, the pending file is preserved, the child exits and no completion is
delivered. This exercises the existing publication guard after staging as well as
the separate held-exec cancellation case; it does not claim rollback after a grant.

The final admission run observes 36 native hosts and 17 sealed helper children,
with clean host exits and no forced fixture cleanup. Its 418 GUI task calls take at
most 34 microseconds under the fixed 100 ms task-interface limit. This measurement
does not include or qualify synchronous recovery-document validation on GTK.

The Linux build, 73 selected shared checks and 336 named cases across twelve native
families pass, including unchanged installed settings/editor, recovery controls,
editor form, store, queue, profile-owner, transfer and helper regressions. IMAGE-JOB
and SCENE-IMAGE additionally pass their C++ CTest checks. All six component graph
checks pass across Linux GCC13, Windows GCC15 and Windows v141_xp. Those Windows
graph checks do not execute the Linux admission or historical guests. Specification
validation accepts 51 schemas and 183 fixtures.

The Windows configure preflights initially stopped at the unchanged workspace
reservation after native packaging consumed headroom. The completed owned recording
was archived and byte/node checked before its duplicate was removed. Resumed checks
use the same allocation and reservations. Raw attempts and archive inventories remain
under ignored out/; no product limit or acceptance expectation changed.

W-11 remains in progress. The installed editor still reports recovery unavailable.
Compose its live authenticated session callback and explicit 0.2 profile download
with this admission, preserve exact applied-draft retirement through lost-result
reconciliation, and move expensive recovery validation off GTK before enabling and
qualifying the complete recovery flow. A changed saved revision withdraws the old
admission; it does not implicitly authorize deletion of an earlier draft.

A final storage grant can race later withdrawal. Preserve resulting files and
uncertain outcomes; closure is not rollback. Protected-policy deployment, native
inspector, telemetry, desktop activation/visibility, lifecycle and all five complete
release editions remain open. No historical guest or public release is qualified.
