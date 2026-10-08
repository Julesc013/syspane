---
type: "SysPane Work Record"
title: "Initial profile and native store checkpoint"
description: "Compiled defaults, atomic first resource generation and policy-bound controller storage."
tags: ["delivery", "setup", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:00:00+11:00"}
sp_id: "SP-PROFILE-STARTUP-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-PROFILE-STARTUP", "SP-PROFILE-OWNER-HANDOFF", "SP-RELEASE-0-1-0"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Initial profile and native store checkpoint

Baseline b47b84650b691c2bdb6e9d593e490e0572f06d83. W-08 now has actual compiled
product defaults and LinuxProfileStore, which composes the existing profile leases,
generation store, immutable content resolver and protected-policy reader. The initial
scene/theme lives in configuration/defaults/profile.json; descriptor defaults remain
the source for settings. Runtime startup needs neither test fixtures nor source paths.
The [package](packages/w-08-profile-startup.md) fixes the exact contracts.

The default scene is an editable primary-display network group/table with receive,
transmit and rate fields. It is a starting scene, not a restriction on required
providers or editions. Its three immutable packages retain exact pins, source bytes
and LicenseRef-SysPane-Pending metadata. The unresolved licensing decision remains;
this component checkpoint supplies no redistribution permission.

## Initial publication and later edits

Bootstrap manifest 0.5 explicitly identifies a resource-backed revision zero with
no client request/receipt. Old manifests retain their meaning. The profile owner
constructs this generation inside its private configuration stage and verifies it
through a fresh native reopen before publishing the leaf. Interrupted attempts retain
their bytes in unselected stages. Existing published roots never invoke the initial
factory or receive a silent reset/default update.

Normal edits continue through Transactions and their existing resource preparation,
request identity, revision increment, durability and restart reconciliation. Saved
authored values remain saved values when mandatory policy changes; effective-layer
resolution and external projection remain separate owners. A coherent previous
generation is readable recovery, never writable normal startup.

LinuxProfileStore defaults to the fixed native machine_policy source. It checks the
complete effective policy snapshot at profile verification/publication and refuses
same-revision changes, unavailability, throwing/reentrant sources or profile loss.
Invalidation is permanent for that owner; fresh admission requires fresh ownership.
The test entry point can supply native in-process fixture policy. It adds no product
CLI, environment or user-file policy override and does not establish provenance.

## Actual checks and limits

The new native family passes 63 cases, including 19 initialization cuts, four profile
publication cuts and six interrupted normal commits. The independent oracle observes
each held process stop and termination, inspects exact selectors/manifests/assets,
preserves orphan bytes and reopens through the real owners. It verifies one initial
generation, edit to revision one, lost-result reconciliation without another revision,
late policy changes, same-revision drift, saved-data preservation, old-format and
corrupt-bootstrap refusal, staged coherent-but-wrong content, read-only fallback,
and a deliberately wrong-byte oracle witness.

The actual fixed native policy source reports unavailable in the unprivileged lab;
the default source refuses startup without mutating the selected root. Positive
cases use the separate fixture entry point. Protected-policy deployment is still
unqualified and no administrative policy was installed or changed.

All three development profiles configure/build and pass configuration.INITIAL-PROFILE
and both component graph checks. Linux PROFILE-OWNER, CONFIG-STORE,
RESOURCE-GENERATIONS, CONTENT-COMMANDS and RECOVERY-STORE regressions pass. These are
component tests on the recorded contemporary environments; the Windows historical
toolset build is not an XP runtime qualification. Specification/tooling/integrity
results, exact input hashes, execution commands and artifact identities are in the
[compact checkpoint](checkpoints/profile-startup.json). Original fixed inputs remain
unchanged. Raw archives are ignored local out/evidence/profile-startup* content;
fresh checkouts regenerate their own evidence with docs/developers/build.md commands.

## Next admitted work

Integrate this store into the supervised installed controller and authenticated IPC,
then native settings/editor startup and the configured import catalog. Keep I/O off
GTK and retain exact worker stop/reap evidence; this class does not itself supply
process supervision. Qualify native mandatory-policy installation only in an admitted
lab. Complete initial renderer/source activation separately from durable storage.

W-08 remains in progress. Full layers/updates, native adapters and profile ownership
outside Linux, complete desktop behavior, accessibility/performance, installation/
upgrade/rollback/uninstall and all five required editions remain open. Preserve older
native failures and missing legacy/Mac qualification; this checkpoint does not close
the release objective or authorize privileged operations/publication.
