---
type: "SysPane Work Record"
title: "Automatic recovery from independent render failure checkpoint"
description: "The persistent controller replaces failed rendering lifetimes and preserves original measured collection."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T12:30:00Z"}
sp_id: "SP-CONTROLLER-RENDER-RECOVERY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-CONTROLLER-RENDER-RECOVERY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Automatic recovery from independent render failure checkpoint

Source baseline: `0fbca746eb5a1b6273a211f6748e77e9ecd031e9`. Git history identifies
the resulting commit; original source archives and native artifact digests identify
each tested snapshot.

The existing persistent native controller now owns one render-health listener,
authenticated connection, ProducerLease and RenderWatch per shell lifetime.
The same recovery-health 0.1 parser and existing three-second deadlines remain
authoritative. A 20 ms source-health poll and 1 ms render read service the independent
controller; ordinary HealthLink callers retain their 100 ms default. Guards advance
before received progress, renewal or shutdown, so queued messages cannot clear an
elapsed deadline. The source continues during detection, native stop and backoff.

The attached GJS render owner shares the existing draw/after-paint instrumentation
and bounded asynchronous teardown. It starts on the first complete projection,
including later generations delivered after replacement. It never owns or signals
the controller. A render stall enters the existing restart gate, releases demand
and both old connections, kills only the held owned shell and waits for actual exit.
A new shell then reattaches full original measured state and a fresh render guard.
Current typed revocation still prevents admission before retry.

Eight source-identical controls retain the three earlier crash cases and add stopped
drawing, hidden drawing, deliberately false progress, a frozen shell and revocation
at render failure. Independent source journals prove continuous original acquisition,
epoch and timestamps. Held process identities, native stop/readiness observations,
draw/paint traces and external glyph pixels prove the replacement lifetime. All
eight cases revalidate; the no-reattachment and false-progress cases remain expected
failed candidates. All 33 evidence-mutation checks pass.

For a frozen shell the observer sends SIGSTOP only to its held laboratory lifetime.
The runnable controller expires it, kills it and admits a distinct replacement.
The observer does not resume the old shell to manufacture recovery. For drawing
stall/hidden cases, ordinary health stays alive while the render challenge expires.
False acknowledgements alone never establish visible success. Native Escape still
dismisses the replacement startup overview before recovered pixel acceptance; fully
unattended overview-free recovery is not qualified.

Complete regressions pass 114 Linux and 105 Windows CTest entries. Native/GJS
implementation bytes remain unchanged after those suites. The desktop oracle's
later pre-run correction distinguishes a challenge issued before injection from a
new false-progress challenge; both source versions are preserved. The package's
poll range was corrected to [1,100] ms to match the existing stream adapter's
rejection of zero waits. Preparation-only type/quoting errors are recorded separately
and did not launch a build or test. The first exploratory native stall case and
the full subsequent matrix both retain their actual source/artifact identity.
The three native queued-message cases also pass: late progress, heartbeat and
normal shutdown cannot erase expiry. The earlier GNOME live render-watch case
passes on the rebuilt artifacts, and both development model packages pass relocated
smoke execution. These checks retain their exact limited scopes.

Public evidence uses `build-support/evidence/w-25-controller-render-recovery-`.
Operational source, delivery, counter bracket and pixel originals remain private
in their owned native attempt directories. No user desktop, guest, privileged
service, public release or AIDE grant was activated.

W-25 and the campaign remain incomplete. Native editor-exit recovery, installed
session/controller/policy/demand ownership, general delivery and complete editions
remain required. Keep the default GNOME focus failure and overview caveat. Windows
synthetic lab designation, historical guest scope and a Mac endpoint remain
unresolved independently; continue useful work without inventing their qualification.
