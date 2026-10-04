---
type: "SysPane Specification"
title: "Change control, compatibility and evidence reuse"
description: "Make safe refactoring inexpensive without hiding semantic changes."
tags: ["governance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-CHANGES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-TESTING", "SP-AUTHORITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-SEMVER", "SRC-AUDIT-2026-10-04"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-SEMVER", "resource": "https://semver.org/spec/v2.0.0.html", "title": "Semantic Versioning 2.0.0"}]
updated: {"by": "codex", "at": "2026-10-04T19:32:52+11:00", "scope": "October audit amendments; no human review attested"}
---

# Change control, compatibility and evidence reuse

## Change classification

Classify edits as editorial, internal implementation, observable behaviour, contract, architecture/security boundary, platform qualification or release. Classification drives review/evidence, not the number of changed lines. A one-line threshold or pipe ACL change may matter more than a large formatting change.

Requirements retain stable IDs. Replacement creates a supersession record; do not silently reuse an old ID for a different promise. A semantic change updates the requirement, owning spec, contract/fixtures, tests, work plan and relevant docs map in one review scope. Generated traceability detects references, not meaning.

## Refactoring

Move by responsibility with stable interfaces and focused tests. Keep one `source/` implementation tree and remove actual duplication rather than creating compatibility forks. Public API/schema changes require migration and backward/forward compatibility decisions. Do not freeze all experimental interfaces merely to avoid future work.

The product version and public contract versions are separate where obligations differ. Semantic Versioning applies only after the public surface is declared.[^SRC-SEMVER] Experimental 0.x contracts still document breaking changes; “experimental” is not permission to discard user data silently.

## Evidence reuse

An evidence key includes the relevant source/dependencies, test/oracle, toolchain, policy, configuration and environment. Reuse when all relevant dependencies match or an explicit reviewed impact analysis establishes equivalence. Preserve the original result/ref and reuse justification. Never edit old evidence to pretend it ran on the new candidate.

Before release, qualify the exact integrated package for mandatory profiles. Dependency-aware reuse reduces redundant work but does not remove final package checks or security admission. A report of candidate tests is not an authoritative scheduler.

## Integration

Use short-lived bounded task branches/worktrees with ownership and cleanup. `main` holds admitted coherent state; an integration branch such as `dev` may aggregate reviewed work if adopted by the repository policy. Do not prescribe dozens of long-lived platform branches. Publication/tag rights remain explicit.

## Learning without drift

Record rejected alternatives, failed experiments and rationale in concise decision/evidence records. Search them before restarting a known failed path. A changed environment can justify reopening a decision; record the changed assumptions rather than pretending the earlier work never happened.

[^SRC-SEMVER]: Semantic Versioning 2.0.0.

## October version and evidence policy

[Version policy](../contracts/versions.md) separates bundle, document, protocol, ABI,
content, target and provider versions. Preserve 0.1 scene/command fixtures and use
copy-on-migrate previews for 0.2. This update does not freeze the SDK, attest human
review or transfer native results. Changed core/host/renderer/oracle dependencies
invalidate corresponding evidence; unrelated prose changes do not trigger every lab.
