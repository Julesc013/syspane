---
type: "SysPane Specification"
title: "Independent recovery and bounded failure"
description: "Preserve diagnostic usefulness and independently expire retained presentation."
tags: ["architecture"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-04T19:16:06+11:00"}
sp_id: "SP-RECOVERY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-PROCESSES", "SP-PERFORMANCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-AUDIT-2026-10-04", "resource": "User-supplied SysPane audits and design reviews, 2026-10-04", "title": "October specification review inputs"}]
updated: {"by": "codex", "at": "2026-10-06T01:39:51+11:00", "scope": "W-25 portable recovery checkpoint; native and visible recovery remain pending"}
---

# Independent recovery and bounded failure


## Failure contract

Within granted OS/session capabilities, optional failure must leave trustworthy
unrelated data and a useful diagnostic route. Denial is not zero. The application
cannot promise fresh pixels after kernel/compositor failure or bypass execution
policy. Process liveness, producer liveness, metric freshness and visible rendering
progress are separate facts.

The surface expires the controller's negotiated lease on its own monotonic clock.
A heartbeat renews producer liveness only; it does not renew individual observations.
On disconnect or expiry, retain permitted data with conspicuous stale/retained state,
producer identity and last accepted update. A new epoch requires a new snapshot.
Render-progress watchdogs are independent of a process merely responding to IPC.

## Independent entry

The planned `SysPane.Diag.exe` / `syspane-diag` entry starts without the controller,
custom scenes/themes/assets, third-party providers, GPU initialization, persistent
history parsing or USK. It reads bounded build/profile and recent failure metadata,
offers preservation of damaged configuration and launches a conservative native
inspector. `--safe-mode` is a proposed product option, not a shipped command.

Safe mode skips optional configuration, not mandatory policy. An unreadable required
policy source fails closed for restricted operations and disclosure while allowing
non-sensitive diagnostics. Restoring an old generation never restores revoked rights.
An independent keyboard/native exit must release an obstructing editor surface.

| Failure | Required action |
|---|---|
| Invalid authored content | Keep the previous accepted generation; preserve rejected input. |
| Provider hangs | Cancel cooperatively, quarantine, or terminate its isolated worker. |
| Surface crashes | Continue independent collection; bounded restart with last error visible. |
| Persistent failures | Open circuit breaker; require explicit reset after diagnosis. |
| Recorder full/corrupt | Stop optional recording, mark gaps, keep live state responsive. |
| Payload damaged | Use an independent intact maintenance source. |
| Read-only data root | Explain unsaved/session-only changes; no silent alternate persistence. |

## Limits

Resource profiles must set queue/frame bytes, entity/text/asset limits, worker
concurrency, timeouts, restart counts/window/backoff, recorder retention and graphics
budgets before a provider is enabled. Health, policy revocation and shutdown have
reserved capacity. Repeated timeouts cannot grow an unlimited replacement pool;
a timeout does not establish that an OS operation stopped.

The [W-25 package](../delivery/packages/w-25-recovery.md) closes the initial portable
lease, rendering-challenge and single-child restart decisions, including exact
deadline equality, stale callbacks, clock regression, bounded backoff and quarantine
until confirmed termination. These guards precede native supervision and independent
diagnostic entry; they do not by themselves establish visible recovery or native
process-stop evidence.

Tests freeze the producer, stall rendering, corrupt optional content, remove storage,
revoke policy and exhaust optional work. Recovery reports measure elapsed time and
all involved processes. Numerical resource ceilings are admitted per profile after
measurement, not presented as universal performance claims.
