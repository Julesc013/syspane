---
type: "SysPane Work Package"
title: "W-05 bounded X11 host investigation"
description: "Observe desktop-type placement and native reveal under a real window and icon manager in an owned lab."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T04:00:00+11:00"}
sp_id: "SP-W05-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-W02-PACKAGE", "SP-LINUX"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 bounded X11 host investigation

The campaign admits this investigation using W-02's calibrated observer. It does
not depend on completing unrelated Windows/macOS adapters. W-05 remains open for
Wayland, GNOME and Plasma; this result must name the exact X11 lab. Source ownership
is `source/desktop/x11/`, the existing marker probe and `tests/desktop/`.

## Question and fixed decision rule

Can a passive EWMH desktop-type window preserve a live marker during the real
Openbox Show Desktop action while remaining behind PCManFM's icons and in front
of its unchanged wallpaper? Investigate above and below the icon manager. Do not
assume stacking two opaque desktop windows satisfies both conditions. No foreign
window drawing, event interception, wallpaper modification or continual restacking
is admitted. An ordinary managed window is the negative reveal control.

Each measured dimension is pass, fail, inconclusive or not-run. A valid experiment
may report a failed candidate. Harness execution success means the evidence is
complete and internally valid, not that a wall is qualified. Preserve original
failed attempts and captured frames; do not revise W-02 marker/time tolerances to
accommodate a candidate. No production capability is enabled by this experiment.

## Laboratory and authority

Use the admitted unprivileged Ubuntu 24.04 WSL account and owned Linux build root.
`build-support/x11-lab-packages.json` pins Openbox 3.6.1, PCManFM 1.3.2 and the missing
Ubuntu package closure by exact versions, archive SHA-256 and bytes. The explicit
`prepare_x11_lab.py` command downloads at most 64 MiB and extracts only into the
build's `x11-lab/sysroot`. It runs no package installation/maintainer scripts, changes
no system configuration and requires no privilege. Ordinary builds remain offline.
Record archive and extracted file identity; keep total owned output below 1 GiB.

Use an owned authenticated 800x600 Xvfb server, isolated XDG config/data/cache/runtime
directories, synthetic Desktop folders and a fixed generated PPM wallpaper. Do not
repurpose the user's HOME or capture their desktop. Launch exact extracted binaries
without session/autostart scripts. Use local GIO, in-memory GSettings and an owned
session bus; inherited user/session bus and display addresses are not lab inputs.
The lab is process/resource isolation for trusted programs, not a hostile-code sandbox.

Native X calls run in a bounded observer process; the parent owns and retains all
launched processes, limits the experiment to 30 seconds per case, then confirms
their exit. A missing dependency, startup timeout or unconfirmed cleanup is a lab
failure/inconclusive result, never host compatibility. No shell belonging to the
user is terminated. Captures, logs and interrupted prefixes stay in the task cache.

Keep the default image-wallpaper/GTK `similar` profile separate from diagnostic
variants. `--gtk-rendering image` selects GTK's documented software backing surfaces;
`--wallpaper-mode color` isolates image-background initialization from placement.
These variants preserve the same pixel/time/input criteria and do not qualify the
failed default profile. A color control can establish configured-color preservation;
the unchanged PPM file is then not displayed and provides no image-wallpaper pass.
Record the variant explicitly and preserve the original native startup failures.

An additional setup-sequence experiment may initialize PCManFM with the synthetic
color, wait for its native desktop, then use that exact instance's ordinary
`--set-wallpaper`/`--wallpaper-mode` command before any candidate or observation.
Record `delayed_wallpaper_setup` separately from startup configuration. A returned
command status is insufficient: the independently captured unobstructed region must
exactly match the corresponding pixels in the fixed 800x600 PPM fixture, and the
configured image/file must remain unchanged through the candidate interval. A working
delayed setup does not retroactively qualify the original failed startup sequence.

## Native icon-input closure

Input stimuli use XTEST only on the owned display; accessibility actions may not
select, activate or open objects as a substitute for pointer/keyboard routing.
Enable an explicitly owned AT-SPI registry on the private session bus, with its bus
address passed explicitly to the observer and GTK icon manager. Use the installed
AT-SPI 2.52 and GI bindings with recorded binary/package identity. No service-activation
directory, user accessibility bus or global settings change is required. Retain and
stop the registry like every other lab process.

The observer reads PCManFM's native accessibility tree, bound to the exact retained
manager PID, along with root pixels and native focus/client state. Limit tree scans
to 256 nodes, 32 children per node, depth 12, names of 256 characters and a three-second
operation deadline. Reject missing/truncated/ambiguous observations as inconclusive;
never infer a successful input operation from XShape flags or a sent event alone.
Accessibility is evidence of native menu/folder state, not a visibility oracle.
This PCManFM build exposes no icon children through AT-SPI. An empty tree therefore
cannot establish empty selection; preserve earlier tree-only attempts as observer
errors. Observe selection through the private display's native clipboard: establish
an owned empty selection, send Ctrl+C through XTEST, then request `text/uri-list` if
the selection owner changes. Allow 500 ms for each phase, at most 4096 bytes and two
URIs, each naming an exact fixture folder. Remove at most one final GTK buffer NUL;
reject any embedded NUL. Reject incremental transfers, unexpected
paths, malformed replies or reply timeouts. Unchanged ownership denotes no selected
files only in these fixed clear scenarios, with PCManFM retaining native focus and
both positive selection controls passing. It cannot establish a standalone pass.
The private display's clipboard is independent of the user's display/clipboard.

The owned runtime directory may use a short `/proc/<parent-pid>/fd/<directory-fd>`
alias to remain within Unix socket path limits. Retain the directory descriptor
until all children stop; it resolves to the same workspace, not a shared temp root.
Confirm the registry's bus-owner PID before starting the manager. Read AT-SPI through
explicit private-bus calls with 250 ms deadlines and service activation disabled;
do not use libatspi's implicit peer-connection path, whose observed timeout is retained
as a laboratory failure. Journal stimuli and completed observations as they occur.

The fixture contains `Probe Folder`, `Second Folder` and `Probe Folder/Sentinel.txt`.
The image and icon geometry are fixed by this exact laboratory. Begin with no
selected icons, then require these externally stimulated results:

| Stimulus | Independent expected result |
|---|---|
| Click Probe Folder at (60,40) | Exactly Probe Folder selected in PCManFM; candidate never becomes native focus owner. |
| Click blank desktop at (700,550) | No icons selected. |
| Drag-select from (10,5) to (115,200) | Exactly both fixture folders selected; neither folder is moved or renamed. |
| Clear, then right-click Probe Folder at (60,40) | PCManFM exposes a showing native popup with its Open in New Window item; candidate does not own focus. Escape dismisses it. |
| Clear, then double-click Probe Folder | A new PCManFM normal window named Probe Folder opens and receives native focus. Native Ctrl+A then Ctrl+C yields exactly Probe Folder/Sentinel.txt through the private clipboard. |
| Close that owned folder window, then click blank desktop | Folder window disappears; icon selection clears; original icon/background pixels are recoverable. |

Capture stage pixels and the matching semantic/native observations. Report each
step independently; a failed prerequisite leaves later dependent steps not-run.
The draft observer originally expected a showing `Open` item. The preserved native
capture/tree demonstrate that this fixture's folder menu hides that action and shows
`Open in New Window`; this laboratory expectation correction does not change the
product requirement that native context menus remain usable.
The opened folder uses a custom item view that also omits file children from its
accessibility tree. Its title, independently owned/focused normal window and exact
clipboard URI after native selection establish folder opening/content; a missing
Sentinel accessibility node is an observer limitation, not a candidate failure.
The ordinary opaque window is also the negative input control: an overlapping click
must fail icon selection while it blocks the icon. EWMH candidates may pass input
while failing placement; neither outcome overrides the other. Keep the original
reveal observation interval separate from user-created menu/folder occlusion.

## Candidate and observations

The native diagnostic probe reuses Marker 0.1 and its generation protocol. The X11
candidate sets `_NET_WM_WINDOW_TYPE_DESKTOP`, skip-taskbar/pager and no-input focus
hints before mapping. An empty XShape input region lets native pointer input pass
through. It paints only its own window. The below candidate requests the below
state and lowers its own window once; it never manipulates the icon manager.
Record the resulting client stacking order, focus, dimensions and pixel observations
separately. Window flags and request acknowledgements cannot establish visibility.

Use Openbox's actual `W-d` binding for `ToggleShowDesktop`, delivered through XTEST
on the private server. Confirm `_NET_SHOWING_DESKTOP` transitions to 1 and back to 0;
capture through the transitions. Issue changing generations while reveal is active.
Use W-02's original 50 ms cadence, 150 ms coverage and 200 ms presentation budgets.
Do not skip baseline failure when the icon manager already obscures the candidate.

Before candidate launch, capture the known icon region and wallpaper; after launch
observe whether the candidate covers icon content, is entirely occluded or has the
required composition. The independent icon manager is the source of icon pixels.
The known icon region must contain at least 100 pixels differing from the synthetic
background; compare those RGB pixels against the first candidate frame to record
actual icon concealment separately from structural stacking. Initial observation
uses unselected icons; later input scenarios require their own selection oracle.
An entirely hidden candidate or a surface above icon pixels fails placement even if
other dimensions pass. Native icon selection, double-click, drag selection and
context-menu adapters require independently observed native results before being
marked executed; structural input hints alone leave those claims not-run.

Record the wallpaper file and PCManFM wallpaper configuration before/after the
candidate interval, after the manager has initialized its own configuration. Require
exact unchanged bytes for a preservation pass. Compare the known unobstructed
wallpaper region separately. Setup of synthetic wallpaper precedes observation;
it is not a candidate operation. Do not claim wallpaper policy qualification.

## Execution and completion

Build through the existing Linux wrapper. Prepare the pinned lab explicitly, then
run `python3 tests/desktop/native_x11_host.py <owned-build-directory>`. Preserve a
unique report with source, binary, package/environment identity, raw observations,
cleanup results and unexecuted dimensions. A negative normal-window control must
actually disappear during reveal, proving that the action/observer combination
distinguishes a live conventional window from desktop persistence.

This initial investigation is complete only when its candidates have measured
placement/reveal/preservation outcomes or an evidenced lab limitation. It does not
complete W-02's full input/recovery scenarios or all W-05 target tracks. Do not
replace the whole-product desktop contract with this finite experiment's scope.

References: [Openbox actions](https://openbox.org/help/Actions),
[key bindings](https://openbox.org/help/Bindings),
[EWMH root properties](https://specifications.freedesktop.org/wm/latest/ar01s03.html),
the [PCManFM 1.3.2 desktop implementation](https://github.com/lxde/pcmanfm/blob/1.3.2/src/desktop.c),
and [GTK's documented rendering modes](https://docs.gtk.org/gtk3/running.html).
