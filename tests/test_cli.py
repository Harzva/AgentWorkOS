from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_awos(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
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
    result = run_awos("init", "--root", str(tmp_path), cwd=ROOT)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "agentworkos.toml").exists()
    explain = run_awos("explain", "三端同步", "--terms", str(tmp_path / "TERMS.md"), cwd=ROOT)
    assert explain.returncode == 0
    assert "Runtime copy" in explain.stdout


def test_scan_detects_skill_and_repo(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    skill = codex_home / "skills" / "demo-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: demo-skill\n---\n# Demo\n", encoding="utf-8")
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
    result = run_awos(
        "scan",
        "--codex-home",
        str(codex_home),
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
    result = run_awos("lock", "--manifest", str(tmp_path / "agentworkos.toml"), "--output", str(lock_path), "--offline", cwd=ROOT)
    assert result.returncode == 0, result.stderr
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["packages"][0]["id"] == "local.terms"
    assert lock["packages"][0]["content_hash"]
