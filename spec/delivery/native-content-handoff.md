---
type: "SysPane Work Record"
title: "Supervised native content checkpoint"
description: "Retained resource editing through authenticated commands and exact controller replacement."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:53:49Z"}
sp_id: "SP-NATIVE-CONTENT-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-NATIVE-CONTENT", "SP-RESOURCE-GENERATIONS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Supervised native content checkpoint

Source baseline: `c65f595ebdae812b957a9a0fb9c357371e286805`. Git history identifies
the resulting commit. The [package](packages/w-08-native-content.md) continues W-08
through the existing transaction worker, native generation store and supervisor.

The common provider loads the current committed selection for every preparation.
An exact match uses only that generation's original packages. Another selection
uses only the configured import loader; dependencies are never borrowed across
catalogs and invalid retained candidates never fall back to imports. New edits
therefore survive loss of the original import directory and controller restart.
Current policy/capabilities, read-only recovery and the commit permit remain intact.

The finite Linux command fixture accepts one explicit private catalog root, or
retained-only mode. Catalog 0.1 lists bounded package child names and grants no
authority. The existing no-follow reader checks private file ownership, bounds,
declared assets and pins. Reads, hashing and closure validation run on the worker.
The same supervised 5000 ms deadline covers preparation and resource publication.

Independent clients negotiate command 0.3, validate actual peer identity and wire
results, and compare original resource bytes in committed generations. Held worker
cases cover preparation, cancellation, the first resource manifest and durable
publication. Replacement requires exact process exit; reconciliation reports the
original outcome without repeating the mutation. Further commits use recovered
content with imports absent. Policy and malformed catalog/negotiation refusals
leave the generation unchanged. Activation stays pending and visibility unproven.

## Evidence

Full suites pass 170 Linux, 152 contemporary Windows and 139 historical-toolset
entries on the modern Windows host. Final implementation/package/schema/fixture/
oracle inputs match all three full runs. The new independent native family has
nine cases; the existing resource, content, storage, command, reconciliation and
supervision families remain passing. Seventeen historical executables pass the
PE/header/import and actual linker-input audit. Specification checks and 56 tooling
tests pass, with two existing Windows symlink skips. This does not qualify execution
on a historical OS.

Evidence is indexed in `out/evidence/w-08-native-content-attempts.json`;
the machine handoff is `out/evidence/native-content-handoff.json`.
The initial native oracle syntax failure is preserved with its exact source archive;
the correction separates function definitions without changing expected behavior.
The next attempt exposed an overly narrow oracle for external SIGKILL observation:
the health pipe may report EOF before the child poll reports exit. Both existing
fault paths require quarantine, exact SIGKILL exit proof and a fresh replacement.
The corrected oracle admits those two observation orders and explicitly verifies
the signal in the reaped record; the failed original expectation is preserved.
An additional oracle correction follows the existing W-08 reconciliation contract:
current policy conceals a stored receipt as unknown/policy.denied with null facts,
whereas a new denied mutation returns denied. The failed expectation is retained.
Verified duplicate cached attempt archives were reclaimed only after matching
their unchanged committed counterparts. The audit retains every path and digest.

## Remaining boundary

W-08 and all five complete release tracks remain open. Next close installed
store/controller/policy ownership, admitted media preparation, native settings and
editing, and actual activation/recovery. Archive import, full configuration layers,
reset/update behavior and non-Linux storage/supervision remain required. This is an
owned Linux IPC/ext4 experiment, without power-cut, installed product or full native
desktop release qualification.
