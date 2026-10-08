---
type: "SysPane Evidence Handoff"
title: "Linux profile directory ownership checkpoint"
description: "Private root selection, interrupted creation, lifetime locks and existing store composition."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T00:00:00+11:00"}
sp_id: "SP-PROFILE-OWNER-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-OWNER", "SP-INSTALL-OWNERSHIP", "SP-RELEASE-0-1-0"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Linux profile directory ownership checkpoint

W-08 now supplies a reusable LinuxProfileOwner for the installed controller's next
composition step. It selects XDG or explicitly chosen portable user-data paths,
uses a hash of the profile identity as a safe directory key, and independently owns
configuration, content and state roots. Each root contains an exact private marker,
an empty exclusive lease and its existing store child. Only complete, locked roots
yield verified paths. No installed controller or privileged policy is activated.

Creation publishes private complete leaves without replacing collisions. Existing
unmarked directories, aliases, unsafe metadata and foreign entries refuse without
repair. Interrupted stages and partial initialization remain recoverable through a
fresh owner; capacity refusal preserves evidence. Fresh verification checks named
paths, marker/lease identity, child directories and current guard. Denial or observed
replacement permanently invalidates the owner. Exact scope and bounds are in the
[frozen package](packages/w-08-profile-owner.md).

## Executed evidence

The independent non-root ext4 family passes 114 cases: literal XDG/portable paths,
exact private files, competing owners for each root, process death, wrong-thread and
reentrant calls, initial/late guard denial, short writes, unsafe filesystem nodes,
capacity, replacements and oracle calibration. It cuts its held process at eight
phases for each of three roots, observes SIGSTOP and SIGKILL, then independently
checks absent-or-complete publication and successful fresh initialization.

Eight additional held pre-publication mutations verify that changed staging, parent,
marker, lease, child, membership, child contents or child permissions refuse before
publication. The real generation and recovery owners persist into the returned
children while the profile locks remain held; fresh reopen preserves the exact
settings, scene and recovery bytes. This does not test hardware power loss.

The five existing CONFIG-STORE and RECOVERY-STORE/QUEUE/APPLY/STORED-APPLY CTest
families pass with unchanged store artifacts. All three development profiles configure,
build and pass both component graph checks. The Windows builds verify that this
Linux-only component is excluded; they do not qualify Windows profile ownership.
Specification schema/fixture, generated-content, tooling and integrity checks are
recorded in the [compact checkpoint](checkpoints/profile-owner.json).

Two implementation/test failures are preserved. The initial build rejected misleading indentation in
the test probe; formatting was corrected without changing compiler warnings. A
subsequent native test demonstrated publication before detecting changed child
permissions. The production fix moves that permission check before the no-replace
rename. The original package and both fixed case files retain their frozen hashes;
no expected outcome was weakened. The earlier 106-case pass remains a narrower run,
not evidence that the later-discovered defect never existed.

Raw source/log archives, native node inventories, artifact identities and failed records
remain local ignored out/evidence/profile-owner* content. The checkpoint binds each
execution to source inputs and artifact hashes; the post-commit local proof binds
the final tree. A fresh checkout regenerates its own evidence using the ordinary
commands in repository docs/developers/build.md. An early specification check also
preserves the unfinished checkpoint link and a rejected link outside the spec bundle;
both documentation links are corrected before final validation.

## Next boundary

Connect this owner to the supervised controller, immutable catalog/default generation
and protected mandatory policy. The caller must separately authorize the selected
profile, keep blocking I/O outside GTK, supervise worker stop/reap, and preserve
payload/setup separation. Environment variables and ownership markers are never
policy grants. This checkpoint provides directory ownership, not installation,
onboarding, catalog import, migration, purge or release qualification.

W-08 remains in progress. Other native storage/profile adapters, full configuration
layers/updates, installed desktop integration, accessibility/performance, lifecycle
and all five complete editions remain required. Preserve earlier native diagnostic
failures and unavailable historical/Mac laboratories; do not substitute development
builds for qualified release profiles.
