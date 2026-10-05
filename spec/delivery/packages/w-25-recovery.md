---
type: "SysPane Work Package"
title: "W-25 independent recovery and producer leases"
description: "Close bounded recovery state before connecting native processes and diagnostic entry."
tags: ["delivery", "architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T01:27:59+11:00"}
sp_id: "SP-W25-PACKAGE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-WORK-PACKAGES", "SP-RECOVERY", "SP-TRANSPORT", "SP-COMPOSITION"]
sp_review: "unreviewed"
sp_sources: ["SRC-READINESS-2026-10-05", "SRC-AUDIT-2026-10-04"]
---

# W-25 independent recovery and producer leases

Prerequisites are W-01 and the initial W-24 native adapter gate recorded in the
[native handoff](../native-transport-handoff.md). The existing user campaign grant
admits implementation. Own `source/diagnostics/`, recovery composition roots in
`source/application/`, required platform adapters and `tests/fault/`. Ordinary
reversible choices remain delegated; no privilege, shell termination, unrelated
process termination, capture of private desktop content or release is admitted.

## Scope and gates

W-25 must deliver independent producer expiry, rendering-progress supervision,
bounded isolated-child recovery and a diagnostic entry that starts without the
controller, optional content/history/providers, renderer or GPU. The diagnostic
composition retains mandatory policy and has a conservative native inspector.
Native keyboard/exit recovery must remain usable when the editor stalls.

The portable state boundary below is ready to implement using the existing
Windows/Linux development profiles and C++17. It is a required component of W-25,
not the complete implementation gate. Native process composition, diagnostic
startup, policy integration and independent visible recovery remain mandatory.
Close their message/launch/handle contracts before enabling them. In particular,
this component does not enable W-24's currently disabled snapshot/delta messages
or advertise a new role/feature based only on typed unit-test fixtures.

## Portable ownership and time

`syspane_recovery` has no JSON, model, GUI, provider or native handle dependency.
One owner serializes each object's calls on an independent health/event loop.
Guard objects are neither copied nor moved; their identity stays with that owner.
Milliseconds come from that owner's monotonic clock, never a producer timestamp.
Every operation advances expiry before handling its input. Equality with a deadline
is expired. Compute elapsed differences without adding potentially overflowing
deadlines. A clock regression latches a fault; only construction in a new clock
domain recovers it. Removal of retained metadata remains allowed after clock fault;
it grants no recovery or disclosure. Neither wall-clock changes nor remote time renew anything.

The owner must tick at least every 100 ms while runnable; scheduling gaps and suspend
are reported by native evidence, not hidden by fabricated ticks. Actual elapsed
monotonic time after a gap is used. An OS clock that excludes suspend needs a
separate resume invalidation before a native profile may claim sleep recovery.
These algorithms establish decisions at observed times, not hard-real-time display
or kernel guarantees. Views are snapshots of the last observed time; they do not
sample a clock themselves. A caller must advance time before using a view.

## Producer lease

One lease owns one authenticated connection attachment and at most two bounded
producer/epoch identities: current attachment and last accepted update. IDs follow
the existing ASCII opaque-ID syntax with 256-byte ceiling. Attach grants a 3,000 ms
initial lease, allocates a strictly increasing local uint64 token and requires a
full snapshot. Reattachment always requires a snapshot, including the same epoch;
old callbacks carry the old token and cannot mutate or fault the new attachment.
Tokens are lifetime guards, never authentication or authorization. Token exhaustion
fails closed rather than wrapping. The native composition authenticates before attach.

An increasing heartbeat sequence renews only the 3,000 ms producer lease. The first
sequence may be zero. Exact duplicates do not renew it; sequence regression closes
the attachment. Snapshot/delta traffic alone does not extend the lease. A heartbeat
arriving at or after expiry cannot resurrect that connection: reconnect, authenticate
and resynchronize. Disconnect expires immediately, even when the deadline is later.

The model/data owner validates an entire publication before notifying this guard.
An accepted snapshot notification supplies current producer/epoch and generation;
a mismatched identity closes the attachment. A snapshot cannot regress an already
accepted generation in that attachment. Same-generation replay while synchronized
is duplicate and leaves last-accepted time unchanged. A full snapshot after a gap
may re-establish the same generation. A new attachment/epoch has no inherited
generation floor and must still receive a full snapshot before any delta.

A delta notification supplies exact current base and a strictly greater next
generation. Before a snapshot, or on a base/order mismatch, request a full snapshot
and retain the previous accepted metadata. No invalid notification replaces it.
A gap marks snapshot-required without extending the lease. New heartbeats cannot
turn that retained generation into synchronized data.

Views distinguish lease-alive, snapshot-required and presentation: waiting (no
accepted data, attached), active (attached and synchronized), retained (previous
accepted data but unsynchronized/closed), empty (no accepted data, closed).
Retained metadata includes its own producer, epoch, generation and local acceptance
time; attaching a new producer never relabels old data. Metric observation times,
freshness and values remain owned by the model and are never rewritten by a lease.
An active producer may have stale metrics. Retained data must be visibly identified
as retained by the future surface; this helper alone proves no pixels.

Policy remains authoritative over all retained data. A `forget` operation discards
accepted metadata and requires a new filtered snapshot without renewing the lease.
Its caller also drops prohibited payloads/caches before presentation. The helper
stores no payload and cannot grant disclosure. Clock fault, expired producer and
policy-unavailable state must never be interpreted as fresh/authorized telemetry.

## Render progress

One render watchdog owns at most one outstanding, strictly increasing uint64
challenge generation. Issue starts a 3,000 ms deadline. Another issue while pending
is busy and cannot move that deadline. Only completion of that exact challenge
before expiry clears it; old, future or duplicate completions do not count.
After completion a new larger challenge may be issued. IPC heartbeat processing
does not call completion. At timeout, stall is latched for that surface lifetime;
late acknowledgement cannot clear it. Replacement constructs a new watchdog.

Completion is an instrumented renderer fact, not independently observed visibility.
W-02 must still observe changing pixels and stale state externally. A native owner
must establish that completion comes from the render path, not the health loop.
Issue challenges at least once per second while a presentation is expected; omit
them only when that presentation is explicitly suspended and not claimed visible.

## Restart budget and process lifetime

A restart gate owns one child slot and three restart timestamps, never a growing
worker pool. Initial launch is allowed once without counting as a restart. A failed
launch counts as a failure of that slot. Failure records a bounded enum reason and
whether the native adapter has confirmed that the exact owned child is stopped.
If stop is unconfirmed, quarantine the slot: no replacement or reset is allowed.
A timeout or request to cancel/terminate is not stop confirmation. The adapter must
hold the child identity/handle and observe termination before confirming it.

After confirmed failure, delays are 1,000, 2,000, then 4,000 ms for consecutive
failures, plus a per-instance jitter in [0,250] ms selected by the composition.
The fixed jitter makes test outcomes reproducible without removing production
jitter. A running interval of at least 60,000 ms resets the consecutive-failure
backoff before processing the next failure. Every admitted replacement records
its timestamp. At most three replacements are allowed in a rolling 60,000 ms
window; a timestamp ages out at exactly 60,000 ms.

If all three reservations remain at a confirmed failure or at attempted restart,
open the circuit. An open circuit never automatically closes after time passes.
Explicit diagnostic reset is allowed only after the child is confirmed absent;
it clears the retry window/backoff and permits one initial launch. Reset does not
erase the last failure record or repair a monotonic-clock fault. Graceful stop
closes the slot without a failure/restart; deliberate relaunch requires reset.
Duplicate failure, stop or start callbacks cannot consume extra reservations.

## Fixed portable acceptance cases

Each ID binds to `tests/fault/recovery_tests.cpp` and the CTest name `recovery.<ID>`.
Tests use literal expected outcomes, independent of the implementation's constants.

| ID | Required observable result |
|---|---|
| LEASE-01 | Attach at 100; snapshot at 101; heartbeat 7 at 1,100; duplicate at 3,000; active through 4,099, retained at 4,100; late heartbeat cannot revive. |
| LEASE-02 | Disconnect immediately retains generation/identity; reattach new epoch needs snapshot; old-token callbacks cannot poison the new clock or state. |
| LEASE-03 | Gap/base mismatch retains metadata; delta is rejected until full snapshot; generation regression and wrong epoch never replace accepted data. |
| LEASE-04 | Heartbeats keep producer alive while an actual model observation becomes stale; forget removes metadata and requires resync. |
| LEASE-05 | Bad IDs, sequence regression, clock regression and arithmetic near uint64 maximum fail safely; no allocation proportional to reconnect count. |
| RENDER-01 | Challenge at 100 cannot be postponed by busy issue or unrelated/old completion; completion at 3,100 is late and stall latches. |
| RENDER-02 | Exact completion permits next challenge; repeated/old generations do not; producer heartbeat remains alive while rendering stalls. |
| RETRY-01 | Initial failure; replacements at 1,000, 3,000 and 7,000; fourth failure opens circuit; later elapsed time cannot close it; explicit reset preserves last error. |
| RETRY-02 | Unconfirmed stop quarantines; no start/reset while occupied; confirmed exit permits bounded recovery; duplicates do not multiply attempts. |
| RETRY-03 | Exact 60-second expiry, successful-run backoff reset, jitter boundary and maximum-time arithmetic obey the declared limits. |
| RECOVERY-CLOCK | Clock regression latches each guard and prevents later mutation/restart; stale attachment tokens alone cannot trigger it. |

## Execution and evidence

From the repository root, configure/build/test the checked-in development presets
using the developer commands in `docs/developers/build.md`.
Expected new outputs are `libsyspane_recovery.a`, `syspane_recovery_tests` (plus
`.exe` on Windows), component graph and CTest case results. A bad/unknown case exits
nonzero. Keep source/artifact/profile digests, exact commands, logs and failures in
the existing `build-support/evidence/` ownership. Profile qualification stays at the
observed development environment; no older target floor is inferred.

W-25 remains in progress until native producer freeze/crash and renderer stall
tests prove independent progress, owned-process stop/restart and circuit behavior;
the independent diagnostic entry passes damaged optional input/current-policy
tests; and its native exit/visible recovery integration is executed in an admitted
desktop lab. Missing lab access blocks those claims without converting portable
tests into native qualification. The next handoff must retain each unmet gate.

## Initial native supervision closure

This boundary adds `source/platform/child.hpp`, native implementations and a finite
`SysPane.RecoveryProbe` composition. It launches only another instance of its own
executable, with an explicit worker role; there is no arbitrary-program, shell,
PID-attachment or remote launch API. One supervisor owns one child slot at a time,
at most four launches per invocation and a 40-second scenario ceiling. Its only
fault targets are these deliberately launched, unelevated synthetic workers.
The finite probe allows a 250 ms observer-attachment interval after announcing each
child, before the server welcomes it; the ordinary five-second hello deadline remains.
No existing user application, shell, network device or privileged service is touched.

The launcher accepts at most 16 printable ASCII arguments, 512 bytes each and
4,096 bytes total, with no NUL. Native executable identity is obtained from the
running module; PATH is not searched. Environment and working directory are inherited
from the admitted development invocation. They are trusted launch inputs, not an
isolation boundary. A production sibling-binary launcher needs its own artifact and
environment closure. Child stdin/stdout/stderr and unrelated native handles are
not inherited; health flows only through W-24's authenticated private local stream.

Windows creates the same executable with an explicit `lpApplicationName`, quoted
arguments, no window and initially suspended primary thread. A private non-inherited
job has kill-on-close and a one-process limit; assignment precedes resume. The
parent retains the returned process handle until signaled exit, then obtains its
exit code. No PID lookup supplies termination authority. Linux uses `posix_spawn`
on `/proc/self/exe`, closes descriptors above 2 and directs standard descriptors
to `/dev/null`. The sole reaper retains a pidfd, signals through that pidfd and
uses `waitid(P_PIDFD)` to observe/reap only its child. SIGCHLD must remain default
without automatic reaping; other threads must not reap this owned child. Failure
to acquire a pidfd cleans up the still-unreaped launch, never an arbitrary PID.

Linux workers arm parent-death SIGKILL before IPC and check that their actual parent
still matches the trusted launch argument; a pre-arming parent death exits the
worker. The Windows job provides the corresponding parent-handle lifetime bound.
These mechanisms are not a sandbox for hostile code; the Linux worker creates no
descendants. Job/pidfd/procfs support and native user/session authentication remain
requirements of the measured development profiles, not XP/7 or other-kernel claims.

`Child::request_stop` is an asynchronous request, never stop proof. `wait(0..5000)`
returns an optional cached exit record only after OS-confirmed exit. Stop waits use
absolute elapsed monotonic time and preserve EINTR deadlines. A failed timeout
keeps the restart gate quarantined. Scope cleanup requests stop and waits at most
two seconds; inability to confirm cleanup terminates this finite supervisor with
exit 125, allowing its parent-lifetime protection to apply and preventing further
launches. It does not invent a successful cleanup or kernel-hang guarantee.
Normal worker shutdown is a protocol shutdown followed by a confirmed exit; forced
stop is reserved for the isolated worker after failed/expired progress or cleanup.

### Health link and render-worker evidence

`recovery-health` document 0.1.0 over existing wire 0.1 has a 4,096-byte frame limit
and required feature `recovery.health`. The server declares console; its exact
expected child PID and allowed client role come from the launch. Collector workers
exchange health only. Desktop test workers additionally require
`recovery.progress`. The handshake body and five-second deadline remain W-24's.
Each launch assigns a new connection ID and producer epoch. Each direction checks
the selected identity, role, version and required features; no second hello or
welcome, command, data subscription or unsolicited message is admitted.

| Message | Direction | Exact body and effect |
|---|---|---|
| heartbeat | Either negotiated peer | `{sequence: uint64-decimal-string}`; send once per second, including sequence zero after negotiation; only increasing receipt renews the independent lease. |
| render.challenge | Supervisor to negotiated desktop worker only | `{generation: uint64-decimal-string}`; one pending challenge; the IPC loop passes it to the separate render worker. |
| render.progress | Desktop worker to supervisor only | Same generation shape; only the actual worker completion can satisfy the outstanding challenge. Unsolicited/future or mismatched completion closes the link. |
| shutdown | Either negotiated peer | Existing exact reason enum; stop this worker connection and cooperatively join its render worker. |

Unknown/unnegotiated types and wrong connection/epoch close the link. These two
new optional message types do not grant W-24 preview sessions a rendering feature.
No full snapshot or delta is enabled by this health profile: it proves producer
liveness while presentation remains waiting, not telemetry synchronization or pixels.
The health owner reads with 100 ms waits, sends with a 100 ms operation bound and
holds at most 16 decoded events per read. Framing still rejects incomplete/oversize
input; the smaller health budget cannot starve a separate data queue.

The synthetic desktop worker has a real separate thread, one pending generation
and one completion value. A stall blocks that worker while the IPC owner continues
one-second heartbeats. It draws no pixels. A producer-hang fault blocks the worker's
health loop after two heartbeat sends; abrupt exit uses `_Exit(73)` after handshake.
These are actual isolated process/thread faults, not an OS-wide freeze or a renderer
qualification. On fault the supervisor records guard state, confirms process exit
before replacement, keeps its own health loop running and applies the portable
restart gate unchanged. Test jitter is explicitly zero.

### Mandatory native cases for this boundary

`tests/fault/native_recovery.py` observes the supervisor and independently holds
OS handles/pidfds for its announced children before checking exit. Per-attempt
non-overwriting reports preserve all process events, elapsed times and failures.
CTest `native.RECOVERY-01` binds these nine cases, with a 180-second suite ceiling.

| Case | Fixed oracle |
|---|---|
| CHILD-GRACEFUL | Three worker heartbeats and two separate-thread completions; protocol shutdown; OS-confirmed child exit 0; no restart. |
| PRODUCER-HANG | Child remains alive while heartbeat progress stops; lease expires 3,000..4,000 ms after the last received heartbeat; stop confirmed, then one replacement after at least 1,000 ms; healthy replacement exits normally. |
| RENDER-STALL | Worker heartbeats advance while no render completion occurs; challenge stalls in 3,000..4,000 ms; stop confirmed and one healthy replacement follows the same backoff. |
| CRASH-CIRCUIT | Four actual abrupt child exits with code 73; replacement delays at least 1,000/2,000/4,000 ms; circuit opens, no fifth child in a further 500 ms observation. |
| QUARANTINE | An actual live child remains unconfirmed for at least 250 ms; reset/start are denied and no replacement appears; later confirmed stop permits exactly one replacement. |
| PARENT-LOSS | External harness terminates only its own supervisor after peer authentication; held OS child identity observes exit within 3,000 ms through parent-lifetime protection. |
| ROLE-DENIAL | Child requests maintenance instead of its launch-assigned role; no heartbeat or render event is accepted; owned child is cleaned up. |
| WRONG-EPOCH | A negotiated child sends an old epoch; no heartbeat is accepted and the link closes; owned child is cleaned up. |
| PROGRESS-DENIAL | A negotiated desktop worker reports the next generation instead of the outstanding challenge; no render completion is accepted and the link closes; owned child is cleaned up. |

Native scheduling tolerance is fixed before measurement; missing deadlines fail
this development check, not a relaxed oracle. Native process supervision can be
implemented independently of the diagnostic executable and W-02 pixel oracle.
Those mandatory W-25 outputs and the full native-host campaign remain open.

Native lifetime references: [CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw),
[job objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects),
[asynchronous termination](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess),
[pidfd ownership](https://man7.org/linux/man-pages/man2/pidfd_open.2.html),
[spawn](https://man7.org/linux/man-pages/man3/posix_spawn.3.html) and
[parent-death signal](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html).
These establish API semantics; measured SysPane cases establish implementation evidence.

## Initial independent diagnostic entry closure

This increment owns `SysPane.Diag.exe` / `syspane-diag`, built-in public build/profile
facts and a conservative Win32/GTK 3 inspector. It opens no scene, theme, history,
provider, user configuration or controller endpoint. It has no child/process-control,
network, renderer, recovery reset, file preservation or clipboard interface yet.
Recent-failure metadata and explicit preservation of damaged configuration remain
required follow-up boundaries; absence of those features keeps W-25 in progress.
The native toolkit is a declared dependency, not the application's custom renderer.

No arguments or `--inspect` opens the inspector. `--report` emits one UTF-8 JSON
object and LF, with exact fields `schema_version: "0.1.0"`, `product: "SysPane"`,
`component: "diagnostic"`, `build_version: "0.0.1"`, `profile` (compiled profile ID),
`policy_state` (`available` or `unavailable`) and `recovery_controls: "not_implemented"`.
No user/machine identity, path, raw policy or arbitrary failure text is exported.
`--help` emits fixed usage; every other argument combination exits 64. Exit 0 means
normal completion, 69 unavailable native UI, 70 internal failure, and 77 denied
report disclosure. Errors use fixed ASCII codes on stderr, never untrusted content.
`--inspect-hidden` creates the same native controls without mapping/showing the
window, for owned-window verification only; a 20-second watchdog exits 70 if the
external test does not close it. This is not visible-desktop qualification.

### Policy document and provenance

`decode_policy` accepts at most 65,536 UTF-8 bytes, including whitespace. It strips
only surrounding JSON whitespace before using the existing strict parser (depth 32,
16,384 nodes, duplicate-key rejection and no BOM). It enforces policy 0.1 schema
and semantic rules: uint64 revision, unique setting paths/capabilities/role-channel
pairs/classifications, known settings with registry types/ranges, and bounded
extension names/count. Integer settings accept mathematical JSON integers such as
`1.0`, consistently with the command boundary and JSON Schema; fractions and bools
are not integers. Unknown extension contents are bounded but ignored. Unknown
capability identifiers remain meaningful future denials; unknown settings fail.
Parsing returns `available=false`: document contents cannot authenticate provenance.
Only the protected native source marks a completely validated snapshot available.

Windows reads only the 64-bit HKLM `SOFTWARE\Policies\SysPane` key, `PolicyJson`
REG_BINARY. Open each path component without following registry links, retain the
handles and check owner/DACL before and after the bounded value read. This initial
adapter accepts only SYSTEM or built-in Administrators ownership and grants of
mutation rights; other owners/unsupported ACE forms fail closed. Ignore inherit-only
ACEs for the current key; deny ACEs cannot grant access. Effective allow ACEs granting
set/create/link/delete/DACL/owner/generic-write/all rights to another SID make the
source unavailable. A null/absent DACL or registry link is unavailable. This narrow
adapter does not yet qualify additional enterprise policy owners or ACL forms.

Linux opens `/`, `etc`, `syspane`, then `policy.json` relative to retained directory
descriptors, with no symlink following. Each component must be root-owned and not
group/world writable; the leaf must be a single-link regular file, at most 65,536
bytes. Nonblocking open prevents a substituted FIFO from blocking the diagnostic.
Recheck file identity, size and modification/change times after the bounded read;
detectable concurrent change makes it unavailable. Administrators are trusted policy
writers on both platforms; no hostile-admin or kernel-I/O-latency guarantee follows.

Missing, unreadable, malformed, unsupported or untrusted mandatory policy yields an
unavailable snapshot and permits only existing public fallback projections. There is
no environment, CLI, current-directory, user-registry or user-file policy override.
The adapter performs no installation, elevation or policy write. Positive native
protected-policy deployment needs a separately admitted lab; portable document and
projection fixtures do not prove native provenance.

### Projection and inspector lifetime

The diagnostic composition grants itself only the local diagnostic role; it does
not grant remote peers this role. Report output requires the current public/export
decision. Inspector content requires both public/inspector and public/accessibility
decisions, since native control text is also an accessibility projection. Denial
replaces all metadata with a fixed restriction notice and leaves Close usable.
Native labels are not selectable and no copy/export button bypasses channel policy.
The inspector reloads policy before initial presentation and every 1,000 ms while
runnable; on the first poll observing revocation it replaces prior metadata. Poll
latency is explicit, not an instantaneous revocation guarantee. The CLI takes one
snapshot immediately before output and retains no data afterwards. No nonpublic
data is ever read or cached by this increment. Previously exported output is not
revocable. Escape, Close and the native window-close event exit without the controller.

### Fixed acceptance for this increment

| ID | Required observable result |
|---|---|
| DIAG-POLICY | Valid schema fixtures decode without granting provenance; duplicate keys/settings/rules, bad roles/classes/types/ranges/revisions, BOM, excess depth/nodes/size and unknown core fields fail. |
| DIAG-PROJECTION | Unavailable policy permits only public metadata; current export denial yields no report; inspector or accessibility denial removes all profile text; a replacement permitted snapshot restores it. |
| DIAG-01.REPORT | A copied diagnostic executable emits the exact report from an unrelated owned working directory without other SysPane binaries or configuration. |
| DIAG-01.DAMAGED | Malformed optional scenes/themes/history/policy lookalikes in that directory and forged environment policy variables do not alter the report or grant authority; file bytes remain unchanged. |
| DIAG-01.ARGUMENTS | Unknown, extra and policy-override arguments exit 64 without JSON output. |
| DIAG-01.NATIVE-CLOSE | An external harness finds only its child's hidden native window, verifies its PID/class/title, sends its native close event and observes exit 0 within five seconds. No pixels or unrelated windows are captured. |
| DIAG-01.NO-DISPLAY | Linux report works with DISPLAY/WAYLAND_DISPLAY unset; native inspector fails with 69 rather than hanging. Windows records this display-server case as not applicable. |

The native report records source/executable/profile identities and original failures.
No installed protected policy is created or changed by tests. If existing policy
denies the required report, record the lab limitation rather than overriding it.
GTK is pinned to the installed development package/runtime identity. Ordinary
configure/build/CTest commands remain the runner; native UI checks are isolated
from the outstanding W-02 external visibility/native-editor-recovery oracle.

Linux hidden-control checks use an owned Xvfb 21.1.12 server with a private random
MIT-MAGIC-COOKIE-1 credential, no TCP listener and no pixel capture. The test chooses
a random high display (30,000..49,999), refuses existing lock/socket paths and enables
only the Linux abstract local transport. This avoids the WSLg-owned filesystem socket
directory without changing it. It waits at most five seconds for the listening socket,
verifies its SO_PEERCRED PID against the retained server process and always stops
that process. Bind collisions fail without replacing an endpoint. An isolated observer has a six-second
hard bound around potentially blocking Xlib calls, while window discovery and
post-close exit retain their five-second bounds. The existing WSLg server is not
restarted or modified. A WSLg connection-opening timeout is preserved as a laboratory
failure; Xvfb success qualifies only this hidden native-control boundary.

API references: [registry opening](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regopenkeyexw),
[key security](https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-reggetkeysecurity),
[registry access rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights)
and [GTK display initialization](https://docs.gtk.org/gtk3/func.init_check.html).
