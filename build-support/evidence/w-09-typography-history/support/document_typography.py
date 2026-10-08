from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();e=r/'build-support/evidence';index=json.loads((e/'w-09-typography-attempts.json').read_bytes());native=json.loads((e/'w-09-typography-native-index.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
assert all(json.loads((r/a['record']['path']).read_bytes())['exit']==0 for rows in index['final_runs'].values() for a in rows.values())
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text(encoding='utf-8');assert a in s,n;write(n,s.replace(a,b))
intro='''The [typography checkpoint](LINKtypography-handoff.md) adds theme 0.2 with
explicit font weight/style and body, label, value and diagnostic roles. Exact
resource pins and current policy govern admission; existing theme output is
preserved. Native text rendering is verified. Role-aware scene composition and
native theme-authoring controls are the next integration boundary; scene rendering
explicitly refuses the new theme version until that boundary is verified.

'''
for path,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 replace(path,'The [native visibility controls]',intro.replace('LINK',link)+'The [native visibility controls]')
replace('spec/delivery/current-state.md','"scope": "Native visibility controls and trusted EditorForm integration verified; installed ownership and complete editions remain open"','"scope": "Theme typography and native font roles verified; scene composition and theme-authoring controls remain open"')
replace('spec/delivery/current-state.md','"at": "2026-10-08T01:42:39.633509+00:00"','"at": "'+now+'"')
replace('TODO.md','## First native campaign\n','''## First native campaign

- [x] W-09 theme typography: versioned complete fonts/roles, exact resource admission and native raster evidence. See the [handoff](spec/delivery/typography-handoff.md).
- [ ] Connect typography roles to scene composition and native theme-authoring controls through existing draft/resource/persistence owners; retain mandatory diagnostics and private-buffer erasure.
''')
replace('spec/delivery/implementation-readiness.md','# Implementation readiness and gates\n\n','''# Implementation readiness and gates

The [typography checkpoint](typography-handoff.md) adds versioned theme fonts and
native role rendering. Current policy and immutable resource identities gate their
use. Scene composition and native authoring are still explicitly unavailable for
theme 0.2; the next package must prove their role mapping and diagnostic behavior.

''')
replace('spec/experience/scene-theme.md','''theme schema still represents five semantic colors, one font and motion. Expanded
typography roles, spacing/density, chart styles and contrast variants require a
versioned schema and native tests before enablement; they are not hidden in extensions.''','''theme 0.1 schema represents five semantic colors, one font and motion. The
[theme 0.2 typography contract](../delivery/packages/w-09-typography.md) adds complete
font weight/style and named body, label, value and diagnostic roles. Absent roles
use the base font; theme 0.1 retains normal weight/style for every role. Family
names are literal data, native fallback preserves the authored name, and resource
admission requires theme.typography under current policy. The
[checkpoint](../delivery/typography-handoff.md) records native text evidence.

Scene composition must refuse theme 0.2 until role mapping and mandatory diagnostic
preservation are verified. Native theme authoring remains the following integration
boundary. Spacing/density, chart styles and contrast variants still require versioned
contracts and native tests; none is hidden in optional extensions.''')
replace('docs/developers/build.md','# Developer setup and checks\n\n','''# Developer setup and checks

The [typography package](../../spec/delivery/packages/w-09-typography.md) introduces
theme 0.2 and `configuration::theme_font(theme, role)`. It returns an owned family,
DIP size, weight and style; `TextRequest.role` defaults to body. ContentCatalog adds
the required `theme.typography` capability for a selected version 0.2 theme even
when its manifest omitted it. Existing theme 0.1 output remains equivalent.

After ordinary preflight/configure/build, run `ctest --preset <profile> -R
'^configuration[.]TYPOGRAPHY-' --output-on-failure`. The owned Linux laboratory runs
`ctest --preset linux-x64-gcc13 -R '^native[.](THEME-TYPOGRAPHY|TEXT-RASTER|SCENE-SURFACE)$'
--output-on-failure`. The new native oracle preserves pixels and positive ignored-role
and ignored-weight fault witnesses. SceneSurface explicitly refuses theme 0.2 pending
role-aware composition. Read the [handoff](../../spec/delivery/typography-handoff.md)
before enabling scene integration or adding native theme authoring.

''')
replace('docs/users/configuration.md','## Content properties in the development editor\n','''## Content properties in the development editor

Custom font editing is still under development. The new theme format supports
font roles, but it is not yet enabled in scene previews or native theme controls.
Continue using the existing theme choices until that integration is available.
''')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());w=next(x for x in v['work_units'] if x['id']=='W-09');w['specs'].append('SP-W09-TYPOGRAPHY');w['package']='delivery/packages/w-09-typography.md';w['evidence']='delivery/typography-handoff.md';w['notes']='Theme 0.2 adds explicit complete font roles, exact resource capability/policy admission and native text raster evidence. Legacy themes remain equivalent. SceneSurface explicitly refuses new themes until role-aware scene composition proves mandatory diagnostics. Continue composition, native theme authoring and installed ownership. Earlier shared binding/layout, text/table/chart/image and visibility checkpoints remain implemented; original failures and source-bound handoffs are preserved. Full accessibility/performance, historical observation-timeout causes, other native adapters and all five complete editions remain open.'
w=next(x for x in v['work_units'] if x['id']=='W-10');w['notes']=w['notes'].replace('typography and remaining property contracts','role-aware typography composition and native theme authoring, remaining property contracts');write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
failed=[a for a in index['attempts'] if a['exit']]
write('spec/delivery/typography-handoff.md',f'''---
type: "SysPane Work Record"
title: "Theme typography and native font-role checkpoint"
description: "Versioned font roles with resource admission and native raster evidence; scene and authoring integration remain open."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-TYPOGRAPHY-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-TYPOGRAPHY", "SP-VISIBILITY-CONTROLS-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Theme typography and native font-role checkpoint

Source baseline: {index['source_base']}. The
[package](packages/w-09-typography.md) closes versioned font meaning and native
text admission without changing existing theme, scene or command identities.

Theme 0.2 adds complete family/size/weight/style fonts and optional body, label,
value and diagnostic roles. Shared resolution returns an owned exact font;
absent roles use the base font. Theme 0.1 retains weight 400 and normal style.
Native setters treat the family as literal data and preserve current fallback,
contrast, alpha, scale, shaping and pixel limits. No new font download or cache
owner is introduced. Immutable content resolution derives theme.typography as
a required capability and applies existing policy authorization and exact pins.

The role-aware scene compositor and native theme-authoring controls remain open.
SceneSurface reports surface.typography_unavailable for theme 0.2 with empty
published caches, including when display is disabled. Current disclosure denial
keeps priority. Replacing it with a legacy theme resumes without old payloads.
This prevents a default body font from masquerading as complete role composition.

## Executed evidence

All 162 affected checks pass on each development profile. Full portable suites
pass 339 Linux GCC13, 336 Windows GCC15 and 333 v141_xp checks (1008 total).
The historical compiler runs on contemporary Windows; no historical qualification
is inferred. Portable tests exercise literal role results, all supported styles
and weights, invalid fonts and roles, ownership, exact theme pins and capability
omission/denial even when a manifest omitted the new required capability.

The new native oracle passes eleven cases. Raw raster observations verify legacy
equivalence, four literal role-to-base comparisons, bold/italic differences,
fractional-size scale invariance, literal missing-family fallback, light/dark
contrast and rejection without partial output. Ignoring a requested role or weight
produces a positive pixel difference. Existing text and scene tests, three native
editor matrices and fifteen rendering regressions also pass.

{len(index['attempts'])} source-bound attempts and {len(native)} native archives
preserve actual commands, fixed inputs, source bytes, runtime/artifact identities
and outcomes. {len(failed)} build/test attempts failed. Initial compilation caught
a missing namespace brace and misleading indentation in a test; both original
attempts remain recorded. v141_xp then accepted a family containing LF where GCC
rejected it through the regex. Explicit UTF-8 byte validation now enforces all
forbidden family controls, commas and edge spaces independently of native regex
behavior. Its unchanged invalid-font examples pass. A separate resource test
failure exposed null IDs produced by a temporary JSON reference inside the test
pin helper's conditional expression under this compiler. The preserved diagnostic
prints those malformed pins. Owning the parsed document and copying its ID before
constructing the pin fixes the fixture without changing the expected resource
identity or production resolver. Evidence lives in build-support/evidence under
w-09-typography-attempts.json, w-09-typography-native-index.json,
w-09-typography-verification.json, w-09-typography-staging.json and
typography-handoff.json.

The first package/schema/literal-case freeze preceded production additions.
Before builds, the schema assigned C1-control rejection to explicit Unicode
semantic validation because byte-based C++ regex cannot interpret Unicode ranges
portably. The literal invalid-font expectations and required rejection did not
change. Original and revised archives remain. The two standalone resolver files
had already been written when that refinement helper ran; changes to existing
production files followed the refinement. The freeze clarification records this
sequence rather than claiming the revised archive preceded every production byte.

All 176 baseline schema/fixture files remain unchanged. Cleanup verified committed
archives before removing 38 native folders and 49 attempt folders from owned
outputs. One build preflight stopped before launch when its standard reservation
did not fit. Commit a4673c4 preserves raw typography evidence before reclaiming
its duplicate outputs; it does not claim a finished feature. The attempt register
records both source bases. The original records remain in Git, cleanup receipts are retained, and
the development allocation stays 7 GiB with existing action reservations.

## Required continuation

Assign every scene text role, including tables, charts, images and mandatory source
or visibility diagnostics; preserve geometry/erasure/resource limits and test actual
pixels before enabling theme 0.2 in SceneSurface. Then add native theme-authoring
controls with exact immutable resource publication and the existing reversible
draft and durable transaction owners. Do not mutate packaged theme bytes in place.
Continue clipboard authority, recovery drafts, installed entry/restoration and the
remaining native adapters and laboratories. W-09/W-10 and all five editions remain
open; older unexplained accessibility timeouts remain unresolved.
''')
with (r/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n# Preserve typography attempts and executed helper bytes.\nbuild-support/evidence/w-09-typography-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-09-typography-history/support/*.ps1 -whitespace\n')
print('Documented typography evidence and remaining scene/authoring integration.')
