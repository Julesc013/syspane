---
type: "SysPane Specification"
title: "Build, release, servicing and deployment"
description: "Make releases reproducible, attributable and honest about support."
tags: ["assurance"]
status: "draft"
generated: {"by": "chatgpt/gpt-6-astra-pro", "at": "2026-09-17T22:05:25+10:00"}
sp_id: "SP-RELEASE"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-TESTING", "SP-SECURITY"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION", "SRC-REPRO", "SRC-AUDIT-2026-10-04", "SRC-READINESS-2026-10-05"]
sources: [{"id": "SRC-CONVERSATION", "resource": "Current conversation through the spec archive request on 2026-09-17", "title": "Current SysPane design conversation"}, {"id": "SRC-REPRO", "resource": "https://reproducible-builds.org/docs/definition/", "title": "Reproducible Builds definition"}]
updated: {"by": "codex", "at": "2026-10-05T19:48:29+11:00", "scope": "Implementation closure review; no native execution or human review attested"}
---

# Build, release, servicing and deployment

## Build identity

Record source commit/tree, generated inputs, compiler/SDK/runtime versions, dependency hashes/licenses, build flags, target architecture and enabled capabilities. Separate host build tools from target runtime. Cross-compilation is useful but does not establish target execution. Import/dependency audits and actual target runs are mandatory for compatibility claims.

CMake targets enforce internal boundaries. Checked-in presets contain reproducible settings, not personal absolute paths or credentials. Historical platforms may need a toolchain adapter or generated build description; they consume the same canonical source inventory. Build outputs remain ignored outside authored source.

## Packaging

Windows ships a portable native application set and an optional managed installer. macOS uses an application bundle; Linux distribution packages declare actual native library baselines. One user-facing application can contain helpers/resources. No mandatory browser engine, database service, Python, AIDE or online account runs on endpoints.

Stage enterprise binaries locally in protected directories. Keep organization policy, user preferences, history and runtime state in appropriate separate locations. Autostart is explicit. An elevated installer must not accidentally leave the ordinary UI running elevated. Upgrades preserve authored scenes/settings and offer tested rollback; uninstall does not silently destroy user data.

## Reproducibility and signatures

Reproduce the declared unsigned payload under recorded inputs. Signing, notarization and timestamping are separate authorized transformations with their own output hashes. Public rebuilders do not need private signing credentials. The Reproducible Builds definition applies to specified artifacts and build inputs, not an unsupported guarantee about external signatures.[^SRC-REPRO]

Provide SBOM, notices, release manifest and provenance using an admitted standard/version where applicable. A hash detects byte differences, not authorship; signatures establish attributable origin, not correctness. No moving published tags or rewriting published releases in place.

## Admission and maintenance

A stable release requires mandatory native profile tests, security and accessibility checks, resource/latency evidence, packaging/rollback tests and authorized publication. Unavailable lab capacity produces a blocked profile, not a fabricated pass. Release notes describe user-visible change and limitations; evidence lives in linked reports rather than dominating the product README.

Maintain vulnerability intake, supported-version policy, deprecation/migration windows and dependency monitoring. License choice and contribution/IP policy need an explicit owner decision before public code distribution; this archive does not fabricate a project license or Microsoft endorsement.

[^SRC-REPRO]: Reproducible Builds definition.

## Concrete delivery contracts

[Targets](../delivery/target-profiles.md) own exact build floors;
[artifacts](../delivery/artifacts.md) own binary names and package closure;
[USK binding](../setup/contract.md), [ownership](../setup/ownership.md) and
[lifecycle](../setup/lifecycle.md) own installation authority and recovery.
Portable and managed forms package the same identified payload, not divergent builds.
Native package managers keep ownership of their resources. Online acquisition has
a separate trust/expiry/rollback gate and stays disabled initially.

Before publication choose code/docs/assets licenses and contribution provenance,
audit redistribution/notices, establish security intake and supported-version/hotfix
ownership, and record signing/publication authority. No license or release consent
is inferred from the audit text or successful specification checks.

Each release needs the finite scope record defined by
[work-package closure](../delivery/work-packages.md#finite-release-closure).
Required profiles, capabilities, document versions, package forms and case bindings
must be concrete. A model/console smoke artifact cannot satisfy the first complete
desktop edition's native controls, editing, telemetry, persistence and recovery.
