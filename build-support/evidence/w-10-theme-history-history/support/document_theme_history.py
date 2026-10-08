from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path.cwd();idx=json.loads((r/'build-support/evidence/w-10-theme-history-attempts.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text();assert a in s,(n,a);write(n,s.replace(a,b))
def append(n,s):
 with (r/n).open('a',encoding='utf-8',newline='\n') as f:f.write(s)
intro='''The [theme-history checkpoint](LINKtheme-history-handoff.md) connects shared
immutable theme resources to editor undo/redo, Apply, reconciliation and reload.
It bounds retained resource bytes alongside scene history and preserves original
package allocations. Native font controls and their independent preview/save/reopen
evidence remain next; all five complete editions remain open.

'''
for name,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 replace(name,'The [durable theme-command checkpoint]',intro.replace('LINK',link)+'The [durable theme-command checkpoint]')
 replace(name,'editor resource history and native font controls remain next; all five complete\neditions remain open.','editor resource history now has the checkpoint above; native font controls and all\nfive complete editions remain open.')
s=(r/'spec/delivery/current-state.md').read_text();s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=now,scope='Atomic theme resource history and durable editor Apply/reload verified; native font controls remain next')),s,flags=re.M);write('spec/delivery/current-state.md',s)
replace('spec/delivery/current-state.md','The immediate theme-editing boundary is atomic editor resource history: carry base,\ndraft and undo/redo resources through Apply/reconcile/reload with bounded retained\nbytes, then add native font controls and independent pixels/save/reopen/erasure checks.\nUse the [theme-command handoff](theme-commands-handoff.md) and W-10 row; preserve','The immediate theme-editing boundary is native base/role font controls: use the\nshared atomic history and command owner, then prove preview pixels, accessibility,\nsave/reopen, lost results and private-input erasure before trusted editor admission.\nUse the [theme-history handoff](theme-history-handoff.md) and W-10 row; preserve')
replace('TODO.md','- [ ] W-10 theme editor integration: atomic base/draft/history resource contexts, Apply/reconcile/reload, native base/role font controls and trusted editor admission; account resource storage and preserve mandatory diagnostics and erasure.','- [x] W-10 atomic theme history: shared immutable package allocations, bounded scene/resource undo/redo, exact command 0.8 Apply/reconcile/reload and independent Linux save/reopen checks. See the [handoff](spec/delivery/theme-history-handoff.md).\n- [ ] W-10 native theme editing: base/role font controls, borrowed draft resource preview, independent pixels/accessibility/save/reopen/lost-result/erasure evidence and trusted editor admission. Preserve mandatory diagnostics and existing limits.')
v=json.loads((r/'spec/delivery/work-units.json').read_bytes());w=next(w for w in v['work_units'] if w['id']=='W-10');w['specs'].append('SP-W10-THEME-HISTORY');w['package']='delivery/packages/w-10-theme-history.md';w['evidence']='delivery/theme-history-handoff.md';w['notes']='Shared editor history now restores scene, selection and immutable resources atomically. Explicitly admitted font changes generate command 0.8 against the accepted baseline; preview, commit, unknown-result reconciliation, reload, current policy and private erasure have portable checks and an independent Linux store exercise. Existing 64-entry/8-MiB history limits include unique additional resource allocations; original base packages are shared. Next implement native base/role font controls, draft-resource preview and independent pixels/accessibility/save/reopen/lost-result/erasure before trusted EditorForm typography admission. Installed ownership, unresolved observation causes, full accessibility/performance, other adapters and all five complete editions remain required.';write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
replace('spec/delivery/implementation-readiness.md','font intent, Linux publication and exact recovery using the earlier immutable\nauthoring/override contracts. Atomic editor resource history and native controls\nremain the next boundary. This checkpoint does not qualify complete editions.','font intent, Linux publication and exact recovery using the earlier immutable\nauthoring/override contracts. The [theme-history checkpoint](theme-history-handoff.md)\nnow connects atomic editor resources, history and Apply/reload. Native font controls\nand their independent evidence remain next; complete editions remain unqualified.')
replace('docs/developers/build.md','Legacy command/store formats and current SettingsDraft consumers reject new\nselections. The command 0.8 admission below now supplies durable storage; editor\nresource history and native authoring require the next integration.','Legacy command/store formats and unadmitted SettingsDraft contexts reject new\nselections. Command 0.8 supplies durable storage; the theme-history integration below\nnow admits shared drafts explicitly. Native controls still require their own evidence.')
append('docs/developers/build.md','''

The [theme-history package](../../spec/delivery/packages/w-10-theme-history.md)
adds `EditorDraft::set_theme_fonts`, `theme_fonts_available` and a const `resources`
borrow. Supply complete font and null/complete role-map values. Existing SceneThemeEdit
retains the override or selects a base theme, preserving null versus explicit ID.
History stores scene/selection/resource snapshots together. `history_bytes` includes
unique additional resource bytes; count and byte limits remain 64 and 8 MiB.
Borrowed resources expire on mutation, policy, reload or close, like the scene borrow.

`ContentCatalog::retained` shares internally owned immutable packages from a validated
ResourceSet. Its optional added package enters by value and receives ordinary checks.
Use the existing explicit context capabilities and large-command admission before
loading versioned selections or authoring fonts. Apply derives one final command 0.8
from the accepted theme, even after several local edits. Selecting another base theme
must be committed before changing its fonts when the final artifact cannot be derived
from the accepted source. Do not bypass this with rewritten request pins.

After ordinary preflight/configure/build run
`ctest --preset <profile> -R '^editor[.]THEME-HISTORY-' --output-on-failure`, affected
editor/settings/configuration/protocol/component tests and the full portable suite.
In the existing non-root Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-HISTORY|THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|SETTINGS-FORM|EDITOR-FORM)$' --output-on-failure`.
The new native test emits requests from the actual EditorDraft, publishes through
ConfigProbe, independently compares files/bytes, and verifies fresh reload and a
lost-result reconciliation. It does not instantiate font controls. The
[handoff](../../spec/delivery/theme-history-handoff.md) preserves failures and evidence.
''')
append('spec/experience/editor.md','''

The [theme resource history contract](../delivery/packages/w-10-theme-history.md)
extends the existing shared draft with atomic scene/selection/resource undo states.
Original immutable base packages share allocations. The existing 8-MiB history limit
also charges unique additional resource metadata and package bytes, with the accepted
baseline retained separately. Explicitly admitted font intent uses command 0.8 against
the committed source. Undo/redo, Apply, unknown results, reload and policy erasure use
the existing transaction owner. Native base/role font controls, borrowed-resource
preview, independent pixels/accessibility and private-input erasure remain required
before trusted EditorForm typography admission.
''')
replace('spec/experience/scene-theme.md','Native authoring still requires atomic editor resource history,\nfont controls, independent pixels/save/reopen and policy-loss erasure evidence.','The [theme-history contract](../delivery/packages/w-10-theme-history.md) now connects\natomic editor resources and Apply/reload. Native authoring still requires font controls,\nindependent pixels/save/reopen and policy-loss erasure evidence.')
write('spec/delivery/theme-history-handoff.md',f'''---
type: "SysPane Work Record"
title: "Atomic theme resource history checkpoint"
description: "Shared package lifetimes, bounded undo/redo and exact durable editor requests."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-THEME-HISTORY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-HISTORY", "SP-THEME-COMMANDS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Atomic theme resource history checkpoint

Baseline {idx['source_base']}. The [package](packages/w-10-theme-history.md)
closes the shared editor resource boundary. Scene, selection and immutable resource
snapshots now move together through local fonts, undo/redo, discard, Preview, Apply,
unknown-result reconciliation and reload. Multiple local font edits generate one
command 0.8 against the accepted source. Exact no-ops preserve both stacks; invalid
or unrepresentable edits leave the draft unchanged. Policy/resource revocation drops
private state and retained resources; a result cannot repopulate erased state.

Retained catalog derivation shares the original internally owned immutable package
allocations and validates new owned bytes. Ordinary edits with unchanged resource
identity reuse the snapshot while rechecking candidate binding and current policy.
Acceptance replaces the context with the committed resources so obsolete overrides
are released. The 64-entry and 8-MiB history limits remain; accounting now includes
unique additional resource snapshots and package bytes, excluding the separately held
accepted baseline. Original content/package/asset limits are unchanged.

## Executed verification

The package and independent literal first/second theme artifacts, scenes, selections
and commands were frozen before production edits. Eight portable families cover
allocation identity/lifetime and input isolation; exact fonts, role null/empty and
no-op/reset/history behavior; baseline-derived commands and durable results; pending,
conflict, lost acknowledgement and reload; admission/policy/erasure; count eviction,
large-scene eviction and large-theme resource-byte eviction. Changing the base theme
before an uncommitted font edit rejects when command 0.8 cannot represent its result.

All 183 affected tests pass on each development profile. Full portable suites pass
360 Linux GCC13, 357 Windows GCC15 and 354 v141_xp checks (1071 total). The historical
toolset ran on contemporary Windows and does not qualify XP. Six native families pass:
THEME-HISTORY, THEME-COMMANDS, RESOURCE-GENERATIONS, CONTENT-COMMANDS, SETTINGS-FORM and
EDITOR-FORM. The new owned ext4 experiment drives actual EditorDraft requests through
the store, independently compares exact request/documents/artifact bytes, saves two
themes and resets, reloads from disk, reconciles a committed lost acknowledgement,
and detects a deliberately false theme report. This does not demonstrate native font
controls; existing native settings/editor checks cover their established behavior.

Failed attempts remain preserved: the new probe's copied-loop compiler warning,
the command test's reused Preview/Apply request identity, a no-op settings change
incorrectly treated as a request, combined/large-scene test deadlines and the Windows
resource-history deadline, the v141_xp fixture's null generated theme pin (including
the diagnostic run which identified it), and the native probe's accidentally reused
full-capacity bootstrap scene. The native
bootstrap now uses this package's frozen baseline and checks its exact initial state.
The generated stress fixture now copies its pin ID from an explicitly retained parsed
document, replacing the temporary JSON subscript that produced a null pin under
v141_xp; fixture schemas are checked before constructing the catalog.
Count, scene-byte and resource-byte checks are now separate; the scene-byte case retains
one authored theme while editing a large scene, and the other cases still cover 75
font replacements and 35 large-theme replacements. Redundant unchanged-resource
preparation was removed; immutable resource metadata sizes are captured with history
states instead of repeatedly serializing retained themes. Current binding/policy
validation remains. Fixed artifact expectations, history limits and the existing
test deadline were not changed.

Evidence under build-support/evidence uses prefix w-10-theme-history: attempts,
native-index, verification, staging and theme-history-handoff.json. The attempts
index retains {len(idx['attempts'])} source-bound executions and original outcomes,
fixed inputs, source archives and artifact identities. All 199 baseline schema/fixture
files retain their bytes. Generated navigation, schema/fixture checks, specification
tool tests and sealed integrity accompany the handoff. Two existing Windows symlink
assertions remain skipped. Verified committed duplicate output copies were reclaimed
within the unchanged 7-GiB development allocation; cleanup receipts retain their scope.
Older duplicate source archives were also deduplicated by verified SHA-256, retaining
one identical archive and a restoration map; their result records and this checkpoint's
original attempts were preserved.

## Next admitted work

Add native base/role font controls using the existing lossless input adapter and
shared draft. Render previews from the draft's matching borrowed resource snapshot,
preserve mandatory diagnostics, and expose precise current admission/failure states.
Independently prove pixels, accessibility, null/empty role choices, undo/redo,
save/reopen, lost-result handling and private-input erasure before trusted EditorForm
typography is enabled. Preserve all existing visibility/edit-lock and recovery gates.

Installed ownership, other native/storage adapters, unresolved observation causes,
full accessibility/performance and all five complete editions remain required. W-10
and the full release goal remain in progress.
''')
append('.gitattributes','\n# Preserve exact theme history attempts, fixed expectations and helper bytes.\nbuild-support/evidence/w-10-theme-history-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-10-theme-history-history/support/*.ps1 -whitespace\n')
