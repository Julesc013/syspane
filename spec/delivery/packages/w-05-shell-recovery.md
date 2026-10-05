---
type: "SysPane Work Package Boundary"
title: "W-05 owned X11 window-manager recovery"
description: "Measure native manager replacement and candidate continuity without promoting failed placement."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-05T23:38:03Z"}
sp_id: "SP-W05-SHELL-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W05-PACKAGE", "SP-W02-PACKAGE", "SP-ORACLE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-05 owned X11 window-manager recovery

Use the existing unprivileged, authenticated Xvfb/Openbox/PCManFM laboratory and
its single host-investigation runner. Add an optional `--restart-window-manager`
experiment after the unchanged reveal interval. Own the observer in
`tests/desktop/`, with independent evidence verification in `build-support/`.
This boundary does not authorize control of an inherited display or user shell.
The campaign's current combined 2 GiB allocation applies.

## Fixed question and ownership

Can the exact owned Openbox process be stopped and replaced while the candidate
continues processing generations, with replacement identity and rendered output
observed independently? Measure manager recovery, candidate progress, pixels,
coverage and wallpaper separately. A continuing event loop is not visible recovery.
The previously failed above/below candidates keep their placement failures.

The parent retains the original Openbox child, kills only that process, and waits
at most two seconds for its native exit. Before requesting the stop, the separate
observer holds a pidfd to that exact process. The parent must receive the observer's
independent exit confirmation before launching one replacement from the same
pinned binary and configuration. Hold the manager absent for at least 350 ms after
that confirmation so the absent interval is observed. Retain both children through
cleanup. PCManFM, Xvfb, the session bus and the candidate remain the original
processes; unexpected exit is a laboratory failure.

Verify the original and replacement manager through the root's
`_NET_SUPPORTING_WM_CHECK`, its self-reference and the X server's X-Resource 1.2
local-client PID for that resource. Preserve `_NET_WM_PID` separately when present;
it is an optional property, not mandatory proof of manager identity. Verify the
candidate HWND-equivalent XID/class/PID through the existing observer. The new
supporting-window/process binding must differ from the old one; an XID can be
reused after its client exits and is not a process creation identity. Allow at most
five seconds from the external restart request to observed replacement readiness,
within the existing 30-second case and 15-second candidate bounds. An unavailable
identity or insufficient time is failed/inconclusive evidence, never inferred success.

The first attempt failed before any shell stop because the observer required
`_NET_WM_PID` on Openbox's supporting window. EWMH does not require that property
there. Correct this observer contract using server-reported resource ownership,
not by accepting an unbound window/name. Preserve the original attempt and source.
Require and pin the installed libXRes runtime; query extension/version first,
request only the single supporting resource's local PID, and reject missing or
ambiguous ownership. Bind the returned client resource base through the server's
bounded (at most 64) client base/mask table; the reply need not repeat the full
window XID. Preserve the two failed equality-check attempts. A transient missing
supporting window during startup remains not-ready, within the same deadline.
This owned X server and its clients share the same PID namespace.
References: [EWMH supporting window](https://specifications.freedesktop.org/wm/1.5/ar01s03.html#idm45539547193552),
[X-Resource protocol](https://sources.debian.org/src/xorgproto/2018.4-4/resproto.txt/).

## Stimulus and observations

The existing reveal trace finishes at generation 3 and remains unchanged. Start a
separate recovery journal/clock, send generation 4, and begin fixed-region root
capture. After at least 250 ms request the stop. After pidfd-confirmed exit, send
generation 5 before permitting replacement. After the new manager's native identity
is observed, send generation 6 and continue capture for at least 700 ms.

Use the existing 50 ms capture cadence, 50 ms maximum capture duration and 150 ms
maximum coverage gap, retaining every frame and the interrupted prefix. Cap this
recovery interval at eight seconds, 160 frames and an 8 MiB journal. Capture origin
remains `display_server_root`; candidate acknowledgements are separate metadata.
Record actual stimulus, stop, exit, launch and readiness times in the observer's
monotonic domain. Do not put this expected shell outage into the no-disappearance
reveal interval or relax that interval's acceptance.

Event-loop continuity requires an observed generation-5 acknowledgement before
replacement readiness and generation 6 afterward. Compute post-ready visible
recovery from every captured frame beginning at least 200 ms after generation 6:
the marker must decode to 6 and the baseline native icon pixels must remain exact.
Missing pixels or concealed icons fail that dimension even when the manager and
candidate recover. A coverage defect alone makes an otherwise passing pixel result
inconclusive. Definite observed defects remain failures. Require three post-deadline
frames. Record the first observed final-generation time, without claiming display
latency beyond the actual capture bracket.

The unchanged wallpaper region and exact configured file/settings bytes remain
separate preservation checks. Initially run the named solid-color profile; any
later image profile must independently preserve its original configuration and
pass the existing image-pixel oracle. No input claim follows from this recovery
experiment. Do not combine it with `--icon-input` until a combined lifetime/resource
contract is closed; existing native input experiments remain available unchanged.

## Acceptance and evidence

For each existing candidate (`live`, `desktop`, `desktop-below`), preserve the
unchanged reveal result, then record the complete owned restart sequence or the
exact failure. A completed investigation may contain failed surface recovery.
Require independently confirmed old-process exit before replacement, observed new
manager identity, candidate continuity, unchanged fixture/preservation evidence and
confirmed exit of every owned process. Recompute pixel/coverage/continuity outcomes
from the recorded frames and events in the recorder; reject invented success,
missing exit proof, wrong identities, changed timestamps and incomplete journals.

This is one initial native shell-recovery track. Icon-manager/compositor crashes,
full controller/collector continuity, product renderer reattachment, input after
recovery, Windows/XP/7/macOS and other Linux shells remain required independently.
It cannot close W-02, W-05 or W-25 as a whole.
