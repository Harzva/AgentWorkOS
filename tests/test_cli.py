from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_aw(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agentworkos.cli", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )


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
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.name", "AgentWorkOS Test"], cwd=repo, check=True, stdout=subprocess.PIPE)
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)

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
