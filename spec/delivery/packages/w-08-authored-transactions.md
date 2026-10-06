---
type: "SysPane Work Package"
title: "Authored scene transactions and generation recovery"
description: "Implement coherent settings and scene replacement with explicit stored, durable and activation facts."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T15:45:00Z"}
sp_id: "SP-W08-AUTHORED"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-COMMANDS", "SP-PERSISTENCE", "SP-ACCEPTANCE-TRACES", "SP-CONFIG-RESOLUTION", "SP-W24-PACKAGE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Authored scene transactions and generation recovery

W-08 consumes the admitted foundation/transport components. Implement the common
authored-state validator and transaction coordinator in `source/configuration/`,
native generation storage in `source/platform/`, and finite native exercises in
`source/application/` and `tests/configuration/`. Existing preview IPC remains
unchanged until its asynchronous commit, cancellation and reconciliation integration
is independently admitted and tested in the subsequent
[command session package](w-08-command-sessions.md). This package does not declare a finished editor,
renderer, preset resolver, native settings application or complete W-08 gate.

## Shared boundary

Use command 0.2, settings 0.1, scene 0.2 and result 0.1. Validate the entire candidate
against their existing schemas and semantic rules. Compile the canonical schema
closure into the binary; unsupported future schema keywords fail generation. Runtime
validation never fetches URLs or loads mutable schemas. Preserve optional extensions.
Settings and scene form one immutable bundle with the same uint64 decimal revision.
Scene roots/children own each widget exactly once, all references exist, no cycles,
maximum depth 16. Layout breakpoints increase strictly, flow bounds are ordered and
container/leaf layout kinds agree. Selectors and pins retain authored meaning; saving
does not claim successful live binding or resolve a missing display by rewriting it.

One serialized coordinator owns a store, current policy checks and the ordinary
request ledger. Native authentication supplies principal and role grants. Only
console/desktop/saver_settings writers with available current policy may change
configuration. Scene replacement is denied for saver_settings. Check denied
`settings.preview`, `settings.commit`, `settings.set`, and `scene.replace` capabilities
as applicable; forced settings cannot be bypassed by a mixed scene transaction.
The controller checks policy generation and expected bundle revision before
preparation and immediately before publication. A preview writes nothing. One new
successful commit advances both document revisions exactly once, including an
otherwise identical candidate; duplicate request replay never advances them.
Maximum revision cannot wrap. No partial operation list is applied.

Command body bytes define replay identity, bounded to 16 KiB; retain existing
ledger counts, 10-minute expiry and 4 KiB result budget. Bound stored settings to
16 KiB and scene to 256 KiB with existing parser depth/node budgets. Reject unknown
operations, duplicate settings and more than one scene replacement. A prepared
candidate owns copies of its inputs, never caller-mutable references. Policy and
revision changes during preparation reject publication. Caller cancellation before
publication leaves the committed generation unchanged; cancellation after publication
is reconciliation, not undo. Storage failure before publication returns explicit
unsaved failure; ambiguous publication yields unknown facts and requires reopening
the store before further writes. Never acknowledge durability from a directory name.

Resource preparation is a mandatory owner-supplied callback before storage work.
The finite native experiment admits only its synthetic built-in `theme:native`
selection; no external theme/preset assets exist in that fixture. Installed resource
resolution, pinned asset closure and per-component activation are still required
before enabling product commits. A failing preparer leaves the old bundle selected.

The store returns a coherent bundle plus its committed request identity (native
principal, original producer epoch, request ID and exact bounded body). Reconciliation
requires that original scope and current authorization. It does not execute commands.
An expired ordinary result can be recovered from a retained committed identity;
missing identity is unknown. A changed body under a retained identity conflicts.
Current and previous committed identities remain available; older identities may
leave this bounded journal when neither selected record retains them. Orphan staging
directories are not a journal and never establish commitment by modification time.
Activation remains pending until a separate component reports activation; stored
or durable state never implies visibility. Recovery applies current policy before
external disclosure or activation and cannot restore revoked permissions.

## Linux storage experiment

Use only an explicitly provided owned private directory on the native Linux cache
filesystem, not a Windows-mounted checkout or installed user configuration. Hold a
nonblocking exclusive writer lock for the store lifetime. Open through directory
handles, reject symlinks, nonregular/multiply-linked files, foreign ownership and
group/other access. Native records use fixed internal filenames and generated names,
never document identifiers as filesystem paths. Bound generation attempts to 32;
capacity exhaustion fails without pruning any recoverable state. No automatic
cleanup is implemented in this first experiment.

The native adapter's `fstatfs` check identifies the ext filesystem family, not the
exact ext4 version or mount profile. The owning caller must admit that profile;
the independent runner additionally verifies an ext4 mount. No other filesystem
is qualified by the shared magic value. Manifests are bounded to 64 KiB, including
the escaped original command body; selecting records are at most 4 KiB.

Write immutable settings, scene and a manifest binding SHA-256 digests and request
identity; flush the files and generation directory. Preserve the verified current
selector as a separately flushed previous selector. Recheck authorization and
revision, then replace the current selector and flush its parent directory. Use
the documented Linux [fsync](https://man7.org/linux/man-pages/man2/fsync.2.html) and
[rename](https://man7.org/linux/man-pages/man2/rename.2.html) boundaries; runtime
acknowledgements do not qualify every filesystem or hardware power-loss behavior.
At startup validate the selected manifest and both documents; if corrupt, fall back
only to the separately verified previous selector with an explicit diagnostic.
Preserve corrupt/incomplete artifacts. If both are unusable, fail closed; do not
invent a fresh default or choose the newest directory. Bootstrap is an explicit
empty-store operation, not an automatic corruption repair.
Recovery from a corrupt selector/document remains read-only; a damaged previous
record also blocks subsequent publication, preserving the original corruption for
explicit repair. A valid current generation remains readable in that latter case.

Inject process interruption before/after each publication transition, including
after durable publication and before response. Recovery must select only coherent
old/new bundles. A media failure before publication retains the old selector;
failure after replacement cannot claim the old state is definitely selected.
The actual experiment records filesystem identity, source/artifact hashes and native
exit observations. Historical/Windows/Mac storage adapters remain separate work.

## Execution and completion

Use ordinary configure/build/test presets after workspace preflight. Shared cases
run on all three development toolsets with `ctest --preset <profile> -R
'^configuration[.]' --output-on-failure`. Bind schema/semantic, mixed atomic edits,
policy/revision conflicts, exact replay, revision exhaustion, cancellation and
storage/recovery cases to literal expected outcomes. Independently validate emitted
documents with the existing specification schemas. Native Linux cases run only on
the owned ext4 laboratory root and retain every failed attempt. A component-only
pass cannot complete the native storage or existing PERSIST wire-reconciliation
trace; record each remaining boundary explicitly in the handoff.

Private decomposition is delegated. Filesystem durability is experiment-dependent.
Supported OS floors, privileged policy installation, licenses and public release
remain reserved. No new instruction to operate a real-user desktop or VM is implied.
