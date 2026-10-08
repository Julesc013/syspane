---
type: "SysPane Work Record"
title: "Durable resource generation checkpoint"
description: "Exact content closure, command identity and coherent Linux recovery."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:20:00Z"}
sp_id: "SP-RESOURCE-GENERATIONS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-RESOURCES", "SP-CONTENT-RESOLUTION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Durable resource generation checkpoint

Source baseline: `cf82416bd0aeb3595bf24f4436cc1672580a5806`. Git history identifies
the resulting commit. The [package](packages/w-08-resource-generations.md) continues
W-08 through the same transaction, asynchronous worker and native generation owner.

Command 0.3 names exact package/preset pins. Immutable resource preparation retains
the complete closure and selected theme, checks current capability/policy constraints
and binds that selection to durable request identity. The final commit permit
rechecks current policy; a legacy command cannot discard a recovered closure.
An opt-in session feature requires the document version and resource provider.

Linux generation manifests version 0.2 bind an index of original manifests and
assets. Files belong to each generation and are flushed before selecting it.
Recovery validates the complete index, file set, bytes, closure and request identity;
it does not revisit import paths or combine resources from different generations.
Corrupt current resources fall back only to a complete previous generation and
leave the original failure and read-only recovery boundary intact.

The independent native oracle removes original import paths after commit, compares
exact bytes and revisions, and tests process interruption at resource and selection
transitions. It also tests corrupt, missing, extra, hardlinked and symlinked files,
changed index/identity bindings and legacy downgrade refusal. Stored/durable facts
remain separate from pending activation and unproven visibility.

## Evidence

Full suites pass 168 Linux, 151 contemporary Windows and 138 historical-toolset
checks on the modern Windows host. All three runs match final implementation,
package, schema, fixture and oracle inputs. The native resource-generation oracle
passes 31 cases, including 20 independently stopped process transitions. Existing
content, storage, command, reconciliation and supervision cases also pass. Seventeen
historical executables pass the PE/header/import and actual linker-input audit.
Specification/schema/generation/integrity checks pass; 56 tooling tests pass with
two existing Windows symlink skips. Historical native OS behavior is not qualified.

Validation is indexed in `out/evidence/w-08-resources-attempts.json`;
the machine handoff is `out/evidence/resource-generations-handoff.json`.
Source archives, native reports, artifact hashes, failures and staged-byte identity
are retained with this checkpoint.
The initial build failure from two misleadingly indented test-helper returns is
preserved; the fix changes formatting and does not weaken an oracle.
The initial schema-identity registration omission and missing import in the expanded
tooling regression are also preserved alongside the corrected passing checks.

## Remaining boundary

All five release tracks and W-08 remain open. Next compose the resource provider
with the installed/supervised controller and native settings/editor, close media
decoding and activate/recover actual presentation under current policy. Full
configuration layers/resets/updates, archives, non-Linux resource storage and
historical native OS qualification remain required. This checkpoint is a finite
owned Linux ext4 experiment, not power-loss or complete product qualification.
