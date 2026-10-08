---
type: "SysPane Handoff"
title: "Native frontend runtime directory ownership"
description: "Private allocation and explicit retirement now compose with the existing controller supervisor."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T21:05:00+00:00"}
sp_id: "SP-RUNTIME-DIRECTORY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-RUNTIME-DIRECTORY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native frontend runtime directory ownership

LinuxRuntimeDirectory now supplies the missing owner for the supervisor's private
runtime root. It admits an existing explicit native base, creates one fresh private
empty directory, and retains the complete ancestor/leaf identity chain. It never
repairs a selected base, follows a symlink, adopts an orphan or chooses a fallback.
Its 50-byte base limit preserves the supervisor's unchanged 70-byte root limit.

Retirement is explicit and descriptor-relative. An independent flock blocks it
while the supervisor still owns the root, including after its state becomes closed.
The caller must first finish native reaping and destroy that supervisor. Unknown
contents or observed replacement permanently invalidate the runtime owner and
preserve the nodes. Destruction only closes descriptors. This is not an additional
security boundary against another process with the same uid racing a final syscall.

## Evidence

All fourteen fixed runtime case families pass on the admitted unprivileged Linux
ext4 laboratory. The independent oracle checks actual modes, inodes, paths, contents,
locks and process lifetimes. It observes both cooperative and forced supervisor
shutdown through an independently held child pidfd. A deliberately wrong empty-root
oracle fails as intended. The nineteen existing native supervisor families also pass.
Both component graph checks pass on all three configured development profiles.
Specification validation passes for 48 schemas and 166 fixtures. Tooling unit tests
were not repeated because their implementation did not change.
No Windows runtime implementation or historical OS qualification is claimed.

The first build failed because the dedicated test probe omitted its native clock
header; the include was added and the original failure retained. The first runtime
execution passed, then the workspace preflight stopped on its intentionally
unreadable restrictive-umask orphan. Its original mode/inode snapshot was preserved
before the independent lab restored owner access. The oracle now records that lab
restoration and verifies the exact orphan is empty. Runtime ownership and the fixed
acceptance expectations are unchanged. The subsequent native execution and storage
preflights pass. No directory was deleted to make the test or accounting pass.
An initial documentation validation ran before its referenced checkpoint existed;
that failed link check is retained. The generated checkpoint closes the link and
the subsequent specification validation passes.

The [checkpoint](checkpoints/runtime-directory.json) binds exact source snapshots,
artifact identities, checks and retained failures. Five native archives preserve
74,323,974 raw bytes, including both runtime attempts, supervisor evidence and their
retained roots. No pruning was performed. tmpfs admission is implemented but was not
qualified by these ext4 cases; the Windows-mounted path is refused by native admission.
Randomness/collision exhaustion and same-uid syscall races were not fault-injected.

## Continue with the actual frontend

W-08 remains in progress. Compose one installed frontend with the verified
installation, this runtime owner, the independently scheduled supervisor and the
authenticated ProfileDownload client. Blocking client connection/read/validation
work must not prevent supervisor polling or GUI callbacks. Read XDG_RUNTIME_DIR for
ordinary frontend startup and report an unavailable state when it is inadmissible.

Connect the existing native settings and editor actions to real commands/results,
preserving original unresolved request identity through producer replacement.
Reconcile before admitting another mutation; never replay automatically or claim an
unknown outcome did not commit. Clear private GUI state on policy/producer loss.
Verify the installation closure of the editor's other private helpers before launch.
Then connect telemetry, activation, import catalogs and installed recovery context.

The native application entry point, protected-policy deployment, package/lifecycle
qualification and all five complete desktop editions remain open. This prerequisite
does not narrow the release objective or turn a settings window into a desktop host.
