---
type: "SysPane Work Package Boundary"
title: "W-25 native GJS measurement-clock boundary"
description: "Expose the existing authenticated Linux clock through a bounded native object before enabling renderer freshness."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:00:00+11:00"}
sp_id: "SP-W25-GJS-CLOCK"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-MEASUREMENT-CLOCK", "SP-W25-NATIVE-NETWORK-CACHE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 native GJS measurement-clock boundary

This bounded prerequisite asks whether the pinned GJS runtime can consume the
existing Linux measurement clock without numeric rounding, weaker peer identity or
unbounded native resource lifetime. It does not enable live network presentation.
The existing native cache continues to display retained values with unknown age.

## Interface and ownership

Build a Linux-only `SysPaneClock-0.1` introspection module, backed by the existing
`Stream::measurement_clock()`. `Clock.new_from_socket(fd, expected_pid)` borrows a
connected nonblocking AF_UNIX stream descriptor and a positive expected process ID.
The caller establishes the connection asynchronously when running inside a shell.
Construction duplicates the descriptor with close-on-exec, changes no caller flags,
and applies the existing SO_PEERCRED/SO_PEERPIDFD, same-user and same-POSIX-session
checks. A numeric PID alone, D-Bus message or forwarded timestamp cannot establish
clock provenance. Connection/path authorization remains the caller's responsibility;
this is not a new public product transport or a grant to an arbitrary local client.

Reject a bad descriptor, wrong socket family/type, unconnected socket, blocking
descriptor, privileged context, zero expected PID or wrong peer. Construction
failure leaves the borrowed descriptor open and retains no native resources.
The object owns its duplicate, held peer handle and optional retained time namespace.
Serialized owner-thread calls only; concurrent callers are outside this interface.

`sample()` returns a freshly allocated canonical decimal UTF-8 string containing the
exact uint64 nanosecond count. No count crosses GI as a floating-point number.
The domain is fixed to `linux.boottime`, representation unit 1 ns, and every sample
uses the unchanged held-peer, namespace, range, monotonicity and fault-latch checks.
The string is a local reading, not serialized proof of another producer's clock.
The adapter must not create a new independent implementation of those checks.

`close()` releases all owned resources immediately and is idempotent. Finalization
also releases them. Sampling a closed or directly default-constructed object fails
`clock.closed`; sampling after native peer exit first fails `clock.peer_exited`,
then `clock.unavailable`. Native errors become GError exceptions with their stable
codes; C++ exceptions must not cross the C ABI. No callbacks, background threads,
waits, clock changes, policy changes or retained telemetry are introduced.

## Fixed acceptance

Run the module in standalone GJS using the existing extracted GNOME laboratory;
do not load it into the desktop bridge yet. A separate Python observer owns a
private endpoint and a finite child server, holds process descriptors, and asserts:

| Case | Required result |
| --- | --- |
| `GJS-CLOCK.ROUNDTRIP` | Python BOOTTIME before request <= GJS native sample <= Python BOOTTIME after response; exact canonical uint64 text, repeated nondecreasing samples; original GIO connection may close without invalidating the owned duplicate |
| `GJS-CLOCK.REJECT` | Invalid FD, wrong expected PID, zero PID, blocking descriptor, unconnected and non-stream/non-Unix descriptors are rejected; valid borrowed descriptors remain usable and open |
| `GJS-CLOCK.CLOSE` | Explicit close twice and default construction yield `clock.closed`; 64 create/sample/close cycles restore the baseline native descriptor set |
| `GJS-CLOCK.PEER-EXIT` | After independently confirmed server exit, first sample rejects `clock.peer_exited`, next rejects `clock.unavailable`; no value escapes; close restores baseline resources |

The test supplies fixed expectations before execution. Native syscall injection,
real namespace migration/denial, suspend/resume and uint64 overflow remain separate
unexecuted qualifications. Native counts need not exceed JavaScript's safe integer
range in this lab; the C ABI and GIR expose strings on every path regardless.
Any future age consumer must separately prove exact parsing and TTL boundary behavior.

## Build, evidence and authority

Use ordinary Linux CMake configure/build and the `native.GJS-CLOCK` CTest entry,
with a completed Windows workspace preflight before each action. The module is a
development target with no installed product payload. Pin the GI compiler and
GObject dependencies; reuse the existing extracted GJS package identity. A missing
laboratory fails this explicit test rather than silently passing or installing tools.
Preserve exact commands, source inputs, library/typelib/GJS identities, raw synthetic
observations and every failure. Run existing native clock/IPC and component checks
after changing shared socket adoption, then the affected full profile suites.

Routine implementation and tests are admitted. Shell integration, live freshness,
support claims, privilege and releases do not follow from this prerequisite.
The next boundary is an asynchronous authenticated shell connection and independently
observed age progression/expiry with real measured telemetry and current policy.

The installed private D-Bus investigation returned ProcessID, UnixUserID,
UnixGroupIDs and LinuxSecurityLabel, but no ProcessFD. This selects authenticated
Unix sockets for this experiment; it does not infer a missing feature on all buses.
The [D-Bus specification](https://dbus.freedesktop.org/doc/dbus-specification.html)
defines optional credentials and held ProcessFD identity. The
[GObject model](https://gnome.pages.gitlab.gnome.org/gtk/gobject/concepts.html)
provides native object finalization; explicit close remains required at teardown.
