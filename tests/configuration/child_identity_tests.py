"""Literal identity traces and replay of the actual installed observer pump."""
import ast
import hashlib
from pathlib import Path
import types
import unittest
from child_identity import sample_identity

ARGV=b'\0'.join([b'syspane-image-worker',b'image/png',b'13',b''])
IMAGE='/memfd:syspane-image-worker (deleted)'
HASH='a'*64


def trace(argv=(ARGV,ARGV), image=(IMAGE,HASH), exits=(False,False)):
    args=iter(argv);states=iter(exits)
    def next_argv():
        value=next(args)
        if isinstance(value,Exception):raise value
        return value
    def executable():
        if isinstance(image,Exception):raise image
        return image
    return sample_identity(next_argv,executable,lambda:next(states),13)


class IdentityTraces(unittest.TestCase):
    def test_verified_literal(self):
        self.assertEqual(trace().record,dict(image=IMAGE,sha256=HASH,argv=['syspane-image-worker','image/png','13']))
    def test_empty_then_complete(self):
        self.assertEqual(trace(argv=(b'',)).reason,'incomplete_argv')
        self.assertEqual(trace().record['argv'],['syspane-image-worker','image/png','13'])
    def test_truncated(self):
        self.assertEqual(trace(argv=(b'syspane-image-worker',)).reason,'incomplete_argv')
        self.assertEqual(trace(argv=(b'\0',)).reason,'incomplete_argv')
    def test_changed_or_empty_second(self):
        for after in (b'',ARGV.replace(b'image/png',b'image/jpeg')):
            with self.subTest(after=after):self.assertEqual(trace(argv=(ARGV,after)).reason,'changing_argv')
    def test_exit_boundaries(self):
        for exits in ((True,),(False,True)):
            with self.subTest(exits=exits):self.assertEqual(trace(exits=exits).reason,'exited')
    def test_disappearance_each_read(self):
        for missing in (FileNotFoundError(),ProcessLookupError()):
            for argv,image in (((missing,), (IMAGE,HASH)),((ARGV,),missing),((ARGV,missing),(IMAGE,HASH))):
                with self.subTest(argv=argv,image=image):self.assertEqual(trace(argv=argv,image=image).reason,'disappeared')
    def test_sandbox_exact_without_hash_claim(self):
        value=trace(image=PermissionError(),exits=(False,False,False))
        self.assertEqual(value.record,dict(image='sandboxed:syspane-image-worker',sha256=None,argv=['syspane-image-worker','image/png','13']))
    def test_exit_during_sandbox_read(self):
        self.assertEqual(trace(image=PermissionError(),exits=(False,True)).reason,'exited')
    def test_wrong_image_tuple_rejected(self):
        for fields in ((b'wrong-role',b'image/png',b'13'),(b'syspane-image-worker',b'wrong-media',b'13'),(b'syspane-image-worker',b'image/png',b'14'),(b'syspane-image-worker',b'image/png'),(b'syspane-image-worker',b'image/png',b'13',b'extra')):
            argv=b'\0'.join([*fields,b''])
            for image,exits in (((IMAGE,HASH),(False,False)),(PermissionError(),(False,False,False))):
                with self.subTest(fields=fields,image=image):
                    with self.assertRaisesRegex(AssertionError,'invalid image child identity'):trace(argv=(argv,argv),image=image,exits=exits)
    def test_unrelated(self):
        self.assertEqual(trace(image=(None,None)).reason,'unrelated')
    def test_oversize_each_argument_read(self):
        for args in ((b'x'*4097,),(ARGV,b'x'*4097)):
            with self.subTest(args=args):
                with self.assertRaisesRegex(AssertionError,'command-line limit'):trace(argv=args)

    def test_real_pump_resamples(self):
        source=Path(__file__).with_name('native_installed_editor.py');tree=ast.parse(source.read_bytes())
        observe=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name=='observe')
        pump=next(v for v in observe.body if isinstance(v,ast.FunctionDef) and v.name=='pump')
        class Node:
            def __init__(self,*parts):self.name='/'.join(str(p) for p in parts)
            def __truediv__(self,n):return Node(self.name,n)
            def iterdir(self):return [Node('task')]
            def read_text(self):return '17'
        state={'argv':b''};report={};fds={};closed=[]
        namespace=dict(timings=lambda:None,extension=True,proc=types.SimpleNamespace(pid=13,poll=lambda:None),Path=Node,helper_pidfds=fds,report=report,os=types.SimpleNamespace(pidfd_open=lambda pid:123,close=closed.append),GLib=types.SimpleNamespace(MainContext=types.SimpleNamespace(default=lambda:types.SimpleNamespace(pending=lambda:False))),observe_child_identity=lambda pid,fd,parent:sample_identity(lambda:state['argv'],lambda:(IMAGE,HASH),lambda:False,parent))
        exec(compile(ast.Module(body=[pump],type_ignores=[]),str(source),'exec'),namespace)
        namespace['pump']();self.assertEqual(fds,{});self.assertEqual(closed,[123]);self.assertNotIn('native_children',report)
        state['argv']=ARGV;namespace['pump']()
        self.assertEqual(fds,{17:123});self.assertEqual(report['native_children'],[dict(pid=17,image=IMAGE,sha256=HASH,argv=['syspane-image-worker','image/png','13'])])
        self.assertEqual(report['child_identity_unqualified'],{'incomplete_argv':1})


if __name__=='__main__':unittest.main(verbosity=2)
