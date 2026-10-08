---
type: "SysPane Work Record"
title: "Initial X11 desktop-host investigation"
description: "Bind real Openbox reveal and PCManFM placement failures to independent pixels, with image-background startup failures preserved."
tags: ["delivery", "assurance", "desktop"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:00:00+11:00"}
sp_id: "SP-X11-HOST-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W05-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Initial X11 desktop-host investigation

This checkpoint begins W-05's native investigations and extends W-02 with a real
Openbox Show Desktop adapter. Neither EWMH candidate is wall-conformant. Base
`db57e8b9ea3b0293cf482f01b444093d69477557`, the containing commit and recorded input
digests identify the work. W-02/W-05 and the overall campaign remain in progress.

## Executed experiment

The unprivileged Linux build now contains a separately owned X11 candidate library,
linked only into the diagnostic marker probe. It requests an EWMH desktop window,
no activation, skip-taskbar/pager state and an empty XShape input region. The below
variant requests below state and lowers its own window once. Neither candidate
draws into PCManFM, changes its wallpaper or continually repairs the stacking order.

The runner starts real Openbox 3.6.1 and PCManFM 1.3.2 on an owned authenticated Xvfb
server. Native XTEST delivers the configured Super+D `ToggleShowDesktop` binding.
The independent observer records `_NET_SHOWING_DESKTOP`, client order/focus and
continuous root pixels while generations advance. Known icon pixels are measured
against the original icon-manager capture, separately from window properties.

The solid-color laboratory produced these results:

| Candidate | Temporal reveal observation | Placement observation |
|---|---|---|
| Ordinary managed window, negative control | Fail: marker disappears during the real reveal action | Above the icon manager; covers icon pixels |
| EWMH desktop window | Pass for the measured changing marker interval | Fail: covers existing icon pixels |
| EWMH desktop window with below request | Fail: marker already hidden at baseline and during reveal | Fail: opaque icon-manager surface hides the candidate |

The configured color, configuration bytes, referenced file bytes and unobstructed
background region remain unchanged in these cases. The PPM file is not displayed
in this control, so it does not establish image-wallpaper preservation. Icon selection,
double-click, drag selection, context menus and input-focus qualification remain
not-run; XShape hints do not prove those behaviors.

The default tiled-image laboratory fails before candidate execution: PCManFM exits
with an X11 `BadDrawable` error. Its ordinary GTK backing mode and a separate documented
software-image backing experiment both failed. These are preserved lab failures,
not failed SysPane reveal results. The color control isolates image initialization
and does not erase or qualify the failed profile. The upstream cause is unresolved.

## Evidence and checks

Linux development profile revision 8 adds the Xext runtime pin and candidate target.
All 54 existing CTest entries pass, preserving the model, IPC, recovery, diagnostic
and oracle calibrations. Windows remains revision 7; configure and the two affected
component graph checks pass. Its earlier 53-entry full run remains historical.

`out/evidence/w-05-x11-experiment.json` binds the final native reports and
extracted dependency identity. The recorder recomputes temporal verdicts and icon
concealment from raw RGB bytes, and verifies exact source/artifact/runtime digests,
named-action states, wallpaper scope and cleanup. It never converts experiment
execution success into candidate conformance. Per-attempt journals preserve frames
and structural observations in the task-owned native cache.

The experiment's 35 missing Ubuntu packages are pinned by version, size and archive
SHA-256. The explicit preparation command extracts them into the owned build cache;
no system package installation, maintainer script or privileged action is used.
The runner uses isolated XDG paths, synthetic folders, an owned bus with no service
activation directories, and no inherited user display/session bus. HOME is unchanged.
All retained processes are stopped; logs record any forced termination separately.

Earlier preparation failures are retained in the attempt record: apt's epoch-bearing
filename differed from the repository Filename field; stale system package metadata
referred to a removed archive; and Git initially rejected WSL-mounted ownership.
Corrections match archive contents to pinned hashes, refresh metadata only in the
owned task cache, and apply an exact per-command safe-directory exception. No global
Git trust or system APT state was changed. The first native attempt also exposed an
Openbox frame-border offset; the explicit laboratory theme disables that border,
preserving the original fixed observation coordinates and tolerances.

## Next admitted work

Investigate the image-background startup failure independently of placement. Complete
real icon input/focus adapters and a strategy that can compose between wallpaper and
icons; the simple two-window stack does not provide that composition here. Continue
Wayland/GNOME/Plasma and the Windows/XP/7/macOS tracks independently as their laboratory
boundaries are available. No result here applies to those desktops or WSLg.

W-25 still needs recent-failure metadata, explicit configuration preservation and
actual data/renderer/visible recovery. Native UI, editing, telemetry, persistence,
product packaging and release qualification remain required by the full campaign.
