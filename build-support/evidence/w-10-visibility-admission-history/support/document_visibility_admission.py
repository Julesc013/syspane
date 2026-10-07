from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();stamp=datetime.now(timezone.utc).isoformat()
def edit(n,a,b):
 p=r/n;s=p.read_text(encoding='utf-8');assert a in s,(n,a);p.write_text(s.replace(a,b,1),encoding='utf-8',newline='\n')
def append(n,s):
 p=r/n;p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n\n'+s+'\n',encoding='utf-8',newline='\n')
intro='''The [visibility-admission checkpoint](spec/delivery/visibility-admission-handoff.md)
adds scene 0.5, negotiated command 0.7, protected typed edits and exact durable
recovery. Conditional scenes explicitly report an unavailable renderer until native
composition and controls enforce the rules. This is a component checkpoint; the
five complete editions and their release qualification remain open.

'''
edit('README.md','The [conditional-visibility evaluator]',intro+'The earlier [conditional-visibility evaluator]')
edit('spec/delivery/current-state.md','The [conditional-visibility evaluator]',intro.replace('spec/delivery/visibility-admission-handoff.md','visibility-admission-handoff.md')+'The earlier [conditional-visibility evaluator]')
for n in ('README.md','spec/delivery/current-state.md'):
 edit(n,'Versioned scene admission and native controls/rendering are the next required\nintegration; this checkpoint does not enable conditional widgets yet.','Native controls/rendering remain required after the authored admission above;\nthe evaluator alone does not enable conditional widgets.')
edit('spec/experience/scene-bindings.md','Versioned scene/command admission, native status/group composition and editor\ncontrols remain required before enablement. The [handoff](../delivery/visibility-handoff.md)\nrecords current execution scope.','Versioned authored admission is recorded below. Native status/group composition\nand editor controls remain required before enablement. The [evaluator handoff](../delivery/visibility-handoff.md)\nrecords the earlier shared prerequisite.')
edit('spec/experience/editor.md','Native private input, reversible draft edits, negotiated persistence, mandatory\nstatus preservation and independent pixels/accessibility checks remain required.','The authored admission below supplies reversible draft edits and negotiated\npersistence. Native private input, mandatory status preservation and independent\npixels/accessibility checks remain required.')
edit('TODO.md','- [ ] W-09/W-10 conditional-visibility integration: new scene/command capability admission, coherent resource/persistence/replay, atomic editor controls, group/status composition and independent native pixels/accessibility/erasure. The evaluator alone does not complete the feature.',
'''- [x] W-09/W-10 visibility authoring admission: scene 0.5, command 0.7 negotiation, protected typed edits/history, exact resource/persistence/replay and explicit renderer refusal. See the [handoff](spec/delivery/visibility-admission-handoff.md).
- [ ] W-09/W-10 native conditional visibility: private editor controls, group/status composition and independent pixels/accessibility/erasure. Stored rules and shared draft operations do not complete the feature.''')
append('spec/experience/scene-bindings.md','''## Versioned conditional scenes

[Scene 0.5](../contracts/scene-v0.5.schema.json) admits optional widget visibility
using the exact visibility 0.1 rule. Absence is unconditional; null rejects.
Scene 0.4 and older remain byte-identical. The entire scene retains its 256 KiB
bound and each embedded rule its 64 KiB bound. All widget kinds support authored
conditions. Version 0.5 requires scene.content, scene.edit-locks and scene.visibility
resources even when no widget carries a condition or lock.

The [admission package](../delivery/packages/w-10-visibility-admission.md) defines
preservation, promotion, current policy and coherent storage. SceneSurface currently
returns alternative/surface.visibility_unavailable with no frame for this version;
authored capability support must never bypass the native composition gate. Native
condition evaluation, layout-space preservation, inherited group rules, unresolved
diagnostics and mandatory status remain required before enablement.''')
append('spec/experience/editor.md','''The [visibility-admission package](../delivery/packages/w-10-visibility-admission.md)
now implements SetWidgetVisibility in the shared draft. It validates all targets
atomically, promotes scene 0.3/0.4 to 0.5 on Set, retains that version on Clear,
preserves exact history and applies ordinary lock/ancestor protection. Current
capability and policy checks apply to Clear and no-op as well as Set. Lock edits
must preserve scene 0.5. Group/Wrap retain child rules and create an unconditional
parent; Ungroup/Unwrap reject a parent's own rule until explicitly cleared.

Apply for a scene 0.5 replacement requires command 0.7 negotiation. Settings-only
changes preserve the existing conditional scene and its resource closure. Native
condition dialogs and WYSIWYG composition remain open; retain unavailable-preview,
authored recovery and durable/activation distinctions in the meantime.''')
append('spec/contracts/transport.md','''The [visibility-admission boundary](../delivery/packages/w-10-visibility-admission.md)
adds [command 0.7](command-v0.7.schema.json), accepting scene versions 0.2 through
0.5. It always requires configuration.transactions, configuration.content,
configuration.scene-content, configuration.large-commands, configuration.edit-locks,
configuration.visibility, command-result 0.1 and the existing 328704-byte frame
floor. The server offers it only with an explicit resource provider that supports
visibility and edit locks. Missing required dependencies reject the handshake;
optional incompatibility removes visibility and a late 0.7 command returns
feature.unsupported before publication. Denied configuration.visibility returns
policy.denied. The 327680-byte body, framing, queues, 128 admissions, exact request
bytes, cancellation and replay semantics retain their owners and limits.''')
append('spec/architecture/persistence.md','''The [visibility admission checkpoint](../delivery/visibility-admission-handoff.md)
extends the existing manifest 0.3/request.json path to command 0.7. It records
owned ext4 process cuts at request, selector_ready, selected and durable, coherent
40/41 recovery, exact original-body replay, cross-epoch reconciliation, revoked
policy and corrupt request/scene fallback. These results cover authored durability,
not renderer activation, hardware power loss or other filesystem/OS qualification.''')
edit('docs/developers/build.md','Existing scene/command versions do not admit this property.','Scene 0.4 and older and command 0.6 and older do not admit this property.')
append('docs/developers/build.md','''The [visibility admission package](../../spec/delivery/packages/w-10-visibility-admission.md)
adds scene 0.5/command 0.7 to the existing validators, resource provider, transaction
ledger and editor. SetWidgetVisibility accepts distinct target IDs and an optional
visibility document; absence means Clear. Do not advertise renderer support from
authored resource capability. The current SceneSurface rejects this version with
surface.visibility_unavailable after the existing policy checks.

After the ordinary workspace preflight/configure/build, run `ctest --preset
<profile> -R '^(editor[.](VIS-|LOCK-)|configuration[.]|composition[.])'
--output-on-failure` and the full non-native suite. On the owned non-root ext4 Linux
profile, native.VISIBILITY-ADMISSION invokes the bounded ConfigProbe visibility-commit
laboratory mode. It installs nothing and does not enable a native visibility UI.
Regress native storage/IPC, SCENE-SURFACE, SCENE-INSPECTOR-MODEL, EDITOR-LOCKS and
EDITOR-CONTAINERS. Exact input examples live in tests/editor/visibility-admission-cases.json;
the [handoff](../../spec/delivery/visibility-admission-handoff.md) binds executed evidence.''')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes())
for row in v['work_units']:
 if row['id']=='W-10':
  row['package']='delivery/packages/w-10-visibility-admission.md';row['evidence']='delivery/visibility-admission-handoff.md';row['specs'].append('SP-W10-VISIBILITY-ADMISSION')
  row['notes']+=' Visibility authoring now has versioned scene/command admission, typed protected edits, exact history, resource closure and durable recovery. The renderer explicitly refuses conditional scenes until native composition/control evidence closes the next boundary; W-10 remains incomplete.'
 if row['id']=='W-09':row['notes']+=' Scene 0.5/command 0.7 authored admission is now recorded in the W-10 visibility-admission handoff. Continue native condition/group/status/pixel/accessibility integration; stored rule support is not activation.'
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
append('.gitattributes','# Preserve exact visibility admission attempts, frozen contracts and helpers.\nbuild-support/evidence/w-10-visibility-admission-history/** -text whitespace=cr-at-eol')
handoff=f'''---
type: "SysPane Work Record"
title: "Visibility authoring and durable admission checkpoint"
description: "Versioned scenes and commands with protected history, coherent recovery and an explicit native rendering gate."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{stamp}"}}
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

Records: build-support/evidence/w-10-visibility-admission-attempts.json,
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
'''
(r/'spec/delivery/visibility-admission-handoff.md').write_text(handoff,encoding='utf-8',newline='\n')
p=r/'spec/delivery/current-state.md';s=p.read_text(encoding='utf-8');import re
s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=stamp,scope='Visibility authoring admission; native conditional rendering and full editions remain open')),s,flags=re.M);p.write_text(s,encoding='utf-8',newline='\n')
print('Updated documentation and work routing for visibility admission.')
