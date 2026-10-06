---
type: "SysPane Work Package Boundary"
title: "W-25 asynchronous native shell clock and visible age"
description: "Qualify same-session clock ownership, native age progression and bounded teardown in the owned GNOME shell."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:10:00Z"}
sp_id: "SP-W25-GNOME-CLOCK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-GJS-CLOCK", "SP-W25-NATIVE-NETWORK-CACHE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 asynchronous native shell clock and visible age

The existing lab starts the network relay and GNOME in distinct POSIX sessions.
The native clock must reject that topology. Keep its peer/session checks unchanged:
this experiment gives GNOME one owned, finite Python clock peer through
Gio.Subprocess, inheriting the shell's session. The next operational integration
must use an equivalently authenticated clock path; ordinary D-Bus PID lookup or
matching textual clock IDs remain insufficient.

This closes the native asynchronous/visible-clock prerequisite. Its sample is a
public native BOOTTIME reading, not operational telemetry. The retained network
cache remains unchanged. No current network value becomes fresh merely because
this public clock experiment passes.

## States, ownership and limits

`--clock-age live|freeze-age|ignore-expiry|peer-exit|pending-disable|wrong-peer`
selects the experiment after the existing live composition prerequisite. The test
interface `org.syspane.ClockExperiment` is admitted only on the private laboratory
bus, with Start, GetState, StopPeer and Disable. These methods are public synthetic
test stimuli, not product command authority. Start is single-use; disable is final.

The serialized shell owner transitions from calibration to starting, ready and
closed/failed. It retains the exact Gio.Subprocess and native clock object. A short
0700 endpoint directory beneath the already admitted IPC root is owned by this
attempt. The child binds one 0600 Unix stream, reports readiness, accepts one
connection and responds once to `sample\n` with canonical uint64 decimal BOOTTIME
nanoseconds plus newline. Reject frames above 64 bytes, malformed values and EOF.
The trusted helper writes at most 64 KiB of public clock/process evidence and exits
within 20 seconds. It observes parent death and removes only its owned socket.

Readiness, connect, write and read use asynchronous GIO calls with one cancellable
and a 1.5-second total startup deadline. There is no synchronous wait in a shell
callback. Native socket adoption authenticates the retained child PID, UID and
POSIX session. A native local sample before the request and after the reply must
bracket the peer's timestamp. Keep all values as canonical strings/BigInt, never
floating-point nanoseconds. No arbitrary peer, retry or producer substitution.

After acceptance a 50 ms timer samples the native clock independently of diagnostic
queries. Display integer age in milliseconds, floor((now - original sample)/1e6),
plus Fresh below 3,000,000,000 ns and Stale at or above that boundary. The original
sample never changes. These are this clock fixture's observable rules; the existing
model still owns operational field freshness and its richer status axes.

Native sampling failure or peer exit closes the clock and removes the age tile.
Disable cancels pending work, closes the clock and GIO connection, removes timer
and actors, and requests child termination. A retained wait callback records actual
exit; after one second a still-live owned child may be force-stopped. Late callbacks
must finish/release their GIO result without publishing a sample or recreating actors.
GetState must not advance time or drive rendering. No callback can reopen a closed
experiment. Extension teardown also disables the owner.

## Fixed native acceptance

The independent observer captures public glyph calibration `1234567890` before
Start. It must obtain ten distinct nonempty 14x26 pixel templates. It then observes
actual age digits and the fixed Fresh/Stale indicator every 50 ms for 3.6 seconds.
Each capture must take at most 50 ms; inter-capture gaps stay below 150 ms. The
displayed integer must lie between the native capture BOOTTIME age minus 200 ms and
the capture-end age, with no negative age. Require fresh and stale witnesses and
monotonic progression by at least 3,000 ms. After sample+3.2 s all settled captures
must be stale. Portable exact-boundary semantics remain unchanged; native pixels
have a 200 ms presentation deadline, not an exact scheduling guarantee.

The observer independently reads the helper's public sample journal, verifies native
parent/session identity, holds its pidfd, and checks the shell's causal bracket.
The fixture cannot supply its own expected digit image. A frozen-age control fails
age acceptance; an ignored-expiry control fails status acceptance while age still
passes. Preserve both failed candidate outcomes.

For peer-exit, StopPeer follows a visible advancing age. Prove actual native exit,
then disappearance within 200 ms and no return. For pending-disable, disable while
the helper deliberately delays readiness; prove native exit, no accepted sample and
no late tile for 800 ms. Wrong-peer deliberately supplies the wrong expected PID:
require `peer.process`, no accepted timestamp and no age tile. Every case ends with
explicit disable, independent child exit, original marker progression and preserved
icon composition. No remaining owned process is an acceptable cleanup result.

## Evidence and continuation

Use the existing pinned GNOME extraction and tested GJS native library/typelib.
Bind their current artifact and source identities; use completed Windows workspace
preflights. Keep exact native reports, source archives, public clock/capture journals,
negative controls and failures. Recheck affected default/optional focus, marker and
retained-cache behavior with their unchanged acceptance criteria. Updating the
retained relay's collector record must preserve the previous evidence separately.

Next connect actual measured network input through this ownership/clock topology,
preserving original sample timestamps and full model freshness/status semantics,
policy revocation, source leases and independent render supervision. Suspend/resume,
namespace migration/denial, general producer admission and a complete desktop edition
remain separate qualification gates. No privileged action or public release follows.

Primary lifecycle references: [asynchronous socket connect](https://docs.gtk.org/gio/method.SocketClient.connect_async.html)
and [Gio.Subprocess ownership and asynchronous waits](https://docs.gtk.org/gio/class.Subprocess.html).
