from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path.cwd();e=r/'build-support/evidence';idx=json.loads((e/'w-08-theme-commands-attempts.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text();assert a in s,(n,a);write(n,s.replace(a,b))
def append(n,s):
 with (r/n).open('a',encoding='utf-8',newline='\n') as f:f.write(s)
intro='''The [durable theme-command checkpoint](LINKtheme-commands-handoff.md) adds
negotiated font edits and exact Linux persistence/recovery. It preserves the original
preset/image closure and one immutable theme override. Interrupted writes, lost
results, replay, cancellation and policy revocation have executable checks. Atomic
editor resource history and native font controls remain next; all five complete
editions remain open.

The earlier [theme authoring](LINKtheme-authoring-handoff.md) and
[resource override](LINKtheme-overrides-handoff.md) checkpoints supply lossless
font input and deterministic artifacts whose identities preserve license metadata.
Native controls still require editor integration and independent preview/save/reopen
evidence before enabling edited theme rendering.

'''
for name,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 s=(r/name).read_text();start=s.index('The [theme-override checkpoint]');end=s.index('The [role-composition checkpoint]',start)
 write(name,s[:start]+intro.replace('LINK',link)+s[end:])
s=(r/'spec/delivery/current-state.md').read_text();s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=now,scope='Negotiated theme commands and Linux durable recovery verified; atomic editor history and native controls remain next')),s,flags=re.M);write('spec/delivery/current-state.md',s)
replace('spec/delivery/current-state.md','## Next work\n\n','## Next work\n\nThe immediate theme-editing boundary is atomic editor resource history: carry base,\ndraft and undo/redo resources through Apply/reconcile/reload with bounded retained\nbytes, then add native font controls and independent pixels/save/reopen/erasure checks.\nUse the [theme-command handoff](theme-commands-handoff.md) and W-10 row; preserve\nthe existing work graph and continue unrelated native tracks independently.\n\n')
replace('TODO.md','- [ ] W-10 durable theme editing: versioned command/store publication and replay, atomic draft/history contexts, native font controls and trusted editor admission; preserve mandatory diagnostics and erasure.', '- [x] W-08 durable theme commands: exact command 0.8 negotiation, Linux generation 0.4/resource index 0.2, independent interrupted-write/replay/recovery checks and unchanged bounds. See the [handoff](spec/delivery/theme-commands-handoff.md).\n- [ ] W-10 theme editor integration: atomic base/draft/history resource contexts, Apply/reconcile/reload, native base/role font controls and trusted editor admission; account resource storage and preserve mandatory diagnostics and erasure.')
v=json.loads((r/'spec/delivery/work-units.json').read_bytes())
for row in v['work_units']:
 if row['id'] in ('W-08','W-10'):row['specs'].append('SP-W08-THEME-COMMANDS')
 if row['id']=='W-08':
  row['package']='delivery/packages/w-08-theme-commands.md';row['evidence']='delivery/theme-commands-handoff.md'
  row['notes']='Command 0.8 now carries exact source-bound font intent and resource selection 0.2 through existing negotiation, serialized transactions, async commands and Linux generation 0.4/resource index 0.2. Original package/image closure, current policy, request bytes, cancellation, interrupted publication and restart reconciliation have fixed portable and independent native evidence. Old formats retain their meaning and limits. Next connect atomic editor resource history and native font controls through W-10; installed store/policy ownership, full layers/updates, non-Linux storage and all five complete editions remain required.'
  row['planned_outputs']+=['source/configuration/theme_command.hpp','spec/contracts/command-v0.8.schema.json']
 if row['id']=='W-10':
  row['notes']='The immutable authoring/override helpers now have negotiated durable command 0.8 and Linux recovery through W-08; see theme-commands-handoff. Next carry resources atomically through editor base/draft/history, Apply/cancel/unknown-result reconciliation and reload, accounting for resource storage as well as scene history. Then add native base/role font controls with independent pixels, save/reopen and private-buffer erasure before trusted EditorForm typography admission. Installed ownership, full accessibility/performance, unresolved observation causes, other native adapters and all five complete editions remain required.'
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
s=(r/'spec/delivery/implementation-readiness.md').read_text();start=s.index('The [theme-override checkpoint]');end=s.index('The [typography checkpoint]',start)
write('spec/delivery/implementation-readiness.md',s[:start]+'''The [durable theme-command checkpoint](theme-commands-handoff.md) closes negotiated
font intent, Linux publication and exact recovery using the earlier immutable
authoring/override contracts. Atomic editor resource history and native controls
remain the next boundary. This checkpoint does not qualify complete editions.

'''+s[end:])
replace('docs/developers/build.md','Existing command/store/SettingsDraft consumers reject new selections. Do not route\nthem through an old command or enable native authoring before the next admission.','Legacy command/store formats and current SettingsDraft consumers reject new\nselections. The command 0.8 admission below now supplies durable storage; editor\nresource history and native authoring require the next integration.')
append('docs/developers/build.md','''

The [durable theme-command package](../../spec/delivery/packages/w-08-theme-commands.md)
adds `prepare_theme_command` to the existing transaction worker. Command 0.8 carries
an exact current source pin, complete base/role fonts and resource selection 0.2.
The owner constructs and validates canonical bytes without importing packages.
The explicit `configuration.theme-overrides` feature requires the existing visibility,
edit-lock, full-scene, content and transaction features plus theme typography support.
Original body bytes remain request identity, including their existing 327680-byte limit.

Linux writes generation manifest 0.4 and resource index 0.2 only for command 0.8.
Recovery checks version pairing, exact files/hashes and fulfilled font intent.
The ConfigProbe `theme-commit <command-file> <fault>` mode uses current resources;
it accepts no import roots. Old generations retain their readers. This does not
enable native font controls or EditorForm typography.

After ordinary preflight/configure/build, run
`ctest --preset <profile> -R '^configuration[.]THEME-COMMAND-' --output-on-failure`,
the affected configuration/editor/protocol/component tests and full portable suite.
In the existing non-root ext4 Linux laboratory run
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-COMMANDS|RESOURCE-GENERATIONS|CONTENT-COMMANDS|CONFIG-STORE|COMMAND-IPC|VISIBILITY-ADMISSION)$' --output-on-failure`.
The independent oracle compares literal artifact bytes, confirms stopped/killed owners,
and preserves corruption and wrong-output witnesses. Read the
[handoff](../../spec/delivery/theme-commands-handoff.md) before editor integration.
''')
replace('spec/experience/scene-theme.md','A versioned durable override, atomic editor history and native controls remain required\nbefore these artifacts become saved theme edits. Construction is not publication.','The durable command boundary below now publishes versioned overrides. Atomic editor\nhistory and native controls remain required before native theme editing is enabled.')
replace('spec/experience/scene-theme.md','The explicit component API preserves image references and\ndoes not enable a wire command, native authoring or new generation recovery. Those\nrequire their own versioned admission and interrupted/replayed transaction evidence.','The explicit component API preserves image references. The\n[durable theme command](../delivery/packages/w-08-theme-commands.md) now admits exact\nsource-bound font intent through command 0.8 and Linux generation 0.4 recovery. It\nretains the original closure and one canonical override, including reset and exact\nrequest reconciliation. Native authoring still requires atomic editor resource history,\nfont controls, independent pixels/save/reopen and policy-loss erasure evidence.')
append('spec/contracts/transport.md','''

The [durable theme-command boundary](../delivery/packages/w-08-theme-commands.md)
adds [command 0.8](command-v0.8.schema.json) with exact resource selection 0.2 and
nullable source-bound base/role font intent. It requires command-result 0.1 and
configuration.theme-overrides in addition to every command 0.7 feature dependency.
The owner must also support theme.typography and configuration.theme-overrides.
Current policy gates edits, resets, retained results and reconciliation; non-null
font intent additionally requires theme.edit and the console or desktop role.
Unknown required combinations fail negotiation; optional incompatibility removes
the feature and late unsupported commands reject before preparation. Existing
framing, parser/body/ledger bounds and raw request replay identity are unchanged.
Linux generation 0.4/resource index 0.2 preserve exact request/artifact bytes and
fulfilled font intent. Stored/durable facts do not assert activation or visibility.
''')
write('spec/delivery/theme-commands-handoff.md',f'''---
type: "SysPane Work Record"
title: "Durable authored theme command checkpoint"
description: "Negotiated font intent, versioned Linux publication and independent restart evidence."
tags: ["delivery", "architecture", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-THEME-COMMANDS-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W08-THEME-COMMANDS", "SP-THEME-OVERRIDES-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Durable authored theme command checkpoint

Baseline {idx['source_base']}. The [package](packages/w-08-theme-commands.md)
defines command 0.8, exact source-bound font intent and selection 0.2. The existing
serialized owner copies the current theme, applies complete base/role font values,
constructs the canonical artifact and verifies the requested selection. It preserves
the original package/preset/image closure and license, with one override. Null intent
supports retaining or resetting that override using only current immutable packages.
No import callback runs. Exact no-change intent rejects rather than creating a revision.

Negotiation requires every existing visibility/lock/full-scene/content/transaction
dependency and the new feature. Current policy is repeated at prepare, publication,
replay and reconciliation. Cancellation and independent supervision retain their
owners. Linux manifest 0.4/resource index 0.2 bind request bytes, documents, artifact
identity and fulfilled font values. Old command/generation formats retain their
meaning. Existing size, concurrency, retention and storage limits are unchanged.

## Executed verification

The package, schema, literal requests/expected revisions, selection/font values and
independent artifact fixtures were frozen before production changes. Five portable
families cover schema/semantic refusal, maximum bodies/scenes, transaction/preview,
ten edit/reset cycles, source/result mismatch, no-op refusal, current policy,
cancellation, exact replay, async delivery and 13 negotiation combinations.

All 175 affected tests pass on each development profile. Full portable suites pass
352 Linux GCC13, 349 Windows GCC15 and 346 v141_xp checks (1047 total). The historical
toolset ran on contemporary Windows; this does not qualify XP. Six native families
pass: THEME-COMMANDS, RESOURCE-GENERATIONS, CONTENT-COMMANDS, CONFIG-STORE, COMMAND-IPC
and VISIBILITY-ADMISSION. The new independent ext4/IPC oracle passes 25 scenarios:
exact save/replay/keep/reset without imports, ten confirmed process cuts, eight
policy/corruption/version faults, five IPC modes and a deliberate wrong-output witness.
It compares exact file sets and manifest/asset/request bytes, verifies coherent
current/previous recovery and reconciles lost acknowledgements without another revision.

Preserved failures include the initial schema-freeze helper's deprecated external-ref
resolver, a compiler indentation warning in the new unit test, and the native oracle's
attempt to reopen an exclusively locked store. The corrected oracle reads immutable
bytes during ownership and reopens only after shutdown; expected bytes and outcomes
did not change. The initial evidence-helper filename error and the specification
tool's missing 0.8 schema-identity admission are also retained; its version list now
includes the new contract. These
are distinct from the final passing records; original source archives/logs remain.

Evidence under build-support/evidence uses prefix w-08-theme-commands: attempts,
native-index, verification, staging and theme-commands-handoff.json. It preserves
{len(idx['attempts'])} source-bound executions, both native attempts, frozen expectations
and artifact identities. All 191 baseline schema/fixture files retain their bytes.
Schema/fixture validation, generated navigation, specification-tool checks and sealed
integrity accompany the handoff; the two existing Windows symlink assertions remain
skipped. Verified committed duplicate outputs were reclaimed within the unchanged
7-GiB workspace allocation, with exact cleanup receipts.

## Next admitted work

Carry immutable resource contexts atomically through editor base/draft/history,
Apply/cancellation, unknown-result reconciliation and reload. Account for retained
resource storage as well as scene history; avoid accumulating copied base packages
per undo entry. Build command 0.8 only when the corresponding contract is admitted.
Then add native base/role font controls with independent preview pixels, accessibility,
save/reopen and private-buffer erasure. Trusted EditorForm typography remains gated.

Installed store/policy ownership, other filesystem/native adapters, full layers/updates,
accessibility/performance qualification and all five complete editions remain required.
W-08/W-10 and the full release goal remain in progress.
''')
append('.gitattributes','\n# Preserve exact theme command attempts, frozen expectations and helper bytes.\nbuild-support/evidence/w-08-theme-commands-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-08-theme-commands-history/support/*.ps1 -whitespace\n')
