---
type: "SysPane Handoff"
title: "Windows polling listener and overlapped lifetime checkpoint"
description: "Responsive same-adapter admission, complete native timings and proved cancellation before storage release."
tags: ["delivery", "transport"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-12T08:48:38.241697+00:00"}
sp_id: "SP-WINDOWS-POLL-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W24-WINDOWS-POLL"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Windows polling listener and overlapped lifetime checkpoint

The Windows polling listener checkpoint supplies the
existing adapter's accept_ready prerequisite for a responsive native controller.
One stable overlapped operation/event/first-byte buffer survives polling, and exact
cancellation plus terminal completion precedes reuse/free. Ten native cases pass,
including delayed/preconnected admission, PID denial/retry, timeout, pending close,
name reuse and retained-stream lifetime. Maximum recorded poll duration is 1 ms;
maximum control-tick gap is 168 ms under fixed 100/250-ms gates. Forty-one controls
pass on each profile, original transport/clock/measurement/subscription families
pass on Windows/Linux, and both historical audits pass. Preserve the first fixture
rearm-race failure and recorder syntax failure. The compiled adapter/probe remain
identical between failed and passing native attempts. Next serialize shared native
measurement access, then reuse the controller/demand/policy owners for Windows
workers under an independent guardian and native UI/desktop integration. All five
complete editions and prior mixed GTK/native qualification failures remain open.
Tools stay in source/build; raw/machine/generated data stay ignored under out/,
and the retired root remains absent.

The [package](packages/w-24-windows-poll.md) closes this native prerequisite.
The [checkpoint](checkpoints/windows-poll.json) binds nine executions to verified
complete source archives, log/preflight hashes, native records, profile artifacts
and component graphs. The existing protected logon-SID ACL, first-instance and
local-only pipe rules, native user/session/token checks, exact expected PID and
held process handles remain the admission authority. No first byte supplies a
role, privilege or collection grant; raw principal keys are not logged.

Windows accept_ready keeps one pending ConnectNamedPipe or first-byte ReadFile
request in listener-owned storage. Polling uses zero-time event checks and reports
empty while work is pending. Preconnected races remain successful connections.
Observed connection completion starts a fixed five-second first-byte deadline.
The consumed byte and its original observation time are returned exactly once.
Blocking accept uses the same state machine with its original overall five-second
bound. An admitted stream owns the shared slot independently; another admission
is busy, and listener destruction cannot invalidate the stream. Rejection and
stream destruction permit another connection. Old client kernel handles close
before the fixture claims first-instance name reuse.

Cancellation targets the exact overlapped request. The existing one-second drain
now checks terminal GetOverlappedResult as well as its signaled event before any
buffer/event/operation can be reused or freed. Missing completion retains the
existing bounded fail-stop behavior. Native identity/system calls cannot claim
preemptibility, so the real controller still requires independent process recovery.
See [Microsoft's cancellation lifetime contract](https://learn.microsoft.com/en-us/windows/win32/fileio/cancelioex-func).

| Execution | Coverage | Result |
| --- | --- | --- |
| Windows x64 GCC 15 | 41 protocol/model/graph controls | pass |
| Linux x64 GCC 13 | same 41 controls | pass |
| Windows x86 v141_xp on current host | same 41 portable controls | pass |
| Windows polling native fixture | 10 actual admission/lifetime/timing cases | pass |
| Existing Windows native families | NATIVE-01, NATIVE-02, NATIVE-CLOCK, NATIVE-MEASURED, NATIVE-SUB | pass |
| Existing Linux native families | same five families | pass |
| Historical pinned-input/PE/import audits | both existing strict cases | pass |

The polling cases include idle, delayed first byte, preconnection, wrong-PID
rejection/retry, first-byte timeout/retry, close during pending connect and read,
two name-reuse checks and a retained stream after listener destruction. The latter
exchanges an actual byte and acknowledgement after releasing the listener. Every
poll call has an ordinal and raw start/end times; every control tick is retained.
The independent oracle checks completeness, fixed duration/deadline gates, peer
PID and exact byte/timestamp behavior. It rejects missing samples, a false slow
call, a false byte and a false PID. Recorded timings use millisecond samples and
do not claim submillisecond accuracy, universal bounds or low-end/GUI qualification.
The named host's maximum recorded poll duration is 1 ms and maximum tick gap
168 ms; all pending destruction samples record 0 ms at that representation.

The first independent client retries immediately after timeout and encounters
native ERROR_PIPE_BUSY before the listener rearms. The failure record preserves
the five started cases and actual process exit. The client now waits only for
that busy condition using WaitNamedPipe and one fixed five-second deadline.
The compiled adapter/probe bytes, admission checks and timing/deadline oracles
remain unchanged. A private evidence-recorder parenthesis error is also preserved
before its correction; it never ran a product test or changed an acceptance oracle.

W-24's initial development transport gate remains implemented with this refinement;
cross-user/logon labs and historical/native target qualification stay unexecuted.
The Windows controller must still reuse the existing session/demand/policy owners,
attach independent worker/guardian supervision and integrate real native UI/desktop
behavior. Source inspection also identifies the existing Linux controller's two
source workers calling one serialized measurement facility without a shared guard.
Close that ownership before the Windows port; no concurrency qualification is
claimed by these transport passes. Preserve all prior native failures, especially
the unresolved mixed GTK accumulation loss. All five complete 0.1.0 editions remain
required, with remaining providers, package/lifecycle and target evidence open.

Shared tools remain under source/build. Compact resumption records are versioned;
raw timings, pipe/process records and machine settings stay in owned ignored output
roots. The retired root stays absent, and AIDE remains optional/inactive.

All 51 schemas and 183 fixtures validate. Specification tooling passes 60 of 62
tests with two existing Windows symlink privilege skips. Integrity and generated
references are checked after recording the final handoff.
