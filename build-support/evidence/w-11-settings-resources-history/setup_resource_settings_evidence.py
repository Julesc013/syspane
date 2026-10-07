from pathlib import Path
r=Path(__file__).resolve().parent
old='b3e1854c20e5bb0b1b101e516ee8610de70d1279';base='252647623e2d56cbc6f2797fb9325d788d9a21d5'
def convert(s):return s.replace('w-11-native-settings','w-11-settings-resources').replace('native-settings-original','resource-settings-original').replace('native-settings-execution-','resource-settings-execution-').replace(old,base)
s=convert((r/'preserve_settings.py').read_text())
a=s.index('helpers=');b=s.index('\nfor p in [',a)
s=s[:a]+"helpers=['resource_settings_step.py','resource_settings_flow.py','archive_resource_settings.py','preserve_resource_settings.py','setup_resource_settings_evidence.py','reclaim_resource_settings_prior.ps1','resource-settings-prior-reclamation.json']"+s[b:]
s=s.replace('==52','==58').replace('==11\n','==17\n')
a=s.index('families=');b=s.index('\nfor family,',a);s=s[:a]+"families={'SETTINGS-FORM':('syspane_settings_window','native_settings.py')}"+s[b:]
s=s.replace("len(report['cases'])==17","len(report['cases'])==18")
s=s.replace("('retain','false-saved')","('retain','false-saved','resource-wrong-selection')")
needle="    assert detail['surface_runtime_sha256']==sha(r/'build-support/surface-runtime.json')"
assert needle in s
s=s.replace(needle,needle+"\n    if c['case'].startswith('resource-'):\n     assert detail['resource_fixture_sha256']==sha(r/'tests/configuration/settings-content-fixture.json')\n     assert detail['resource_cases_sha256']==sha(r/'tests/configuration/settings-content-cases.json')")
a=s.index("with zipfile.ZipFile(history/'original.zip')");b=s.index("write(r/(prefix+'attempts.json')",a)
s=s[:a]+"for n in ('tests/configuration/settings-content-fixture.json','tests/configuration/settings_content_fixture.py'):\n assert sha(r/n)==json.loads((history/'resource-fixture.json').read_text())[n]\n"+s[b:]
s=s.replace("('original','native-original')","('original','resource-fixture','native-original')")
s=s.replace('52 affected settings/authored/policy/dependency checks on each of three development profiles; 11 owned native settings modes and six existing native storage/command families.','58 affected settings/authored/policy/dependency checks on each of three development profiles; 18 owned native settings modes including exact resource selection/bytes and deliberate faults.')
(r/'preserve_resource_settings.py').write_text(s,encoding='utf-8',newline='\n')
s=convert((r/'finish_settings_checks.py').read_text())
needle="commands += [[python,'-X','utf8','-m','unittest','discover','-s','spec/tools/tests','-v']]"
assert needle in s
s=s.replace(needle,"commands += [[python,'-X','utf8','tests/configuration/settings_content_fixture.py','--check']]\n"+needle)
(r/'finish_resource_settings_checks.py').write_text(s,encoding='utf-8',newline='\n')
s=convert((r/'stage_settings.py').read_text()).replace('native-settings-handoff.json','settings-resources-handoff.json').replace('native-settings-staging-paths.txt','resource-settings-staging-paths.txt')
a=s.index("   before=json.loads(z.read('spec/experience/settings-registry.json'))");b=s.index("native=json.loads",a)
s=s[:a]+"  if name=='resource-fixture':\n   for n in ('tests/configuration/settings-content-fixture.json','tests/configuration/settings_content_fixture.py'):check(n,inputs[n])\n"+s[b:]
s=s.replace("('retain','false-saved')","('retain','false-saved','resource-wrong-selection')")
needle="    check('tests/configuration/settings-cases.json',detail['fixture_sha256']);check('build-support/surface-runtime.json',detail['surface_runtime_sha256'])"
assert needle in s
s=s.replace(needle,needle+"\n    if c['case'].startswith('resource-'):\n     check('tests/configuration/settings-content-fixture.json',detail['resource_fixture_sha256']);check('tests/configuration/settings-content-cases.json',detail['resource_cases_sha256'])")
s=s.replace('Owned Linux settings controls and storage outcomes are verified','Owned Linux settings controls, resource identity/bytes and storage outcomes are verified')
(r/'stage_resource_settings.py').write_text(s,encoding='utf-8',newline='\n')
