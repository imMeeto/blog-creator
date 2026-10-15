"""Build the native plugin and portable kit without changing installed caches."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile
import yaml

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE
OUT = BASE / "dist"
VERSION = "1.1.2"
POINTER = "Перед применением прочитай [правила интеграции «Блог с нуля»](../../context/10-blog-runtime.md). Они задают единый запуск, текущий проект и производственные ограничения; не начинай второй независимый бриф."
UPSTREAM = "8683dd9c8022b84c081647ca71a498b0e17ea552"

def prepare_library():
    # Mechanical compatibility normalization; methods and supporting resources stay intact.
    for file in sorted((ROOT / "skills").glob("*/SKILL.md")):
        if not (file.parent.name.startswith("cp-") or file.parent.name == "content-producer"):
            continue
        text = file.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            raise ValueError(f"Bad frontmatter: {file}")
        # Upstream has two-line plain descriptions containing ': ', invalid YAML.
        # Read those exact scalar values and quote them without changing wording.
        try:
            front = yaml.safe_load(match[1])
        except yaml.YAMLError:
            front = dict(line.split(':', 1) for line in match[1].splitlines())
            front = {key: value.strip() for key, value in front.items()}
        header = "---\nname: " + json.dumps(front["name"], ensure_ascii=False) + "\ndescription: " + json.dumps(front["description"], ensure_ascii=False) + "\n---\n"
        body = text[match.end():]
        if POINTER not in body:
            body = "\n" + POINTER + "\n" + body
        file.write_text(header + body, encoding="utf-8")

def inline_text(text):
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    # The standalone guide cannot depend on local paths.
    return re.sub(r"\[([^\]]+)\]\((?!https?://|#)[^)]+\)", r"\1 (включено ниже либо доступно в полном пакете)", text)

def portable_guide():
    intro = """# Блог с нуля · переносимое руководство 1.1.2

Издатель: INMI Digital (основатель midi). Инструмент команды midi.film, полностью бесплатный. Прикрепите этот файл для работы в текущем чате.
Команда: «Помоги мне начать блог. Начни с вопросов».
Если ZIP плагина доступен и среда умеет устанавливать его, инициируй поддерживаемую установку. Если нет — используй это руководство в сессии.
Это руководство содержит основной 15-этапный маршрут. 45 дополнительных cp-навыков доступны только когда их файлы из полного пакета действительно предоставлены среде; не утверждай, что прочитал отсутствующие навыки.

"""
    parts = [intro]
    for path in ["skills/blog-start/SKILL.md", "context/10-blog-runtime.md", "skills/blog-launch/SKILL.md"]:
        parts.append(inline_text((ROOT / path).read_text(encoding="utf-8")))
    parts.append("## Дополнительные возможности полного пакета\n\n" + inline_text((ROOT / "context/11-blog-routing.md").read_text(encoding="utf-8")))
    for file in sorted((ROOT / "skills/blog-launch/references").glob("*.md")):
        parts.append(inline_text(file.read_text(encoding="utf-8")))
    parts.append("# Шаблон состояния\n\n```json\n" + (ROOT / "skills/blog-launch/assets/project-state.example.json").read_text(encoding="utf-8") + "\n```")
    parts.append("# Пример воронки\n\n```mermaid\n" + (ROOT / "skills/blog-launch/assets/funnel.example.mmd").read_text(encoding="utf-8") + "\n```")
    (ROOT / "START-BLOG.md").write_text("\n\n---\n\n".join(parts) + "\n", encoding="utf-8")

def files_for_package():
    roots = {"skills", "context", "assets", "docs", "qa"}
    singles = {"plugin.json", "README.md", "INSTALL.md", "START-BLOG.md", "CHANGELOG.md", "AUTHORING.md", "LICENSE", "LICENSE.midi-skills", "NOTICE", "CREDITS.midi-skills.md", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"}
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
                  and (p.relative_to(ROOT).parts[0] in roots or p.relative_to(ROOT).as_posix() in singles)
                  and not any(x in {"__pycache__", "node_modules"} for x in p.relative_to(ROOT).parts)
                  and p.suffix != ".pyc")

def validate():
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    legacy = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == legacy["name"] == claude["name"] == "blog-from-zero"
    assert manifest["version"] == legacy["version"] == claude["version"] == VERSION
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    interface = manifest["extensions"]["com.openai"]["interface"]
    assert len(interface["shortDescription"]) <= 30
    assert interface["defaultPrompt"] == legacy["interface"]["defaultPrompt"]
    assert interface == legacy["interface"]
    assert (ROOT / manifest["extensions"]["com.openai"]["onboardingSkill"]).is_file()
    names = []
    for file in (ROOT / "skills").glob("*/SKILL.md"):
        text = file.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        assert match, str(file)
        front = yaml.safe_load(match[1])
        assert front["name"] == file.parent.name
        assert isinstance(front["description"], str) and front["description"].strip()
        assert file.stat().st_size <= 1024*1024
        names.append(front["name"])
    assert len(names) == len(set(names)) == 54
    # Check authored and upstream relative Markdown resources against the exact package.
    for file in [p for p in files_for_package() if p.suffix == '.md']:
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if link.startswith(("http:", "https:", "#", "mailto:", "app:")):
                continue
            target = link.split("#")[0]
            if "<" in target or ">" in target:
                continue
            resolved = (file.parent / target).resolve()
            assert resolved.is_relative_to(ROOT.resolve()), (file, link, "outside plugin")
            assert resolved.exists(), (file, link, "missing")
    for file in [p for p in files_for_package() if p.suffix == '.json']:
        json.loads(file.read_text(encoding="utf-8"))
    for file in [p for p in files_for_package() if p.suffix == '.yaml']:
        yaml.safe_load(file.read_text(encoding="utf-8"))
    return names

def build():
    prepare_library()
    portable_guide()
    names = validate()
    OUT.mkdir(exist_ok=True)
    native = OUT / f"blog-creator-{VERSION}.zip"
    with zipfile.ZipFile(native, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in files_for_package():
            archive.write(file, file.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(native) as archive:
        assert "plugin.json" in archive.namelist()
        assert ".claude-plugin/plugin.json" in archive.namelist()
        assert len([p for p in archive.namelist() if re.match(r"skills/[^/]+/SKILL.md$", p)]) == 54
        assert not any("marketplace.json" in p for p in archive.namelist())
        assert archive.testzip() is None
    kit = OUT / f"blog-from-zero-kit-{VERSION}.zip"
    with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(native, native.name)
        for name in ["START-BLOG.md", "INSTALL.md", "README.md", "CHANGELOG.md"]:
            archive.write(ROOT / name, name)
    report = {
        "version": VERSION,
        "source_repo": "https://github.com/imMeeto/midi-skills",
        "source_commit": UPSTREAM,
        "skill_count": len(names),
        "skills": sorted(names),
        "native_archive": str(native),
        "native_sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
        "native_bytes": native.stat().st_size,
        "kit_archive": str(kit),
        "identity_preserved": True,
        "default_prompts_preserved": True,
        "scope": "USER",
        "visibility": "PRIVATE",
        "host_dialogue_tests": "not_run",
        "public_install_link": "not_published"
    }
    (OUT / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    shutil.copy2(native, OUT / "blog-creator.zip")
    # Preserve links already shared with users while adopting the new download name.
    shutil.copy2(native, OUT / "blog-from-zero.zip")
    shutil.copy2(kit, OUT / "blog-from-zero-kit.zip")
    for name in ["START-BLOG.md", "INSTALL.md"]:
        shutil.copy2(ROOT / name, OUT / name)
    download_names = ["blog-creator.zip", "blog-from-zero.zip", "blog-from-zero-kit.zip", "START-BLOG.md", "INSTALL.md"]
    checksums = [hashlib.sha256((OUT / name).read_bytes()).hexdigest() + '  ' + name for name in download_names]
    (OUT / 'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    build()
