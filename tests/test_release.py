import importlib.util
import hashlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release", BASE / "scripts/build_release.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReleaseTests(unittest.TestCase):
    def test_complete_components_and_links(self):
        self.assertEqual(len(module.validate()), 55)

    def test_onboarding_modes_and_scope(self):
        text = (module.ROOT / "skills/blog-start/SKILL.md").read_text(encoding="utf-8")
        for phrase in ["midi.film", "https://instagram.com/midi.film", "https://t.me/midifilm",
                       "голосом или текстом", "не создавать дубликат", "установка недоступна",
                       "аудит", "Только подтверждённый результат", "Не путай Plugin Creator"]:
            self.assertIn(phrase, text)
        self.assertNotIn("автоматически установлен", text)

    def test_generation_constraints(self):
        text = (module.ROOT / "context/10-blog-runtime.md").read_text(encoding="utf-8")
        for phrase in ["Оригинальные", "оригинальные фотографии", "точный фрагмент сценария",
                       "Не добавляй", "пакета", "не снижает", "1080×1920", "Согласования"]:
            if phrase != "Оригинальные":
                self.assertIn(phrase, text)

    def test_runtime_on_all_imported_skills(self):
        files = [p for p in (module.ROOT / "skills").glob("*/SKILL.md")
                 if p.parent.name.startswith("cp-") or p.parent.name == "content-producer"]
        self.assertEqual(len(files), 45)
        for file in files:
            self.assertEqual(file.read_text(encoding="utf-8").count(module.POINTER), 1)

    def test_native_archive_contains_one_plugin(self):
        with zipfile.ZipFile(module.OUT / f"blog-creator-{module.VERSION}.zip") as archive:
            names = archive.namelist()
            self.assertIn("plugin.json", names)
            self.assertNotIn(".claude-plugin/marketplace.json", names)
            self.assertEqual(archive.testzip(), None)
            self.assertEqual(json.loads(archive.read("plugin.json"))["version"], module.VERSION)
            self.assertNotIn("brands/midifilm/", "\n".join(names))
            skill_names = {name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md")}
            self.assertEqual(len(skill_names), 55)
            self.assertIn("skills/reels-storyboard-method/SKILL.md", skill_names)
            for path in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                self.assertEqual(json.loads(archive.read(path))["version"], module.VERSION)
            for file in module.files_for_package():
                self.assertEqual(archive.read(file.relative_to(module.ROOT).as_posix()), file.read_bytes())

    def test_portable_guide_is_self_contained_for_core(self):
        text = (module.ROOT / "START-BLOG.md").read_text(encoding="utf-8")
        self.assertIn("Шаблон состояния", text)
        self.assertIn("Пример воронки", text)
        self.assertIn("без", text)
        self.assertIn("45 дополнительных", text)
        self.assertIn("https://t.me/midifilm", text)
        self.assertIn("# Навык reels-storyboard-method", text)
        self.assertIn("| Текст | Кадр |", text)
        self.assertIn("## Семь архетипов", text)
        self.assertIn("Восемь видов зацепки", text)
        self.assertNotIn("сценарий blog-scripts остаётся в трёх колонках", text)

    def test_portable_guide_matches_generator(self):
        self.assertEqual((module.ROOT / "START-BLOG.md").read_text(encoding="utf-8"), module.portable_guide_text())

    def test_marketplace_version_mismatch_is_rejected(self):
        original = Path.read_text
        marketplace = module.ROOT / ".claude-plugin/marketplace.json"

        def read_text(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path == marketplace:
                value = json.loads(text)
                value["plugins"][0]["version"] = "0.0.0"
                return json.dumps(value)
            return text

        with patch.object(Path, "read_text", read_text):
            with self.assertRaises(AssertionError):
                module.validate()

    def test_kit_contains_exact_native_archive_and_guide(self):
        native = module.OUT / f"blog-creator-{module.VERSION}.zip"
        with zipfile.ZipFile(module.OUT / f"blog-from-zero-kit-{module.VERSION}.zip") as kit:
            self.assertIsNone(kit.testzip())
            self.assertEqual(kit.read(native.name), native.read_bytes())
            self.assertEqual(kit.read("START-BLOG.md"), (module.ROOT / "START-BLOG.md").read_bytes())
            with zipfile.ZipFile(io.BytesIO(kit.read(native.name))) as nested:
                self.assertIn("skills/reels-storyboard-method/SKILL.md", nested.namelist())

    def test_download_aliases_and_checksums(self):
        native = (module.OUT / f"blog-creator-{module.VERSION}.zip").read_bytes()
        for name in ("blog-creator.zip", "blog-from-zero.zip"):
            self.assertEqual((module.OUT / name).read_bytes(), native)
        entries = (module.OUT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        expected = {"blog-creator.zip", "blog-from-zero.zip", "blog-from-zero-kit.zip", "START-BLOG.md", "INSTALL.md"}
        self.assertEqual({line.split("  ", 1)[1] for line in entries}, expected)
        for line in entries:
            digest, name = line.split("  ", 1)
            self.assertEqual(hashlib.sha256((module.OUT / name).read_bytes()).hexdigest(), digest)

if __name__ == "__main__":
    unittest.main()
