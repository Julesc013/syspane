from pathlib import Path
import json
import subprocess
import jsonschema
r = Path.cwd()
e = r/'build-support/evidence'
prefix = 'w-10-theme-controls-'
hp = e/'theme-controls-handoff.json'
sp = e/(prefix+'staging.json')

def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')

if not sp.exists():
    write(sp, dict(outcome='not_run'))
index = json.loads((e/(prefix+'attempts.json')).read_bytes())
verification = json.loads((e/(prefix+'verification.json')).read_bytes())
assert all(c['exit'] == 0 for c in verification['checks'])

def check(name, suffix, outcome='pass'):
    return dict(name=name, outcome=outcome, evidence='build-support/evidence/'+prefix+suffix+'.json' if suffix else None)

h = dict(schema_version='0.1.0', work_id='W-10', source_ref=index['source_base'],
         objective='Connect exact native base/role font controls to current draft preview, atomic history and durable save/reopen.', changed_files=[],
         decisions=['Preserve exact no-ops, explicit empty versus omitted role maps and inactive private values.',
                    'Use the current borrowed draft resources for preview, content choices and creation; retain no redundant original catalog.',
                    'Require all seven existing capabilities and large-command admission for trusted EditorForm typography.',
                    'Resolve font-only intrinsic metrics in the queued paint; preserve immediate geometry-edit resolution.',
                    'Verify fixed literal font pixels, exact stored bytes and private erasure with explicit native replies; preserve original oracle and diagnostic failures.'],
         checks=[check('Four font-control families and 187 affected tests per profile', 'attempts'),
                 check('Full portable suites: 364 Linux, 361 Windows GCC15, 358 v141_xp', 'attempts'),
                 check('Nineteen native font cases and ten native regression families', 'native-index'),
                 check('Specification, fixtures, tooling, audited oracle correction and integrity', 'verification'),
                 check('Staged source/oracle/artifact identity', 'staging', 'not_run'),
                 check('Installed desktop ownership and clipboard/recovery drafts', None, 'not_run'),
                 check('Five complete editions and release qualification', None, 'not_run')],
         open_questions=['Historical target floors and Mac laboratories remain unresolved.',
                         'Historical accessibility timeout causes remain unexplained.'],
         next_step='Close bounded clipboard/recovery-draft contracts and installed controller/catalog/policy ownership, then scene-aligned entry/restoration with independent recovery. Continue available independent platform tracks.',
         authority_used=['user:foundation-native-campaign-2026-10-05', 'User-expanded complete SysPane 0.1.0 release objective', 'User instruction to commit and sync main'],
         limitations=['Native controls run in an owned Linux GTK/X11 component laboratory, not an installed complete edition.',
                      'Historical toolset execution on contemporary Windows does not qualify XP.',
                      'Two existing Windows symlink tooling assertions remain skipped.',
                      'Installed ownership, full accessibility/performance, other adapters and all complete-edition gates remain open.'])
paths = set(subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], text=True).splitlines()) | set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()) | {'build-support/evidence/theme-controls-handoff.json'}
h['changed_files'] = sorted(paths)
jsonschema.validate(h, json.loads((r/'spec/contracts/handoff.schema.json').read_bytes()))
write(hp, h)
print('Prepared handoff for', len(paths), 'files.')
