---
type: "SysPane Work Package"
title: "W-05 owned GNOME shell/compositor replacement"
description: "Observe exact shell exit, native replacement, bridge reattachment and input on the replacement desktop."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:27:15Z"}
sp_id: "SP-W05-GNOME-SHELL-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-ICON-RECOVERY", "SP-W05-GNOME-COMPOSITION", "SP-W05-GNOME-INPUT", "SP-ORACLE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 owned GNOME shell/compositor replacement

Run `--shell-recovery live|no-reattach|no-restart` on the existing authenticated,
owned Xvfb laboratory. Keep the original display, private buses, registry, settings,
fixture and observer alive. First pass the unchanged native composition prerequisite.
This experiment replaces the GNOME process that owns both the window manager and
X11 compositor. It does not qualify Wayland, physical GPU presentation, a user
session manager or the product controller/renderer/collector.

## Ownership and replacement

The observer binds the original supporting window through XRes, its self-reference
and exact shell PID, executable, arguments, group/session and start time. Hold
pidfds for the shell and original DING process and retain their mapped-file hashes
before stopping either. The parent retains its actual shell child and confirms
the observer's armed notification before permitting this expected exit.

Paint generation 4, settle for 250 ms, then start the recovery clock and continuous
capture. At 250 ms (within 50 ms), after at least three frames, revalidate the
original shell identity and signal only its held pidfd with SIGKILL. Independently
observe pidfd exit within two seconds. Preserve the old DING lifetime separately;
it need not die with its parent. Never signal an inherited display or user process.

After confirmed shell exit, keep the manager absent for at least 350 ms. The
observer then requests one replacement. The parent must confirm its original
child exited with -9 before launching the identical pinned shell command and
environment in a new retained group/session. No second replacement or retry is
admitted. Record both launch and independent readiness. Require native replacement
readiness within five seconds of the request; an XID may be reused but a process
start identity may not.

The unchanged pinned DING constructor cleans previous instances whose command
starts with its own extension's exact `app/ding.js` path. That path is unique to
this owned workspace. Observe the old DING pidfd exit and a new desktop window
bound to the replacement shell's group/session. The harness must not manually
launch DING or silently substitute the old instance. Preserve cleanup failures.

Readiness requires the new native supporting window, a held live replacement
shell, old DING exit, a held live new DING identity, and the private bus's
`org.gnome.Shell` owner PID matching the replacement. Check that the laboratory
bridge methods are exported. A process or bus acknowledgement alone is not visible
recovery. Transient missing/BadWindow observations are not-ready; unrelated native
query errors fail.

## Reattachment, pixels and controls

Keep every recovery frame, including startup, missing-surface and icon outages.
Observe marker, original icon/transparent-overlap and background regions together
at 50 ms cadence; allow at most 150 ms uncovered time and 50 ms per paired capture.
Record all process-lifetime observations in the same monotonic domain. Bound the
recovery interval to ten seconds, 200 frames and a 12 MiB/240-record journal.
The ordinary 40-second attempt and owned process cleanup limits remain in force.

After native readiness, dismiss the replacement's startup overview with the
existing native Escape stimulus, request generation 5 and explicitly enable the
bridge scene. Observe 250 ms of settling, then a separate 2,400 ms acceptance
interval: generations 5/6/7 at 0/800/1,600 ms. Reuse the unchanged temporal decoder
and its 200 ms generation deadline. Compare every post-recovery icon and rectangle
sample to the original pre-crash calibration; do not recalibrate or reposition.
Require original background pixels and native settings. Preserve the entire outage
prefix separately; the post-recovery interval does not erase an earlier failure
or claim uninterrupted visibility during an intentional compositor crash.

- `live`: require exact old shell exit, one native replacement, old DING exit,
  replacement-bound icons, bridge progress/composition and subsequent full input.
- `no-reattach`: perform the same native replacement and generation requests but
  omit scene enablement. Require native recovery and icons to pass while the
  external marker and rectangle fail. Dependent input remains unexecuted.
- `no-restart`: deliver the same exact shell fault but omit replacement. Continue
  captures for 2,500 ms after confirmed exit. No native recovery, reattachment,
  post-recovery interval or input may be claimed from surviving pixels or DING.

After all live recovery gates pass, execute the existing native input sequence
against the new shell and DING identities, retaining both pidfds. Require selection,
clear, drag selection, menu/dismissal, real owned folder contents/open/close,
restored selection and final changing composition. Old shell/DING ownership must
not satisfy new accessibility, clipboard or folder observations.

## Verification and continuation

Preserve exact source archives, original mapped files, private environment and
fixture identities, parent/observer messages, raw pixels/journal, native logs,
failures and cleanup. Ordinary runtime/composition checks must retain their
single-shell and original-lifetime rules. Only this family may supply independently
verified shell/DING exit and a second exact launch. Recompute native, coverage,
visual and input outcomes independently; mutation checks must reject false exits,
identity reuse, missing launch/readiness, incorrect timing, missing frames, stale
generation, wrong icon pixels and input from the old process.

A native failure is a valid investigation result and must remain failed. The
known Show Desktop focus-restoration failure and all product qualification gates
remain independent. This experiment cannot complete W-02, W-05 or W-25 as a whole.
