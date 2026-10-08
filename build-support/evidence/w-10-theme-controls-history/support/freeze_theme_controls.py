from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,subprocess
r=Path.cwd();base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert base=='b2bc1fcac26399084aae72fa824ca9441cba61ea'
out=r/'out/campaign/w-10-theme-controls';out.mkdir(exist_ok=True)
package=r/'spec/delivery/packages/w-10-theme-controls.md';cases=r/'tests/editor/theme-controls-cases.json';assert not package.exists() and not cases.exists()
now=datetime.now(timezone.utc).isoformat()
package.write_text('''---
type: "SysPane Work Package"
title: "Native font controls and draft resource preview"
description: "Lossless base/role editing, current immutable preview and independent durable native evidence."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {"by": "codex", "at": "'''+now+'''"}
sp_id: "SP-W10-THEME-CONTROLS"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "normative-proposal"
sp_requires: ["SP-W10-THEME-HISTORY", "SP-W10-THEME-AUTHORING", "SP-W09-ROLE-COMPOSITION"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Native font controls and draft resource preview

Connect the existing lossless font input and atomic resource history to EditorForm.
Preserve theme 0.2, command 0.8, generation 0.4 and all limits. This is native
component integration; installed ownership, other adapters and complete editions
remain separate requirements.

## Controls and exact input

Fonts is a scene-wide action, independent of selected widgets. Enable it only when
EditorDraft.theme_fonts_available permits edits, properties are clean and no modal,
pending request or conflict is active. It does not override widget edit locks or
modify geometry. A lazy native modal fits the owned 800x600 laboratory and exposes
names, roles, values, keyboard activation and explicit validation feedback.

Target selects Base, Body, Label, Value or Diagnostic. Each complete font exposes
literal family, size in DIP, weight and normal/italic/oblique style. Reuse the
existing lossless parser; family input is bounded to 512 UTF-8 bytes, numeric fields
to 64 bytes. Existing 128-codepoint family, finite size and weight constraints apply.
No installed-font substitution, trimming or locale coercion is allowed.

Role overrides offers Use base font for all roles or Customize roles. The first
omits font_roles and ignores inactive private role values. Customize stores an
explicit map, including an empty map when no individual role is enabled. Each role
has a Use this role font toggle; disabled roles inherit the base font. A newly
enabled role starts from the base font captured on open unless a private value
already exists from this modal. Switching target or mode retains raw private values,
including invalid input, until Set or erasure. Inactive fields cannot invalidate Set.

Hydration preserves source values. An unchanged Set returns the exact original
theme, including schema version, omitted defaults, numeric representation and
absent versus empty role map. A changed Set validates a complete theme 0.2, keeping
all non-font values and source license unchanged, and invokes existing atomic font
authoring once. Invalid input leaves the modal and draft unchanged with actionable
feedback. Set changes the draft; Apply saves it. Cancel changes nothing.

Use settings theme performs existing SceneThemeEdit(null), ignoring private invalid
font values. It restores scene-level inheritance from settings, not a guessed font.
Undo/redo retains exact scene/selection/resources and the existing count/byte limits.

## Lifetime, preview and admission

While Fonts is open, main selection, gestures, properties, history, reload and
submission are disabled. Wipe all private field/model/snapshot/error values on
Cancel, successful Set/reset, close, any policy change, command disconnection,
topology change or reload. Held native references must observe erasure within the
existing 200-ms bound. Regrant alone never restores private buffers. Keep exceptions
inside GTK callbacks. Private text must not export either clipboard selection.

Preview, content choices and widget creation must consume the current draft's
matching borrowed resources. Never resolve an authored override through the original
settings catalog. SceneSurface receives its own validated snapshot sharing immutable
packages; no unsafe borrowed pointer may outlive the draft. Do not retain a redundant
catalog in EditorForm after the shared draft owns it. Current policy/resource loss
clears draft, private modal and preview state together.

Trusted EditorForm may enable typography only with the existing explicit large
command/context admission (all seven theme/history capabilities) and current policy.
Font edit permission is distinct from permission to display a retained theme.
Direct SceneSurface defaults remain unchanged. A disabled Fonts action explains
missing capability, current edit unavailability or pending private properties.
Preserve mandatory diagnostics and the established visibility/edit-lock gates.

## Durable and independent acceptance

Apply emits existing command 0.8 against the accepted source; accepted generations
advance once. Lost results reconcile the original identity across epochs. Fresh
reopen restores exact artifacts, font values and role membership. Durability,
activation and external visibility remain distinct facts. Theme reset and ordinary
content/image operations after a font edit retain coherent resources.

Freeze this package and independent artifact/scene/selection/font examples before
production edits. Portable cases cover unchanged hydration, explicit empty versus
omitted roles, every role, inactive invalid values, invalid active values, one undo
step, reset, admission, policy and pending state. Run affected/full suites on all
three development profiles.

Owned non-root Linux cases must operate actual GTK/AT-SPI controls, compare literal
font requests through the independent text probe with observed canvas pixels, and
verify exact stored generation/artifact bytes and fresh reopen. Exercise base and
all role fonts, no-op, null/empty roles, invalid correction, undo/redo, reset,
pending cancellation, lost acknowledgement/restart, denial and modal erasure on
each lifetime boundary. Show positive witnesses for wrong committed font intent,
retained private text and frozen preview; a timeout is not fault detection.
Preserve accessibility diagnostics and current source-status rendering. Regress
native editor/content/visibility, theme history/commands and role composition.
Preserve all failures with source/artifact/environment identity within 7 GiB.
This evidence cannot qualify a whole edition or a historical OS.
''',encoding='utf-8',newline='\n')
read=lambda n:json.loads((r/n).read_bytes());fixed=read('tests/editor/theme-authoring-cases.json');source=fixed['source'];authored=read('tests/editor/native-cases.json')['authored'];fixture=read('tests/configuration/settings-content-fixture.json');history=read('tests/editor/theme-history-cases.json')
v=copy.deepcopy(fixture['authored']['scene']['widgets'][1]);v.update(id='widget:value',title='Receive');v['layout']['base']=dict(kind='fixed',x=280,y=180,width=180,height=150);authored['scene']['widgets'].append(v);authored['scene']['roots'].append(v['id'])
enc=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n';sha=lambda b:hashlib.sha256(b.encode()).hexdigest()
font=dict(family='Noto Sans',size_dip=19.5,weight=700,style='normal')
roles={k:dict(family='Noto Sans',size_dip=float(size),weight=weight,style=style) for k,size,weight,style in [('body',17,400,'normal'),('label',12,700,'normal'),('value',22,400,'normal'),('diagnostic',14,400,'italic')]}
artifacts={};scenes={};selections={}
for key,overrides in [('base',None),('roles',roles),('empty',{})]:
 theme=copy.deepcopy(source);theme['schema_version']='0.2.0';theme['font']=font
 if overrides is not None:theme['font_roles']=overrides
 seed=copy.deepcopy(theme);seed.pop('theme_id');identity=sha('SysPane authored theme 1\n'+enc(dict(license=fixed['expected_license'],theme=seed)));theme['theme_id']='theme:authored:'+identity;asset=enc(theme)
 manifest=dict(schema_version='0.1.0',package_id='package:authored-theme:'+identity,version='0.1.0',kind='theme',license=fixed['expected_license'],dependencies=[],assets=[dict(path='theme.json',media_type='application/json',sha256=sha(asset),bytes=len(asset.encode()))],total_unpacked_bytes=len(asset.encode()),required_capabilities=['theme.typography'],optional_capabilities=[])
 raw=enc(manifest);pp=dict(id=manifest['package_id'],version='0.1.0',sha256=sha(raw));tp=dict(id=theme['theme_id'],version='0.1.0',sha256=sha(asset));artifacts[key]=dict(theme=theme,asset=asset,manifest=raw,package_pin=pp,theme_pin=tp)
 scene=copy.deepcopy(authored['scene']);scene['theme_id']=theme['theme_id'];scenes[key]=scene
 selection=copy.deepcopy(history['base_selection']);selection['theme_override']=dict(package=pp,theme=tp);selections[key]=selection
value=dict(authored=authored,source=source,artifacts=artifacts,scenes=scenes,selections=selections,base_selection=history['base_selection'],expected_fonts=dict(base=font,**roles),body_text='Editable pane\nMove me',value_blocks=[dict(role='label',text='Receive'),dict(role='value',text='80 byte'),dict(role='diagnostic',text='Current')],erase_ms=200,native_cases=['base','roles','empty','inherit','noop','invalid','reset','restart','cancel-request','deny','revoke','capability-loss','policy','disconnect','topology','close','retain-font','frozen-preview','wrong-font'])
cases.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
paths=[package,cases,r/'tests/editor/theme-authoring-cases.json',r/'tests/configuration/settings-content-fixture.json']
(out/'fixed-inputs.json').write_text(json.dumps(dict(source_base=base,recorded_at=now,inputs={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n',encoding='utf-8')
print('Frozen contract and independent native font examples:',base)
