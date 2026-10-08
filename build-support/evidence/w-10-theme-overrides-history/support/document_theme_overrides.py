from pathlib import Path
from datetime import datetime,timezone
import json,re
r=Path.cwd();e=r/'build-support/evidence';idx=json.loads((e/'w-10-theme-overrides-attempts.json').read_bytes());now=datetime.now(timezone.utc).isoformat()
def write(n,s):(r/n).write_text(s,encoding='utf-8',newline='\n')
def replace(n,a,b):
 s=(r/n).read_text();assert a in s,(n,a);write(n,s.replace(a,b))
frozen=json.loads((r/'out/campaign/w-10-theme-overrides/fixed-inputs.json').read_bytes())
replace('spec/delivery/packages/w-10-theme-overrides.md','"at": "2026-10-08T04:00:00Z"','"at": "'+frozen['at']+'"')
intro='''The [theme-override checkpoint](LINKtheme-overrides-handoff.md) adds an explicit
versioned resource selection and immutable replacement of one authored theme. It
preserves the original preset/image closure, bounds repeated edits and keeps existing
command/store readers closed to the new format. Durable command/store integration,
atomic editor resource history and native controls remain required. All five complete
editions remain open.

'''
for name,link in [('README.md','spec/delivery/'),('spec/delivery/current-state.md','')]:replace(name,'The [theme-authoring prerequisite]',intro.replace('LINK',link)+'The [theme-authoring prerequisite]')
for name in ('README.md','spec/delivery/current-state.md'):
 replace(name,'Native controls still require a versioned\nresource override and durable command/store integration; these helpers do not save\nor enable edited themes by themselves.','The override component now has the checkpoint above. Native controls still require\ndurable command/store integration; these helpers do not save or enable edited themes\nby themselves.')
s=(r/'spec/delivery/current-state.md').read_text();s=re.sub(r'^updated: .*$', 'updated: '+json.dumps(dict(by='codex',at=now,scope='Bounded versioned theme selection and replacement verified; durable command/store integration remains next')),s,flags=re.M);write('spec/delivery/current-state.md',s)
replace('TODO.md','- [ ] W-10 durable theme editing: versioned exact resource override, command/store publication and replay, atomic draft/history contexts, native font controls and trusted editor admission; preserve mandatory diagnostics and erasure.','- [x] W-10 bounded theme resource override: exact versioned selection, immutable base/image closure, canonical artifact validation, repeated replacement/reset and unchanged capacity limits. See the [handoff](spec/delivery/theme-overrides-handoff.md).\n- [ ] W-10 durable theme editing: versioned command/store publication and replay, atomic draft/history contexts, native font controls and trusted editor admission; preserve mandatory diagnostics and erasure.')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes());row=next(w for w in v['work_units'] if w['id']=='W-10');row['specs'].append('SP-W10-THEME-OVERRIDES');row['package']='delivery/packages/w-10-theme-overrides.md';row['evidence']='delivery/theme-overrides-handoff.md';row['notes']='Versioned theme resource selection and immutable replacement now preserve the original preset/image closure and retain at most one external authored theme. Canonical content/license artifacts, exact pins, collisions, reset, policy and existing depth/package/asset/byte bounds have fixed portable examples. Existing command/store consumers reject the new selection. Next close versioned command/store publication/reconciliation, atomic draft/history resource contexts and native font controls. Installed ownership, full accessibility/performance, unresolved observation causes, other native adapters and all five complete editions remain required.';write('spec/delivery/work-units.json',json.dumps(v,indent=2)+'\n')
replace('spec/delivery/implementation-readiness.md','# Implementation readiness and gates\n\n','# Implementation readiness and gates\n\nThe [theme-override checkpoint](theme-overrides-handoff.md) closes bounded immutable\nresource selection/replacement. Its explicit component API is not yet a negotiated\ncommand or durable generation format; close those next before native controls.\n\n')
replace('spec/delivery/implementation-readiness.md','input and deterministic immutable artifact construction. Durable resource override,\ncommand/store admission, draft/history and native controls remain the next boundary.','input and deterministic immutable artifact construction. Resource overrides now have\nthe checkpoint above; command/store admission, draft/history and native controls remain.')
with (r/'docs/developers/build.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''

The [theme-override package](../../spec/delivery/packages/w-10-theme-overrides.md)
adds explicit `ContentCatalog::theme_resources` for resource selection 0.2 and
`replace_theme_resources` for one immutable authored override or reset. The latter
requires current source/result policy and `configuration.theme-overrides` admission.
It retains `ResourceSet::base_packages()` and validates canonical artifact bytes;
it never appends a preset layer. `ContentCatalog::resources` keeps the legacy shape.
Existing command/store/SettingsDraft consumers reject new selections. Do not route
them through an old command or enable native authoring before the next admission.

After ordinary workspace preflight/configure/build, run
`ctest --preset <profile> -R '^configuration[.]THEME-OVERRIDE-' --output-on-failure`
and the affected/full portable suites. The non-root Linux laboratory runs
`ctest --preset linux-x64-gcc13 -R '^native[.](RESOURCE-GENERATIONS|CONTENT-COMMANDS)$'
--output-on-failure` for legacy consumer regressions. These native checks do not
qualify storage of new selections. See the [handoff](../../spec/delivery/theme-overrides-handoff.md).
''')
with (r/'spec/experience/scene-theme.md').open('a',encoding='utf-8',newline='\n') as f:f.write('''

The [bounded theme override contract](../delivery/packages/w-10-theme-overrides.md)
defines exact resource selection 0.2 and immutable replacement/reset beside the
original preset closure. The explicit component API preserves image references and
does not enable a wire command, native authoring or new generation recovery. Those
require their own versioned admission and interrupted/replayed transaction evidence.
''')
write('spec/delivery/theme-overrides-handoff.md',f'''---
type: "SysPane Work Record"
title: "Bounded theme resource override checkpoint"
description: "Versioned immutable selection and replacement before durable command/store integration."
tags: ["delivery", "experience", "assurance"]
status: "draft"
generated: {{"by": "codex", "at": "{now}"}}
sp_id: "SP-THEME-OVERRIDES-HANDOFF"
sp_profile: "syspane-spec/0.1.0"
sp_authority: "informative"
sp_requires: ["SP-W10-THEME-OVERRIDES", "SP-THEME-AUTHORING-HANDOFF"]
sp_review: "unreviewed"
sp_sources: ["SRC-CONVERSATION"]
---

# Bounded theme resource override checkpoint

Baseline {idx['source_base']}. The [package](packages/w-10-theme-overrides.md)
defines resource selection 0.2 with exact original package/preset pins and one
optional authored theme override. An explicit resolver retains the base closure
and requires exact canonical content/license artifact bytes, package/document pins
and candidate binding. A separate pure replacement helper keeps one external theme,
supports reset and authorizes source/result policy. Original images and packages
stay unchanged, including when the same canonical artifact already belongs to base.

The existing resources API rejects the new shape; theme_resources rejects the old
shape. All old command versions reject versioned selections. Native storage and
commands continue using the legacy resolver, so this checkpoint does not claim new
theme persistence or native font controls. No historical contract fixture changed.

## Executed verification

The package, schema, literal closure/selection examples and referenced independent
theme artifact bytes were frozen before production changes. Six structural fixtures
cover valid replacement/reset and malformed versions, digests, missing fields and
multiple overrides. Four portable families cover exact image/base preservation,
canonical bytes and mutable-struct tampering, pin and document/package collisions,
current policy, reset, reordered catalogs and 70 bounded replacements.

Capacity cases admit 63 base packages plus one override, reject 64 plus one, retain
an eight-deep base without adding a dependency layer, and reject an additional asset
at exactly 1024 assets or 64 MiB. Rejections leave existing snapshots and candidate
documents unchanged. Existing product bounds are unchanged.

All 170 affected tests pass on each development profile. Full portable suites pass
347 Linux GCC13, 344 Windows GCC15 and 341 v141_xp checks (1032 total). Native
RESOURCE-GENERATIONS and CONTENT-COMMANDS regressions pass for existing formats.
These are not new-format durable tests. The historical compiler ran on contemporary
Windows, not XP. The two existing Windows symlink tooling assertions remain skipped.

Evidence under build-support/evidence uses prefix w-10-theme-overrides: attempts,
native-index, verification, staging and theme-overrides-handoff.json. The attempts
index retains {len(idx['attempts'])} exact source-bound executions, fixed inputs,
artifact identities and all original outcomes. Schema/fixture checks, generated
navigation, spec-tool tests, sealed integrity and staged-byte verification accompany
the handoff. All 184 baseline schema/fixture files retain their original bytes.
The package's initial generated.at placeholder was corrected to the actual freeze
timestamp after testing; archived originals remain and its contract text is identical.
Verified committed duplicate attempts/native outputs were reclaimed inside the
existing 7-GiB development allocation; receipts preserve the exact cleanup scope.

## Next admitted work

Close a negotiated command version that carries exact authored theme intent/artifact
identity, validates it against the current source and policy, and publishes a new
versioned generation/resource index. Preserve base/image bytes, single-override
capacity, original request bytes and no-duplicate-revision reconciliation. Freeze
interruption, corruption, unavailable-import, repeated edit, reset and lost-result
cases before implementation. Existing formats must retain refusal of the new fields.

Then carry resource contexts atomically through editor history, Apply, cancellation,
unknown results, restart/reconcile and reload. Complete native base/role font controls,
private-buffer erasure and independent preview/save/reopen evidence before trusted
EditorForm typography is enabled. Installed ownership, full accessibility/performance,
other native adapters and all five complete editions remain required. W-10 and the
full release goal remain in progress.
''')
with (r/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n# Preserve exact theme override attempts, fixed expectations and helper bytes.\nbuild-support/evidence/w-10-theme-overrides-history/** -text whitespace=cr-at-eol\nbuild-support/evidence/w-10-theme-overrides-history/support/*.ps1 -whitespace\n')
