---
type: "SysPane Work Record"
title: "Owned GNOME shell marker checkpoint"
description: "A real pinned shell bridge now presents changing externally decoded pixels; desktop composition remains open."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:23:00Z"}
sp_id: "SP-GNOME-MARKER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W05-GNOME-PACKAGE", "SP-CAMPAIGN-ADMISSION", "SP-X11-RECOVERY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Owned GNOME shell marker checkpoint

From `2607efb68b5080d240004b693ff58d5d9e7fb905`, a small trusted GNOME 46 extension
now paints Marker 0.1 in the real shell background group. An independent X11 root
capture observes all three requested generations. The hidden and frozen controls
fail the original oracle as required. This establishes a working shell bridge and
its temporal observer; it does not establish a conforming desktop host.

## Exact scope and results

The [package](packages/w-05-gnome-investigation.md) fixes the laboratory, bridge
stimulus, resource limits and acceptance boundary before execution. GNOME Shell
`46.0-0ubuntu6~24.04.15`, Mutter `46.2-1ubuntu0.24.04.16` and GJS `1.80.2-1build2`
run from extracted Ubuntu packages under the existing unprivileged WSL account.
The 196-package lock includes DING for the next experiment, but DING was not enabled
in these measurements. No packages, system services or user-session extensions
were installed. The runtime is a laboratory dependency, not a SysPane release payload.

The shell uses an authenticated owned 800x600 Xvfb display, software rendering,
private HOME/XDG directories and two private buses without service activation.
The second bus lets native system-service proxies connect while exposing no real
system services. Missing account, login, policy, camera, calendar and input-method
services remain visible in the original logs and unqualified. This is deliberately
not a complete GNOME login session or a hostile-code sandbox.

| Candidate control | External result | Samples | Maximum capture gap | Maximum capture duration |
|---|---|---:|---:|---:|
| Live | Pass; generations 1, 2 and 3 | 48 | 53,031 us | 488 us |
| Hidden | Fail; marker absent | 48 | 53,551 us | 469 us |
| Frozen | Fail; generation deadline, only generation 1 | 48 | 53,934 us | 477 us |

All three use the same source inputs and unchanged 150 ms coverage/200 ms
presentation thresholds. The separate synthetic background witness remains exactly
`(48,72,96)` in each case. X-Resource binds the actual manager to the retained shell
process. Native shell, frame helper, observer, display and private bus exits are
confirmed; no surviving owned process-group member is accepted.

The recorder recomputes raw pixel/time outcomes, archive identities, native manager
binding, background witnesses and cleanup. Nine evidence checks reject changed
pixels, capture provenance, source identity, generations, ownership and exit claims.
The extension remains an explicitly uninstalled laboratory artifact owned by the
optional runner; it does not alter the CMake product graph or supported profiles.

## Preserved failures and environment decisions

The initial package snapshot encountered an HTTP 404 for an obsolete GVfs archive.
Signed Ubuntu metadata was refreshed only under the owned cache, then a revised
exact lock was prepared. Final archives total 123,909,062 bytes; extraction totals
325,327,686 bytes. The measured development workspace allocation is now 3 GiB,
separate from all product resource/acceptance limits.

The first runner preflight hit Git's mounted-checkout ownership check before any
native process launched. A command-local exception for the exact admitted checkout
resolved it without modifying global Git configuration. Six native bootstrap
failures then exposed missing private library/typelib paths, Mutter's frame-helper
lookup (including the shell's HOME working directory), absent system-bus connection
and the extracted weather database path. Original logs and source archives remain.

Mutter's [uninstalled frame-helper fallback](https://raw.githubusercontent.com/GNOME/mutter/46.2/src/core/frame.c)
and GNOME's [change to HOME](https://raw.githubusercontent.com/GNOME/gnome-shell/46.0/src/main.c)
explain the owned helper link. GNOME's [extension documentation](https://gjs.guide/extensions/development/debugging.html)
also makes the in-process isolation limit explicit. No foreign installation path,
shell binary or acceptance oracle was patched to obtain the working result.

Eleven native attempts, including preliminary successes, six failures and the final
three controls, are preserved under `build-support/evidence/w-05-gnome-*`, with their
original source ZIPs committed beside the records. The source archive never contains
display authorization cookies. The previous C++ CTest/smoke results retain their own
checkpoint identity; those suites were not rerun for this optional shell experiment.

## Next work

W-02 and W-05 remain in progress. Enable the pinned real icon manager only after
closing and calibrating a new composition fixture: a legible marker region plus a
separate overlap witness with independently measured opaque icon anchors. Correctly
layered icons may occlude drawing and blend antialiased edges. Do not reinterpret
the earlier full-marker/icon-overlap experiment as a positive oracle or erase its
negative X11 results.

Then measure real reveal, icon selection/menu/opening, unchanged wallpaper,
shell/icon-manager recovery and bridge reattachment independently. A background
actor's structural location or successful D-Bus response proves none of those.
Wayland, native GPU presentation, other shell versions and Windows/XP/7/macOS remain
separate tracks. The product controller, complete renderer/settings/editor and
native verticals still need implementation and evidence; the campaign is incomplete.
