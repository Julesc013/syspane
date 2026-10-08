from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();e=r/'build-support/evidence';idx=json.loads((e/'w-10-theme-authoring-attempts.json').read_bytes());native=json.loads((e/'w-10-theme-authoring-native-index.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text();assert a in s,(n,a);write(n,s.replace(a,b))
intro='''The [theme-authoring prerequisite](LINKtheme-authoring-handoff.md) now validates
lossless base/role font input and creates deterministic immutable theme artifacts.
Exact no-ops retain the original document, and generated identities bind both theme
content and preserved license metadata. Native controls still require a versioned
resource override and durable command/store integration; these helpers do not save
or enable edited themes by themselves. All five complete editions remain open.

'''
for name,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:replace(name,'The [role-composition checkpoint]',intro.replace('LINK',link)+'The [role-composition checkpoint]')
replace('spec/delivery/current-state.md','Role-aware scene composition verified with explicit development admission; native theme authoring remains next','Shared theme authoring input and immutable artifacts verified; versioned durable override and native controls remain next')
replace('spec/delivery/current-state.md','"at": "2026-10-08T02:15:13.857835+00:00"','"at": "'+now+'"')
replace('TODO.md','- [ ] W-10 native theme authoring and trusted editor admission through existing draft/resource/persistence owners; retain mandatory diagnostics and private-buffer erasure.','- [x] W-10 shared theme-authoring input and immutable artifact construction: exact no-op/reset, policy admission, preserved license and deterministic content pins. See the [handoff](spec/delivery/theme-authoring-handoff.md).\n- [ ] W-10 durable theme editing: versioned exact resource override, command/store publication and replay, atomic draft/history contexts, native font controls and trusted editor admission; preserve mandatory diagnostics and erasure.')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());row=next(w for w in v['work_units'] if w['id']=='W-10');row['specs'].append('SP-W10-THEME-AUTHORING');row['package']='delivery/packages/w-10-theme-authoring.md';row['evidence']='delivery/theme-authoring-handoff.md';row['notes']='Shared theme input now validates complete base/role fonts, exact no-op/reset and legacy migration. Pure immutable artifact construction preserves source bytes/license, derives deterministic license-bound IDs and exact content pins, and enforces current resource/capability policy. Portable examples and native font/composition regressions pass. These helpers do not publish themes or enable native controls. Next close versioned resource override and command/store publication/reconciliation, atomic draft/history resource contexts and native font controls. Earlier native editor/visibility/geometry/content checkpoints remain implemented. Installed ownership, full accessibility/performance, unresolved observation causes, other native adapters and all five complete editions remain required.';write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
replace('spec/delivery/implementation-readiness.md','# Implementation readiness and gates\n\n','# Implementation readiness and gates\n\nThe [theme-authoring prerequisite](theme-authoring-handoff.md) closes lossless font\ninput and deterministic immutable artifact construction. Durable resource override,\ncommand/store admission, draft/history and native controls remain the next boundary.\n\n')
with (r/'docs/developers/build.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''

The [theme-authoring package](../../spec/delivery/packages/w-10-theme-authoring.md)
adds `interfaces::theme_input/theme_edit` and `configuration::author_theme`.
Input hydration and editing return owned values; no-op returns the original theme.
Artifact construction needs current resource policy and `theme.typography`, preserves
the source license and emits exact theme/package pins. It performs no I/O, draft
mutation or durable publication. A changed artifact alone cannot be submitted through
old command schemas or enable EditorForm typography.

After ordinary configure/build and workspace preflight, run
`ctest --preset <profile> -R '^editor[.]THEME-' --output-on-failure` and the full
portable suite. The pinned Linux laboratory also runs `native.THEME-TYPOGRAPHY` and
`native.ROLE-COMPOSITION`. Read the [handoff](../../spec/delivery/theme-authoring-handoff.md)
before extending resource selection, commands, generations and native controls.
''')
with (r/'spec/experience/scene-theme.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''

The [theme-authoring input/artifact contract](../delivery/packages/w-10-theme-authoring.md)
preserves exact no-ops and authors complete base/role fonts without mutating an
installed package. Generated identity binds the source license and edited content.
A versioned durable override, atomic editor history and native controls remain required
before these artifacts become saved theme edits. Construction is not publication.
''')
body=f'''---
type: "SysPane Work Record"
title: "Theme authoring input and immutable artifact checkpoint"
description: "Exact font input and license-bound theme artifacts; durable and native integration remain open."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-THEME-AUTHORING-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-AUTHORING", "SP-ROLE-COMPOSITION-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Theme authoring input and immutable artifact checkpoint

Baseline ed3adc07f6900846ec347e4019b822f44fce59d7. The
[package](packages/w-10-theme-authoring.md) implements the shared input and immutable
artifact boundary needed for native font editing. It leaves every existing schema,
fixture, command, generation and native admission meaning unchanged.

ThemeInput owns a complete base font and explicit named roles. Hydration is lossless
and locale independent; editing validates exact family/size/weight/style, permits
role reset and upgrades legacy documents only on a change. Parsed no-ops return the
original document, including version and absent versus empty roles. Other authored
values are preserved. Invalid input changes nothing.

Authored theme construction authorizes current resources and theme.typography, permits
only font changes and creates a new dependency-free theme package with exact hashes,
byte counts, source license and pins. Its identity binds the canonical edited content
and license. Identical content reuses identity independently of the source theme ID;
a license difference has a different identity. Original packages remain immutable.
It performs no filesystem I/O, does not append a catalog or preset layer, and does
not claim a font edit has been saved or rendered.

## Verification and design refinement

The initial independent Python examples and package were frozen before production
changes. First executions passed, but review found that a theme-only identity seed
could give two different licensed manifests the same package ID/version. The revised
seed wraps both license and theme. A second independently derived MIT/BSD-2-Clause
pair proves distinct identities and exact preservation. Original contract/examples,
both freezes and the preliminary runs remain. The stronger contract was frozen before
the implementation revision; earlier passes do not establish the stronger claim.

All four authoring families and 166 affected checks pass on each development profile.
Full portable suites pass 343 Linux GCC13, 340 Windows GCC15 and 337 v141_xp checks
(1020 total). Native font and semantic role-composition regressions pass on the pinned
Linux adapter. Tests cover owned input, legacy migration, all roles, reset, exact
no-op, locale independence, negative fields and non-font edits, current policy,
exact package bytes/pins, repeated identity, license distinction and immutable source.

{len(idx['attempts'])} source-bound attempts and {len(native)} native archives retain
actual commands, source snapshots, fixed oracles and artifact/runtime identities.
All 184 baseline schema/fixture files remain byte-identical. Specification tooling,
schema/fixture validation, generated navigation, sealed integrity and staged-byte
verification accompany this handoff. The two existing Windows symlink assertions
remain skipped. Historical compiler checks ran on contemporary Windows, not XP.

Cleanup verified committed bytes before removing 24 duplicated native folders
(439813107 bytes) and 23 duplicated attempt folders (40437806 bytes). The 7-GiB
workspace bound is unchanged. Evidence is under build-support/evidence with prefix
w-10-theme-authoring (attempts, native-index, verification, staging), plus
theme-authoring-handoff.json.

## Next admitted work

Close the versioned resource-selection override and theme command/generation boundary.
Keep one authored theme override separate from the base preset closure, preserving
original image references; repeated edits must not grow dependency depth or accumulate
orphaned theme packages. Validate exact pins, collisions, capacity, current policy,
interruption and lost-acknowledgement/restart against frozen cases before implementation.

Then carry scene and resource contexts through the existing atomic draft/history,
Apply and reconciliation owners. Native base/role font controls need preview, inherit,
reset, Cancel/Set, undo/redo, save/reopen and private-buffer erasure evidence before
trusted EditorForm typography is enabled. Clipboard/recovery drafts, installed desktop
ownership, complete accessibility/performance, other native adapters and all five
complete editions remain required. W-10 and the full release goal remain in progress.
'''
write('spec/delivery/theme-authoring-handoff.md',body)
print('Updated theme authoring prerequisite and next durable/native boundaries.')
