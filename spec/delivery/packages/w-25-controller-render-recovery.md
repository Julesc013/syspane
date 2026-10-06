---
type: "SysPane Work Package Boundary"
title: "W-25 automatic recovery from independent render failure"
description: "Connect the existing render and health guards to the persistent native desktop replacement owner."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T12:12:00Z"}
sp_id: "SP-W25-CONTROLLER-RENDER-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-GNOME-CONTROLLER-RECOVERY", "SP-W25-GNOME-RENDER-WATCH"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 automatic recovery from independent render failure

Extend the existing finite controller composition and GNOME recovery experiment.
Retain the original `live`, `no-reattach` and `revoke` crash controls and their
oracles. Add five explicitly named controller controls below; run all eight with
identical source inputs. No installed desktop or unrelated process is admitted.

## Native ownership and interaction

The existing native controller owns one additional listener, accepted stream,
HealthLink, ProducerLease and RenderWatch per admitted shell lifetime. Reuse the
recovery-health 0.1 contract and exact child/session authentication. Bind `r/s`
inside the existing owned IPC root before launching the child. A shell must attach
its render health within two seconds of its admitted operational subscription;
the prior fifteen-second shell-startup allowance remains unchanged before that
subscription. Health grants no operational disclosure authority.

Use the same challenge/paint callback path as the separately owned watcher. For
this attached controller mode, start it on the first original complete projection;
replacement snapshots need not have generation 2. Keep one pending challenge,
one-second challenge/heartbeat cadence, three-second render and health deadlines,
and the existing asynchronous startup/teardown bounds. The shell's attached render
session never owns or signals the controller. Bound its diagnostic receipts and
paint trace to 256 entries for the existing sixty-second composition; earlier
eighteen-second standalone watcher limits remain unchanged.

Service the independent controller loop with a 20 ms source-health poll and at
most 1 ms render read per turn. The existing synchronous HealthLink gains a bounded
poll wait argument in [1,100] ms, defaulting to its original 100 ms. No portable
deadline changes. Tick both guards before every received progress, renewal or
shutdown and on idle turns. Queued messages cannot clear an elapsed deadline.
Record the original pending challenge, completion count and last heartbeat age
when a deadline latches. Preserve that reason before disconnecting the renderer.

Route a render stall into RestartGate's render-stalled failure category; route
other failures to their existing corresponding category. Quarantine the failed
consumer, release both connections/demand, terminate only the held owned shell and
confirm its native exit. Preserve one/ two/ four-second retries and the existing
replacement ceiling. Current typed desktop policy must still permit replacement.
The original controller/source and collection demand survive; a new connection and
new render guard must import original full measured state and resume genuine paint
progress. No old challenge or completion can acknowledge the replacement lifetime.

## Fixed operational experiments

Retain private original source/delivery/bracket/pixel records and the public bounded
controller lifecycle log. Before a fault require two native completions backed by
the original operational draw/paint trace and the existing two-second live pixel
baseline. The observer may read diagnostic trace immediately outside capture
intervals, and invoke only the named fault. It must not drive replacement attachment,
paint progress or source values. Native Escape retains its explicit overview caveat.

| New control | Fault and required observation |
|---|---|
| render-stall | Freeze only drawing; health and collection continue, pixels freeze, an outstanding challenge expires, the controller kills/replaces the held shell and current original pixels/paint progress recover |
| hidden | Hide only the operational tile; background pixels prove absence, unrelated stage paints cannot acknowledge it; independent expiry and replacement restore the tile |
| false-progress | Freeze drawing and acknowledge challenges from the injected health path; native completions continue without replacement, while fixed external pixel acceptance fails |
| shell-freeze | SIGSTOP the held owned laboratory shell; the runnable controller detects render/health or earlier telemetry-lease expiry, kills that same stopped lifetime and replaces it; the observer never resumes it to manufacture recovery |
| render-revoke | Freeze drawing, then apply typed revision 8 at the resulting fault before retry; no replacement/delivery follows, while independently authorized collection continues |

For render-stall, hidden and render-revoke, require a pending challenge with no
timely completion and fault age in [3000,3200] ms, with an independently live old
shell, last heartbeat younger than 1200 ms and continued source acquisition. Record
the issue-to-fault interval, not merely time since injected drawing failure. Allow
up to one second from the injected fault to the next challenge, and require old
shell exit within 4500 ms of injection. Shell-freeze may reach an existing competing
data lease first; preserve its actual reason and deadline, without extending either
lease. In all replacing modes retain the original ten-second complete outage and
seven-second native readiness bounds, old-exit-before-replacement proof, one-second
first backoff, exact original measurements and two seconds of recovered pixels.

The false-progress observation lasts at least five seconds after injection, with
at least three native completions but frozen age for at least 1500 ms. It is an
expected failed candidate, not an observer error or a successful recovery. For
render-stall/shell-freeze preserve at least 1500 ms of actually frozen age before
termination; hidden preserves at least 1500 ms of absent operational pixels.
Use paired CLOCK_BOOTTIME and monotonic capture times to bind pixels to native
watchdog events; no suspend qualification is inferred.

Preserve every attempted source archive and failure. Independently recompute the
eight controls and mutate challenge identity, late progress, unhealthy-heartbeat,
old-lifetime reuse, missing exit, continued post-revocation delivery and frozen
recovery pixels. Run the prior native/standalone suites, native queued-deadline
experiment and existing GNOME live render-watch case against exact new artifacts.
This closes bounded render-failure recovery only. Native editor-exit recovery,
installed ownership/policy/demand, overview-free recovery, other profiles and full
desktop editions remain mandatory independent work.
