---
type: "SysPane Work Package"
title: "Durable pinned resource generations"
description: "Bind command identity and generation recovery to the exact prepared content closure."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-06T18:20:00Z"}
sp_id: "SP-W08-RESOURCES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W08-CONTENT", "SP-W08-AUTHORED", "SP-W08-COMMAND-SESSIONS", "SP-PERSISTENCE"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Durable pinned resource generations

Continue W-08 in the existing authored coordinator, asynchronous worker, session
and Linux generation store. Preserve all command 0.2 and generation 0.1 semantics.
This package admits resource persistence and coherent recovery, not decoded media,
installed policy ownership or visible activation. Those remain required before release.

## Request and preparation

Command 0.3 retains the 0.2 envelope, operations and 16 KiB ceiling, adding required
`content: {package: <manifest pin>, preset: <document pin>}`. Both pins use the
existing id/version/sha256 shape. Raw request replay identity therefore includes
the exact selected closure. No filesystem path, URL or capability grant is accepted
from the command. Runtime content is supplied by a trusted immutable catalog owner.
Selection requires the additional `content.select` policy capability; existing
role, setting, scene and preview/commit checks still apply.

The common coordinator prepares the candidate through prepare_authored, resolves
the pinned closure, checks required capabilities against the trusted adapter set
and current policy, and keeps an immutable resource snapshot. Scene/theme selection
is evaluated from the candidate: explicit scene theme, otherwise application theme.
The selected preset's non-null theme pin disambiguates that same identity only;
it does not overwrite an authored edit. Missing or ambiguous themes fail. All
parent references and package closure checks from SP-W08-CONTENT still apply.
Preset identity records the immutable base; authored scene/settings may be edited
derivatives and need not equal the original preset materialization.

Before selecting the generation, recheck the current policy, required resource
capabilities, document revision and cancellation, then obtain the existing commit
permit. No media or capability is activated by persistence. Same request identity
with changed content pins conflicts; committed replay/reconciliation returns the
original revision without rereading an external package directory.

Legacy resource-free stores retain command 0.2. Resource-bearing generations require
0.3 for subsequent edits, including unchanged content selection. A 0.2 command must
not silently discard a recovered closure. A coordinator without a resource provider
refuses new 0.3 work. Read-only receipt recovery remains possible. Policy revocation
does not corrupt a generation: recovery verifies bytes without authorizing their use.

Session advertisement of command 0.3 and `configuration.content` requires a resource
provider. The feature also requires command-result 0.1 and configuration.transactions,
with the existing 8192-byte frame floor. An unnegotiated document version/content
feature returns a bounded unsupported result before admission. Existing 0.2 clients
remain valid; content is never inferred from inert extensions.

## Generation format and native sequence

Resource-free generation manifests retain version 0.1. Resource-bearing manifests
use 0.2 with the existing revision/settings/scene/identity fields plus `resources`,
the SHA256 of `resources.json`. The selecting record remains version 0.1 and binds
the entire manifest. `resources.json` is at most 64 KiB, with exactly:

- `version: "0.1.0"`;
- `selection`: the command's content object;
- `theme`: the selected theme document pin;
- `packages`: sorted unique manifest SHA256 strings, one per closure package.

Each generation owns a private `resources/` directory. Original manifests are
`m-<sha256>.json`; original assets are `a-<sha256>.bin`. Logical paths remain in
the original manifests. Equal bytes share a file within that generation only;
no hardlinks, cross-generation lookup or global cache is required for recovery.
Retain exact whitespace and bytes. The existing content limits apply before writes:
64 packages, 1024 declared assets, 64 MiB aggregate declared payload and individual
manifest/asset/JSON bounds. The existing 32-generation ceiling remains unchanged.

Write and fsync every resource file, the resource index and resource directory
before the generation manifest/parent flush and selecting-record replacement.
Reopen and verify the complete staged generation before publication. Recovery
checks canonical names, exact file set, hashes, size totals, schemas, pinned closure,
theme binding and command/selection identity. It never repairs from the original
import paths. A corrupt current resource selects only a complete previous generation
and leaves the store read-only under the existing recovery rule. No mixed generation
or newest-directory guess is allowed; original corruption and orphan staging survive.

## Acceptance and handoff

Portable tests cover exact selected pins, retained resources, changed-pin replay,
unsupported legacy/provider paths, policy recheck and 0.3 negotiation. Native tests
independently hash stored manifests/assets, delete or alter original import inputs,
recover exact revisions/resources, and inject process interruption during resource
and selecting-record transitions. Test corruption, missing/extra/linked resources,
complete-previous fallback, same-ID replay and current-policy refusal. Activation
remains pending and visible remains false. Keep ordinary commands and source-bound
evidence on all three profiles; historical-toolset host checks do not qualify old OSes.
