from __future__ import annotations

import tomllib
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def profile_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for profile in manifest.get("profiles", []):
        name = profile.get("name", "")
        if name:
            profiles[name] = profile
    return profiles


def resolve_profile(manifest: dict[str, Any], profile_name: str | None) -> dict[str, Any]:
    if not profile_name:
        profile_name = manifest.get("stack", {}).get("default_profile", "")
        if not profile_name:
            return manifest

    profiles = profile_map(manifest)
    if profile_name not in profiles:
        raise ValueError(f"unknown profile: {profile_name}")

    package_ids: list[str] = []
    repo_ids: list[str] = []
    visited: set[str] = set()

    def visit(name: str, stack: list[str]) -> None:
        if name in stack:
            cycle = " -> ".join([*stack, name])
            raise ValueError(f"profile inheritance cycle: {cycle}")
        if name in visited:
            return
        if name not in profiles:
            raise ValueError(f"unknown profile in extends: {name}")
        profile = profiles[name]
        for parent in _as_list(profile.get("extends")):
            visit(str(parent), [*stack, name])
        package_ids.extend(str(item) for item in _as_list(profile.get("packages")))
        repo_ids.extend(str(item) for item in _as_list(profile.get("repos")))
        visited.add(name)

    visit(profile_name, [])

    selected = deepcopy(manifest)
    all_packages = manifest.get("packages", [])
    all_repos = manifest.get("repos", [])

    if package_ids and "*" not in package_ids:
        available = {package.get("id") for package in all_packages}
        missing = [package_id for package_id in dict.fromkeys(package_ids) if package_id not in available]
        if missing:
            raise ValueError(f"profile {profile_name} references missing package ids: {', '.join(missing)}")
        allowed = set(package_ids)
        selected["packages"] = [package for package in all_packages if package.get("id") in allowed]
    elif profile_name and not package_ids:
        selected["packages"] = []

    if repo_ids and "*" not in repo_ids:
        available = {repo.get("id") for repo in all_repos}
        missing = [repo_id for repo_id in dict.fromkeys(repo_ids) if repo_id not in available]
        if missing:
            raise ValueError(f"profile {profile_name} references missing repo ids: {', '.join(missing)}")
        allowed = set(repo_ids)
        selected["repos"] = [repo for repo in all_repos if repo.get("id") in allowed]
    elif profile_name and not repo_ids:
        selected["repos"] = []

    selected["_selected_profile"] = profile_name
    return selected


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
