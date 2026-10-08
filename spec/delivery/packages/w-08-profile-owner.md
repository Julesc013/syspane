---
type: "SysPane Work Package"
title: "Linux profile directory ownership"
description: "Explicit paths, private atomic initialization and exclusive controller lifetime."
tags: ["delivery", "setup", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:00:00+11:00"}
sp_id: "SP-W08-PROFILE-OWNER"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-INSTALL-OWNERSHIP", "SP-PERSISTENCE", "SP-W10-RECOVERY-STORE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-XDG"]
---

# Linux profile directory ownership

Supply the directory-lifetime prerequisite for the installed controller through
one platform component. Preserve existing generation, content and recovery owners.
This component does not install a policy, select product defaults, bootstrap a
scene, authorize edits, launch a desktop or qualify an installed edition. Its
development probe is a test target, never an installed policy override.

## Selection and fixed layout

The caller supplies an existing protocol identifier as profile ID. Its lowercase
SHA-256 is the directory key; the original ID is retained in each ownership marker.
For XDG mode resolve CONFIG_HOME, DATA_HOME and STATE_HOME independently. Unset,
empty or relative values use HOME/.config, HOME/.local/share and HOME/.local/state,
respectively. HOME must be absolute when a fallback is needed. Do not consult cwd,
search directories, payload writability or policy preference files. Follow the
[XDG defaults](https://specifications.freedesktop.org/basedir/latest/).

An explicitly supplied portable data root replaces all three bases. Empty portable
selection is invalid, not XDG fallback. The mode is recorded. This API only owns
user data: the installation owner must separately prove payload/setup separation.

Append syspane/configuration/KEY, syspane/content/KEY and syspane/state/KEY to the
corresponding bases. Equal bases are allowed. Refuse overlapping final roots before
I/O. Normalize trailing slashes only; reject NUL, relative paths, empty interior
components, dot/parent components, names over 255 bytes, paths over 4096 bytes and
more than 64 components (including the final child). No automatic redirection.

Each profile root has exactly .owner.json, .lease and one directory: generations,
packages or recovery respectively. Marker bytes are sorted compact UTF-8 JSON with
no trailing newline and exactly format=SysPane.Profile, schema_version=0.1.0,
profile=the original ID, kind=configuration/content/state, mode=xdg/portable.
Markers are at most 1024 bytes. The lease is empty. Both are regular, single-link,
current-uid 0600 files; roots/children are current-uid 0700 directories. No special
permission bits. Children hold the existing store formats; do not put profile
markers inside those formats. Never take over or repair foreign/unmarked roots.

## Creation, locks and authority

Only the admitted non-root Linux ext4 development environment is qualified here.
The ext-family primitive gate is not evidence for other filesystems. Walk every
component with no-follow directory descriptors; ancestors must belong to root or
the current uid and have no group/other write or special bits. Root-owned /tmp with
sticky permissions is intentionally outside this profile. Existing permissions
remain unchanged. New ancestors are private 0700 and their parent is flushed.

Creation is an explicit constructor flag; false means no filesystem mutation.
A mandatory caller guard establishes current native authority, including profile
selection and mandatory policy, on every check/publication. Missing, false or
throwing guards refuse. No environment string, marker or test argument is authority.
Perform all filesystem operations on a serialized worker, outside GTK callbacks.
Potentially blocked filesystem work requires the existing supervised-process
boundary before installed use; elapsed time alone cannot prove a worker stopped.

Initialize a missing leaf in a private same-parent random staging directory named
.KEY.pending-NONCE (128-bit random lowercase hex). Create/flush the marker, empty
lease and empty child; lock the lease exclusively and nonblockingly before publishing.
Flush the stage, recheck current authority, path and node identities, then publish
with renameat2(RENAME_NOREPLACE), and flush the parent. No replacing destination and
no fallback to a weaker operation. A concurrent publisher produces a refusal and
preserved staging, never overwrite. Each published leaf is absent or complete after
a process interruption; this is not a hardware power-loss qualification.

Acquire configuration, content, state in that fixed order. Reopen existing complete
roots without modifying them, and retain all three exclusive .lease locks for the
controller lifetime. A shared role root blocks a second owner even if the other
bases differ. Return verified child paths only after all roles are complete and
locked. Partial multi-role initialization is preserved and a fresh owner can finish
it; no usable profile is returned halfway through. Destruction releases descriptors
without deletion. Descriptors are close-on-exec; callers must not fork and retain
an inherited owner. flock semantics are described in the
[Linux manual](https://man7.org/linux/man-pages/man2/flock.2.html).

Preserve unfinished staging; never adopt it as current and never recursively clean
unknown files. Before creating a missing leaf, scan at most 4096 parent entries
and refuse if eight names with this profile's pending prefix already exist. This
bounds sequential failed attempts; simultaneous callers may race the count and
leave additional bounded stages, so it is not a global disk quota. Existing valid
leaves can reopen regardless of orphan count. Report capacity without changing
staging; explicit reviewed cleanup is a separate operation.

Each verified-path call reopens the full path, checks exact root membership,
marker/lease identities and bytes, child identity/permissions and current guard.
Changed roots, lease replacement, metadata/content changes or denied authority
permanently invalidate that owner. Regrant requires a fresh owner. Wrong-thread or
reentrant calls refuse. Guarded checks are linearization points, not an impossible
promise against later same-uid changes. Store operations still perform their own
checks. Finite loops bound scans/reads and allow at most 16 EINTR retries; no sleeps
or lock retries. Errors are bounded profile.* codes without paths/content.

## Fixed verification and completion

Freeze this package and tests/configuration/profile-owner-cases.json before source
changes. The native Python oracle constructs expected paths/marker bytes itself,
inspects actual files and kills only its own held probe at each declared phase.
Cover XDG/portable planning and invalid bounds, exact reopen, all three lock roles,
guard denial, process death, partial initialization, staged capacity, foreign entries,
symlinks, hardlinked/special/oversized files, permissions and root/node substitution.
Reject an intentional wrong marker to calibrate the byte oracle. Open the child
directories through actual generation/recovery owners and check persisted content.

Use ordinary preflight, cmake --preset linux-x64-gcc13, cmake --build --preset
linux-x64-gcc13 and ctest --preset linux-x64-gcc13 -R
'^(native[.]PROFILE-OWNER|composition[.])' --output-on-failure. Run existing native
configuration/recovery-store regressions; configure and check component graphs on
both Windows development profiles. Preserve source/artifact/environment identities,
fixed-input hashes and failed attempts in ignored out/evidence. Keep the compact
handoff in spec/delivery, with W-08 in progress. Next integrate the owner into the
supervised controller with catalog/default generation and protected machine policy.
All other native adapters, lifecycle and five complete editions remain required.
