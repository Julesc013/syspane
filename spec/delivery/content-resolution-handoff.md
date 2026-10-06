---
type: "SysPane Work Record"
title: "Pinned content and preset preview checkpoint"
description: "Verified content identities and immutable resource snapshots for common authored previews."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:00:00Z"}
sp_id: "SP-CONTENT-RESOLUTION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-CONTENT", "SP-TRANSACTION-SUPERVISION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Pinned content and preset preview checkpoint

Source baseline: `e349e782c210d48ddcc4cbfee47eadcf4e27a9a9`. Git history identifies
the resulting commit. The [package](packages/w-08-content-resolution.md) continues
W-08 with a content resolver in the existing authored component and one Linux
private-directory adapter. No duplicate settings engine or runtime schema fetch exists.

Selection pins both the root manifest and its preset document. Dependencies pin
manifest bytes; references pin entry bytes. All declared asset sizes/digests, paths,
schemas, identities and dependency bounds are checked. Resolution cannot borrow a
document outside its owning package's pinned closure. Required capabilities and
current policy govern preview admission; missing optional capabilities are explicit.

Parent settings compose in a fixed order, retaining each winning preset pin. The
selected leaf scene/theme and application theme inheritance produce one candidate
through prepare_authored. Original bytes retain their authored revisions. Shared
ownership keeps the admitted resource snapshot alive after the catalog is destroyed
or source files change. No storage or presentation success is claimed.

The Linux reader uses held directory handles, bounded no-follow opens and exact
private regular-file checks. It rejects symlinks, hardlinks, executable/special
files, undeclared entries, case aliases and path escapes. Native tests independently
compute hashes and compare complete candidate/command/provenance output. The snapshot
case edits an actual file after reading, checks the original plan, then verifies
that a fresh read refuses the changed digest.

## Evidence

Full suites pass 164 Linux, 148 contemporary Windows and 135 historical-toolset
checks on the modern host. All three runs match the final source, package, schema,
fixture and oracle inputs. The independent content oracle passes 17 native cases;
six portable content families pass on all three toolsets. Existing storage,
command, reconciliation and supervision cases also pass. Seventeen historical
executables pass the PE/header/import and pinned linker-input audit.

Specification/schema/generation/integrity checks pass; 56 tooling tests pass and
two existing Windows symlink assertions are skipped. These results do not qualify
historical native operating systems. Source archives, every build/test attempt,
native reports and artifact hashes are indexed in
`build-support/evidence/w-08-content-attempts.json`. The machine handoff is
`build-support/evidence/content-resolution-handoff.json`; specification checks
and staged-byte verification use the same evidence prefix.

## Remaining boundary

W-08 and all five complete release tracks remain open. Next persist the exact
prepared resource closure with generations and recover it coherently; then connect
native settings/direct editing and actual activation. Installed ownership/policy,
media decoding, archives, complete configuration layers/resets/updates, external
edits and non-Linux readers/storage/supervision remain required. Current preview
commands retain their 16 KiB ceiling. The current native generation store still
admits only its built-in resource fixture. Historical-toolset checks on the modern
host do not qualify historical operating systems.
