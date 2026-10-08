---
type: "SysPane Work Record"
title: "Visibility authoring and durable admission checkpoint"
description: "Versioned scenes and commands with protected history, coherent recovery and an explicit native rendering gate."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T23:31:04.147035+00:00"}
sp_id: "SP-VISIBILITY-ADMISSION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-VISIBILITY-ADMISSION", "SP-VISIBILITY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Visibility authoring and durable admission checkpoint

Source baseline: `40f9e0fba3e223bb40d882bb199a3b4a6285f302`. The
[package](packages/w-10-visibility-admission.md), new scene/command schemas, exact
authored/expected scenes and positive/negative fixtures were frozen before production
changes. Old schemas and fixture bytes remain unchanged. The fixture catalog only
appends examples.

## Implemented boundary

Scene 0.5 admits optional visibility 0.1 rules on every widget kind. The shared
editor validates protected edits atomically, preserves exact selection/history and
version, rejects conditional-parent ungrouping/unwrapping, and retains rules across
other edits. Policy/capability checks cover removal, no-op and history travel. The
resource closure names visibility and locks even when all own fields are absent.

Command 0.7 requires the existing transaction/content/scene-content/large/edit-lock
dependencies plus visibility. Unsupported negotiation cannot publish a request.
The 327680-byte original body uses the existing ledger and manifest 0.3/request.json
recovery. SceneSurface explicitly returns alternative/surface.visibility_unavailable
with no frame/cache, including when authored capabilities are present. Policy denial
retains priority. This gate prevents unimplemented condition composition from showing
unconditional content.

## Executed evidence

All 59 affected checks pass on each development profile. Full non-native suites pass
325 Linux GCC13, 322 Windows GCC15 and 319 v141_xp checks (966 total). Development
execution with v141_xp does not establish XP or historical OS qualification.

Native VISIBILITY-ADMISSION passes nine owned ext4 scenarios: exact commit/replay/
reconciliation, stopped-and-killed processes at four publication stages, policy
revocation, explicit permission denial and corrupt request/scene fallback. Recovery
returns coherent revision 40 before publication and 41 after publication. Lost
acknowledgement and exact replay never create revision 42. The reader independently
checks original request bytes, selecting/manifest hashes, documents and resource
closure. This is process-crash evidence, not hardware power-loss qualification.

Six native storage/resource/IPC regressions pass, as do SCENE-SURFACE (including the
new refusal gate), SCENE-INSPECTOR-MODEL, EDITOR-LOCKS and EDITOR-CONTAINERS. Conditional
native pixels and condition dialogs remain unimplemented and unqualified.

Original failed attempts remain preserved: the first configure referenced the output
filename instead of the CMake target; an added layout-preservation test omitted its
required measurement map. The corrections register the existing target and supply
explicit metrics, with frozen authored and expected documents unchanged.
The native null/pending regression also detected an accidental encoding change to
the existing em dash placeholder during source editing. Its original UTF-8 bytes
were restored; the existing exact text expectation is unchanged. Documentation
editing now specifies UTF-8 explicitly. Earlier native runs retain their actual
source and artifact identities instead of being attributed to the final build.
The first specification validation rejected command 0.7 because its schema-identity
allowlist still stopped at 0.6. The allowlist now includes the new version; the
failed output and exact earlier validator are preserved alongside the final checks.

Records: out/evidence/w-10-visibility-admission-attempts.json,
w-10-visibility-admission-native-index.json, w-10-visibility-admission-verification.json,
w-10-visibility-admission-staging.json and visibility-admission-handoff.json. They
bind commands, exact source archives, failed attempts, fixtures and final artifacts.
Nine duplicate native folders were verified against the baseline commit before
344,143,433 file bytes were reclaimed. Another 24 raw attempt folders were verified
against their committed archives before reclaiming 40,148,646 bytes. The 7 GiB
workspace maximum is unchanged.

## Required continuation

Implement native conditional composition and private editor controls from the
existing visibility contract. Freeze expected group inheritance, retained layout
space, unresolved diagnostics, mandatory status, pixels, accessibility and policy
erasure before enabling that capability. Preserve the stored-rule recovery path.
W-09/W-10, typography, clipboard/recovery drafts, installed ownership, remaining
adapters/laboratories and all five complete release editions remain open. Historical
accessibility timeout causes remain unresolved. No release publication or privileged
operation is included in this checkpoint.
