---
type: "SysPane Work Package"
title: "W-02 independent temporal desktop oracle"
description: "Close externally captured marker decoding, time coverage and native calibration before desktop qualification."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T03:17:03+11:00"}
sp_id: "SP-W02-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-ORACLE", "SP-DESKTOP", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-READINESS-2026-10-05"]
---

# W-02 independent temporal desktop oracle

W-01 and the [campaign admission](../campaign-admission.md) admit this bounded
implementation. Own `tests/desktop/`, its native diagnostic fixture and required
build targets. Do not capture the user's unrelated desktop, change their wallpaper,
restart their shell, activate privileged operations or infer target qualification.

## Scope and independence

Implement a reusable external pixel decoder and temporal evaluator, fixed independent
oracles and a native capture/stimulus runner. Parent test identities remain
T-DESKTOP-REVEAL, T-ICON-INPUT and T-WALLPAPER. W-02 also needs real platform adapters
for named reveal actions, icon input/focus and wallpaper configuration evidence.
This first boundary calibrates the pixel/time observer against native faults; it
does not complete those remaining adapters or qualify a desktop host.

The observer consumes pixels obtained from the display server/compositor, never
a screenshot, visibility bit or acknowledgement supplied by the candidate. Native
structural findings and candidate acknowledgements are separate evidence. A correct
window tree cannot replace a missing marker. A live renderer alone cannot establish
behind-icons placement or reveal persistence. Linux's owned Xvfb root is an admissible
synthetic capture source; it is not a GNOME/Plasma/Wayland or real icon-manager lab.
Windows external desktop capture remains unexecuted until an admitted synthetic
desktop is available; portable decoding/time checks still run there.

## Marker 0.1

The marker is exactly 128 by 96 RGB8 pixels, a 16 by 12 grid of 8-pixel cells.
All pixels in each cell have its declared color. Border cells alternate blue
(16,96,224) and orange (240,160,16), blue when `(column+row)` is even. The bottom-left
border cell alone is violet (160,32,192), fixing orientation. The 14 by 10 interior
cells carry 140 bits in row-major, most-significant-bit-first order: ASCII `SYPN`
(32 bits), version 1 (8), generation (uint64 big-endian, 64), standard IEEE CRC-32
of those preceding 13 bytes (32), then four zero padding bits. Interior zero is
(32,32,32), one is (224,224,224). Generation zero and uint64 maximum are valid.

Decode the central 4 by 4 pixels of every cell; every sampled component must be
within 8 of its declared channel value. Do not average away a corrupt pixel or
accept a checksum mismatch, wrong border, version, dimensions or padding. Placement
is the exact independently configured capture rectangle in this initial profile;
no search, rescaling, interpolation, alpha or text-rendering tolerance is inferred.
Golden matrix fixtures include literal bit rows/CRC values independently of the
native C++ painter. Python uses its standard CRC implementation; the native fixture
uses a separate bitwise implementation. No encoder generates the oracle at test time.

## Temporal observation 0.1

Inputs are an observation interval, strictly increasing stimulus generations/times,
and ordered frame records. All times are nonnegative integer microseconds in the
observer's monotonic domain, not wall clock or producer time; bools are invalid.
Limit an interval to 60 seconds, 128 stimuli and 1,200 frames. A frame holds exactly
36,864 RGB bytes, start/end observation times and an explicit capture origin.
Stored frames use bounded zlib plus base64 with a SHA-256 of the uncompressed RGB.
The decoder caps both compressed input and decompressed output; a trace file is at
most 32 MiB. Duplicate JSON keys and unsupported trace versions are invalid.

The first stimulus precedes/equal interval start and is the already-established
baseline. Every later stimulus lies within the interval and has at least 200 ms
before the next stimulus/end. Frames lie entirely within the interval, have
nondecreasing nonoverlapping capture ranges, and at least one frame is required.
Malformed bounds/order are invalid evidence, not a successful observation.

Capture at a nominal 50 ms cadence. A capture duration over 50 ms, missing initial
or final coverage over 150 ms, or a gap between consecutive capture ranges over
150 ms makes otherwise successful evidence inconclusive. Equality is within budget.
At least three frames and one observed post-baseline generation change are required
for a temporal pass. Durations and actual gaps are recorded; no synthetic frames
fill a gap. Only `display_server_root` or `compositor_output` can establish temporal
pixel evidence; `candidate_buffer`, `window_flags` and unknown origins are ineligible.

An invalid/missing marker in any eligible observed frame is a failure, including a
single intervening disappearance between correct before/after frames. A generation
never issued by frame end, or a regression below the last observed generation, fails.
The previous issued generation is permitted while a new update is within its 200 ms
presentation budget. Once frame start is at/after that deadline, the current issued
generation must be present. Each stimulus must be observed before its next stimulus
or the interval end. A definite observed defect remains fail even if a separate gap
also exists; insufficient/ineligible observation alone is inconclusive. The evaluator
reports reason codes, observed generations, maximum gap/capture time and sample count.

## Native calibration and lifetime

`SysPane.OracleProbe` is a Linux/X11 test executable, not the product surface or a
supported desktop host. It creates one owned 128x96 window at (32,32), paints the
fixed marker and accepts only the `_SYSPANE_ORACLE_GENERATION` native ClientMessage
on that window. Two uint32 words encode the generation, remaining words are zero,
format is 32 and generations increase. A native close message exits. At most 128
updates and 15 seconds per invocation are allowed. Synthetic fault modes are live,
hide-on-second-until-third generation, and freeze-after-first generation. An accepted
generation property records event-loop progress independently of actual painting.
No command carries a path, code, arbitrary window handle or production privilege.

The runner launches only this exact artifact and an owned authenticated Xvfb server
with no TCP listener, following the diagnostic harness's private-cookie/abstract
socket/PID checks. Use only the owned server's root, not inherited DISPLAY. All
capture and native input work runs in a bounded child; a blocked X call cannot hang
the parent indefinitely. The parent retains every launched process and confirms
exit before cleanup. The X server's own windows contain synthetic content only.
No screenshot of a user desktop or shell termination is admitted by this package.

The native observer controls stimulus independently, captures root pixels at the
known rectangle and records every frame, not only successful ones. It checks the
probe's announced XID against the owned process PID and fixed class/name. Surface
stdout contains only bounded bootstrap data; property acknowledgements cannot
override capture. Before launch and after confirmed exit, root pixels/configuration
are recorded separately: full 800x600 synthetic root pixel digest and bounded
`_XROOTPMAP_ID`, `ESETROOT_PMAP_ID`, `_XSETROOT_ID`, `_NET_SUPPORTING_WM_CHECK`,
`_NET_CURRENT_DESKTOP`, `_NET_SHOWING_DESKTOP` property presence/type/value snapshots.
A mismatch prevents a wallpaper-preservation calibration
claim, which remains distinct from real wallpaper-file/policy qualification.

Each calibration lasts about two seconds with baseline generation 1, then 2 and 3
at independently measured stimulus times. Native targets, oracles and trace digests
are bound to the exact source/profile. A failed calibration preserves its original
frames and failure record. No tolerance is widened after a failure.
Flush each frame/stimulus to a task-owned capture journal so interruption does not
discard the entire observed prefix. Successful reports embed all compressed frames;
the journal remains in owned build output with a digest. Confirm candidate, observer
and X server exit; unconfirmed cleanup cannot produce a calibration pass.

| Case | Fixed result |
|---|---|
| ORACLE-UNIT | Literal golden matrices decode; corruption, overflow, dimension/encoding errors, replay, unsupported origins, exact deadline boundaries and coverage gaps have fixed outcomes. |
| ORACLE-01.LIVE | Independently captured root marker advances through all three generations with complete bounded coverage; temporal observation passes. |
| ORACLE-01.DISAPPEAR | Native probe unmaps for generation 2 and returns at 3; before/after can be correct, but intervening missing pixels produce fail. |
| ORACLE-01.FREEZE | Probe acknowledges later generation events while marker remains at 1; temporal observation fails its update deadline. |
| ORACLE-01.OCCLUDE | A second owned test window covers the marker temporarily; root capture sees the obstruction and fails despite an unchanged live candidate. |
| ORACLE-01.GAP | Deliberately omit capture for at least 300 ms; otherwise valid advancing pixels yield inconclusive, never pass. |

The test suite passes when the calibrated evaluator produces these predeclared
outcomes; fault cases are not desktop-product passes. Evidence keeps evaluator
outcome and calibration-test outcome separate. Ordinary CMake/CTest commands run
the portable checks on both profiles and native X11 calibration only on Linux.
Profile-specific component metadata identifies the Linux-only executable explicitly.

## Completion and handoff

W-02 remains in progress until named native reveal action/input/focus/wallpaper
adapters and their admitted lab checks exist. W-03 through W-06 can use a calibrated
observer for bounded candidate experiments, reporting missing lab capabilities and
unexecuted dimensions individually. No conventional preview, headless X server,
static screenshot or window flag may be promoted into a wall-conformant result.
The next handoff identifies executable commands, passed calibration, original
failures, raw capture ownership, exact environment and pending platform adapters.

Native references: [Xlib image capture and native events](https://www.x.org/releases/current/doc/libX11/libX11/libX11.html)
and [EWMH window-type properties](https://specifications.freedesktop.org/wm/latest/ar01s05.html).
Property declarations are structural intent, not independent visibility evidence.
