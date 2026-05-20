from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def quote_toml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_sample_stack(path: Path, codex_home: Path | None = None) -> None:
    codex = str(codex_home or Path.home() / ".codex").replace("\\", "/")
    claude = str(Path.home() / ".claude").replace("\\", "/")
    content = f"""[stack]
name = "default-agentworkos"
version = "0.1.0"
platforms = ["windows-x64", "darwin-arm64", "linux-x64"]
codex_home = {quote_toml(codex)}
claude_home = {quote_toml(claude)}

[[packages]]
id = "io.github.just-agent.readme-design"
type = "skill"
source = "git+https://github.com/Just-Agent/README-Design-Skill.git"
path = "skills/readme-design"
install_to = "skills/readme-design"
ref = "main"

[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"

[[packages]]
id = "local.terms"
type = "terms"
source = "./TERMS.md"
install_to = "agents/TERMS.md"

[[packages.targets]]
runtime = "codex"
install_to = "agents/TERMS.md"

[[packages.targets]]
runtime = "claude-code"
install_to = "TERMS.md"
adapter = "terms-to-claude-memory"

[[repos]]
id = "io.github.harzva.make-windows-silky"
source = "https://github.com/Harzva/make_windows_silky_Patch.git"
checkout_to = "repos/make_windows_silky_Patch"
ref = "main"
"""
    path.write_text(content, encoding="utf-8")


def write_sample_terms(path: Path) -> None:
    content = """# TERMS

| Term | Expanded meaning | Required behavior |
| --- | --- | --- |
| 三端同步 | Runtime copy, local source repo, and remote GitHub repo are synchronized | Update all three and verify clean status |
| 工作流资产化 | Repeated work becomes a reusable asset | Produce a Skill, rule, SOP, checklist, script, prompt, hook candidate, or project card |
"""
    path.write_text(content, encoding="utf-8")
