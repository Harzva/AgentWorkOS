from __future__ import annotations

from pathlib import Path
from typing import Any

from .util import default_claude_home, default_codex_home, git_commit, git_dirty, git_remote, is_git_repo


def scan_skills(codex_home: Path) -> list[dict[str, Any]]:
    roots = [codex_home / "skills"]
    skills: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for skill_file in root.rglob("SKILL.md"):
            skill_dir = skill_file.parent
            skills.append(
                {
                    "name": skill_dir.name,
                    "path": str(skill_dir),
                    "relative_path": str(skill_dir.relative_to(codex_home)),
                    "has_skill_md": True,
                }
            )
    return sorted(skills, key=lambda item: item["relative_path"].lower())


def scan_agents(codex_home: Path) -> list[dict[str, Any]]:
    agents_root = codex_home / "agents"
    if not agents_root.exists():
        return []
    cards: list[dict[str, Any]] = []
    for path in agents_root.rglob("*.md"):
        if path.name.upper() == "TERMS.md":
            continue
        cards.append({"name": path.stem, "path": str(path), "relative_path": str(path.relative_to(codex_home))})
    return sorted(cards, key=lambda item: item["relative_path"].lower())


def scan_terms(codex_home: Path) -> list[dict[str, Any]]:
    candidates = [codex_home / "agents" / "TERMS.md", codex_home / "TERMS.md"]
    return [{"path": str(path), "exists": path.exists()} for path in candidates]


def scan_claude(claude_home: Path) -> dict[str, list[dict[str, Any]]]:
    skills: list[dict[str, Any]] = []
    agents: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []

    skills_root = claude_home / "skills"
    if skills_root.exists():
        for skill_file in skills_root.rglob("SKILL.md"):
            skill_dir = skill_file.parent
            skills.append({"name": skill_dir.name, "path": str(skill_dir), "relative_path": str(skill_dir.relative_to(claude_home))})

    agents_root = claude_home / "agents"
    if agents_root.exists():
        for path in agents_root.rglob("*.md"):
            agents.append({"name": path.stem, "path": str(path), "relative_path": str(path.relative_to(claude_home))})

    commands_root = claude_home / "commands"
    if commands_root.exists():
        for path in commands_root.rglob("*.md"):
            commands.append({"name": path.stem, "path": str(path), "relative_path": str(path.relative_to(claude_home))})

    return {
        "skills": sorted(skills, key=lambda item: item["relative_path"].lower()),
        "agents": sorted(agents, key=lambda item: item["relative_path"].lower()),
        "commands": sorted(commands, key=lambda item: item["relative_path"].lower()),
    }


def scan_repos(workspace: Path, max_depth: int = 2) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    if not workspace.exists():
        return repos

    def visit(path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if is_git_repo(path):
            repos.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "remote": git_remote(path),
                    "commit": git_commit(path),
                    "dirty": git_dirty(path),
                }
            )
            return
        try:
            children = [child for child in path.iterdir() if child.is_dir() and not child.name.startswith(".")]
        except OSError:
            return
        for child in children:
            visit(child, depth + 1)

    visit(workspace, 0)
    return sorted(repos, key=lambda item: item["path"].lower())


def scan_environment(
    codex_home: Path | None = None,
    claude_home: Path | None = None,
    workspace: Path | None = None,
) -> dict[str, Any]:
    codex = (codex_home or default_codex_home()).expanduser().resolve()
    claude = (claude_home or default_claude_home()).expanduser().resolve()
    root = (workspace or Path.cwd()).expanduser().resolve()
    skills = scan_skills(codex)
    agents = scan_agents(codex)
    terms = scan_terms(codex)
    claude_state = scan_claude(claude)
    repos = scan_repos(root)
    return {
        "schema": "agentworkos.state.v1",
        "codex_home": str(codex),
        "claude_home": str(claude),
        "workspace": str(root),
        "summary": {
            "skills": len(skills),
            "agents": len(agents),
            "terms_files": sum(1 for item in terms if item["exists"]),
            "claude_skills": len(claude_state["skills"]),
            "claude_agents": len(claude_state["agents"]),
            "claude_commands": len(claude_state["commands"]),
            "repos": len(repos),
            "dirty_repos": sum(1 for item in repos if item["dirty"]),
        },
        "skills": skills,
        "agents": agents,
        "terms": terms,
        "claude": claude_state,
        "repos": repos,
    }


def render_audit(state: dict[str, Any]) -> str:
    lines = [
        "# AgentWorkOS Audit",
        "",
        f"Codex home: `{state['codex_home']}`",
        f"Claude home: `{state['claude_home']}`",
        f"Workspace: `{state['workspace']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in state["summary"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Skills", "", "| Name | Relative path |", "| --- | --- |"])
    for item in state["skills"][:200]:
        lines.append(f"| {item['name']} | `{item['relative_path']}` |")

    lines.extend(["", "## Agents", "", "| Name | Relative path |", "| --- | --- |"])
    for item in state["agents"][:200]:
        lines.append(f"| {item['name']} | `{item['relative_path']}` |")

    lines.extend(["", "## Claude Code Runtime", "", "| Type | Name | Relative path |", "| --- | --- | --- |"])
    for kind in ("skills", "agents", "commands"):
        for item in state["claude"][kind][:200]:
            lines.append(f"| {kind[:-1]} | {item['name']} | `{item['relative_path']}` |")

    lines.extend(["", "## Repositories", "", "| Name | Dirty | Remote | Commit |", "| --- | --- | --- | --- |"])
    for item in state["repos"][:200]:
        commit = item["commit"][:12] if item["commit"] else ""
        lines.append(f"| {item['name']} | {item['dirty']} | `{item['remote']}` | `{commit}` |")

    return "\n".join(lines) + "\n"
