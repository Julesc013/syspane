---
type: "SysPane Work Package Boundary"
title: "W-25 explicit private configuration preservation"
description: "Preserve opaque damaged input without replacing source bytes, weakening policy or claiming a configuration commit."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T06:15:00+11:00"}
sp_id: "SP-W25-PRESERVATION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W25-PACKAGE", "SP-W25-FAILURE-METADATA", "SP-POLICY", "SP-PERSISTENCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# W-25 explicit private configuration preservation

The independent diagnostic entry must offer a local private copy of an explicitly
selected damaged file. It never parses, imports, activates, repairs or restores that
input. This operation is separate from W-08 generation persistence and from a
redacted support bundle. A private opaque copy may retain sensitive bytes already
present in the user's file; none becomes telemetry, a preset, UI text, clipboard
content or diagnostic-export data. No automatic discovery or directory traversal is
enabled. Scope this initial adapter to the modern Windows/Linux development profiles.

## Authority and selection

Require available current protected policy and no denial of
`diagnostic.preserve_configuration`. The CLI also requires public/export permission
for its fixed acknowledgement. Native path controls require operational permission
for both inspector and accessibility. An unavailable/denied policy prevents source
or destination I/O. A file, command-line switch or typed document cannot provide
policy provenance. Native tests with a typed policy fixture establish operation/UI
bindings only; they do not establish installed protected-policy deployment.

Pin the initially admitted policy revision for the operation. Recheck availability,
that revision and the relevant capability/channel permissions before reading,
after reading, before staging creation, between 64 KiB transfers and immediately
before publication. A changed/denied snapshot cancels publication. This is an
observed decision before the filesystem operation, not an atomic transaction with
an external policy administrator. Publication already completed is not revoked by a
later policy update; deleting a preserved copy needs separate user authority.

The operator supplies a source and a new destination. Paths obey the existing
explicit Unicode path limits in SP-W25-FAILURE-METADATA, including trusted selected
parent directories. The destination must leave room for the eight-character
`.partial` suffix within those limits. Parents must exist. The source must be a same-user, single-link
regular file of at most 8 MiB; no other non-administrative identity may write it.
Read access for other identities is permitted on the source. Symlink/reparse leaves,
devices, FIFOs, foreign ownership and hard links are rejected. Destination files
must be private; source permissions are never copied into a broader destination.

## Copy state and filesystem behavior

An existing destination or `<destination>.partial` is a conflict. Never overwrite,
truncate, replace or delete either, including a dangling link or a name that races
publication. Never modify the source. Access-time updates caused by reads are not
claimed absent. Keep native source identity/handle through verification. Windows
source sharing excludes writers/deletion; Linux verifies identity, size, permission,
modification/change times and bytes again before publication. Detectable concurrent
change fails; this is no hostile same-user/kernel snapshot guarantee.

Read at most 8 MiB into a bounded buffer. Exclusively create the partial file with
0600 (Linux) or a protected current-user DACL (Windows), non-inherited handles and
no leaf-link following. Write in at most 64 KiB chunks, request a file flush, read
the staged bytes back and compare them with the buffered original. Re-read and
compare the held source before the final policy/cancel decision. Buffers are cleared
when the operation ends; no raw bytes enter result objects or logs.

Publish the verified staging file through the profile's no-replace rename:
`renameat2(RENAME_NOREPLACE)` on Linux and handle-based `FileRenameInfo` with
`ReplaceIfExists=FALSE` on Windows. Unsupported publication fails without a weaker
fallback. The original remains unchanged and a preexisting final name survives.
No directory flush/power-loss qualification is claimed: `durable` is always false.

Outcomes are `preserved`, `denied`, `cancelled`, `conflict`, `invalid_path`,
`source_unavailable`, `source_changed` or `io_error`. `partial` means this invocation
created staging that was not published; failures preserve those private bytes for
inspection and never label them a completed copy. A new explicit attempt must
choose another destination while its partial name exists. Retention is bounded to
one at-most-8-MiB staging file per explicit attempt, with no automatic retry pool.
Interruption can leave only an incomplete private staging file or a completed
verified copy; no success is inferred from mere existence after a crash.

## Commands and native controls

`--preserve <absolute-source> <absolute-destination>` is an explicit action. It
prints only `{ "outcome": <enum>, "partial": <boolean>, "durable": false }` and LF.
No path, bytes, digest, parser/native error or user identity is printed. Exit 0 means
preserved; 77 denied; 64 bad arguments/path; 73 conflict; 74 source/I/O failure;
75 cancellation. Existing report/inspector behavior and codes remain otherwise.

The Win32/GTK inspector has native source/destination text fields, Preserve copy,
Cancel copy and a fixed status label. There is no automatic copy on editing a field.
Preserve captures the explicit pair and starts at most one background worker.
While busy, inputs/Preserve are disabled and Cancel/Close remain usable. Policy
revocation observed by the one-second UI policy poll clears both path fields,
replaces status and requests cancellation.
No path or content is retained in the public report. These native entry controls
are the initial selection UI; file-picker dialogs are not required by this boundary.

The worker owns immutable selected paths and cancellation state, and never touches
native controls. A completed worker is joined before another is admitted. Close
requests cancellation and must not join a worker blocked in file I/O; process exit
reclaims it. The operation owner lives for the diagnostic entry's lifetime, so
closing/reopening jobs cannot grow an unbounded detached pool. Cancellation checked
before publication prevents it; a request after that decision may be too late.
An OS/kernel I/O stall is not a hard real-time storage guarantee.

## Fixed acceptance

| Case | Required observation |
|---|---|
| PRESERVE-POLICY | Unavailable policy, capability denial, wrong revision or missing channel denies; permitted typed snapshots allow only the declared channel scope. |
| PRESERVE-NATIVE | Exact malformed/binary/empty/Unicode input copies to private output; originals and preexisting destination/partial bytes remain unchanged. Reject source size/type/ownership/write permissions, links, relative/device paths and unsupported publication. |
| PRESERVE-ABORT | Deny/cancel before read, before staging and before publish; no final copy appears. After staging, only the owned partial may remain. External child termination during a checkpoint likewise never modifies source or publishes incomplete bytes. |
| PRESERVE-CHANGE | Windows rejects an existing writer; Linux detects a source changed after the initial read. A destination created immediately before publication remains intact. |
| PRESERVE-UI | The same native control library binds selected text to a real private copy in a typed-policy fixture, updates status, refuses a second busy job and exits while work is blocked. Programmatic control activation is not external pointer/keyboard/accessibility qualification. |
| DIAG-01 preservation | Actual diagnostic CLI under unavailable policy performs no file I/O and returns denied; hidden native Close stays usable with preservation disabled. No policy override is added. |

Use ordinary component/preset/CTest commands. Bind results to source, artifact,
profile, filesystem and exact executed case identities. Retain failed attempts and
missing Windows symlink privileges explicitly. W-25's real telemetry/renderer,
payload revocation and independent editor-exit gates remain open.

References: [Windows handle publication](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info),
[file information updates](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle),
and [Linux no-replace rename](https://man7.org/linux/man-pages/man2/rename.2.html).
