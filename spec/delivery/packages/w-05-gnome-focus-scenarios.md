---
type: "SysPane Work Package"
title: "W-05 native focus lifetimes, modality and workspace changes"
description: "Extend the optional focus experiment with externally observed user choices and invalidated pending targets."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:26:58Z"}
sp_id: "SP-W05-GNOME-FOCUS-SCENARIOS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-FOCUS-INTEGRATION", "SP-W05-GNOME-REVEAL", "SP-WINDOWS", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native focus lifetimes, modality and workspace changes

Use the existing owned GNOME 46/DING X11 lab and original candidate focus baseline.
The controller remains optional and off by default. `--focus-scenarios observe|restore|helper-exit`
owns its candidate-baseline and private two-workspace setup; it cannot combine
with other experiment flags. Retain the existing 40-second attempt, workspace
preflight, original source/runtime identity and complete cleanup.

The Windows native track still needs an admitted interactive synthetic desktop.
A noninteractive window station is not a substitute for display/input evidence:
[Microsoft's window-station contract](https://learn.microsoft.com/en-us/windows/win32/winstation/window-stations).
This constraint does not block this independent Linux track or qualify Windows.

## Fixed behavior and stimuli

After the unchanged original reveal/F9/F10 interval, the retained parent launches
exactly one owned GTK helper on the same private display. It creates two normal
windows, alpha and beta. An actual F6 delivered to beta opens its modal transient;
Escape closes that dialog. The helper records actual F9 receipts by role in an
exclusive, bounded private journal. It supplies no screenshot or focus verdict.
No helper command chooses a focus target. All focus choices use real native input.

- Explicitly select beta and reveal/restore; the selected beta must regain focus
  and receive F9. Select alpha and repeat; alpha must regain focus and receive F9.
  A fixed first-window target cannot satisfy both cases.
- Open beta's modal dialog and reveal/restore. Actual dialog focus and F9 receipt
  must return to the modal dialog; focusing its parent behind the modal cannot pass.
  Keep the existing controller initially and investigate native focus redirection.
  Do not broaden eligibility or weaken modality merely to satisfy the test.
- Close the retained beta while desktop mode is active through WM_DELETE_WINDOW
  to its independently bound native window. Restoration must not focus/recreate
  that dead lifetime. Let the native shell choose among surviving windows; the
  controller must clear its target and abstain from restoration.
- Enter desktop mode with alpha, switch to workspace 2 using the configured native
  chord, then return. Leaving the workspace invalidates pending restoration; the
  controller must not restore from that old pending transition. The other workspace
  must not focus a window still on workspace 1. If native desktop mode remains
  active on return, use one declared native chord to leave it, with no repair loop.
- Explicitly select alpha again and perform a fresh reveal/restore. Its new entry
  must restore alpha and deliver F9, proving invalidation did not permanently disable
  the optional controller.

Configure exactly two static workspaces and native Ctrl+Alt+1/2 bindings in the
existing private keyfile settings only. Preserve Super+D. Record those settings,
workspace membership, current workspace and exact final settings. All normal
fixture windows begin on workspace 1; DING retains its native desktop role.

The restore candidate must meet these externally observable outcomes. Observation
mode omits the focus call and records the same fixed evaluations honestly; modal
or native fallback behavior may pass independently. Do not invent a required
observation failure for a scenario whose native behavior has not been established.
The original observation-mode focus/F9 failure remains the calibrated negative.

## Evidence, resource limits and completion

Each declared step captures native client state and independent root pixels every
50 ms for 400 ms. Keep the existing 200 ms transition allowance, 50 ms capture and
150 ms gap bounds, with at least three settled observations. Bind each new window
through XRes to the retained helper PID/group/start time, verify its native type,
modal/transient relationship and bounded geometry, and retain actual role-specific
key receipt. Helpers never return pixel evidence. The marker/background witnesses
remain unobstructed; run the original changing-marker oracle again afterward.

Bound the helper to two normal windows and one transient, 128 events and 32 KiB
of journal data. The parent accepts one exact launch request only. Native client
lists, raw frames, stimulus times, decisions and journals remain source-bound;
failed/interrupted prefixes are preserved. Flush each raw sample immediately; bound
the observer journal to 400 records and 12 MiB. Closing beta leaves alpha and the
helper alive until retained parent cleanup. No unrelated process is signaled.

When an owned window closes between client enumeration and property retrieval,
retain the raw BadWindow code/resource/request and all captured pixels. Only an
exact closing modal/beta GetProperty BadWindow within the transition allowance
may have unavailable native state. Never retry away that frame or let an unknown,
foreign or settled query failure pass; require subsequent settled native coverage.
The first unhandled closing-window race remains preserved as a failed attempt.

The helper-exit control first completes the original baseline, then deliberately
exits the newly retained helper with code 7 before creating windows. The outer
report and native process command must fail, with no scenario completion claim.
This calibrates the outer exception path: an earlier passed substep must not leave
a failed attempt marked pass. Keep the original erroneous pass-with-error record.

Independent verification must reject wrong selected targets, parent focus in place
of modal focus, dead/native-reused identities, cross-workspace restoration, missing
invalidation, absent or misattributed F9, repaired timing, changed settings, missing
frames and unconfirmed cleanup. Re-run the original optional focus/guard comparison
and default reveal/composition/marker calibration after relevant changes.

This package does not qualify lock/session transitions, moved windows, alternate
reveal triggers, other compositors, real session management or the complete host.
Keep those gates open; W-02/W-05 and the campaign are not complete from this package.
