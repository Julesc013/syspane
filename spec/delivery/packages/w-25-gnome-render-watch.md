---
type: "SysPane Work Package Boundary"
title: "W-25 independent supervision of the measured GNOME tile"
description: "Bind render challenges to drawing and enforce their deadlines outside the shell event loop."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T10:00:00Z"}
sp_id: "SP-W25-GNOME-RENDER-WATCH"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-W25-GNOME-LIVE-NETWORK"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 independent supervision of the measured GNOME tile

The existing producer/data tests do not supervise rendering. Reuse RenderWatch and
the admitted recovery-health 0.1 protocol in an independent native process. Keep
process health, producer health, sample freshness, instrumented render completion
and observed pixels distinct. This package adds no authority to terminate a user
shell or restart an installed desktop.

## Native ownership and protocol

Add a Linux-only `render-watch ENDPOINT JOURNAL` mode to the existing RecoveryProbe.
GNOME launches and retains that child in its own POSIX session. The child arms the
existing parent-death guard, binds one owned 0600 Unix socket under an owned 0700
directory and admits only its actual parent PID. Its native event loop owns one
RenderWatch and one ProducerLease; it does not run in the GNOME main loop.

Use recovery-health 0.1 with desktop role and recovery.progress, unchanged frame,
handshake, epoch, connection and direction rules. Extract an asynchronous input/
output surface from the existing HealthLink state machine; its existing native
stream adapter must keep identical behavior. Bound each supplied read to 4 KiB,
each receive turn to 16 messages, and pending output to 16 frames/64 KiB. A framing,
identity, ordering, timeout or capacity error closes that protocol lifetime. GJS
uses this same native parser through the existing introspection library; no second
JavaScript health protocol is introduced.

The common asynchronous process/socket owner serves both network and health
sessions. Retain two-second startup and eighteen-second overall bounds, 50 ms
service ticks, one-second heartbeat cadence and one-second forced-child teardown
fallback. No blocking socket IO or process wait is added to shell callbacks. GJS
holds the native peer PID/socket and exact uint64 challenge strings. Policy stays
owned by the network consumer; health messages carry no operational payload or
disclosure grant.

The native watcher challenges at least once per second when its previous challenge
is complete. Exactly one challenge may be outstanding. Its existing 3,000 ms expiry
cannot be postponed by heartbeat, unrelated drawing or another challenge request.
An exact timely completion clears it; late completion cannot clear a stalled
lifetime. The watcher observes native time at least every 100 ms while runnable.
Native capture allows up to 200 ms scheduling/observation latency; portable exact
deadline equality is unchanged.

Advance both guards before dispatching every admitted health event as well as on
idle turns. Progress, renewal and normal shutdown queued while the watcher was
stopped cannot erase a deadline that has already elapsed at native receipt.
`tests/fault/native_render_deadline.py` stops only its held owned watcher, queues
each of those three messages after expiry and independently requires the original
latched fault and native failure exit. Its stopped interval does not claim runnable
scheduling latency; fault publication must occur within 200 ms of confirmed resume.

The watcher writes at most 64 KiB of public lifecycle/challenge/heartbeat events
to an exclusively created 0600 journal under the attempt's 0700 directory. Include
original native monotonic times, pending challenge, completion count and time since
heartbeat. No interface identifiers, counters or operational pixel data appear in
this journal. On render or health expiry, record the latched fault independently,
request session shutdown and exit with failure. Explicit client shutdown exits
normally. A dead watcher cannot be treated as a healthy renderer. Native watcher
exit is separately observed through a held pidfd.
The native shell-side health view also expires its watcher's heartbeat lease after
3,000 ms; a living but stopped watcher cannot leave the tile indefinitely trusted.

## Drawing completion and closure

Start supervision after the second real network publication. A pending challenge
is consumed only by the operational drawing path after it updates the tile's
labels/status from the native projection. A subsequent stage after-paint callback
may complete that staged challenge while the tile is visible and mapped. Neither
heartbeat processing nor GetState may complete a challenge. Only one staged
generation is retained; the next challenge cannot overwrite it.

The stage callback is instrumented paint progress, not proof of display visibility.
GNOME's [after-paint signal](https://mutter.gnome.org/clutter/signal.Stage.after-paint.html)
precedes presentation; qualify its use against the pinned laboratory runtime and
retain independent pixels. An unrelated global paint cannot rescue a challenge
that the operational drawing path has not consumed. Remove the callback, pending
generation and actors before acknowledging revocation or explicit closure. Late
IO/paint callbacks cannot reopen the owner. Watcher failure clears the network
tile and closes its session; all three native descendants must actually exit.

## Fixed owned native experiments

The private test interface may freeze only the drawing path, hide the tile, or
deliberately lie about progress. It remains unavailable on an active user desktop.
Use the same calibrated operational glyphs and original source journal as the
measured-tile package. Record all operational crops privately. Begin each case
with two independently observed paint completions and advancing age.

| Mode | Required observation |
|---|---|
| live | Native challenges complete; original values and age advance; normal stop clears actors and confirms all child exits |
| render-stall | Drawing stops while source and shell health continue; pixels freeze; independent render expiry latches within the deadline allowance and closure erases the tile |
| false-progress | Drawing stops but the injected fault acknowledges challenges from the health path; native health alone remains satisfied while independent pixel/progress acceptance fails |
| hidden | Drawing is made invisible; unrelated stage paints cannot complete its challenge; independent expiry and closure follow |
| revoke | Typed revision 8 denial erases pixels, removes pending paint callbacks and gracefully stops the watcher and collector before any later projection |
| watch-exit | Kill only the held owned watcher through its pidfd; the shell clears the tile and releases the collector; no replacement or silent reset |
| watch-hang | SIGSTOP only the held watcher; the native client expires its heartbeat lease, clears the tile, and confirms forced watcher exit after the existing one-second grace |
| shell-freeze | SIGSTOP only the held owned laboratory shell; the separate watcher records render/health failure while shell pixels stop; SIGCONT that same lifetime in a finally path, then require erasure and native exits |

The stopped shell cannot repaint. Measure shell-freeze erasure from confirmed
resume, explicitly preserving the interval of surviving pixels. Do not claim that
a watchdog can repaint a stopped compositor. The independent observer remains
runnable and records the original native fault before resuming the shell.

The shell also stops renewing its existing telemetry consumer lease. That lease
may close the worker before the independent watcher expires; neither timer is
extended for this experiment. In shell-freeze only, admit either normal source
shutdown or the existing consumer-expiry path (worker exits normally, supervisor
records health/data EOF, observed child exit or peer-clock loss and exits with
failure). The two sockets and child wait have no promised delivery order. Require original lifecycle evidence
and actual exits in both cases. A nonzero child exit remains a failed owner even
when a sibling initiated closure before the wait callback delivered that exit.
Preserve the first failed experiment and its original normal-source-only oracle;
this amendment recognizes the previously specified independent consumer lease.

For stall/hidden cases require an original pending challenge, no completion for it,
native elapsed time in [3,000,3,200] ms, and a last heartbeat younger than 1,200 ms
at the render fault. The healthy producer/watch remains independently alive until
closure. False progress must retain a failed candidate outcome despite continuing
native completions. Final clearing has the existing 200 ms presentation allowance,
450 ms coverage and at least three settled blank captures. Restore the original
marker and icon-manager checks after all operational pixels are cleared.

Run native cases with completed Windows workspace preflights, exact build/library/
typelib identities and source archives. Preserve failures and independently recompute
results from original journals/crops. Recheck native health adapters, the existing
network session, measured tile, public clock and affected extension inventories.
Automatic renderer replacement, editor-exit recovery, protected policy and complete
product recovery remain mandatory separate gates; this watcher does not claim them.
