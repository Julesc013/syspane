---
type: "SysPane Implementation Handoff"
title: "Standalone native GJS measurement-clock checkpoint"
description: "Exact native clock strings, authenticated peer lifetime and deterministic resource cleanup before live desktop freshness."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:54:41.725669+00:00"}
sp_id: "SP-GJS-CLOCK-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GJS-CLOCK"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Standalone native GJS measurement-clock checkpoint

The Linux development profile now builds `libsyspane_gjs_clock.so` and
`SysPaneClock-0.1.typelib`. A standalone GJS process uses the same native
measurement-clock implementation as the authenticated C++ transport. This closes
one prerequisite to live freshness; the desktop bridge still presents retained
network samples with unknown age.

The [package](packages/w-25-gjs-clock.md) fixes socket admission, ownership, exact
representation and errors. Construction duplicates a connected nonblocking Unix
stream, verifies the native peer with SO_PEERCRED/SO_PEERPIDFD, and requires the
expected process, effective user and POSIX session. Each sample preserves the
existing time-namespace, held-peer and fault-latch checks. Values cross GI as decimal
strings, never JavaScript numbers. Explicit close releases all native resources;
object finalization also owns cleanup. No new privileged operation or dependency
installation was needed.

## Executed results

The independent Python observer checks sixteen BOOTTIME causal brackets around
actual GJS calls, rejected invalid/socket/PID inputs, unchanged borrowed descriptor
flags, sixty-four create/sample/close cycles without descriptor leaks, and sampling
after independently confirmed peer exit. The first post-exit call reports
`clock.peer_exited`; the second reports `clock.unavailable`. Explicit close is
idempotent and removes the held clock resources. Both native children exit normally.

Complete CTest suites pass: **108 Linux, 102 Windows and 94 historical-toolset host
checks**. The shared socket-adoption implementation is Linux-only. The historical
suite remains Windows 10/WOW64 execution, not XP/7 guest qualification. The local
model smoke archives pass relocated execution on all three profiles; they do not
include or qualify a complete desktop product.

Evidence records use `out/evidence/w-25-gjs-clock-`; the machine handoff
is `out/evidence/gjs-clock-handoff.json`. They bind original commands,
source archives, native reports, library/typelib identities, complete CTest logs and
smoke artifacts. Synthetic clock observations contain no network payload or desktop
capture. Prior native desktop evidence retains its original source/artifact identity.

Three failed attempts remain preserved: a quoted typelib output argument caused
build failure; the initial observer passed a string where the existing ownership
helper required a Path; and the first GJS launch omitted its private typelib search
path. These were build/harness corrections. The fixed clock and peer-exit acceptance
conditions did not change. A later evidence-validation attempt rejected a GJS
deprecation warning from the old Gio Unix-input-stream alias. The client now uses
GioUnix.InputStream; the final Linux suite was rerun and both original warning
transcripts remain preserved.

## Remaining work and next entry

Connect the adapter asynchronously inside the owned shell experiment, bind the
connection to the admitted producer and current policy, and independently observe
age progression, TTL equality and expiry for real measured samples. Reuse exact
integer parsing and the shared measured-data semantics; a local clock reading alone
is not proof of forwarded remote timestamps. Native suspend/resume, real namespace
change/denial, counter overflow/regression and shell-thread latency remain unexecuted.
Garbage-collection timing was not qualified; shell teardown must explicitly close.

The retained-cache laboratory pins its previously tested collector record. This
checkpoint rebuilds the collector through shared transport changes. Before running
that laboratory against the new binary, explicitly bind its relay to the new full
suite evidence and preserve the old record; do not bypass the digest check or imply
that earlier desktop captures used this binary. Continue native cache lease faults,
product controller policy/demand, general delivery queues and renderer supervision.

W-25 and the campaign remain incomplete. Other native platform tracks continue
independently. Default GNOME Show Desktop focus restoration remains failed; optional
focus integration remains disabled by default. No user desktop, guest VM, installed
service, privileged operation, release publication or AIDE activation is involved.
