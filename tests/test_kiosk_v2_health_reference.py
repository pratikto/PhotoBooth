"""Pin actual existing Device Health source/UI/worker rather than recreating them."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class HealthReferenceTests(unittest.TestCase):
    def test_all_original_backend_panel_and_tests_are_unchanged(self):
        data=json.loads((ROOT/'docs/qa/portrait-v2-operator-health/reused-source.json').read_text())
        for file,sha in data['files'].items():
            with self.subTest(file=file):
                self.assertEqual(hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),sha)

    def test_controller_worker_is_the_verbatim_v1_method(self):
        data=json.loads((ROOT/'docs/qa/portrait-v2-operator-health/reused-source.json').read_text())
        for item in data['extracted_methods']:
            raw=(ROOT/item['target_file']).read_text()
            cls=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef) and n.name==item['target_class'])
            method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==item['method'])
            region='\n'.join(raw.splitlines()[method.lineno-1:method.end_lineno])+'\n'
            self.assertEqual(hashlib.sha256(region.encode()).hexdigest(),item['method_sha256'])
