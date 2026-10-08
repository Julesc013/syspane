"""Executed tests cover specification tooling/fixtures, not a native SysPane app."""
from __future__ import annotations
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import specctl as s
HAVE_SCHEMAS=importlib.util.find_spec('jsonschema') is not None and importlib.util.find_spec('referencing') is not None

class PureFunctions(unittest.TestCase):
    def test_json_duplicate_keys_rejected(self):
        with self.assertRaises(s.SpecError):s.strict_json('{"x":1,"x":2}')
    def test_nested_duplicate_keys_rejected(self):
        with self.assertRaises(s.SpecError):s.strict_json('{"x":{"y":1,"y":2}}')
    def test_nonfinite_rejected(self):
        for text in ('NaN','Infinity','-Infinity','1e999'):
            with self.subTest(text=text),self.assertRaises(s.SpecError):s.strict_json(text)
    def test_frontmatter_json_flow(self):
        m,b=s.metadata('---\ntype: "Example"\ntags: ["one", "two"]\n---\n# Body\n')
        self.assertEqual(m['tags'],['one','two']);self.assertTrue(b.startswith('# Body'))
    def test_frontmatter_duplicate_rejected(self):
        with self.assertRaises(s.SpecError):s.metadata('---\ntype: "A"\ntype: "B"\n---\n')
    def test_general_yaml_not_falsely_accepted(self):
        with self.assertRaises(ValueError):s.metadata('---\ntype: bare YAML scalar\n---\n')
    def test_metadata_unknown_extension_preserved(self):
        m,_=s.metadata('---\ntype: "A"\ncustom_key: {"v": 3}\n---\n')
        self.assertEqual(m['custom_key'],{'v':3})
    def test_dag_cycle_rejected(self):
        with self.assertRaises(s.SpecError):s.check_dag({'a':['b'],'b':['a']})
    def test_dag_unknown_rejected(self):
        with self.assertRaises(s.SpecError):s.check_dag({'a':['missing']})
    def test_dag_valid(self):
        s.check_dag({'a':[],'b':['a'],'c':['a'],'d':['b','c']})
    def test_uint64_overflow(self):
        self.assertIn('uint64 overflow',s.semantic_errors({'value':{'kind':'uint64','data':'18446744073709551616'}},'observation'))
    def test_uint64_maximum(self):
        self.assertEqual(s.semantic_errors({'value':{'kind':'uint64','data':'18446744073709551615'}},'observation'),[])
    def test_recovery_digest_is_not_a_counter(self):
        digest='4'*64
        self.assertEqual(s.semantic_errors({'identity':{'generation':digest}},'editor-recovery'),[])
        for value, schema in [({'identity':{'generation':digest}},'observation'),
                              ({'generation':digest},'editor-recovery'),
                              ({'nested':[{'identity':{'generation':digest}}]},'editor-recovery'),
                              ({'identity':{'revision':digest}},'editor-recovery')]:
            with self.subTest(value=value,schema=schema):
                self.assertIn('uint64 overflow',s.semantic_errors(value,schema))
    def test_evidence_pass_requires_execution(self):
        self.assertTrue(s.semantic_errors({'outcome':'pass','executed_at':None},'evidence'))
    def test_unimplemented_capability_not_qualified(self):
        self.assertTrue(s.semantic_errors({'capabilities':[{'qualification':'qualified','implemented':False}]},'capability'))
    def test_heading_anchors(self):
        self.assertEqual(s.anchors('# Hello World\n## Hello World\n'),{'hello-world','hello-world-1'})

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='syspane-spec-test-')
        self.base=Path(self.temp.name)
        self.root=self.base/'spec'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    def tearDown(self):
        self.temp.cleanup()
    def write_json(self,rel,value):
        (self.root/rel).write_bytes(s.json_bytes(value))
    def directory_symlink(self, link, target):
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            if getattr(exc, 'winerror', None) == 1314:
                self.skipTest('Windows identity lacks symlink creation privilege; assertion not executed')
            raise
    def test_bundle_structural_validation(self):
        result=s.validate_bundle(self.root)
        self.assertEqual(result['status'],'pass',result['errors'])
        self.assertEqual(result['native_tests_executed'],0)
    def test_paths_reject_escape_and_windows_devices(self):
        for path in ('../outside','/absolute','C:/outside','x\\y','.git/config','NUL','folder/CON.txt','a/../b','x?.json'):
            with self.subTest(path=path),self.assertRaises(s.SpecError):s.safe_path(self.root,path)
    def test_symlink_rejected(self):
        outside=self.base/'outside';outside.mkdir()
        self.directory_symlink(self.root/'escape', outside)
        with self.assertRaises(s.SpecError):s.safe_path(self.root,'escape/data.json')
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_broken_link_fails(self):
        p=self.root/'product/charter.md';p.write_text(p.read_text(encoding='utf-8')+'\n[bad](missing.md)\n',encoding='utf-8')
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_duplicate_concept_id_fails(self):
        shutil.copyfile(self.root/'product/charter.md',self.root/'product/duplicate.md')
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_missing_requirement_test_fails(self):
        x=s.read_json(self.root/'requirements/catalog.json');x['requirements'][0]['tests']=['T-MISSING']
        self.write_json('requirements/catalog.json',x)
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_work_dependency_cycle_fails(self):
        x=s.read_json(self.root/'delivery/work-units.json');x['work_units'][0]['depends_on']=['W-01']
        self.write_json('delivery/work-units.json',x)
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_fake_native_result_in_plan_fails(self):
        x=s.read_json(self.root/'assurance/tests.json');x['tests'][0]['execution']='pass'
        self.write_json('assurance/tests.json',x)
        self.assertEqual(s.validate_bundle(self.root)['status'],'fail')
    def test_generated_is_deterministic(self):
        s.generate(self.root)
        before=s.generated_payloads(self.root)
        s.generate(self.root)
        self.assertEqual(before,s.generated_payloads(self.root))
        self.assertEqual(s.generate(self.root,True)['status'],'pass')
    def test_generated_detects_drift(self):
        s.generate(self.root)
        p=self.root/'product/charter.md';p.write_text(p.read_text(encoding='utf-8')+'\nChanged explanatory note.\n',encoding='utf-8')
        self.assertEqual(s.generate(self.root,True)['status'],'fail')
    def test_context_mandatory_not_truncated(self):
        with self.assertRaisesRegex(s.SpecError,'nothing was silently truncated'):
            s.context_packet(self.root,'network',100)
    def context_fixture(self):
        # Exercise packet accounting with fixed inputs, not a size assumption
        # about the growing delivery history in the real network route.
        root=self.base/'context';root.mkdir()
        for name in ('tools','requirements','assurance','delivery'):(root/name).mkdir()
        (root/'required.md').write_text('---\nsp_id: "FIXTURE"\n---\n# Required\nComplete required body.\n',encoding='utf-8')
        (root/'optional.txt').write_text('Optional body.\n'*1000,encoding='utf-8')
        for path,value in {
            'tools/routes.json':{'core':['required.md'],'topics':{'network':{'required':['required.md'],'optional':['optional.txt']}}},
            'requirements/catalog.json':{'requirements':[{'id':'R-FIXTURE','owner':'FIXTURE','statement':'Complete required body.','tests':['T-FIXTURE']}]},
            'assurance/tests.json':{'tests':[{'id':'T-FIXTURE','execution':'not_run'}]},
            'delivery/work-units.json':{'work_units':[]}
        }.items():(root/path).write_bytes(s.json_bytes(value))
        return root
    def test_context_budget_and_hashes(self):
        root=self.context_fixture()
        text,manifest=s.context_packet(root,'network',4096)
        self.assertLessEqual(len(text),4096)
        self.assertEqual(manifest['actual_characters'],len(text))
        self.assertEqual(manifest['mandatory'],['required.md'])
        self.assertEqual([x['path'] for x in manifest['included']],['required.md'])
        self.assertEqual(manifest['omitted_optional'],['optional.txt'])
        self.assertIn((root/'required.md').read_text(encoding='utf-8'),text)
        self.assertIn('R-FIXTURE',text);self.assertIn('T-FIXTURE',text)
        for item in manifest['included']:
            self.assertEqual(item['sha256'],s.sha((root/item['path']).read_bytes()))
        self.assertIsNone(manifest['git']['commit'])
    def test_context_exact_budget_boundary(self):
        root=self.context_fixture()
        text,_=s.context_packet(root,'network',4096)
        # Keep the budget's serialized digit count constant at this boundary.
        self.assertGreater(len(text),1000)
        self.assertLess(len(text),4096)
        exact,manifest=s.context_packet(root,'network',len(text))
        self.assertEqual(len(exact),len(text))
        self.assertEqual(manifest['character_budget'],len(exact))
        with self.assertRaisesRegex(s.SpecError,'nothing was silently truncated'):
            s.context_packet(root,'network',len(text)-1)
    def test_context_unknown_topic(self):
        with self.assertRaises(s.SpecError):s.context_packet(self.root,'nonexistent',65000)
    def test_context_changed_source_changes_packet(self):
        root=self.context_fixture()
        a,ma=s.context_packet(root,'network',4096)
        p=root/'required.md';p.write_text(p.read_text(encoding='utf-8')+'\nNew source note.\n',encoding='utf-8')
        b,mb=s.context_packet(root,'network',4096)
        self.assertNotEqual(a,b)
        self.assertNotEqual(ma['included'][0]['sha256'],mb['included'][0]['sha256'])
    def test_output_cannot_overwrite_spec(self):
        with self.assertRaises(s.SpecError):s.output_file(self.root/'oops.md',b'x',self.root)
    def test_output_refuses_different_existing_file(self):
        p=self.base/'packet.md';p.write_bytes(b'old')
        with self.assertRaises(s.SpecError):s.output_file(p,b'new',self.root)
        self.assertEqual(p.read_bytes(),b'old')
    def test_impact_candidates(self):
        x=s.impact(self.root,'spec/telemetry/network.md')
        self.assertIn('T-NETWORK',x['candidate_tests'])
        self.assertTrue(any(r.startswith('R-NETWORK-') for r in x['candidate_requirements']))
    def test_ready_is_not_authorized(self):
        # Exercise readiness with a controlled fixture, independent of actual
        # campaign progress. Completed work must not make this test stale.
        fixture={'work_units':[
            {'id':'prerequisite','status':'in_progress','depends_on':[],'execution_grant':'fixture-only'},
            {'id':'dependent','status':'planned','depends_on':['prerequisite'],'execution_grant':None},
            {'id':'independent','status':'planned','depends_on':[],'execution_grant':None}]}
        self.write_json('delivery/work-units.json',fixture)
        ready=s.work_ready(self.root)
        self.assertEqual([w['id'] for w in ready],['independent'])
        self.assertIsNone(ready[0]['execution_grant'])
        fixture['work_units'][0]['status']='complete'
        self.write_json('delivery/work-units.json',fixture)
        ready=s.work_ready(self.root)
        self.assertEqual([w['id'] for w in ready],['dependent','independent'])
        self.assertTrue(all(w['execution_grant'] is None for w in ready))
        self.assertEqual(s.read_json(self.root/'delivery/work-units.json'),fixture)
    def test_integrity_success_and_tamper(self):
        (self.root/'checksums.json').write_bytes(s.json_bytes(s.integrity_payload(self.root)))
        self.assertEqual(s.verify_integrity(self.root)['status'],'pass')
        p=self.root/'README.md';p.write_bytes(p.read_bytes()+b'\nTampered.\n')
        self.assertIn('README.md',s.verify_integrity(self.root)['changed'])
    def test_integrity_unexpected_file(self):
        (self.root/'checksums.json').write_bytes(s.json_bytes(s.integrity_payload(self.root)))
        (self.root/'unexpected.txt').write_text('new')
        self.assertIn('unexpected.txt',s.verify_integrity(self.root)['added'])
    def test_bootstrap_preview_no_writes(self):
        repo=self.base/'repo';repo.mkdir()
        x=s.bootstrap(self.root,repo)
        self.assertEqual(x['mode'],'preview');self.assertEqual(list(repo.iterdir()),[])
    def test_bootstrap_apply_idempotent(self):
        repo=self.base/'repo';repo.mkdir()
        s.bootstrap(self.root,repo,True)
        self.assertTrue((repo/'AGENTS.md').is_file())
        x=s.bootstrap(self.root,repo,True)
        self.assertTrue(all(f['action']=='unchanged' for f in x['files']))
    def test_bootstrap_conflict_no_partial_writes(self):
        repo=self.base/'repo';repo.mkdir();(repo/'README.md').write_text('owned by user')
        with self.assertRaises(s.SpecError):s.bootstrap(self.root,repo,True)
        self.assertFalse((repo/'AGENTS.md').exists())
        self.assertEqual((repo/'README.md').read_text(),'owned by user')
    def test_bootstrap_symlink_parent_refused(self):
        repo=self.base/'repo';repo.mkdir();outside=self.base/'outside';outside.mkdir()
        self.directory_symlink(repo/'docs', outside)
        with self.assertRaises(s.SpecError):s.bootstrap(self.root,repo,True)
        self.assertEqual(list(outside.iterdir()),[])
        self.assertFalse((repo/'AGENTS.md').exists())
    def test_cli_invalid_root_nonzero(self):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            code=s.main(['--root',str(self.base/'missing'),'validate'])
        self.assertEqual(code,2)
    @unittest.skipUnless(HAVE_SCHEMAS,'full schema dependencies not installed; core tests remain available')
    def test_full_fixture_conformance(self):
        x=s.validate_fixtures(self.root)
        self.assertEqual(x['status'],'pass',x)
        self.assertGreater(x['fixture_count'],20)
    @unittest.skipUnless(HAVE_SCHEMAS,'full schema dependencies not installed')
    def test_recovery_generation_digest_shape(self):
        validators=s.schema_validators(self.root)
        value=s.read_json(self.root/'fixtures/valid/editor-recovery.json')
        for digest in ('4'*64,'f'*64,'a1'*32):
            value['identity']['generation']=digest
            self.assertFalse(list(validators['editor-recovery'].iter_errors(value)))
            self.assertEqual(s.semantic_errors(value,'editor-recovery',self.root),[])
        for digest in ('4'*63,'4'*65,'A'*64,'g'*64,'../current.json',40):
            value['identity']['generation']=digest
            self.assertTrue(list(validators['editor-recovery'].iter_errors(value)))
    @unittest.skipUnless(HAVE_SCHEMAS,'full schema dependencies not installed')
    def test_schema_unknown_ref_fails_offline(self):
        p=self.root/'contracts/theme.schema.json';x=s.read_json(p);x['$ref']='https://untrusted.invalid/schema'
        p.write_bytes(s.json_bytes(x))
        with self.assertRaisesRegex(s.SpecError,'nonlocal'):
            s.schema_validators(self.root)
    def test_setting_default_wrong_type_rejected(self):
        value=s.read_json(self.root/'experience/settings-registry.json')
        value['settings'][0]['default']='1000'
        self.write_json('experience/settings-registry.json', value)
        self.assertTrue(any('wrong type' in e for e in s.validate_settings(self.root)))
    def test_boolean_is_not_integer_setting(self):
        self.assertTrue(s.setting_value_errors(True, {'type':'integer','minimum':1,'maximum':32}))
    def test_mathematical_integer_setting_matches_json_schema(self):
        rule = {'type':'integer','minimum':1,'maximum':32}
        self.assertEqual(s.setting_value_errors(1.0, rule), [])
        for invalid in (1.5, float('inf'), float('nan'), 33.0):
            self.assertTrue(s.setting_value_errors(invalid, rule))
    def test_duplicate_policy_projection_rejected(self):
        value = s.read_json(self.root/'fixtures/valid/policy.json')
        value['disclosure'].append(dict(value['disclosure'][0], allow_classifications=[]))
        self.assertIn('duplicate policy role/channel rule', s.semantic_errors(value, 'policy', self.root))
    def test_setting_default_outside_bounds_rejected(self):
        value=s.read_json(self.root/'experience/settings-registry.json')
        value['settings'][0]['default']=1
        self.write_json('experience/settings-registry.json', value)
        self.assertTrue(any('outside bounds' in e for e in s.validate_settings(self.root)))
    def test_descriptor_enum_member_type_rejected(self):
        value=s.read_json(self.root/'experience/settings-registry.json')
        value['settings'][0]['constraints']['enum']=[1000,'fast']
        self.write_json('experience/settings-registry.json', value)
        self.assertTrue(any('invalid enum member' in e for e in s.validate_settings(self.root)))
    def test_descriptor_dependency_cycle_rejected(self):
        value=s.read_json(self.root/'experience/settings-registry.json')
        row=value['settings'][0]; row['dependencies']=[row['id']]
        self.write_json('experience/settings-registry.json', value)
        with self.assertRaises(s.SpecError): s.validate_settings(self.root)
    def test_setting_schema_drift_rejected_and_regenerated(self):
        value=s.read_json(self.root/'contracts/settings.schema.json')
        value['properties']['sampling']['properties']['resources_ms']['minimum']=1
        self.write_json('contracts/settings.schema.json', value)
        self.assertTrue(any('projection drift' in e for e in s.validate_settings(self.root)))
        s.generate(self.root)
        self.assertEqual(s.validate_settings(self.root), [])
    def test_command_constraint_drift_rejected(self):
        for name in ('command-v0.2', 'command-v0.3', 'command-v0.4','command-v0.5'):
            with self.subTest(name=name):
                path=f'contracts/{name}.schema.json'
                original=s.read_json(self.root/path);value=copy.deepcopy(original)
                value['properties']['operations']['items']['oneOf'][0]['properties']['value']['type']='string'
                self.write_json(path, value)
                self.assertTrue(any('projection drift' in e for e in s.validate_settings(self.root)))
                self.write_json(path, original)
    def test_scene_content_semantics(self):
        value=s.read_json(self.root/'fixtures/valid/scene-content.json')
        self.assertEqual(s.semantic_errors(value,'scene-v0.3',self.root),[])
        for body in ('\x7f','\u0085','\n'*64):
            changed=copy.deepcopy(value);changed['widgets'][0]['content']['body']=body
            self.assertTrue(s.semantic_errors(changed,'scene-v0.3',self.root))
        for path in ('images/CON.png','images/pixel.','images//pixel.png'):
            changed=copy.deepcopy(value);changed['widgets'][6]['content']['asset']['path']=path
            self.assertTrue(s.semantic_errors(changed,'scene-v0.3',self.root))
    def test_scene_content_versions(self):
        validators=s.schema_validators(self.root)
        value=s.read_json(self.root/'fixtures/valid/scene-content.json')
        self.assertFalse(list(validators['scene-v0.3'].iter_errors(value)))
        self.assertTrue(list(validators['scene-v0.2'].iter_errors(value)))
        command=s.read_json(self.root/'fixtures/valid/command-content-scene.json')
        self.assertFalse(list(validators['command-v0.4'].iter_errors(command)))
        command['schema_version']='0.3.0'
        self.assertTrue(list(validators['command-v0.3'].iter_errors(command)))
    def test_scene_nesting_bound(self):
        value=s.read_json(self.root/'fixtures/valid/scene-portable.json')
        group=value['widgets'][0]
        value['roots']=['g0'];value['widgets']=[]
        for n in range(17):
            value['widgets'].append({**group,'id':f'g{n}','children':[f'g{n+1}'] if n<16 else []})
        self.assertIn('scene nesting exceeds 16',s.semantic_errors(value,'scene-v0.2',self.root))
    def test_scene_duplicate_owner_rejected(self):
        value=s.read_json(self.root/'fixtures/valid/scene-portable.json')
        value['roots'].append('widget:adapters')
        self.assertTrue(s.semantic_errors(value,'scene-v0.2',self.root))
    def test_migration_fixture_preserves_authored_intent(self):
        old=s.read_json(self.root/'fixtures/valid/scene.json')
        new=s.read_json(self.root/'fixtures/valid/scene-migrated-0.1.json')
        self.assertEqual((old['scene_id'],old['revision'],old['theme_id']),
                         (new['scene_id'],new['revision'],new['theme_id']))
        self.assertEqual(new['roots'],[w['id'] for w in old['widgets']])
        for before,after in zip(old['widgets'],new['widgets'],strict=True):
            self.assertEqual(before['id'],after['id'])
            self.assertEqual(before['display_id'],after['display']['local_id'])
            self.assertEqual(before['layout'],{k:v for k,v in after['layout']['base'].items() if k!='kind'})
            self.assertEqual(before['bindings'],[{'entity_id':b['entity_id'],'field':b['field']} for b in after['bindings']])
            self.assertTrue(all(b['kind']=='unresolved_pin' for b in after['bindings']))
    def test_native_verticals_are_independent_with_early_safety(self):
        work=s.registries(self.root)[2]
        def ancestors(wid):
            result=set(work[wid]['depends_on'])
            for parent in work[wid]['depends_on']: result.update(ancestors(parent))
            return result
        for vertical,host in [('W-27','W-03'),('W-28','W-04'),('W-29','W-05'),('W-30','W-06')]:
            dependencies=ancestors(vertical)
            self.assertTrue({host,'W-24','W-25','W-26'} <= dependencies)
            self.assertFalse(dependencies & ({'W-03','W-04','W-05','W-06'}-{host}))
            self.assertFalse(dependencies & {'W-12','W-13','W-20','W-21'})
    @unittest.skipUnless(HAVE_SCHEMAS,'full schema dependencies not installed')
    def test_timestamp_offset_required_without_optional_format_package(self):
        validator=s.schema_validators(self.root)['observation']
        value=s.read_json(self.root/'fixtures/invalid/timestamp-without-offset.json')
        self.assertTrue(list(validator.iter_errors(value)))
    @unittest.skipUnless(HAVE_SCHEMAS,'full schema dependencies not installed')
    def test_scene_versions_remain_distinct(self):
        validators=s.schema_validators(self.root)
        legacy=s.read_json(self.root/'fixtures/valid/scene.json')
        portable=s.read_json(self.root/'fixtures/valid/scene-portable.json')
        self.assertFalse(list(validators['scene'].iter_errors(legacy)))
        self.assertFalse(list(validators['scene-v0.2'].iter_errors(portable)))
        self.assertTrue(list(validators['scene'].iter_errors(portable)))
        self.assertTrue(list(validators['scene-v0.2'].iter_errors(legacy)))

if __name__=='__main__':unittest.main()
