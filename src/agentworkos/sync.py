from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml
from .util import copy_file, copy_tree, default_claude_home, default_codex_home


def runtime_home(stack: dict[str, Any], target: str) -> Path:
    if target == "codex":
        return Path(stack.get("codex_home") or default_codex_home()).expanduser()
    if target in {"claude", "claude-code"}:
        return Path(stack.get("claude_home") or default_claude_home()).expanduser()
    raise ValueError(f"unknown sync target: {target}")


def target_install_to(package: dict[str, Any], target: str) -> str:
    targets = package.get("targets", [])
    aliases = {target}
    if target == "claude":
        aliases.add("claude-code")
    if target == "claude-code":
        aliases.add("claude")
    for target_config in targets:
        if target_config.get("runtime") in aliases:
            return target_config.get("install_to", "")
    if targets:
        return ""
    return package.get("install_to", "")


def sync_manifest(manifest_path: Path, apply: bool = False, target: str = "codex") -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    base = manifest_path.parent
    stack = manifest.get("stack", {})
    home = runtime_home(stack, target)
    actions: list[str] = []

    for package in manifest.get("packages", []):
        source = package.get("source", "")
        install_to = target_install_to(package, target)
        path_inside = package.get("path", "")
        if not source or not install_to:
            actions.append(f"skip {package.get('id', '<unknown>')}: missing source or install_to for {target}")
            continue
        if source.startswith(("git+", "https://")):
            actions.append(f"skip {package.get('id')}: remote package sync requires checkout cache (planned)")
            continue
        source_path = (base / source).resolve()
        if path_inside:
            candidate = source_path / path_inside
            if candidate.exists():
                source_path = candidate
        target_path = home / install_to
        if source_path.is_dir():
            actions.append(copy_tree(source_path, target_path, apply=apply))
        elif source_path.is_file():
            actions.append(copy_file(source_path, target_path, apply=apply))
        else:
            actions.append(f"missing source: {source_path}")

    return {"schema": "agentworkos.sync.v1", "apply": apply, "target": target, "actions": actions}
