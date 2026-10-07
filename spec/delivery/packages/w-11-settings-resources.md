---
type: "SysPane Work Package"
title: "Resource-aware native settings"
description: "Preserve exact resource selection through settings drafts, native commits and restart."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "2026-10-07T02:36:31Z"}
sp_id: "SP-W11-SETTINGS-RESOURCES"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W11-NATIVE-SETTINGS", "SP-W08-RESOURCES", "SP-W09-SCENE-CONTENT"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Resource-aware native settings

Continue W-11 by connecting its existing draft/form to the exact selected resource
closure. Retain all settings-only behavior, result identities, disclosure rules and
native controls. The common transaction coordinator remains the sole persistence
owner. This is a prerequisite for resource-backed installed settings and W-10 editing;
it does not discharge editor, installed lifecycle or other adapter requirements.

## Snapshot ownership and command identity

The trusted host supplies coherent Authored documents plus an optional resource
context: an immutable validated ContentCatalog, exact package/preset selection and
adapter capability set. Prepare that catalog before entering the UI owner, from the
same admitted generation's immutable packages. The UI never imports paths, reads
files or chooses fallback packages. Validate selection and document/resource binding
through the existing ContentCatalog; do not invent another resource resolver.

A resource-bearing settings draft always emits command 0.3 with its exact content
selection, base revision and current policy generation. Settings-only command 0.3
preserves scene 0.3 exactly under the established resource contract. Command 0.4
is needed when a later editor changes versioned widget content, not merely because
an unchanged scene already uses it. Resource-free scene 0.2 retains command 0.2.
Reject a bare scene 0.3 or a reload that drops an already-required resource context.
Caller-supplied context is copied into the owner; no later external selection mutation.

Only reload may replace the selected catalog/selection. Reload remains explicit and
requires no unresolved request. A missing/malformed context rejects atomically and
preserves the old draft. Current disclosure denial still erases it. Remember that a
resource context is required even across revocation, so regrant cannot silently admit
a resource-free reload. A fresh valid reload supplies all documents and resources.

## Editing, policy and lifetime

Prepare each setting through the existing authored validator. Resolve its candidate
resources from the admitted immutable catalog and the unchanged exact selection.
With no scene override, this permits a valid theme ID already in that closure;
missing or ambiguous effective themes reject the edit with an inline error,
without changing any other draft value.
Preserve a non-null scene theme override; changing the setting beneath it does not
silently clear that override or change the effective scene theme. The setting then
remains the requested default; resource validation resolves the effective scene theme.

Retain accepted and draft resource snapshots alongside the accepted and draft
documents. Revert restores both; accepted commit advances both once. Preview and
unknown results do not adopt a new accepted snapshot. No-op suppression remains.
Use the existing content.select, setting/preview/commit and required-resource
capability checks. Unavailable/denied resource capabilities lock editing and
submission with a policy reason; readable configuration remains inspectable when
its operational inspector/accessibility grants remain valid. The native worker
independently rechecks resources and current policy at publication.

Disclosure revocation or close drops all local catalog/resource/document references,
native values, errors and results. Retain only bounded unresolved request identity
and the fact that resources are required. Regrant alone cannot restore any content.
The trusted host may retain its independently authorized catalog. Materialized bytes
remain bounded by the existing content closure limits and use immutable shared
ownership; no extra filesystem or network permission is implied.

## Acceptance before installed routing

Preserve fixed expected settings, scene content, exact pins and transitions before
implementation. Portable settings cases must cover command version/selection,
unchanged scene 0.3 text/table/chart/image data, valid/missing theme, scene override,
preview/revert/commit, content.select and required-capability denial, atomic reload,
revocation/regrant and original-request reconciliation. Run all three development
profiles with the existing affected transaction/policy/component checks.

Extend the independent native settings runner with resource-backed generations.
Use an actual valid PNG and coherent scene 0.3. The native owner bootstraps a resource
generation through the ordinary transaction API, then makes imports unavailable.
Controls must still preview/apply, choose an admitted theme, save/reopen and reconcile
across restart using the stored closure. Compare settings and scene documents,
resource index selection/theme pins, every manifest/asset byte and their hashes
independently. No duplicate revision or blind retry. Exercise publication-time
policy change, invalid theme and disclosure erasure with the original 200 ms bound.
Retain the existing native deliberate controls and add a wrong-selection control
that must be detected by the exact resource-selection oracle.

Use ordinary bounded workspace and build/test commands. Preserve original failures
and exact source/artifact/runtime identities. Existing schemas, fixtures and release
acceptance criteria remain unchanged. Full installed settings, native editor,
persistent inheritance reset, clipboard/export, localization, representative
accessibility and platform qualification remain required.
