---
type: "SysPane Work Package"
title: "Supervised native content commands"
description: "Connect retained resource preparation to authenticated native commands and exact controller replacement."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:40:00Z"}
sp_id: "SP-W08-NATIVE-CONTENT"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-RESOURCES", "SP-W08-SUPERVISION", "SP-W08-COMMAND-SESSIONS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised native content commands

Continue W-08 by composing the existing resource provider, asynchronous coordinator,
native generation store, authenticated session and independent supervisor. Preserve
command 0.3, resource generation 0.2 and transaction-watch identities. This package
does not establish installed endpoint/policy ownership, media decoding or activation.

## Resource provenance and owner lifetime

The common resource provider borrows the generation owner and runs only on its one
transaction worker. For a selection exactly equal to the current committed selection,
derive the candidate's resource snapshot solely from that generation's retained
original packages. Never reread imports, combine different catalogs or fall back to
imports when a retained candidate fails validation. An edited scene may choose a
different theme already available in the retained closure; existing identity and
ambiguity rules still apply. Selection equality includes both complete pins.

For every other selection, invoke the trusted configured import loader once for that
preparation and resolve only its returned catalog. Missing dependencies cannot be
borrowed from the active generation. A missing loader gives resource.unavailable.
Malformed, changed or unavailable imports leave the committed state intact. The
provider neither repairs a corrupt store nor bypasses read-only previous recovery.

Load the current generation at each preparation, so a successfully committed new
selection becomes the source for subsequent edits. Retained replay/reconciliation
does not invoke resource preparation. Import I/O, hashing and closure construction
stay outside the IPC owner loop. Snapshot bytes survive later input-path changes.
Current policy/capability checks and the existing commit permit remain mandatory.

## Configured native catalog

The Linux development composition accepts one explicit private catalog root, or
`-` for retained resources only. The root's `catalog.json` follows content-catalog
0.1: schema_version and one to 64 unique package directory basenames. Names use
ASCII letters/digits/underscore/hyphen, start with a letter/digit and are at most
64 bytes; ASCII case aliases are refused. No path separators, parent traversal,
absolute path, URL, capability grant or client-chosen discovery root is admitted.

Read the at-most-16-KiB catalog through the existing private no-follow directory
adapter. Its listed child directories use the same bounded package reader and
existing manifest/dependency pins. Unlisted root entries confer no content access;
package directories still reject undeclared assets. Discovery supplies candidate
bytes, not policy authority. Do not preload imports before serving the health link.

The finite CommandProbe gains a `content <root-or-dash>` prefix for its existing
direct and supervisor forms. The prefix is forwarded unchanged to each exact owned
replacement child, within the existing Child argument budget. The content mode
installs the common resource provider and negotiates command 0.3 plus
configuration.content. Existing non-content modes remain unchanged. Typed laboratory
permission and scene.selector capability remain explicit and are not installed policy.

## Failures and acceptance

Resource preparation and publication consume the same absolute 5000 ms supervised
transaction deadline. Health traffic cannot extend it. Add one finite hang after
the first resource manifest write; do not introduce another recovery owner or retry
budget. Replacement requires confirmed exact child exit, a fresh epoch/endpoint
and coherent store reopening. Uncertain original requests are reconciled, never
automatically replayed. Current complete closure enables new edits after restart
even when imports are absent. Pre-publication hangs leave the old generation;
post-durable hangs recover the new generation. Activation remains pending.

Portable checks cover retained edits, adoption of a committed selection, unavailable
imports, nonmatching selection, no catalog merging/fallback and existing policy
guards. Native independent cases cover actual command 0.3 negotiation, responsive
heartbeats while a worker is held, cancellation without fake stop, preparation/
resource-write/durable hangs, replacement after pidfd exit proof, original-epoch
reconciliation and further commits using recovered original bytes. Compare stored
files and resource hashes independently. Test policy and catalog/negotiation refusal.
Keep the complete release scope and all independently blocked platform tracks open.

## Execution and completion

Source ownership stays in source/configuration (shared provider), source/platform
(private Linux catalog reader) and source/application (finite native composition).
Tests stay in tests/configuration. No new installed executable is introduced.
Run the ordinary workspace preflight, `cmake --preset <profile>`, `cmake --build
--preset <profile>` and `ctest --preset <profile> --output-on-failure` on the admitted
linux-x64-gcc13, windows-x64-gcc15 and windows-x86-v141-xp development profiles.
Use the declared Linux cache root and non-root laboratory identity. The portable
RESOURCE-RETAINED case runs on all three; native.CONTENT-COMMANDS runs only on Linux.

Completion requires passing source-bound full suites, the existing historical
artifact audit, specification/schema/integrity checks and preserved original
failures. Record the native report, command/store executable hashes, oracle hash,
exact source archive and observed exit/replacement order. Missing native product
qualification remains not_run; these development results do not finish W-08.
