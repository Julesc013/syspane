---
type: "SysPane Work Package"
title: "W-05 native GNOME icon-input experiment"
description: "Verify real icon selection, menu and folder activation independently of the passive drawing bridge."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T02:00:05Z"}
sp_id: "SP-W05-GNOME-INPUT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-ORACLE", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 native GNOME icon-input experiment

Run this independent gate while retaining the failed Show Desktop focus result.
Use the pinned owned GNOME/DING composition scene. Input may interact only with
its synthetic 800x600 display, private clipboard, owned fixture and retained native
processes. Keep the current 40-second overall observation and cleanup limits.

## Observable sequence and authority

`--icon-input live|block-pointer|no-selection` owns the live composition prerequisite
and excludes reveal/focus modes. After the unchanged three-generation composition
oracle, derive the icon centre from the independently calibrated opaque pixels;
require the complete 64x64 four-quadrant square within the overlap rectangle.
Do not use candidate coordinates or accessibility actions to drive input.

Use native XTEST pointer/key stimuli in this order: clear selection at (700,550),
click the icon, clear, drag from (1,33) to (179,251) in twelve 20 ms steps, clear,
right-click the icon, dismiss the menu, clear, double-click the icon with 50 ms
between clicks, inspect the opened folder, close only that identified folder
window, and restore clear selection. Each click holds its button for 30 ms.
Every prerequisite failure stops later steps and records them as unexecuted.
The native folder window and its accessibility application may appear separately:
allow up to three seconds for the exact held PID to register after the window is
identified, without activating services or accepting another application's tree.
The first registration race remains preserved as an observer failure.

For selection, first take ownership of the private clipboard in a new requestor
window, issue Ctrl+C, and require a new owner within 500 ms for a selected item.
Read `x-special/gnome-copied-files`: exact `copy` followed by the owned Probe Folder
file URI, with at most one trailing NUL. DING's native shell action supplies this
clipboard data; bind its selection owner through XRes to the retained shell PID.
For clear selection, require a fresh shell-owned payload containing exactly the
`copy` operation and no file URI. The first native attempts demonstrated that DING
publishes this empty payload, rather than leaving the observer as clipboard owner.
Preserve those original observer failures. An unchanged owner is not evidence of
clear selection. No stale clipboard contents or candidate-reported state can pass.
Clipboard requests/responses are bounded to 4 KiB, 256 events and 500 ms each.

Enable the existing pinned AT-SPI registry explicitly on the private bus, with
service activation disabled. Verify its bus owner PID. Use read-only accessible
trees bound to DING's native PID to require a showing `Open` menu item after the
right-click and its absence after dismissal. Bound a tree to 256 nodes, depth 12,
32 children, 256-character names, 250 ms per call and three seconds total.
Record external root pixels and native active-client identity at each step.
Selection/clear/drag steps require the DING desktop to be the active client.

For folder activation, bind `inode/directory` only in this attempt's private MIME
configuration to the already pinned PCManFM from the existing X11 laboratory.
Record its exact runtime identity; do not install or patch a file manager. This is
an explicit GNOME/DING/PCManFM laboratory profile, not Nautilus qualification.
Require exactly one new normal native window whose XRes PID, executable, arguments,
group/session and live process handle identify that owned file manager. Its
read-only AT-SPI frame must name `Probe Folder`; native Ctrl+A/C must yield exactly
the owned `Sentinel.txt` through its clipboard. The new window must receive focus.
A title alone, successful launch call or empty accessible tree cannot prove open.
After an ordinary close request, require its native window to disappear. Preserve
the fixture files and desktop entries; do not run file-operation menu actions.

## Controls, visibility and evidence

The live bridge remains nonreactive/nonfocusable. The `block-pointer` negative
control adds one transparent reactive test actor above the icon rectangle, handling
pointer events without taking keyboard focus. It exists only under the explicit
laboratory flag and shares scene enable/disable lifetime. It must leave the original
composition pass intact while causing the icon-selection prerequisite to fail.
Register that actor with GNOME's [layout input-region tracking](https://raw.githubusercontent.com/GNOME/gnome-shell/46.0/js/ui/layout.js)
and unregister it on disable. The first untracked reactive actor did not intercept
native X11 input and unexpectedly passed; preserve that invalid control and its
sources rather than treating it as negative calibration.
`no-selection` omits only the icon click, retaining the clear and clipboard probes;
it must fail that same selection step. A startup/instrumentation failure cannot
stand in for a calibrated negative control.

Record marker pixels and unchanged background settings at each completed input
step, and rerun the fixed marker/composition trace after successful restoration.
Menus or normal folder windows may cover the marker during interaction; this is
ordinary foreground occlusion, not a new desktop-reveal visibility claim. The
unchanged initial/final composition oracles remain separate from input acceptance.

Preserve raw step/stimulus/clipboard/accessibility journals, capped at 8 MiB/256
records, plus native process identities, fixture/runtime/source archives and full
cleanup evidence. Verify exact URIs, fresh owners, native focus, visible menus,
folder contents, step order and negative controls from raw observations. Classify
missing laboratory services separately from an observed input obstruction.
Keep all failed attempts. A pass closes this named input experiment only; focus
restoration, taskbar, image wallpaper, shell recovery and product qualification
remain independent gates.
