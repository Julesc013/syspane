---
type: "SysPane Work Package Boundary"
title: "W-25 measured network pixels in the owned GNOME shell"
description: "Connect the tested native session to independently observed values, age, freshness and lease state."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T09:00:00Z"}
sp_id: "SP-W25-GNOME-LIVE-NETWORK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-LIVE-NETWORK-SESSION", "SP-W25-GNOME-CLOCK"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 measured network pixels in the owned GNOME shell

Reuse `networkSession.js` unchanged as the asynchronous native owner. The owned
GNOME extension launches the real collector through that owner, in its own POSIX
session. The tested native NetworkView owns measurement age, freshness, lease and
policy. JavaScript formats the supplied age as integer milliseconds and draws the
four supplied counter/rate strings; it cannot renew a sample or infer freshness
from producer health. The ordinary retained-cache and public-clock tests keep
their separate meanings and acceptance rules.

The fixed selection is `network:interface:1`, policy revision 7, telemetry 0.2 and
the four fields already admitted by the live-session package. Two original native
samples precede a deliberate acquisition pause while the watch remains registered.
The independent observer verifies original counters against native reads and rates
against original counter/time pairs. No generated value substitutes for collection.

## Lifetime, stimuli and limits

The private-bus test interface `org.syspane.NetworkLive` exposes Calibrate, Start,
GetState, Revoke, Stop and Cleanup. It exists only in the owned laboratory. The tile
is initially hidden; Calibrate follows the composition prerequisite and displays
public glyphs. Start is single-use. GetState reports lifecycle facts only, never
operational values, and cannot drive rendering. Start after closure returns closed.

Use the existing 50 ms native projection callback and existing session limits,
including bounded asynchronous IO, two-second startup, eighteen-second owner
lifetime and one-second bounded termination fallback. There are no synchronous
process waits in shell callbacks. Four rows hold at most 32 glyphs each; age holds
at most 16. The tile is 448 by 210 pixels at (300,310), below the independent marker.
Its age indicator is green when current and amber when stale. A separate blue
indicator means active data lease; red means retained/expired. New snapshots do not
renew the lease: only accepted increasing heartbeats do.

Revoke applies native revision 8 denial and clears actors and all retained glyph
strings synchronously before acknowledging. Stop initiates the same erasure and
asynchronous shutdown; it does not claim native exit. The observer holds pidfds for
both native descendants and checks their actual exits. Native peer loss or health
expiry also clears the tile. Late callbacks cannot recreate it. Cleanup always
erases actors, including an intentionally faulty negative control, before any
subsequent public desktop capture. Extension disable closes and unexports the owner.

The short endpoint directory is owned 0700 beneath the admitted IPC root, with
owned h/d/v subdirectories. Remove only known socket leaves after confirmed exit
of the owned process group; unexpected entries fail cleanup. Original producer
JSON and operational crops remain private, bounded to 4 MiB and 16 MiB respectively,
mode 0600 inside the attempt's 0700 directory. Public reports retain hashes and
sizes, public lifecycle facts and outcomes. They never contain operational pixels.

## Fixed independent acceptance

Run `native_gnome_bootstrap.py BUILD --network-live MODE` with the existing pinned
GNOME lab and tested live-session native artifact record. Modes are live,
freeze-age, ignore-expiry, wrong-value, ignore-clear, lease-loss, revoke, peer-exit
and hang. The latter two native modes are existing producer experiments; remaining
modes use hold. Run the ordinary workspace preflight before every native attempt.

Calibrate all digits, decimal point and missing marker from native pixels. After
the second original publication and 200 ms settling, capture the four values, age
and both indicators every 50 ms. Captures take at most 50 ms and gaps at most
150 ms. Require exact independently derived values. Age must lie between native
capture-begin age minus 200 ms and capture-end age, remain monotonic and advance
at least 3,000 ms across at least 55 samples. No diagnostic queries occur during
this interval. Require three current witnesses before sample+3 s and three stale
witnesses after sample+3.2 s. Normal data leases remain active through stale data.
Lease-loss must retain values and show independent data expiry while its producer
and network watch remain alive. Accepted heartbeat times in the original journal
bound the expiry transition; journal forwarding and presentation may lag by 200 ms.

For peer-exit and hang use a shorter 2.2 s interval, at least 30 samples, at least
1,500 ms advancing age and three current witnesses, before observing closure.
Peer-exit sends SIGKILL only through the held supervisor pidfd. Hang relies on the
existing health supervisor and requires its forced-worker-exit evidence. After
revocation, stop or observed native exit require blank pixels within 200 ms and
continued erasure for 450 ms with at least three settled witnesses. Confirm native
child exits, cleared owner resources, unchanged icon manager and live marker after
cleanup. No private pixel may enter that final public marker trace.

Frozen age must fail age acceptance; ignored expiry must fail freshness; wrong
counter must fail value acceptance; ignored clearing must fail erasure. Preserve
their failed candidate outcomes. An evidence verifier recomputes these results
from original private captures and source journals, checking artifact/source
identities. Oracle corrections are contract changes, with the first failure kept.

This closes one operational shell experiment, not a complete renderer or desktop
edition. Suspend, namespace changes, protected policy, full selection/configuration,
independent render supervision and recovery remain separate gates. No active user
desktop, privileged operation, public release or compatibility claim is admitted.
