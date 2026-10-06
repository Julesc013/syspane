---
type: "SysPane Work Package"
title: "W-05 owned GNOME composition investigation"
description: "Test a pinned shell bridge on a private display without claiming a supported desktop."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:05:00Z"}
sp_id: "SP-W05-GNOME-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-PACKAGE", "SP-W02-PACKAGE", "SP-LINUX", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 owned GNOME composition investigation

The existing Openbox/PCManFM window-stacking experiments remain failed placement
evidence. Investigate the separate GNOME shell bridge already admitted by SP-LINUX:
an owned drawing actor above the shell background and below desktop icon actors or
windows. Keep collection and untrusted document processing outside the shell.
This bridge explicitly has reduced process isolation: extension code executes in
the shell. No product capability is enabled by this laboratory investigation.

## Laboratory closure

Use only the existing unprivileged Ubuntu 24.04 WSL account, an owned authenticated
800x600 Xvfb display and the declared Linux build root. Pin GNOME Shell 46, its
Mutter/GJS dependencies and Desktop Icons NG through the exact Ubuntu package
versions, archive sizes and SHA-256 values in `build-support/gnome-lab-packages.json`.
The lock is a snapshot of locally available APT metadata with recommends disabled.
Preparation downloads at most 128 MiB and extracts at most 512 MiB in a new
`gnome-lab/sysroot`; it never installs packages or runs their scripts. Record the
full extracted identity. Existing/partial outputs are preserved, not replaced.

Use private HOME, XDG directories, session bus, accessibility bus and display
authentication. Do not inherit the user's display, Wayland, session-manager or bus
addresses. The private bus has no service activation directories. Disable inherited
system-bus access by directing it to a second owned bus with no system services.
The initial nonexistent-socket experiment failed during GNOME login-manager proxy
construction and is preserved. An empty private bus supplies connection plumbing,
not real login, device, power or policy services; none of those behaviors is qualified.
Never run a session
manager, system service, portal, package installer or user autostart. GSettings uses
an owned keyfile backend and copied/compiled pinned schemas; only the synthetic
lab's wallpaper configuration may be initialized before observations. This isolates
trusted laboratory activity; it is not a security sandbox for hostile extensions.

Launch only retained owned children; a parent bounds observation to 40 seconds,
with at most 20 additional seconds for confirmed group termination and reaping,
records exit status/logs and confirms termination. A failed bootstrap or unavailable
dependency is a laboratory failure, not desktop incompatibility. Record actual
software rendering/display characteristics; an Xvfb result cannot qualify native
Wayland, GPU presentation, the user's session or another shell version.

The first executable gate is shell bootstrap: its real window-manager resource
must become available on the private display, with captured root pixels and exact
runtime identities. This is a prerequisite, not a placement or input pass. Preserve
failed attempts and their exact source bytes before adjusting the bootstrap.

## Composition and acceptance boundary

The next bounded prerequisite enables a trusted Marker 0.1 extension on this shell.
It owns a nonreactive 128x96 actor at (300,200) in the existing background group.
It exports only the laboratory `org.syspane.LabMarker.SetGeneration(uint32)` method
at `/org/syspane/LabMarker` on the private shell connection; values 1 through
4,294,967,295 paint the existing uint64 marker encoding. This is an experiment
stimulus, not a production transport or public capability. Disable destroys the
actor and unexports the object. No collection, document loading or external plugin
code runs in this bridge.

`--marker` enables this prerequisite. Dismiss the initial overview through native
Escape on the owned display before sampling. Request generations 1, 2 and 3 at
0, 800 and 1,600 ms across a 2,400 ms trace. Reuse the fixed 50 ms cadence, 150 ms
coverage and 200 ms presentation deadlines with the unchanged external decoder.
Keep the first image after the initial 250 ms paint allowance; an absent marker
fails rather than extending that allowance. Preserve shell/native identity and
whole-desktop baseline/end frames separately. This trace proves only changing
background-layer pixels on a shell without an admitted icon-overlap fixture;
icon composition, native reveal/input and wallpaper policy remain not-run.
Calibrate that same trace with `--marker-control hidden` and `frozen`. The hidden
actor still accepts stimuli but must fail marker presence; the frozen actor keeps
generation 1 and must fail the generation deadline. Neither control relaxes the
live trace. A failing candidate returns exit 1 and retains its complete raw trace;
the verification record distinguishes an expected negative control from a lab error.

Keep Marker 0.1 and its independent decoder/time tolerances. Before claiming a
composition pass, close a versioned fixture with a legible marker region and a
separate intentional icon-overlap witness. A correctly layered icon may occlude
part of a drawing, and antialiased icon edges may blend with its background; the
old overlapping full-marker experiment must not be silently reinterpreted as a
positive composition oracle. Preserve its verdicts. Require independently calibrated
opaque icon anchors and above/below negative controls in the new fixture.

Native reveal, focus/taskbar/input routing, wallpaper preservation, icon-manager and
shell recovery need separate observations. An actor's parent, a submitted frame,
an extension enable result or a shell screenshot does not prove visible placement.
Capture from the independent display server/compositor output. No foreign window
painting, icon rearrangement, wallpaper rewrite during a candidate interval or
ordinary-window fallback is admitted.

The implementer may choose trusted bridge internals and bounded lab plumbing,
recording material choices. Changing the product desktop contract, claiming an
unobserved outcome, controlling the user's shell or privileged operations is outside
this package. Keep W-05 open until the remaining platform/capability gates are met.

## Execution and handoff

Prepare with `python3 build-support/prepare_gnome_lab.py <owned-build-directory>`
after the workspace preflight. Run the bounded bootstrap with
`python3 tests/desktop/native_gnome_bootstrap.py <owned-build-directory>`.
Record the source base plus exact changed inputs, archives/runtime, commands,
captured pixels, process cleanup and every unexecuted claim. The next package step
is a calibrated composition/reveal fixture, then live bridge generations and input.
