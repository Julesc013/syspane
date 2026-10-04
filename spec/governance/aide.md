---
type: "SysPane Specification"
title: "AIDE consumer integration and authority"
description: "Use AIDE as the development control plane without coupling the product to a particular model."
tags: ["governance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-AIDE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-AUTHORITY", "SP-TESTING"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-AIDE", "SRC-GIT", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-AIDE", "resource": "https://github.com/Julesc013/aide/blob/aec53b1d3675f02e2fdd17cc718fdcff6cd4e9f3/README.md", "title": "AIDE README and OKF decision"}, {"id": "SRC-GIT", "resource": "https://git-scm.com/docs/git-worktree", "title": "Git worktree documentation"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# AIDE consumer integration and authority

## Verified starting point

The inspected AIDE main-branch README and OKF decision at `aec53b1d3675f02e2fdd17cc718fdcff6cd4e9f3` describe implemented-for-review protocol slices and a knowledge projection while separating many later runtime capabilities.[^SRC-AIDE] This is not an empty two-line repository, and it is not evidence that every future service, worktree, test-broker or publication feature has already been executed.

SysPane is a consumer of the future overhauled AIDE. Its native application does not link to AIDE or require models, Python or orchestration services. The ordinary build/test commands are canonical; AIDE invokes them rather than creating agent-only alternatives.

## Migration stages

Stage 0: this portable spec bundle, JSON work plan and local validation work without AIDE. Stage 1: inspect and pin the actual AIDE contract/version and implement a consumer adapter with round-trip tests. Stage 2: admit work/execution/evidence and context workflows using actual validated schemas. Stage 3: delegate integration/release operations only under explicit scoped policy.

`governance/aide-binding.proposed.json` is a **SysPane intent record**, not an upstream AIDE schema and not an active grant. Migration preserves stable IDs, source refs and evidence links. Once AIDE owns live execution, this work-plan JSON remains an immutable campaign baseline; generated knowledge views replace hand-maintained duplicate queues.

## Independent authority axes

Record the authorized root model/effort, allowed descendants, spend/retry limits, file scope, execution/network/credential privileges, lab leases, integration rights and publication rights separately. Model choice is not execution privilege. Availability of a stronger paid provider is not permission to use it. A downgrade that compromises expected capability is surfaced rather than hidden.

After a bounded work unit is admitted, routine reversible edits, local builds/tests and task-local commits proceed without repeated permission prompts. Security-boundary changes, protected refs, hardware-disruptive tests, signing and deployment require corresponding grants. Do not use the word autonomous to imply unlimited authority.

## Evidence and recovery

Work units produce attempt records, tested artifacts, failures, blocked resources and a handoff. Cache evidence by relevant source/dependency/toolchain/policy/oracle/environment hashes. Reuse unaffected results conservatively; do not re-run the whole lab for a typo, and do not reuse shell evidence after a relevant OS/driver/renderer change.

Keep credentials outside workers, use actual sandboxes, and lease test machines. A worktree organizes files but shares repository state.[^SRC-GIT] Disruptive tests require recovery independent of the interface under test. Record cancellation and timeout limitations of the actual provider; an API field called cancel is not proof it terminates work.

## Upstream boundaries

Destination contribution/license/AI-provenance rules are checked before submission. A grant to develop SysPane does not authorize hiding model use or submitting to an upstream that disallows that contribution. No claimed Microsoft adoption or certification is created by these standards.

[^SRC-AIDE]: Pinned AIDE README and OKF knowledge-plane decision, inspected during preparation.
[^SRC-GIT]: Git worktree documentation.

## October source checkpoint

The supplied reviews cite AIDE README at
`3d186d0584bb40f18402a626c9fe099260fae3d4` as a newer foundations checkpoint.
That is attributed review input, not a locally verified consumer binding. Preserve
the existing inspected-ref record and inactive grants; inspect actual selected
upstream schemas/provider interfaces and test mappings before replacing the pin.
No two-line-skeleton characterization is current here. Track workspace roots, quotas,
model/budget and integration/publication authority independently when binding.
