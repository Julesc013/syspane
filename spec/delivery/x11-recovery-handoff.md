---
type: "SysPane Work Record"
title: "Owned X11 window-manager recovery checkpoint"
description: "Separate observed manager recovery from continuing candidate placement failures."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:49:51Z"}
sp_id: "SP-X11-RECOVERY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-SHELL-RECOVERY", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Owned X11 window-manager recovery checkpoint

From `fad7e2e0fed1205f28647282cb5119f60ead9766`, the existing X11 investigation
now has an optional [owned manager-recovery experiment](packages/w-05-shell-recovery.md).
It reuses the pinned Openbox/PCManFM/Xvfb laboratory, marker painter, root capture,
reveal trace and evidence recorder. No native application binary or build profile
changed in this checkpoint.

The parent stops only its retained Openbox child. A separate observer holds a pidfd
before the stop and confirms exit before the parent starts one replacement. During
the absent interval, the same candidate processes the next marker generation.
The observer binds the replacement's supporting window to its actual local process
through X-Resource, then observes another generation and post-ready root frames.
Capture coverage, event-loop progress, wallpaper and visible recovery remain separate.

## Observed results

Both the solid-color control and delayed-image profile complete all three candidates.
Each has confirmed native manager recovery, continuing candidate progress, bounded
capture coverage and unchanged wallpaper pixels/configuration. Every candidate still
fails surface recovery's combined visible-marker/unchanged-icon requirement. A live
window or a recovered window manager is not a qualified SysPane desktop host.

The supporting window's numeric XID is reused by the replacement in the measured
runs. The held old process, native exit and new server-reported PID distinguish
the lifetimes. Treating a repeated XID as the original window owner would be wrong.

Three early attempts stopped before any shell termination. The first observer
incorrectly required `_NET_WM_PID` on the supporting window; subsequent resource
queries incorrectly required the reply to repeat the entire window XID. The
diagnostic attempt recorded the returned client base and mask. The corrected
observer binds that base to the requested resource and requires the exact manager
PID; it does not accept an unbound window name or success flag. Original reports,
source archives and cleanup evidence are preserved.

The recorder recomputes coverage, native owner binding, exit/replacement order,
candidate progress, icon concealment and wallpaper results from raw observations.
Nine adversarial checks reject altered claims even when an altered report carries
a matching replacement journal. The existing image/input experiment and its fifteen
evidence checks are also rerun against the changed harness. Specification checks
and exact source/artifact/journal/runtime identities accompany the handoff.

The native report, verification and attempts records are under
`build-support/evidence/w-05-shell-recovery-*`. This is additional optional laboratory
evidence; the preceding 96/101/88 CTest results and model smoke packages belong to
their recorded collector checkpoint, not a new run or product qualification here.

## Remaining native work

W-02, W-05 and W-25 remain open. Conforming composition, icon-manager/compositor
failure, product renderer reattachment, continuous real collection during shell
failure and post-recovery input still need their own evidence. Other Linux shells
and the Windows/XP/7/macOS tracks remain independent.

Windows laboratory review ruled out promoting a private noninteractive window
station into a visible desktop oracle. Microsoft's [window-station contract](https://learn.microsoft.com/en-us/windows/win32/winstation/window-stations)
limits displayed UI/input to the interactive station. This is a documented laboratory
constraint, not an executed Windows capture test. No station switch, user-desktop
capture or guest mutation was performed. An admitted synthetic Windows display
laboratory remains necessary; the existing guest-scope question remains open.

Continue work on a composition strategy that meets the original icon/wallpaper
contract, using this recovery observer alongside the unchanged reveal and input
oracles. Preserve these negative placement/recovery results when evaluating a new
strategy. The full campaign remains incomplete.
