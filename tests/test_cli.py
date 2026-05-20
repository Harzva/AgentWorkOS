from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_aw(*args: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agentworkos.cli", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src"), **(env or {})},
    )


def init_git_repo(path: Path) -> None:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.name", "AgentWorkOS Test"], cwd=path, check=True, stdout=subprocess.PIPE)


def commit_all(path: Path, message: str = "init") -> None:
    subprocess.run(["git", "add", "."], cwd=path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, stdout=subprocess.PIPE)


def make_bare_github_repo(source: Path, github_root: Path, owner: str, repo: str) -> str:
    target = github_root / owner / f"{repo}.git"
    target.parent.mkdir(parents=True)
    subprocess.run(["git", "clone", "--bare", str(source), str(target)], check=True, stdout=subprocess.PIPE)
    return github_root.as_uri()


def test_init_and_explain(tmp_path: Path) -> None:
    result = run_aw("init", "--root", str(tmp_path), cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "agentworkos.toml").exists()
    explain = run_aw("explain", "三端同步", "--terms", str(tmp_path / "TERMS.md"), cwd=ROOT)
    assert explain.returncode == 0
    assert "Runtime copy" in explain.stdout


def test_scan_detects_skill_and_repo(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    skill = codex_home / "skills" / "demo-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: demo-skill\n---\n# Demo\n", encoding="utf-8")
    claude_skill = claude_home / "skills" / "demo-claude"
    claude_skill.mkdir(parents=True)
    (claude_skill / "SKILL.md").write_text("---\nname: demo-claude\n---\n# Demo\n", encoding="utf-8")
    claude_agent = claude_home / "agents" / "reviewer.md"
    claude_agent.parent.mkdir(parents=True)
    claude_agent.write_text("---\nname: reviewer\n---\n# Reviewer\n", encoding="utf-8")
    claude_command = claude_home / "commands" / "ship.md"
    claude_command.parent.mkdir(parents=True)
    claude_command.write_text("# Ship\n", encoding="utf-8")
    repo = tmp_path / "repo"
    init_git_repo(repo)
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    commit_all(repo)

    output_json = tmp_path / "state.json"
    output_md = tmp_path / "audit.md"
    result = run_aw(
        "scan",
        "--codex-home",
        str(codex_home),
        "--claude-home",
        str(claude_home),
        "--workspace",
        str(tmp_path),
        "--output-json",
        str(output_json),
        "--output-md",
        str(output_md),
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    state = json.loads(output_json.read_text(encoding="utf-8"))
    assert state["summary"]["skills"] == 1
    assert state["summary"]["claude_skills"] == 1
    assert state["summary"]["claude_agents"] == 1
    assert state["summary"]["claude_commands"] == 1
    assert state["summary"]["repos"] == 1


def test_lock_offline_local_terms(tmp_path: Path) -> None:
    (tmp_path / "TERMS.md").write_text("# TERMS\n", encoding="utf-8")
    (tmp_path / "agentworkos.toml").write_text(
        """
[stack]
name = "test"
version = "0.1.0"

[[packages]]
id = "local.terms"
type = "terms"
source = "./TERMS.md"
install_to = "agents/TERMS.md"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    lock_path = tmp_path / "agentworkos.lock.json"
    result = run_aw("lock", "--manifest", str(tmp_path / "agentworkos.toml"), "--output", str(lock_path), "--offline", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["packages"][0]["id"] == "local.terms"
    assert lock["packages"][0]["content_hash"]


def test_lock_offline_github_source_is_remote(tmp_path: Path) -> None:
    (tmp_path / "agentworkos.toml").write_text(
        """
[stack]
name = "test"
version = "0.1.0"

[[packages]]
id = "remote.skill"
type = "skill"
source = "github:Owner/Skill"
path = "skills/skill"
install_to = "skills/skill"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    lock_path = tmp_path / "agentworkos.lock.json"
    result = run_aw("lock", "--manifest", str(tmp_path / "agentworkos.toml"), "--output", str(lock_path), "--offline", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["packages"][0]["source_kind"] == "git-remote"


def test_sync_uses_runtime_targets(tmp_path: Path) -> None:
    package_dir = tmp_path / "skill"
    package_dir.mkdir()
    (package_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    codex_home = tmp_path / ".codex"
    claude_home = tmp_path / ".claude"
    codex_home_toml = str(codex_home).replace("\\", "/")
    claude_home_toml = str(claude_home).replace("\\", "/")
    manifest = tmp_path / "agentworkos.toml"
    manifest.write_text(
        f"""
[stack]
name = "test"
version = "0.1.0"
codex_home = "{codex_home_toml}"
claude_home = "{claude_home_toml}"

[[packages]]
id = "local.skill"
type = "skill"
source = "./skill"
install_to = "skills/local-skill"

[[packages.targets]]
runtime = "codex"
install_to = "skills/local-skill"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/local-skill-claude"
adapter = "skill-to-claude-skill"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    codex = run_aw("sync", "--manifest", str(manifest), "--target", "codex", cwd=ROOT)
    claude = run_aw("sync", "--manifest", str(manifest), "--target", "claude-code", cwd=ROOT)

    assert codex.returncode == 0, codex.stderr
    assert claude.returncode == 0, claude.stderr
    assert "skills\\local-skill" in codex.stdout or "skills/local-skill" in codex.stdout
    assert "skills\\local-skill-claude" in claude.stdout or "skills/local-skill-claude" in claude.stdout


def test_install_github_stack_dry_run_and_apply_all(tmp_path: Path) -> None:
    stack_repo = tmp_path / "stack-src"
    init_git_repo(stack_repo)
    (stack_repo / "skill").mkdir()
    (stack_repo / "skill" / "SKILL.md").write_text("# Stack Skill\n", encoding="utf-8")
    codex_home = tmp_path / "runtime" / ".codex"
    claude_home = tmp_path / "runtime" / ".claude"
    codex_home_toml = str(codex_home).replace("\\", "/")
    claude_home_toml = str(claude_home).replace("\\", "/")
    (stack_repo / "agentworkos.toml").write_text(
        f"""
[stack]
name = "stack"
version = "0.1.0"
codex_home = "{codex_home_toml}"
claude_home = "{claude_home_toml}"

[[packages]]
id = "stack.skill"
type = "skill"
source = "./skill"
install_to = "skills/stack-skill"

[[packages.targets]]
runtime = "codex"
install_to = "skills/stack-skill"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/stack-skill"
adapter = "skill-to-claude-skill"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    commit_all(stack_repo)
    github_base = make_bare_github_repo(stack_repo, tmp_path / "github", "Owner", "Stack")
    env = {"AW_HOME": str(tmp_path / "aw-home"), "AW_GITHUB_BASE_URL": github_base}

    dry_run = run_aw("install", "github:Owner/Stack", "--target", "all", cwd=ROOT, env=env)
    assert dry_run.returncode == 0, dry_run.stderr
    assert "detected stack repo" in dry_run.stdout
    assert "dry-run only" in dry_run.stdout
    assert not (codex_home / "skills" / "stack-skill" / "SKILL.md").exists()

    apply = run_aw("install", "github:Owner/Stack", "--target", "all", "--apply", cwd=ROOT, env=env)
    assert apply.returncode == 0, apply.stderr
    assert (codex_home / "skills" / "stack-skill" / "SKILL.md").exists()
    assert (claude_home / "skills" / "stack-skill" / "SKILL.md").exists()


def test_install_github_package_repo(tmp_path: Path) -> None:
    package_repo = tmp_path / "package-src"
    init_git_repo(package_repo)
    skill = package_repo / "skills" / "package-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Package Skill\n", encoding="utf-8")
    codex_home = tmp_path / ".codex"
    (package_repo / "agentpkg.toml").write_text(
        """
[package]
id = "package.skill"
name = "package-skill"
type = "skill"
version = "0.1.0"

[source]
path = "skills/package-skill"

[install]
target = "skills/package-skill"

[[targets]]
runtime = "codex"
install_to = "skills/package-skill"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    commit_all(package_repo)
    github_base = make_bare_github_repo(package_repo, tmp_path / "github", "Owner", "Package")
    env = {
        "AW_HOME": str(tmp_path / "aw-home"),
        "AW_GITHUB_BASE_URL": github_base,
        "CODEX_HOME": str(codex_home),
    }

    result = run_aw("install", "github:Owner/Package", "--target", "codex", "--apply", cwd=ROOT, env=env)
    assert result.returncode == 0, result.stderr
    assert "detected package repo" in result.stdout
    assert (codex_home / "skills" / "package-skill" / "SKILL.md").exists()


def test_install_missing_manifest_fails(tmp_path: Path) -> None:
    repo = tmp_path / "empty-src"
    init_git_repo(repo)
    (repo / "README.md").write_text("# Empty\n", encoding="utf-8")
    commit_all(repo)
    github_base = make_bare_github_repo(repo, tmp_path / "github", "Owner", "Empty")
    env = {"AW_HOME": str(tmp_path / "aw-home"), "AW_GITHUB_BASE_URL": github_base}

    result = run_aw("install", "github:Owner/Empty", cwd=ROOT, env=env)
    assert result.returncode == 2
    assert "does not contain agentworkos.toml or agentpkg.toml" in result.stderr


def test_install_unsupported_target_fails(tmp_path: Path) -> None:
    result = run_aw("install", "github:Owner/Stack", "--target", "cursor", cwd=ROOT)
    assert result.returncode == 2
    assert "invalid choice" in result.stderr
