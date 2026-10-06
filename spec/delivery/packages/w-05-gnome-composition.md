---
type: "SysPane Work Package"
title: "W-05 GNOME icon composition experiment"
description: "Calibrate separated marker and opaque icon witnesses against a real owned DING desktop."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T00:30:00Z"}
sp_id: "SP-W05-GNOME-COMPOSITION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-PACKAGE", "SP-W02-PACKAGE", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 GNOME icon composition experiment

Use the pinned owned GNOME laboratory and its source-bound runner. This extends
the optional investigation, not the product runtime or public transport. The
original Openbox/PCManFM placement failures and GNOME marker calibration remain
unchanged historical evidence. Collection never runs inside the shell bridge.

## Fixture and independent observations

`tests/desktop/fixtures/gnome-composition-0.2.json` owns scene version 0.2.0. The owned
800x600 desktop has the existing solid background (48,72,96), a marker at (300,200)
with its original 128x96 encoding, and a separate overlap rectangle at (0,32), size
180x220, painted (192,32,128) by the candidate. Keep the observer outside the shell.

Create one synthetic `Probe Folder` containing `Sentinel.txt` in the private HOME's
Desktop. An owned icon theme supplies a 64x64 fully opaque folder PNG with four
32x32 quadrants: (24,208,80), (40,80,232), (232,176,24), (208,40,40). The native
icon manager chooses its normal initial position and scales the icon if required.
Disable home/trash/volume icons in this laboratory. Never move/reorder an icon or
adjust the scene to the candidate's observed output during a case.

Copy the exact pinned DING extension into this attempt's private extension directory
and retain its file identity. Its stale-process reconciliation then names a unique
owned path. Enable DING through the ordinary private GNOME settings before startup;
no DING source patch or fake icon painter is admitted. Bind the real icon window
through X-Resource to its local GJS process, exact owned `app/ding.js` argument and
the retained shell's process group/session. Hold its pidfd through observation.
Missing/ambiguous native ownership is a lab failure, never composition success.

Before enabling the candidate, dismiss the shell overview through native Escape.
Allow at most five seconds for the icon-manager prerequisite. While the candidate
remains hidden, initialize the owned background to black, then white, then restore
(48,72,96). For each stage, allow at most five seconds for an independently captured
background witness to equal the requested RGB value and take three stable overlap
frames 100 ms apart. Each fixture quadrant must contribute at least 64
exact-color pixels in the overlap region, and at least 400 region pixels must equal
the known background. Each stage's three frames must match exactly. Those native root pixels
define fixed opaque anchors and clean background witnesses for that case; their
locations cannot be changed after candidate enablement. A missing fixture is a
laboratory failure rather than a weakened or empty mask.

An opaque anchor must have the same quadrant RGB in all three background stages.
A clean witness must equal black on the black background, white on white, and the
baseline color after restoration, at the same coordinate. No candidate pixels
participate in selecting either mask. The independent oracle requires every opaque
anchor to retain its original RGB value and every clean witness to show the
candidate's rectangle color. It does not
compare antialiased label/edge pixels against their old background. This permits
normal alpha blending while proving the drawing exists behind opaque icon content.
The separate unoccluded marker must satisfy the unchanged Marker 0.1 timing oracle.
All three dimensions are required for a composition pass.

The preserved 0.1.0 fixture selected clean pixels from the dark baseline alone.
Its first live result failed because 189 label-shadow pixels rounded to the same
dark RGB but yielded (191,32,127) over the expected (192,32,128). That does not prove
bare background: alpha compositing and integer rounding explain the ambiguity.
Version 0.2.0 explicitly calibrates transparent and opaque witnesses against two
independent extreme backgrounds before the candidate exists visually. Keep the
0.1.0 fixture, original result and source archive; do not relabel that run as passed.
No pixel tolerance, native icon requirement or marker deadline is relaxed.

## Controls, lifetime and bounds

`--composition live|above-icons|below-wallpaper` enables this fixture. All modes
begin with the candidate hidden; the observer issues the additional laboratory
`SetSceneEnabled(bool)` method on the existing private marker object after capturing
the baseline. The ordinary marker-only mode retains its original method surface.
The selected parent is fixed for a case: background group above background actors
for live, shell UI group above desktop windows for the negative above-icons control,
or index zero of the background group for the negative below-wallpaper control.
For the below control, move only the two owned actors to the bottom once when
enabling the scene, after all background calibration finishes. GNOME replaces
background actors during those setup changes; a creation-time index alone was
observed to leave the original below control above the replacement background.
Preserve that unexpected passing negative-control result as an implementation
error; it cannot calibrate the fixture. Do not restack during the measured interval.
Both the marker and overlap rectangle share that parent/visibility lifetime. All
are nonreactive and nonfocusable; disable destroys both and unexports the object.

Capture the unchanged 2,400 ms / three-generation marker trace and an accompanying
overlap frame at each sample. Record timestamps for both captures. Require at most
50 ms combined capture duration and 150 ms coverage gaps. The first candidate
sample follows the same fixed 250 ms initialization allowance. No extra warmup is
introduced to hide an absent marker or concealed icon. Keep a separate unchanged
background witness at (600,400), size 128x96, and read the private background setting
values before/after the interval. This proves only the selected synthetic color
case, not image-wallpaper or mandatory-policy qualification.

The above-icons control must retain a live marker and visible overlap rectangle
while failing opaque-anchor preservation. The below-wallpaper control must preserve
opaque anchors while failing rectangle visibility and marker visibility. A native
startup error cannot satisfy either negative control. Preserve complete traces and
interrupted journal prefixes, capped at 8 MiB/160 records, inside the owned attempt.
Use the existing 40-second observation and bounded group-cleanup limits.

## Completion and next boundary

Record exact source/runtime/fixture identities, independent native window ownership,
raw baseline/sample pixels, recomputed results and confirmed process cleanup for all
three controls. A candidate may fail; a complete, valid experiment is still evidence.
Run adversarial evidence checks that reject altered masks, ownership, captures,
timestamps, settings, verdicts and missing controls. Keep native startup/oracle
failures and their original source inputs.

This package does not qualify reveal, focus/taskbar behavior, icon input, multi-monitor
scaling, image wallpaper, shell/icon-manager recovery, Wayland or the full product.
Those require separate native observations after this composition boundary works.
