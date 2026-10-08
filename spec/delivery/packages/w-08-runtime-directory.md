---
type: "SysPane Work Package"
title: "Frontend runtime directory ownership"
description: "Give the native frontend a bounded private runtime root with explicit, identity-checked retirement."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-08T20:55:00+00:00"}
sp_id: "SP-W08-RUNTIME-DIRECTORY"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-SUPERVISOR", "SP-W26-HELPER-IDENTITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Frontend runtime directory ownership

Close the remaining runtime-path ownership prerequisite for installed Linux frontend
composition in W-08. Implement LinuxRuntimeDirectory in source/platform. Existing
profile data, installation and controller ownership remain separate. This package
does not complete the frontend, settings/editor routing, deployment or any edition.

## Admission and allocation

The serialized off-GUI owner supplies an explicitly selected runtime base. The
frontend will read XDG_RUNTIME_DIR for ordinary installed operation; no implicit
fallback to the working directory, payload, HOME, /tmp or an invented user directory.
This API takes the selected string and neither reads nor changes environment values.
An absent, relative, noncanonical, NUL-containing or overlong selection fails before
creation. Require an absolute path of at most 50 bytes, no trailing slash, repeated
slash, dot or parent component, and at most 32 non-root components. Root itself is
not a private runtime base. These limits preserve the supervisor's 70-byte root
ceiling and its full uint64 generation endpoint paths.

Require the existing unprivileged native context. Walk from / using held directory
descriptors, O_NOFOLLOW and O_CLOEXEC. Each ancestor must be root- or current-uid
owned, without group/other write or special mode bits. The selected base must be
current-uid owned, exactly 0700, on ext4 or tmpfs. Do not create, chmod or repair the
base or any ancestor. Validate all inputs before creating anything. A failed native
allocation may leave its newly created node; preserve it when ownership is uncertain.

Create one fresh directory named sp- followed by sixteen lowercase hex digits from
eight native random bytes. The name provides collision avoidance, not authentication.
Use nonblocking native randomness, at most sixteen interrupted reads and eight
exclusive mkdir attempts. Never reuse or inspect a colliding directory. Require
the resulting directory's exact current-uid/0700 identity; a restrictive caller
umask that removes required owner permissions fails without changing the umask.
The directory is initially empty so the existing supervisor can own its flock and
generation children. Retain the base/ancestor chain and new directory descriptors
and identities for this object lifetime. No marker, journal, traversal of the base,
or persistent adoption mechanism is needed for this ephemeral allocation.

## Verification and retirement

path() returns the canonical allocated root only after rechecking every held and
named ancestor and leaf identity, owner and mode. A detected replacement, rename,
permission change or missing node permanently invalidates this owner; restoring
the old path does not restore authority. Calls from another thread fail without
invalidating the legitimate owner. No method changes global process state.

cleanup() is explicit. First verify the complete chain, then open a separate file
description for the leaf and acquire LOCK_EX|LOCK_NB. The supervisor's independent
flock must block cleanup even after its state says closed, until it is destroyed.
A busy lock is retryable and removes nothing. Inspect at most three directory
entries (including dot entries); any non-dot entry blocks cleanup, preserves all
contents and permanently invalidates this owner. Never recurse, unlink a socket,
clear an orphan, or infer child exit from elapsed time. The supervisor remains
responsible for actual child reaping and its generation/socket cleanup.

After the empty check, reverify the chain and fresh lock descriptor, then remove
only the exact recorded empty leaf with unlinkat(AT_REMOVEDIR) relative to the held
base. Retain the lock until removal completes. Successful cleanup is idempotent;
path() after cleanup refuses. Native removal failure invalidates the owner and
does not permit a repair or retry against a replacement. Destruction closes native
descriptors only; it never deletes files implicitly. A crash or omitted cleanup
leaves the root untouched. Later owners allocate fresh names and do not adopt old
roots. XDG session retirement or separately admitted explicit cleanup owns orphans.

This contract detects observed substitutions and uses descriptor-relative writes.
It is not a security boundary against another process with the same uid changing
names between the final identity check and unlinkat. Such a process already has
the same filesystem authority. Cleanup never follows a substituted symlink or
recursively deletes unexpected content.

## Fixed independent cases

Freeze this package and tests/configuration/runtime-directory-cases.json before
implementation. A separate native Python oracle must inspect actual modes, inode
identities, directory contents and peer process exit. Cover valid allocation and
idempotent retirement; simultaneous independent owners; malformed/overlong paths;
symlink and writable-ancestor refusal; private-base permission checks; unsupported
filesystem rejection; busy flock and retry; unexpected contents; leaf and ancestor
replacement plus permanent invalidation; wrong-thread refusal; destructor and
crash preservation; and actual cooperative/forced supervisor shutdown.

For the composed supervisor cases use the existing dedicated helper and ordinary
supervisor, observe its exact child through an independent pidfd, and prove the
root remains while the supervisor owns its lock. After native exit, destroy that
supervisor before retiring the root. A deliberately incorrect empty-directory
oracle must be rejected. Preserve snapshots of rejected and orphaned nodes rather
than deleting them to make a case pass. No production test hooks or policy override.

Run native.RUNTIME-DIRECTORY plus existing native.PROFILE-SUPERVISOR and component
graph checks. Linux-only code does not require unrelated portable-suite reruns;
configure and graph-check all three profiles to verify conditional composition.
Record source/artifact identities, failures, storage preflights and the next actual
frontend integration step in the existing delivery graph. Full five-edition release
scope, protected-policy qualification and public-release authority stay open.
