---
type: "SysPane Implementation Handoff"
title: "Asynchronous GNOME clock and visible age checkpoint"
description: "Native authenticated clock ownership, independently observed public age and expiry, and bounded startup/exit cleanup."
tags: ["delivery", "desktop", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T07:35:00Z"}
sp_id: "SP-GNOME-CLOCK-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W25-GNOME-CLOCK", "SP-CAMPAIGN-ADMISSION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Asynchronous GNOME clock and visible age checkpoint

From `ccc5da5bb3b8fb7b06bc504dade28ba3fd0f4314`, the owned GNOME experiment
attaches the qualified native clock asynchronously and displays the age of one
public native BOOTTIME sample. This closes the shell attachment, visible age/expiry
and teardown prerequisite. Operational network values still have unknown age;
the public clock fixture does not qualify their freshness or change their status.

The [package](packages/w-25-gnome-clock.md) fixes the six modes, admission,
deadlines, immutable timestamp and external pixel oracle. The existing native
adapter requires a same-session peer. The independently launched retained-network
relay does not satisfy that condition. This experiment therefore gives the shell
one finite Gio.Subprocess child in its own POSIX session; no native peer check is
weakened. The child supplies public time only, not operational network data.

Readiness, connection, write and read use cancellable asynchronous GIO operations
under a 1.5-second startup deadline. The native adapter authenticates the retained
child PID, UID and session. Exact decimal strings and BigInt preserve nanoseconds.
Native local samples bracket the peer's original timestamp; a 50 ms timer then
updates visible integer age independently of diagnostic calls. The sample never
changes. Fresh becomes Stale at the fixture's three-second TTL; native presentation
must settle within 200 ms, while exact-boundary model semantics remain unchanged.

| Native case | Independently verified outcome |
|---|---|
| `live` | 69 public captures, advancing native age and observed expiry |
| `freeze-age` | Age acceptance fails; expiry acceptance passes |
| `ignore-expiry` | Expiry acceptance fails; age acceptance passes |
| `peer-exit` | Held child exit, tile disappearance within 200 ms and no return |
| `pending-disable` | Disable during delayed readiness; no accepted sample or late tile |
| `wrong-peer` | `peer.process` rejection, no accepted sample and no tile |

All six final attempts use identical source inputs. Every child exits normally;
the owner closes native clock/socket resources, releases subprocess and actor
references, and rejects restart after closure. The observer holds native process
identity, independently checks the public peer journal, and requires the original
marker and icon composition after teardown. The fixed age/expiry oracle includes
capture timing and coverage limits; self-reported update counters cannot satisfy it.

## Evidence and preserved failures

Evidence uses `build-support/evidence/w-25-gnome-clock-`; the machine handoff is
`build-support/evidence/gnome-clock-handoff.json`. Public reports, clock/pixel
journals, commands, preflights, source archives and artifact hashes identify each
attempt. Source archives are deduplicated by their exact archive digest. Operational
network documents, receipts and pixel crops remain in owned ignored directories;
committed evidence records their identities without copying their contents.

Six clock modes and four retained-cache modes passed verification of their expected
outcomes. **148 evidence checks passed:** 16 clock, 25 cache, 22 default reveal,
47 optional focus and 38 surface lease. The reveal, focus and lease native cases
were rerun with the same final source set. Default Show Desktop focus restoration
still fails; the optional integration stays disabled by default. Negative age,
expiry, cache and reveal candidate outcomes remain failures in the original records.

Three corrections retain their original evidence:

- The first startup used a nonexistent `GioUnix.SocketAddress` constructor. The
  installed API is `Gio.UnixSocketAddress`; its failed startup and cleanup remain.
- A later live attempt passed its pixel checks but recorded child exit `-15`.
  Independent validation rejected that attempt. Signalling before socket close
  resolves the EOF/termination race; the observer also now requires normal exit.
  The original outer `pass` field remains intact and is not final qualification.
- The first six-case verifier incorrectly required the native shared library to
  be mapped after pending-startup disable. GI loads it lazily on first class access.
  The corrected check requires it in the other five modes and verifies its identity
  if present in this cancelled mode; every mode still requires the exact typelib.

The final matrix was repeated after explicit actor/subprocess disposal and verifier
corrections. Existing C++ code, build targets and profiles did not change. The
previous 108 Linux, 102 Windows and 94 historical-toolset host checks and three
relocated smoke packages retain their earlier evidence identities. This checkpoint
refreshes the retained relay's collector binding to the qualified GJS-clock build
record and verifies the four native cache cases against it; older records remain.

## Next admitted boundary

Connect actual measured network input through the qualified asynchronous owner and
clock path, keeping original measurement timestamps and the shared model's complete
freshness/status semantics. Continue independent native cache lease faults, product
controller demand/current policy, general bounded delivery and render supervision.
Native suspend/time-namespace changes, installed protected policy, full editor and
complete desktop lifecycle remain separate qualification work.

Audit coverage of the initial campaign before further GNOME expansion: contemporary
Windows host investigation remains unexecuted, historical guest scope is unresolved,
and no macOS laboratory is available. These tracks must continue independently.
W-25 and the campaign remain incomplete. No complete desktop host, installer or
public release is qualified by this public clock experiment.
