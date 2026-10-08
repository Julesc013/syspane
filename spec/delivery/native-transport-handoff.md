---
type: "SysPane Work Record"
title: "Native local IPC implementation handoff"
description: "Bind W-24's Windows and Linux adapter gate to real process and stream evidence."
tags: ["delivery"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:04:36+11:00"}
sp_id: "SP-NATIVE-TRANSPORT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-CAMPAIGN-ADMISSION", "SP-W24-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native local IPC implementation handoff

W-24's initial Windows/Linux development adapter gate is implemented. The full
foundation/native-experiment campaign remains active. Source base:
`47cc01fdbbb02dcd5a9726dde1fd63ae068a4d1c`; the containing commit and recorded input
digests identify this integration. The earlier [portable checkpoint](transport-handoff.md)
and its evidence remain historical. This is not a desktop/product qualification.

## Implementation and executed evidence

`source/platform/local_ipc.hpp` exposes move-only native streams/listeners and
monotonic read observations. Windows uses a private local named pipe, protected
logon-SID DACL, first-instance ownership, remote-client rejection, identification
SQOS and user/session/logon/process checks. Linux uses a private directory and
pathname socket, kernel peer credentials and a held peer pidfd around the POSIX
session check. Both ends authenticate before the protocol session admits messages.
No client document grants roles or machine policy.

`SysPane.IpcProbe` composes those adapters with the existing frame decoder,
connection state machine, ledger and policy checks. It checks that its own process
is unelevated/non-root with no effective Linux capabilities before opening an
endpoint. It runs at most one live connection and two sequential clients. Real
stream deadlines, cancellation cleanup and endpoint cleanup are exercised by a
separate Python process harness with fixed expected results.

Both development profiles passed 37 CTest entries: 35 model/portable checks and
two native families. NATIVE-01 contains nine concrete cases on each OS; NATIVE-02
contains six on Windows and seven on Linux. Cases cover actual fragmented/coalesced
exchanges, preview/replay, reconnect/result retrieval, a client that closes before
reading a command result, truncated/invalid/oversize frames, hello/frame/write
deadlines, endpoint collision, expected-process denial on both peers, role spoofing,
forged authority and old epochs. Linux also executes a same-UID client in a distinct
POSIX session and observes denial on both sides. That is not a desktop-session test.

The lost-acknowledgement case preserves one preview request reservation and returns
that result on reconnect. It changes no stored configuration. W-08's durable
generation/journal crash trace remains pending; this case does not substitute for it.

Current records are `out/evidence/w-24-native-<profile>.json`, matching
normalized CTest logs and `NATIVE-01`/`NATIVE-02` JSON transcripts. They bind case
commands, source/dependency/profile inputs, probe/library hashes and actual process
outcomes. The recorder requires every named child case and refuses missing/failing
evidence. No third-party native laboratory result is inherited from API documentation.

## Preserved failure and qualification limits

The first Windows adapter compilation failed because MinGW's C++ headers already
define NOMINMAX. The source now guards that macro; warnings remain errors. The
original diagnostic and source digest are preserved in
`out/evidence/w-24-native-attempts.json`. No acceptance oracle was relaxed.

Cross-user execution and a second Windows logon/terminal session are unavailable
in the admitted laboratory and remain blocked qualification. DACL inspection and
an expected-PID mismatch are recorded separately; neither is labelled a real
cross-user/logon denial. Linux's native run uses unprivileged UID 1000 in WSL2;
SO_PEERPIDFD and procfs are required by this development adapter. Its POSIX-session
rule is a launched-process boundary, not a portable desktop-login identity policy.
XP/7 and Mac qualification remain pending/blocked under the existing lab record.

No telemetry subscription, durable command, native settings/editor, independent
recovery service, desktop host or release package is enabled by this gate. Probe
deadlines prove the observed operations in these runs, not hard-real-time OS
scheduling or recovery from a kernel hang. A Windows cancellation that cannot drain
terminates this probe rather than freeing buffers still owned by the kernel; W-25
must supply independently observed restart/recovery behaviour.

## Resume the campaign

W-02 can build its independent desktop oracle from W-01. W-25 can now use W-24's
authenticated local stream and bounded state to close producer leases, diagnostic
independence and crash/hang recovery. Extend role/feature contracts before enabling
new recovery or surface messages. Native host experiments depend on W-02/W-24 and
must retain the behind-icons/desktop-reveal acceptance criterion; ordinary windows
and WSLg alone are insufficient. Missing historical/Mac laboratories must not stop
independent contemporary Windows implementation or deterministic recovery work.
