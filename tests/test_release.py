import importlib.util
import json
from pathlib import Path
import unittest
import zipfile

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release", BASE / "scripts/build_release.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReleaseTests(unittest.TestCase):
    def test_complete_components_and_links(self):
        self.assertEqual(len(module.validate()), 54)

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
        with zipfile.ZipFile(module.OUT / "blog-from-zero-1.1.1.zip") as archive:
            names = archive.namelist()
            self.assertIn("plugin.json", names)
            self.assertNotIn(".claude-plugin/marketplace.json", names)
            self.assertEqual(archive.testzip(), None)
            self.assertEqual(json.loads(archive.read("plugin.json"))["version"], "1.1.1")
            self.assertNotIn("brands/midifilm/", "\n".join(names))

    def test_portable_guide_is_self_contained_for_core(self):
        text = (module.ROOT / "START-BLOG.md").read_text(encoding="utf-8")
        self.assertIn("Шаблон состояния", text)
        self.assertIn("Пример воронки", text)
        self.assertIn("без", text)
        self.assertIn("45 дополнительных", text)
        self.assertIn("https://t.me/midifilm", text)

if __name__ == "__main__":
    unittest.main()
