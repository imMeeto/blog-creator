"""Check traceable source coverage and the method actually shipped to both entry paths."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('producer_release', ROOT / 'scripts/build_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
SOURCE = ROOT / 'context/producer-method/source-map.json'


class ProducerMethodTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(SOURCE.read_text(encoding='utf-8'))

    def validate_with_source(self, value):
        original = Path.read_text

        def read_text(path, *args, **kwargs):
            return json.dumps(value) if path == SOURCE else original(path, *args, **kwargs)

        with patch.object(Path, 'read_text', read_text):
            return release.validate()

    def test_source_covers_the_complete_chapter_timeline(self):
        self.assertEqual(self.source['source']['video_id'], 'yq7eQO108QU')
        self.assertEqual(len(self.source['chapters']), 36)
        self.assertEqual(self.source['source']['duration_seconds'], 8174)
        self.assertGreater(self.source['evidence']['transcript']['last_end_seconds'], 8173)
        self.assertFalse(self.source['evidence']['visual_review']['continuous_frame_review'])
        self.assertFalse(self.source['evidence']['case_claims_independently_verified'])
        self.assertEqual(len(release.validate()), 55)

    def test_timeline_gaps_cannot_be_packaged_as_complete(self):
        value = copy.deepcopy(self.source)
        value['chapters'][10]['start_seconds'] += 1
        with self.assertRaises(AssertionError):
            self.validate_with_source(value)

    def test_unimplemented_source_sections_are_rejected(self):
        value = copy.deepcopy(self.source)
        value['chapters'][20]['implementation_refs'] = ['context/producer-method/absent.md']
        with self.assertRaises(AssertionError):
            self.validate_with_source(value)

    def test_method_version_must_match_the_release(self):
        value = copy.deepcopy(self.source)
        value['method_version'] = '0.0.0'
        with self.assertRaises(AssertionError):
            self.validate_with_source(value)

    def test_native_and_portable_paths_ship_the_same_operational_method(self):
        guide = (ROOT / 'START-BLOG.md').read_text(encoding='utf-8')
        with zipfile.ZipFile(release.OUT / f'blog-creator-{release.VERSION}.zip') as archive:
            paths = set(archive.namelist())
            for file in (ROOT / 'context/producer-method').iterdir():
                relative = file.relative_to(ROOT).as_posix()
                self.assertIn(relative, paths)
                self.assertEqual(archive.read(relative), file.read_bytes())
                if re.match(r'\d\d-.*\.md$', file.name):
                    self.assertIn(release.inline_text(file.read_text(encoding='utf-8')), guide)
            for chapter in self.source['chapters']:
                for path in chapter['implementation_refs']:
                    self.assertIn(path, paths)
            self.assertFalse(any('transcript' in p.lower() or 'video-review' in p.lower() for p in paths))
        # The neutral workflow keeps attribution in internal provenance, not automatic output.
        self.assertNotRegex(guide, r'(?i)Тимочк|Митрошин')
        for file in (ROOT / 'skills').glob('*/SKILL.md'):
            self.assertNotRegex(file.read_text(encoding='utf-8'), r'(?i)Тимочк|Митрошин')


if __name__ == '__main__':
    unittest.main()
