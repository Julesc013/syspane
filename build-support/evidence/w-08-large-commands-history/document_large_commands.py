from pathlib import Path
from datetime import datetime,timezone
import json
r=Path(__file__).resolve().parents[2];stamp=datetime.now(timezone.utc).isoformat()
def edit(name,old,new):
    p=r/name;s=p.read_text(encoding='utf-8');assert old in s,name;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
def prepend(name,heading,body):edit(name,heading,heading+'\n\n'+body)
prepend('README.md','These are development targets; supported versions and release qualification remain open.',
'''The [complete-scene command checkpoint](spec/delivery/large-commands-handoff.md)
carries full 256 KiB scenes through negotiated commands, bounded admission and
crash-safe request receipts. Portable boundary checks and native IPC/storage/editor
cases cover exact replay, cancellation, policy changes and restart. Legacy command
limits remain compatible; installed integration and complete editions remain open.''')
edit('README.md','The full editor, larger-scene command envelope and\ncomplete authoring controls remain required.','The full editor and complete authoring controls remain required; negotiated\nlarge-command support now has the checkpoint above.')
prepend('TODO.md','## First native campaign',
'''- [x] W-08/W-10 complete-scene transport: command 0.5 negotiation and parser bounds, unchanged ledger capacity, explicit draft opt-in and manifest 0.3 request files; portable and independent native checks. See the [handoff](spec/delivery/large-commands-handoff.md).''')
edit('TODO.md','recovery drafts, larger-scene transport, full accessibility/performance','recovery drafts, full accessibility/performance')
prepend('spec/delivery/current-state.md','# Current state and next admitted boundary',
'''The latest [complete-scene command checkpoint](large-commands-handoff.md) closes
the local-scene/wire-size mismatch. Command 0.5, explicit capability negotiation and
manifest 0.3 carry exact full-scene requests through the existing owners. Fixed
boundary inputs and native IPC/storage/GTK checks cover recovery without duplicate
publication. Next close remaining authoring/property contracts and installed
controller/catalog/policy routing, then scene-aligned entry/restoration. Complete
editions, historical labs and release gates remain open.''')
edit('spec/delivery/current-state.md','Next close larger-scene transport and remaining authoring/property boundaries, then','Larger-scene transport now has the checkpoint above. Close remaining authoring/property boundaries, then')
prepend('spec/contracts/commands.md','## Command envelope',
'''[Command 0.5](command-v0.5.schema.json) carries a complete 256 KiB authored scene.
The [complete-scene package](../delivery/packages/w-08-large-commands.md) defines
320 KiB raw/canonical command bounds, explicit negotiation, parser headroom,
unchanged resource policy and exact-body replay. Content is optional for resource-free
scene 0.2; scene 0.3 replacement requires exact content pins. Versions 0.2/0.3/0.4
retain their 16 KiB command limits. No large-command capability implies commit authority.''')
prepend('spec/contracts/transport.md','# '+(r/'spec/contracts/transport.md').read_text().split('\n# ',1)[1].split('\n',1)[0],
'''Command 0.5 additionally requires the exact document version, command-result 0.1,
`configuration.transactions`, `configuration.large-commands` and a negotiated frame
ceiling of at least 328,704 bytes. The [complete-scene package](../delivery/packages/w-08-large-commands.md)
owns its 327,680-byte body and 18,432-node/depth-below-40 wrapper profile. Embedded
scenes retain their own 262,144-byte, 16,384-node/depth-below-32 limits. Other messages
and legacy commands retain their existing parser profile. The 1 MiB frame limit,
incomplete-frame deadline and 16 MiB request ledger remain unchanged. Larger requests
consume more of the existing body-plus-4-KiB reservation; no unexpired result eviction.''')
prepend('spec/architecture/persistence.md','# Configuration persistence and recovery',
'''[Manifest 0.3](../delivery/packages/w-08-large-commands.md) stores an original
command 0.5 in a private `request.json` file, bounded at 327,680 bytes and SHA-256
bound by the manifest identity. Flush and validate it with the complete generation
before selection. Exact file membership, command version, revision, request/intent
and resource pins are verified during recovery. Missing, changed or linked request
files invalidate that generation; fallback remains coherent and read-only. Older
manifest 0.1/0.2 readers and inline 16 KiB identities retain their original contract.''')
prepend('docs/developers/build.md','# Developer setup and checks',
'''The [complete-scene command package](../../spec/delivery/packages/w-08-large-commands.md)
adds command 0.5 and Linux generation manifest 0.3. Pass `large_commands=true` as the
last `SettingsDraft`, `EditorDraft` or `EditorForm` constructor argument only after
the host has negotiated the exact version, features and frame floor. Legacy default
behavior remains unchanged. Do not rewrite an unresolved request on reconnect.
ContentCatalog preview accepts the explicit `configuration.large-commands` capability.

After the ordinary workspace preflight/configure/build, run `ctest --preset <profile>
-R '^(configuration[.]LARGE-|editor[.]|settings[.]|configuration[.]|protocol[.]|composition[.])'
--output-on-failure`. Linux additionally runs `ctest --preset linux-x64-gcc13 -R
'^native[.](LARGE-COMMANDS|CONFIG-STORE|COMMAND-IPC|CONTENT-COMMANDS|RESOURCE-GENERATIONS|SCENE-CONTENT|EDITOR-FORM|SETTINGS-FORM)$'
--output-on-failure` in the declared non-root campaign workspace. The new native
family uses private ext4, authenticated IPC and owned Xvfb/DBus. Its records bind
original request bytes, coherent documents, resource pins and actual process exit.''')
edit('docs/developers/build.md','Local scenes retain their 256 KiB contract, while oversized current wire commands\nreject without discarding the draft. The larger-scene envelope and native editing\nsurface remain required.','Local scenes retain their 256 KiB contract. Legacy oversized commands reject\nwithout discarding the draft; explicitly negotiated command 0.5 supports full scenes.\nThe initial native editing component is recorded in the native editor handoff.')
for name in ('native-editor-handoff.md','editor-draft-handoff.md'):
    p=r/'spec/delivery'/name;s=p.read_text();at=s.index('\n# ');line=s.index('\n',at+1)
    s=s[:line]+'''\n\nSubsequent checkpoint: [complete-scene commands](large-commands-handoff.md) closes
the larger-scene transport limitation recorded below. This page preserves the
original checkpoint and its remaining independent gates.\n'''+s[line:];p.write_text(s,encoding='utf-8',newline='\n')
p=r/'spec/delivery/work-units.json';v=json.loads(p.read_bytes())
for row in v['work_units']:
    if row['id'] in ('W-08','W-10'):
        row['specs'].append('SP-W08-LARGE-COMMANDS');row['notes']=row['notes'].replace('larger-scene commands, ','')
        row['notes']+=' Command 0.5 now carries full authored scenes through explicit negotiation, bounded ledger admission, native requests and manifest 0.3 recovery. See the complete-scene handoff; installed ownership and full work-unit acceptance remain open.'
    if row['id']=='W-08':row['package']='delivery/packages/w-08-large-commands.md';row['evidence']='delivery/large-commands-handoff.md'
p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Updated current specification routing and developer documentation at',stamp)
