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
