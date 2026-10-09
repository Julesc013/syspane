---
type: "SysPane Work Package"
title: "Current draft admission and preview resource ownership"
description: "Remove repeated reconstruction of owned draft state while retaining current authorization and full mutation validation."
tags: ["delivery", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-09T05:04:13.9612684Z"}
sp_id: "SP-W11-DRAFT-ADMISSION"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-RECOVERY-HOTPATHS", "SP-W11-RECOVERY-GUI-LIMITS"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Current draft admission and preview resource ownership

W-11's fixed maximum-input GUI qualification remains failing. Measure clipboard
availability and submit eligibility separately from preview preparation on the same
maximum scenes before changing production code. Diagnostic completion is not a
latency pass. Preserve the preceding source, artifacts and measured outcomes.

## Owned current state

SettingsDraft owns its authored base/current documents and immutable resource
snapshots. Construction/reload, settings changes, scene edits, history travel and
recovery preparation validate new documents and their resource bindings before
adoption. Accepted results only advance the matched revision coherently. No caller
can supply a mutable alias to the owned documents or ResourceSet package bytes.

The first measurement shows immediate clipboard refusal on this recovery profile;
clipboard is not the measured bottleneck and keeps its original implementation.
Repeated may_submit calls rebuild and structurally validate the same command.
SettingsDraft may retain at most two optional booleans: structural acceptance of
its internally built draft.check command for preview and commit. Cache no document,
command bytes, authority or policy result. The first call still performs the full
original validation, including its exact serialized envelope limit. A structural
rejection may be retained; an authorization rejection must never be retained.

Discard both results at entry to every operation that may change base/current
documents, resources, context, revision, policy or transaction state, including
failed attempts: set, revert, scene adoption, begin, finish/reconciliation,
cancel/disconnect, policy, reload, erase/close. Candidate preparation that changes
no owned state may retain them, including rejected edits. Copies start with empty results;
detached recovery work cannot transfer them. Selection-only changes leave the
authored state unchanged. Invalid intent and unavailable/pending/conflict/clean
guards still run before cache access. Construct the current command and perform
current role/grant, policy generation, operation, forced-setting and resource
authorization on every eligible call. No externally supplied cache key or proof.

All mutations, incoming clipboard, recovery preparation and actual begin/submission
retain full validation independently of these UI eligibility hints. No retained
true result authorizes a submission. Valid-to-oversized-to-valid undo/redo, policy
denial/regrant and accepted/rejected requests must not leave stale eligibility.

## Preview resource ownership

EditorDraft may return an owning shared pointer to its existing immutable resource
snapshot, or null when unavailable. It conveys lifetime only, not permission or a
validated binding to arbitrary authored documents. EditorForm transfers that owner
to its existing SceneSurface with the same current authored values. SceneSurface
still fully validates the supplied authored/resource binding, layout and native
text backend, and checks current policy before disclosure.

Do not reconstruct an equivalent ContentCatalog and ResourceSet solely for that
transfer. Resource changes, history, reload and accepted revisions select the
draft's actual current snapshot. Replaced surfaces release their prior ownership;
policy/disclosure withdrawal and close retain existing clearing and retirement.
No global cache, retained authorization, new thread, timer, scheduler or relaxed
history/resource budget is admitted.

## Fixed verification

Before production changes, extend existing portable fragment cases with explicit
availability outcomes across clean/dirty state, rejected edits, undo/redo/discard,
pending/unknown/conflict/accepted results, reload, monotonic policy changes, forced
values, role/grant/capability denial and scene versions. Run those expectations on
the original implementation. Add snapshot identity and immutable lifetime checks
for the new owning accessor alongside existing theme/resource history tests.

Run ordinary profile configure/build and `ctest --preset <profile> -R
'^(editor|settings|configuration|scene|protocol|composition)[.]' --output-on-failure`
on Linux GCC 13, Windows GCC 15 and v141_xp; retain both legacy PE checks. Run Linux
native clipboard, theme history, scene/role/visibility and erasure checks, installed
recovery/editor/settings, frontend recovery, preparation and recovery controls.
Measure the same preview stages and rerun every RECOVERY-GUI-LIMITS case without
altering fixed inputs, 100 ms timing, 200 ms erasure or any helper/native deadline.

Use owned ignored output roots and source/artifact-bound evidence. Preserve failed
attempts and unexplained Apply/controller observations. Production recovery remains
disabled until full qualification passes. This package does not complete W-11,
the native inspector, installed desktop integration or any of the five required
0.1.0 editions. Record the next dependency-ready boundary in the existing catalog.
