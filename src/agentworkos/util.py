from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".py",
    ".ps1",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
}

EXCLUDED_TREE_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "agentworkos.egg-info",
    "dist",
    "build",
}

EXCLUDED_TREE_FILES = {
    "agentworkos.lock.json",
    "agentworkos.state.json",
    "agentworkos.detected.toml",
    "AGENTWORKOS_AUDIT.md",
}


def default_codex_home() -> Path:
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".codex"


def default_claude_home() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".claude"


def default_aw_home() -> Path:
    env = os.environ.get("AW_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".agentworkos"


def json_dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def git_commit(path: Path) -> str:
    return run_git(["rev-parse", "HEAD"], cwd=path)


def git_remote(path: Path) -> str:
    try:
        return run_git(["remote", "get-url", "origin"], cwd=path)
    except RuntimeError:
        return ""


def git_dirty(path: Path) -> bool:
    try:
        return bool(run_git(["status", "--porcelain"], cwd=path))
    except RuntimeError:
        return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(path: Path) -> str:
    digest = hashlib.sha256()
    files = [
        item
        for item in path.rglob("*")
        if item.is_file()
        and not (set(item.parts) & EXCLUDED_TREE_PARTS)
        and item.name not in EXCLUDED_TREE_FILES
        and item.suffix.lower() in TEXT_EXTENSIONS
    ]
    for item in sorted(files):
        rel = item.relative_to(path).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(item).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def copy_tree(source: Path, target: Path, apply: bool) -> str:
    if not apply:
        return f"would copy {source} -> {target}"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return f"copied {source} -> {target}"


def copy_file(source: Path, target: Path, apply: bool) -> str:
    if not apply:
        return f"would copy {source} -> {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"copied {source} -> {target}"
