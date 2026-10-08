---
type: "SysPane Work Package"
title: "Initial profile and policy-bound native store"
description: "Shipped default content, atomic first generation and existing transaction composition."
tags: ["delivery", "setup", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T04:00:00+11:00"}
sp_id: "SP-W08-PROFILE-STARTUP"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-PROFILE-OWNER", "SP-W08-RESOURCES", "SP-POLICY", "SP-CONFIG-RESOLUTION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Initial profile and policy-bound native store

Connect the existing Linux profile and generation owners to shipped initial content
and the protected policy adapter. Keep the existing transactions/resource provider;
do not create another settings engine. This worker-side component is a prerequisite
for the installed supervisor/controller, not a desktop launcher or release claim.

## Shipped initial content

configuration/defaults/profile.json owns the initial scene and theme. Compile these
bytes into the shared authored component through a generated private header. Runtime
startup reads no build/test fixtures or cwd-relative product files. Settings come
from the existing generated descriptor defaults, with both document revisions zero.
The initial scene uses a primary-display group containing one network table: current
receive/transmit counters and rates, collection selectors limited to eight. This is
an editable starting scene, not a limit on providers, widgets or required editions.

Use theme:native, scene:default, preset:default and package IDs
package:syspane-default-theme, package:syspane-default-scene and
package:syspane-default-preset, version 0.1.0. Canonical sorted compact JSON without
LF supplies each asset and manifest. Theme and scene packages have no dependencies;
the preset depends on the theme then scene pins, selects the scene, inherits the
settings theme and has no setting overrides or parent. Each package contains one
JSON asset named for its kind, with exact bytes/digest/total length. Scene requires
scene.content; the other packages add no capabilities. License metadata is
LicenseRef-SysPane-Pending: it records the existing unresolved licensing decision,
not redistribution permission. Native system fonts are referenced, never bundled.

The immutable initial ResourceSet is resolved through ContentCatalog. Require
available policy and current capabilities; reject profile.open/profile.create,
settings.commit, scene.replace or preset.apply denials when creating it. Apply only
valid known forced settings to the initial requested defaults, then validate the
whole authored state and resource binding. Unsupported forced themes refuse; do
not silently pick another theme. Existing saved documents are never reseeded or
rewritten for a policy/default update. Full effective-layer provenance remains the
existing configuration-resolution work, not an implicit rewrite of saved overrides.

## Resource bootstrap generation 0.5

Add an explicit native bootstrap entry point requiring an empty generation owner,
revision zero, null request identity, an admitted ResourceSet and a current guard.
Its private manifest is version 0.5.0 with exactly the existing resource-manifest
fields: version, revision, settings, scene, identity, resources. Revision must be
"0", identity null, resources present, resource index 0.1, no request.json and no
theme override. Preserve every earlier manifest's meaning and validation. An
ordinary resource commit still requires its real authenticated request identity;
bootstrap is never a fabricated command, request result or extra revision.

Use existing private files, immutable resource hashes, flushes, selector publication
and generation_token. No new file-writing recipe or reset path. The new bootstrap
method checks the guard before writing and at selector publication. Later commands
use their existing formats, normal revision increment and receipt/reconciliation.
Read-only previous-generation recovery remains read-only.

## Publish the initialized profile atomically

Extend LinuxProfileOwner with an optional trusted initial-profile factory. Invoke
it only for a missing configuration leaf, after authority and before stage creation;
never invoke it for existing roots or for content/state. The factory returns the
typed immutable bootstrap value, not paths or permission. Default callers retain
the earlier empty-child contract exactly.

Inside the configuration leaf's private stage, initialize generations through the
real generation owner before flushing the child. Forward diagnostic transitions as
configuration.initial.PHASE. A fresh native reopen must match initial authored bytes,
selection, theme pin and all package manifest digests before the profile leaf is
published, with current authority and exact directory identity/permissions. Repeat
this validation after a held publish_ready transition. An initialized child may be
nonempty only through this factory; ordinary callers still require it empty.

After a process interruption, configuration is either absent (all partial/complete
seed bytes remain in an ignored orphan stage) or a complete revision-zero store.
A fresh owner can create a new stage or reuse the published root. Existing orphan
limits apply; no abandoned bytes are deleted. A cut after configuration publication
but before other roles finish can be resumed without another initial generation.
This covers process interruption, not hardware power loss or arbitrary filesystem
qualification. No profile is returned until all three roots are locked/verified.

## Composed LinuxProfileStore

Expose a GenerationStore implementation that owns LinuxProfileOwner followed by
LinuxGenerationStore; release generation ownership before profile locks. Select the
native machine_policy source by default. A trusted in-process PolicySource can be
injected for deterministic component tests; no product CLI/environment/file override
is introduced. Positive protected-policy deployment still needs its admitted lab.

Bind one effective policy snapshot at construction: availability, revision, forced
settings, denied capabilities and disclosure rules. A missing, throwing, unavailable
or changed snapshot invalidates the owner before further disclosure/publication.
Compare all fields, so a same-revision semantic change cannot preserve authority.
Regrant requires a fresh owner. The current native source must be checked at each
profile verification and commit guard. profile.open denial refuses both new and
existing stores; profile.create denial affects only creation. Existing documents
require their current resource capabilities. Client command permissions and forced
values continue through Transactions; raw load is for the trusted controller only,
not an external projection or proof of activation.

Guard load, generation identity, receipts, reconciliation and publication with the
current policy/profile. Retained-result reconciliation is still independently
authorized by Transactions. Support its synchronous readback during a publication
guard while rejecting recursive publication and policy-source reentry. One worker
thread owns all operations; no native I/O runs in GTK. Filesystem latency/stop/reap
must be supervised before installed use. Never claim an acknowledged scene is active
merely because its store is durable.

An existing marked but uninitialized/corrupt/resource-less configuration is an error;
never seed it as a fresh profile. Missing current with coherent previous remains
read-only recovery. Unknown publication poisons the native owner; a fresh open must
verify it. Current policy denial restricts access and does not delete retained data.

## Fixed verification

Freeze this package, the literal default scene/theme and independent expected
settings/pins/commands before production edits. Portable checks on all three profiles
compare exact initial packages/selection, policy constraints and capability refusal.
The native oracle observes paths/files separately, opens default native policy in
the actual environment, and uses a separate test entry point for injected policy.
Never infer protected provenance from those positive fixture cases.

Cover cold startup/reopen with no reseed, revision-zero resources/no receipt, ordinary
edit to revision one and restart reconciliation, all initial generation/resource
process cuts, policy changes during initialization/publication, changed same-revision
policy, unavailable/regranted policy, saved-data preservation, unsupported capabilities,
existing empty/foreign/corrupt stores and read-only previous recovery. Verify staged
resource substitution cannot publish altered initial content. Preserve failed runs
and deliberate wrong-byte/old-manifest oracle controls.

Use ordinary budget preflight/configure/build; run configuration.INITIAL-PROFILE on
all profiles, native.PROFILE-STARTUP and native.PROFILE-OWNER on Linux, existing
CONFIG-STORE/RESOURCE-GENERATIONS/CONTENT-COMMANDS and recovery-store regressions,
and all component graphs. Record exact source/artifact/environment identities and
next installed-supervisor integration in W-08 without another scheduler. All five
complete editions, full layers/updates, protected-policy positive qualification,
native lifecycle and public release authority remain required.
