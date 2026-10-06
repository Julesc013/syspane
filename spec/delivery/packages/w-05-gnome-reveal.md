---
type: "SysPane Work Package"
title: "W-05 GNOME native desktop reveal experiment"
description: "Observe the composed scene while a real foreground window disappears and returns through Show Desktop."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:00:00Z"}
sp_id: "SP-W05-GNOME-REVEAL"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-GNOME-COMPOSITION", "SP-W02-PACKAGE", "SP-DESKTOP"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 GNOME native desktop reveal experiment

Extend the owned GNOME 46 X11/DING experiment, retaining its pinned runtime,
private buses, authenticated Xvfb, exact icon calibration and temporal oracle.
The question is whether the live composition persists through native Show Desktop
with an ordinary foreground window present. This is one named reveal scenario;
it cannot qualify other shell actions, Wayland or a complete product host.

## Closed scenario and independent observations

`tests/desktop/fixtures/gnome-reveal.json` fixes the experiment. The parent launches
one owned GTK 3 process on the private display. It draws a solid (24,160,192),
undecorated normal window at (500,60), size 200x120. It is neither a desktop window
nor a candidate surface. Bind its X window through X-Resource to the exact retained
process, script, process group/session and start ticks; hold a pidfd through the
trace. Check normal type, exact client geometry and an interior 20x20 pixel witness
at (540,90). An absent, displaced, ambiguous or dead window is a laboratory failure.
This fixture does not overlap the marker, icon rectangle or background witness.

Before measurement, the private setting
`org.gnome.desktop.wm.keybindings show-desktop` is explicitly `['<Super>d']`.
This is a named configured action, not a claim about GNOME's default binding.
Run the complete existing live composition prerequisite. Click the foreground
fixture through native XTEST and allow at most two seconds for it to become the
active client, show the exact cyan witness and report `_NET_SHOWING_DESKTOP=0`.
Read the binding and background settings before and after; never change them
during the measured interval. The helper may request its fixed geometry during
setup only. No restacking, layout repair or foreign window changes are admitted.

Observe 2,400 ms. Initialize marker generation 4 with the existing 250 ms allowance;
issue generations 5 and 6 at 800 and 1,600 ms. Send real Super+D press/release
events at 400 ms and 2,000 ms. Record actual action start/end times. Each action
must start within 50 ms of its scheduled time and finish within 50 ms. Within
200 ms of each completed action, the native desktop state and foreground pixels
must change together: first state 1 and the unchanged background RGB where the
foreground witness was; then state 0 and the exact cyan witness again. Preserve
those outcomes until the next action starts/end of trace. Initial and restored
normal states must name the foreground client as active. No specific focus target
is mandated during desktop reveal. Record actual native focus throughout.

Capture marker, icon overlap, foreground witness and background witness in each
50 ms sample. Preserve each capture's order and the complete native state snapshot.
The combined capture/state observation must take at most 50 ms; coverage gaps at
most 150 ms. The unchanged marker oracle requires continuous visible valid frames
and each generation within 200 ms. Reuse the independently established opaque and
transparent masks for every overlap frame. Every background witness must retain
the exact configured color. Native flags or successful key injection alone cannot
satisfy the visible transition. Final recovery cannot erase earlier disappearance.

## Controls, evidence and completion

`--reveal live|no-action|transient-blank` implies live composition. `no-action`
records the two scheduled stimuli as intentionally omitted; it must preserve
marker/composition/background but fail the native/pixel reveal transition.
`transient-blank` performs both native actions and temporarily hides only the two
owned candidate actors through the existing laboratory method at 1,000 ms,
restoring them at 1,200 ms. It must pass native reveal and icon/background
preservation, but fail continuous marker and rectangle visibility. For control
calibration, record native visible transitions separately from foreground-focus
restoration. Both remain required for full reveal acceptance; a failure in one
must not obscure the other. Retain the
later visible frames too. This controls the prohibition on repairing a temporal
failure into a pass. A startup error cannot satisfy either control.

Keep original sources, raw frames, stimuli, settings, native ownership, mapped
runtime identities and an append-only journal (8 MiB, 180 records). Keep the
existing 40-second observation and bounded owned-group cleanup limits. Stop only
retained owned groups. Recompute all verdicts independently of the shell bridge;
reject altered state/pixels/timing/ownership, incomplete controls or unconfirmed
exit. Complete all three controls with identical source inputs and preserve every
failed attempt. A valid failed candidate still informs the next bounded experiment.
The first complete live attempt restored the window's pixels but left the native
active client on DING. Preserve its failed acceptance and do not relax the focus
requirement. Diagnostic visibility/focus fields explain that same failure; they
do not turn the candidate into a pass. Its cause requires a separate native
baseline comparison before attributing it to GNOME, DING or the candidate bridge.

Icon input/drag/menu/opening, taskbar and task-switcher absence, broader focus
behavior, image wallpaper/policy, shell/icon-manager recovery, GPU presentation,
scaling, other GNOME versions and the product vertical remain separate gates.
Use the ordinary runner/recorder commands in the build guide. No privileged
operation, user desktop or public release is part of this package.
