---
type: "SysPane Work Package Boundary"
title: "W-25 bounded recent-failure metadata"
description: "Connect recorded failures to independent diagnosis without treating a local file as live health or policy authority."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T05:40:15+11:00"}
sp_id: "SP-W25-FAILURE-METADATA"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-POLICY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 bounded recent-failure metadata

This boundary adds an advisory failure history to the existing independent
diagnostic entry. It does not load scenes, configuration, history databases,
providers or the controller. Explicit configuration preservation, editor exit and
real-renderer/data recovery remain required W-25 work. Use the same modern Windows
and Linux development profiles. The portable codec also builds on the historical
profile; native historical file handling remains disabled.

## Ownership, format and limits

One supervisor invocation owns one newly created file at an explicitly selected
absolute path. It never reopens, replaces, truncates, rotates or deletes an existing
file. No environment variable or current-directory file is discovered implicitly.
The existing synthetic recovery probe accepts an optional fifth argument naming
that output; its metadata contains only its synthetic fault facts. A future product
composition must choose its data root, retention and current operational/logs policy
before enabling recording. This probe grants no product storage or disclosure right.

The exact ASCII header is `SYSPANE-FAILURES 0.1` followed by LF. It is followed by
zero to sixteen JSON objects, each terminated by LF and at most 512 bytes including
LF. The whole file is at most 8,192 bytes. Every object has exactly these fields:

| Field | Contract |
|---|---|
| `sequence` | Canonical unsigned decimal string, consecutive from `"1"` through `"16"`. |
| `elapsed_ms` | Canonical uint64 decimal string, nondecreasing elapsed monotonic time since this supervisor invocation began. No UTC or age relative to a later process is implied. |
| `role` | `collector` or `desktop`. |
| `reason` | `launch_failed`, `crashed`, `producer_expired`, `render_stalled`, `operation_timeout` or `protocol_rejected`. |
| `stop_confirmed` | Boolean OS-stop observation at that record's instant. It never authorizes a later restart or proves current process state. |

No PID, endpoint, path, free-form error, user identity, setting, telemetry or secret
is accepted. The existing strict JSON parser rejects duplicate keys, BOM and invalid
JSON; exact shape, enums and decimal ranges add format-specific validation.
The supervisor captures the fault after the restart gate accepts it, using only
fixed reasons, and appends it only after the owned failed child is confirmed stopped.
Optional file I/O cannot precede that cleanup. The record retains the original
fault's time and stop observation. Graceful operation creates an empty journal. The original recovery cases
and their stop/restart timing criteria remain unchanged.

The writer retains one native handle and appends bounded complete records. It
requests a filesystem flush after the header and every append. A failed write or
flush permanently disables that writer and preserves any bytes already written;
recovery continues and emits a fixed recording-status event. Capacity exhaustion
also stops recording without overwriting older records. Neither a flush request nor
this optional journal establishes durable configuration or power-loss guarantees.
Kernel/filesystem I/O latency is not a hard real-time promise.

## Native access and interrupted input

Creation uses exclusive create, a non-inherited handle and private permissions:
0600 on Linux; a protected Windows DACL granting the current user full control.
Readers require a same-user, single-link regular file and private permissions.
Linux denies group/world access; Windows rejects effective allow ACEs for identities
other than that user, SYSTEM or Administrators. Reparse/symlink leaves, directories,
devices, FIFOs, hard-linked or oversized files are unavailable. Linux opens with
nonblocking/no-follow flags. Reads inspect the same held object before and after;
detectable size/identity/time change produces unavailable with no records.

Paths are explicit caller selections, not authenticated controller identities.
They must be absolute, contain no `.`/`..` component or NUL, and be at most 4,096
UTF-8 bytes. Windows supports ordinary local drive paths up to 240 UTF-16 code units,
without alternate streams, UNC or device namespaces. UTF-8 arguments come from the
native Unicode command line. Parent directories are caller-selected and trusted;
this does not claim isolation from hostile same-user directory replacement.
Nothing creates a parent directory or traverses a configuration tree.

Missing files yield `absent`; rejected/unreadable/concurrently changed native input
yields `unavailable`. A complete header with no records yields `empty`; valid full
records yield `complete`. An exact partial header, or an unterminated final line
within the remaining record budget, yields `incomplete` and only the preceding
fully validated records. A malformed completed line, wrong header, bad ordering,
unknown field, excess line/file/record limit or trailing complete garbage yields
`invalid` and no records. A newline is an observed framing boundary, not a durability
or authenticity proof. Neither incomplete nor invalid input prevents startup/Close.

## Projection and command contract

Existing argument-free/report behavior remains unchanged. `--report --failures
<absolute-path>`, `--inspect --failures <absolute-path>` and the owned hidden
inspector equivalent opt into this boundary. Every other combination remains exit
64. The existing public projection checks still run first. Failure metadata is
operational: export needs current operational/export permission; native labels need
both operational/inspector and operational/accessibility permission. A denied or
unavailable policy produces `restricted` without invoking the reader at all.
No user-controlled file can supply policy provenance or grant a diagnostic role.

An opted-in report adds `failure_history` with exact fields `status`,
`trust: "unverified_local_metadata"`, `live_health: false`, and `records` (validated
objects or an empty array). Paths/raw bytes are never projected. The inspector
shows status, record count and only the most recent validated record with an explicit
recorded/not-live label. Each existing 1,000 ms policy poll rechecks permission and
reloads the file; revocation replaces prior details and prevents further reads.
There is no cross-poll metadata cache and no clipboard/export bypass.

## Fixed acceptance

| Case | Required observable result |
|---|---|
| FAILURE-CODEC | Literal valid records round-trip; consecutive IDs, decimal bounds, nondecreasing time, exact fields/enums, duplicate rejection and 16-record/512-byte/8,192-byte limits hold. |
| FAILURE-INTERRUPT | Truncate at every byte of a two-record fixture: retain only completed records; malformed completed data returns invalid with none. |
| FAILURE-PROJECTION | A read spy stays uncalled under unavailable/export/inspector/accessibility denial; permitted typed policy exposes only validated facts; replacement denial removes all history. |
| FAILURE-STORE | Real native exclusive creation, Unicode path, private permissions, append/reopen, existing-file preservation, partial-tail recovery and rejection of hard links/oversize/relative paths run in an owned directory. Linux additionally rejects symlinks/FIFO/broad permissions. Windows reparse testing is reported separately when creation privilege is unavailable. |
| RECOVERY-01 metadata | Existing nine real fault cases retain their original oracles. The journal's fixed reason/count/role/stop facts match independently observed process events; parent loss and graceful operation have no invented fault. |
| DIAG-01 metadata | Copied independent diagnostic supports opted-in reporting/hidden inspector, does not read restricted malformed/nonexistent input, and retains normal Close/argument behavior. Native positive policy deployment remains a separate lab gate; typed fixtures do not prove it. |

Record exact source/artifact/profile identities and preserve failed attempts.
Ordinary CMake/CTest commands remain the runner. W-25 stays in progress until its
remaining preservation, current-policy deployment and visible recovery gates close.

API references: [Windows file creation](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew),
[Unicode command line](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-commandlinetoargvw),
and [Linux open flags](https://man7.org/linux/man-pages/man2/open.2.html).
