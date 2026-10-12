---
type: "SysPane Work Package Boundary"
title: "Windows polling listener admission and overlapped lifetime"
description: "Keep controller health responsive while a private named pipe waits for a peer or first byte."
tags: ["delivery", "transport"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T08:20:00+00:00"}
sp_id: "SP-W24-WINDOWS-POLL"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W24-PACKAGE", "SP-TRANSPORT", "SP-WORK-PACKAGES"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Windows polling listener admission and overlapped lifetime

Continue the native Windows controller prerequisites from d04818d0. The current
Windows listener has only blocking five-second accept; the existing controller
needs polling admission to service independent health. Extend the existing
Listener/Stream adapter, not a second pipe/identity stack or scheduler. This work
does not activate Windows product telemetry/UI or qualify historical systems.
Native controller/worker/guardian integration and all complete editions remain
required. The Linux controller's two source workers also need serialized access
to the shared measurement facility during the subsequent controller work.

## Admission and ownership

Expose Listener::accept_ready(expected_process) on Windows with the same optional
Stream result as Linux. One serialized listener owner performs a bounded poll:
empty while connection or its first byte is pending, one authenticated Stream on
success, or the existing distinct safe IpcError. No polling call waits for future
connection/read completion. Native authentication calls themselves are not
preemptible; an independent guardian remains required for an unresponsive process.

Keep exactly one persistent pending OVERLAPPED request/event and stable first-byte
buffer inside the listener. Use overlapped ConnectNamedPipe and ReadFile, manual
reset events and zero-time readiness checks. Preserve ERROR_PIPE_CONNECTED as a
successful preconnected race, ERROR_IO_PENDING as queued work and completed error
outcomes. Reuse neither event/OVERLAPPED nor its buffer until completion is proved.
Cancellation alone is not completion. Listener destruction, admission timeout or
failure cancels the exact queued operation and proves terminal completion before
freeing storage. Retain the existing one-second cancellation-drain bound and
fail-stop behavior if completion cannot be established safely.

Idle polling may keep one connection request armed indefinitely. Once connection
completion is observed, one five-second first-byte deadline starts; polling does
not extend it. Retain that observed connection time in the admitted Stream and
return the consumed first byte exactly once with its completion observation time.
Use the existing logon-SID-only protected ACL, first-instance ownership, local-only
pipe, peer token/session/logon comparison, exact expected PID and held peer handle.
No role or collection grant comes from the byte or PID. Do not print raw principal
keys. Only successful admission marks the shared slot busy. While its Stream is
live, another admission reports endpoint.busy. Rejection or Stream destruction
disconnects that instance and permits a fresh attempt on the same owned listener.
Destroying a listener with an admitted Stream must not invalidate the Stream's
independently retained slot. No unowned endpoint or process is cleaned up.

Keep blocking accept(expected_process) as the compatibility wrapper over this
same state machine. Its original overall five-second bound starts at that call
and is not extended by a connection or trickled byte. Linux acceptance remains
unchanged; modern Windows qualification does not add APIs to the historical build.

## Fixed native checks

Use the existing IPC probe and private development endpoints. A polling probe
reports each actual call's start/end ticks and emits an independent control-loop
tick every 100 ms. In this named development lab normal polling calls must finish
within 100 ms and control ticks must have no gap above 250 ms while waiting. These
are measured local prerequisite gates, not low-end/GUI or universal kernel bounds.
Record every raw call duration; never clip, omit a slow call or relax a gate to pass.
Cancellation/destruction is separately bounded by 1250 ms here, including the
existing 1000-ms drain, and does not become a normal polling timing claim.

Cover idle/no peer, connected peer withholding its first byte, delayed first-byte
admission with byte/time preservation, wrong-PID rejection followed by a correct
peer, busy admitted slot, first-byte deadline with retry, destruction during pending
connect and destruction during pending first-byte read. Closing a pending listener
must release its server endpoint; close the client's old kernel handle before
claiming a new first-instance listener can own the name. Retain a
real client through independent verification and prove actual probe exit. The
Python oracle owns only its exact launched probes and private pipes, checks native
returned peer PID and every timing sample, and rejects a removed timing sample or
false byte/PID/timing result. Do not infer cross-user/logon authorization from the
same-user lab. Existing NATIVE-01/NATIVE-02 and native-clock checks must still pass
on Windows; run Linux transport/clock regressions for the shared API/probe change.

Build ordinary Windows/Linux profiles with the fixed component graph and current
workspace preflights. Record source/archive/artifact/environment identities and
preserve failures. Keep the historical build/import controls unchanged. Update
handoff/routing/README/TODO/commands after verification. Shared tools remain in
source/build; raw/machine/generated outputs stay ignored under owned out/ roots
and the retired root remains absent.

Primary references: [ConnectNamedPipe](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe),
[overlapped pipe I/O](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-server-using-overlapped-i-o),
and [CancelIoEx lifetime](https://learn.microsoft.com/en-us/windows/win32/fileio/cancelioex-func).
