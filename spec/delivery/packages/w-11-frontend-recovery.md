---
type: "SysPane Work Package"
title: "Frontend recovery authority and accepted-request identity"
description: "Connect the actual frontend backend to scoped recovery admission and preserve exact accepted-draft metadata."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T02:40:00+00:00"}
sp_id: "SP-W11-FRONTEND-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-PREPARATION", "SP-W11-RECOVERY-ADMISSION", "SP-W11-INSTALLED-EDITOR"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Frontend recovery authority and accepted-request identity

The actual LinuxFrontendBackend negotiates profile-request/result 0.2 and
configuration.recovery-context, retaining its existing command/result versions.
Each download names the locally selected profile and a new bounded editor-session
identity. The authenticated receiver validates the complete transfer. A null
recovery context leaves ordinary settings/editor commands usable. Recovery resources
are admitted locally for receiving the context; do not change the legacy resource
capability header or enable the installed recovery UI before its remaining gates.

The existing supervisor worker constructs LinuxRecoveryAdmission from that validated
view and the local ProfileLocation. Its current-authority callback obtains the
actual authenticated connection/epoch, locally allocated session/profile, authored
revision and projected current policy. It never takes authority from a GUI task.
Admission and filesystem checks run outside the backend/channel mutexes. Use the
existing helper owner and preparation slot; add no native threads or task schedulers.

Loading/reloading, submission, disconnect, supervisor replacement, policy withdrawal
and close synchronously withdraw the backend's admission. Old tasks close on the
native worker, erase results and cannot revive on regrant. A fresh download is
required. Expose the existing GUI recovery/preparation factories, without adding
filesystem work to GUI calls. No recovery factory may fall back to unverified paths.

## Exact accepted-draft retirement

Submit optionally carries the canonical digest of this editor's completed durable
capture. This is bounded metadata on the existing pending request, not a second
ledger or an authority grant. Null is required for a kept/undecided record or an
unavailable capture. Validate the digest syntax and current recovery scope before
admission. On the client worker, require a commit with exactly one scene.replace
operation and the original authored/policy revisions. Convert only intent to preview
and request_id to editor:recovery; its canonical recovery envelope under the original
profile/generation must hash to the supplied digest before any command dispatch.
A mismatch never sends the mutation or authorizes retirement.

Preserve only that digest and original scope while a dispatched request has unknown
outcome. An authenticated accepted result, including original-request reconciliation
after controller replacement, creates one bounded retirement receipt for revision
old+1. Preview, rejection, conflict, unknown or an undispatched request does not.
Ordinary reply delivery does not consume this receipt. It confers no storage grant.

Attach the receipt's digest to a newly downloaded FrontendProfile only when the
profile and accepted revision match, the selecting-record generation changed, and
state/recovery uid, device, inode and path equal the originally captured directory.
Require current retention and erase permission. Missing permission exposes no
digest; do not infer deletion. A later nonmatching revision or replaced directory
must not inherit the receipt. Keep at most one receipt and clear it on the next
admitted submission or an explicit acknowledgement naming the current profile serial.
A stale acknowledgement fails without clearing current metadata.

The consuming editor must first close/reap its previous task, then load through
fresh current admission. It may retire only if that load's digest equals the
receipt, using the existing conditional filesystem mutation. A replacement is
preserved and offered; acknowledgement follows that decision, not an inferred
successful deletion. Unknown retirement remains unavailable, with actual files
preserved. Frontend-process loss need not persist this metadata: an old record then
requires ordinary explicit recovery decisions, never guessed accepted authority.

## Verification and remaining integration

Freeze this package, the case register and literal expected command before editing
production. Run the actual backend and verified helper bundle in a relocated native
fixture with the existing two workers. Independently inspect selecting records,
directory identities, exact recovery bytes and stored scenes. Cover null/denied
context, load/capture, stale scope, invalid/mismatched capture metadata, accepted
retirement, unknown and reconciled acceptance, kept records, replacement conflicts,
erase denial, replaced directories, policy withdrawal and shutdown. Calibrate a
wrong expected digest. Observe real child exit and runtime retirement.

Cases have 45-second ceilings and the family 600 seconds. Existing 100 ms GUI task,
storage/heartbeat deadlines and workspace limits remain unchanged. Re-run installed
settings/editor and helper/admission regressions plus all component graphs. Preserve
failures, exact source/artifact identities and qualification limits.

This boundary is compiled into the installed frontend backend. The next integration
must connect EditorForm's completed capture/submission and receipt consumption, then
qualify the complete worker/supervisor loop and maximum-size GUI operations before
enabling installed recovery. That work, native inspector/desktop/telemetry/lifecycle
and all five full SysPane 0.1.0 editions remain required.
