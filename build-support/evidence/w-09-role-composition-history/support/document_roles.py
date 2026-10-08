from pathlib import Path
from datetime import datetime,timezone
import json
r=Path.cwd();e=r/'build-support/evidence';idx=json.loads((e/'w-09-role-composition-attempts.json').read_bytes());native=json.loads((e/'w-09-role-composition-native-index.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text(encoding='utf-8');assert a in s,(n,a);write(n,s.replace(a,b))
intro='''The [role-composition checkpoint](LINKrole-composition-handoff.md) connects theme
fonts to body text, labels, values and diagnostics in the Linux scene renderer.
Independent pixels, table geometry and policy/visibility erasure checks pass.
Legacy themes keep their previous rendering. Theme 0.2 still requires explicit
trusted development admission; native theme-authoring controls and their editor
integration are next. Installed ownership and all five complete editions remain open.

'''
for name,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:
 s=(r/name).read_text();start=s.index('The [typography checkpoint]');end=s.index('The [native visibility controls]',start);s=s[:start]+intro.replace('LINK',link)+s[end:];write(name,s)
replace('spec/delivery/current-state.md','Theme typography and native font roles verified; scene composition and theme-authoring controls remain open','Role-aware scene composition verified with explicit development admission; native theme authoring remains next')
replace('TODO.md','- [ ] Connect typography roles to scene composition and native theme-authoring controls through existing draft/resource/persistence owners; retain mandatory diagnostics and private-buffer erasure.','- [x] W-09 role-aware scene composition: bounded semantic blocks, exact native pixels, preserved diagnostics and erasure; explicit development admission. See the [handoff](spec/delivery/role-composition-handoff.md).\n- [ ] W-10 native theme authoring and trusted editor admission through existing draft/resource/persistence owners; retain mandatory diagnostics and private-buffer erasure.')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes())
rows=v if isinstance(v,list) else v['work_units']
for row in rows:
 if row['id']=='W-09':
  row['specs'].append('SP-W09-ROLE-COMPOSITION');row['package']='delivery/packages/w-09-role-composition.md';row['evidence']='delivery/role-composition-handoff.md';row['notes']='Theme 0.2 now has explicit semantic roles through the Linux scalar, table, chart and conditional-diagnostic composition paths. Independent literal-font pixels, geometry, contrast, scale and erasure checks pass; existing theme pixels and content identities remain. Direct consumers still need explicit experimental_typography plus resource/capability/policy admission. Continue native theme authoring and trusted editor integration, installed ownership, full accessibility/performance, unresolved historical observation causes, other native adapters and all five complete editions. Preserve original failures and contract-based oracle corrections.'
 if row['id']=='W-10':row['notes']=row['notes'].replace('role-aware typography composition and native theme authoring','native theme authoring and trusted typography integration')
write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
replace('spec/delivery/implementation-readiness.md','Scene composition and native authoring are still explicitly unavailable for\ntheme 0.2; the next package must prove their role mapping and diagnostic behavior.','The [role-composition experiment](role-composition-handoff.md) now verifies scene\nroles with explicit development admission. Native theme authoring and trusted editor\nintegration remain the next gate.')
replace('spec/experience/scene-theme.md','Scene composition must refuse theme 0.2 until role mapping and mandatory diagnostic\npreservation are verified. Native theme authoring remains the following integration\nboundary.','The [role-composition contract](../delivery/packages/w-09-role-composition.md)\nassigns semantic roles and preserves mandatory diagnostics with bounded native\ncomposition. Theme 0.2 requires explicit trusted development admission in addition\nto current resource authority; direct consumers still refuse by default. Native theme\nauthoring and trusted editor integration remain the following boundary.')
replace('docs/developers/build.md','SceneSurface explicitly refuses theme 0.2 pending\nrole-aware composition. Read the [handoff](../../spec/delivery/typography-handoff.md)\nbefore enabling scene integration or adding native theme authoring.','The [role-composition experiment](../../spec/delivery/role-composition-handoff.md)\nnow connects those roles to semantic scene blocks. Set SurfaceConfig.experimental_typography\nonly in a trusted development owner, alongside theme.typography capability/current policy.\nIt defaults false; native authoring and trusted editor integration remain pending.\nRun `ctest --preset linux-x64-gcc13 -R \'^native[.]ROLE-COMPOSITION$\' --output-on-failure`\nafter ordinary workspace preflight/configure/build. The oracle uses literal base fonts\nand independent raw-pixel composition, with exact table rectangles and diagnostic checks.')
with (r/'docs/users/configuration.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\nTheme 0.2 font roles now have verified development scene composition. The editor\nstill needs native font-authoring controls before this becomes an ordinary editing\nfeature. Existing themes and settings remain usable. See the [checkpoint](../../spec/delivery/role-composition-handoff.md).\n')
body=f'''---
type: "SysPane Work Record"
title: "Semantic typography composition checkpoint"
description: "Bounded scene font roles with independent pixels and preserved diagnostics."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-ROLE-COMPOSITION-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W09-ROLE-COMPOSITION", "SP-TYPOGRAPHY-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Semantic typography composition checkpoint

Baseline e5ebf1b2f1d6fb65901d17c6c56e8ca58f01819a. The
[package](packages/w-09-role-composition.md) assigns fonts at semantic construction,
without parsing titles or user text to guess roles. Owned blocks distinguish body,
label, value and diagnostic text. Scalar/table/chart composition retains original
plain/accessibility strings and resource identities. Conditional warnings use the
diagnostic font; unfittable warnings reject the presentation rather than disappear.
Images keep existing bitmap/marker/alt behavior. Legacy themes retain their old path.

Frame and cell blocks count toward existing text bounds. Composites count parts and
output against construction capacity, apply the background once, and retain native
padding, scale, fallback and contrast. Policy loss, hidden payload reset, replacement
and close erase blocks with the old frame; the inspector rejects hidden retained
blocks. Theme 0.2 requires current resource authority plus explicit trusted
experimental_typography. Default refusal, including disabled displays, remains;
ordinary capability advertisement alone cannot enable this development experiment.

## Evidence and corrections

Full portable suites pass 339 Linux GCC13, 336 Windows GCC15 and 333 v141_xp checks
(1008 total); 162 affected checks also pass on each. Native.ROLE-COMPOSITION records
19 passing cases plus an asserted empty-frame case. Independent literal base fonts
produce expected premultiplied pixels and table rectangles, without calling the
production block compositor or adopting its chosen roles. All-body fault witnesses
differ positively. Coverage includes current/pending/failed/retained values, status,
embedded newlines, body, table, chart/window expiry, conditional warnings, contrast,
scale, budgets, admission, replacement/regrant, group propagation and hidden erasure.
Six native typography/text/visibility checks, three editor matrices and fifteen
existing rendering/erasure regressions pass.

Two native attempts originally failed because the new expected examples conflicted
with established contracts. The one-second chart window must expire a sample at
100 ns when time reaches 3000000100 ns, even under a retained lease; its expected
sample/segment counts changed from one to zero. Visibility checks nonactive leases
before freshness, so a disconnected stale input says Source lost while retaining the
Retained | Stale status line. Existing chart/visibility contracts and earlier fixed
examples independently establish both corrections. Production history and visibility
decision logic stayed unchanged. Original examples, all three freeze manifests and
both failure records remain alongside the corrected expectations. The pixel-oracle
algorithm and this package's role/budget/erasure requirements did not change.

The evidence index preserves {len(idx['attempts'])} actual source-bound attempts and
{len(native)} native archives, exact source snapshots, executable identities, runtime
identities, fixed expectations and native observations. Two tested files were converted
from CRLF to canonical LF after execution: the new probe and components.json. The
staging audit proves that each final byte stream equals its archived tested stream
with only CRLF replaced by LF; no semantic edit is hidden in that normalization.
All 184 earlier schema/fixture files remain byte-identical. Specification/fixture,
tooling, generated navigation and sealed integrity results accompany the handoff.

Cleanup reclaimed only 14 verified committed native directories (355175668 bytes)
and 16 committed attempt directories (28098132 bytes). A wider read-only duplicate
search found none eligible and deleted nothing. The 7-GiB allocation is unchanged.
Native results cover the pinned Linux development adapter; historical-toolset checks
on contemporary Windows do not qualify historical systems. The two pre-existing
Windows symlink tooling skips and historical accessibility timeout questions remain.

Evidence: build-support/evidence/w-09-role-composition-attempts.json,
w-09-role-composition-native-index.json, w-09-role-composition-verification.json,
w-09-role-composition-staging.json and role-composition-handoff.json.

## Next boundary

Implement native font/theme authoring through the existing private draft input,
immutable resource publication and durable transaction owners; specify exact theme
version/pin creation, validation, role fallback/reset, preview, undo, Apply/reconcile,
recovery and erasure before enabling the trusted editor path. Preserve the role
composition oracle. Then continue clipboard/recovery drafts, installed desktop
ownership, accessibility/performance and every required native edition. W-09/W-10
remain in progress; no complete release or historical qualification is claimed.
'''
write('spec/delivery/role-composition-handoff.md',body)
print('Updated README, TODO, campaign row, contracts guidance and source-bound handoff.')
