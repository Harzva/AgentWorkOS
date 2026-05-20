from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml
from .remote import clone_or_fetch, is_remote_source, remote_cache_path, resolve_remote_source
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


def target_names(target: str) -> list[str]:
    if target == "all":
        return ["codex", "claude-code"]
    return [target]


def source_path_for_package(
    package: dict[str, Any],
    base: Path,
    aw_home: Path | None,
    apply: bool,
    actions: list[str],
) -> Path | None:
    source = package.get("source", "")
    path_inside = package.get("path", "")
    if not source:
        return None
    if is_remote_source(source):
        remote = resolve_remote_source(source)
        checkout = remote_cache_path(remote, aw_home)
        ref = package.get("ref", "main")
        actions.extend(clone_or_fetch(remote, checkout, ref, apply=apply))
        source_path = checkout
    else:
        source_path = (base / source).resolve()
    if path_inside:
        source_path = source_path / path_inside
    return source_path


def sync_manifest_data(
    manifest: dict[str, Any],
    base: Path,
    apply: bool = False,
    target: str = "codex",
    aw_home: Path | None = None,
) -> dict[str, Any]:
    stack = manifest.get("stack", {})
    actions: list[str] = []

    for selected_target in target_names(target):
        home = runtime_home(stack, selected_target)
        for package in manifest.get("packages", []):
            install_to = target_install_to(package, selected_target)
            if not package.get("source") or not install_to:
                actions.append(f"skip {package.get('id', '<unknown>')}: missing source or install_to for {selected_target}")
                continue
            package_actions: list[str] = []
            source_path = source_path_for_package(package, base, aw_home, apply, package_actions)
            actions.extend(package_actions)
            if source_path is None:
                actions.append(f"skip {package.get('id', '<unknown>')}: missing source for {selected_target}")
                continue
            target_path = home / install_to
            if source_path.is_dir() or (not apply and not source_path.suffix):
                actions.append(copy_tree(source_path, target_path, apply=apply))
            elif source_path.is_file() or (not apply and source_path.suffix):
                actions.append(copy_file(source_path, target_path, apply=apply))
            else:
                actions.append(f"missing source: {source_path}")

    return {"schema": "agentworkos.sync.v1", "apply": apply, "target": target, "actions": actions}


def sync_manifest(
    manifest_path: Path,
    apply: bool = False,
    target: str = "codex",
    aw_home: Path | None = None,
) -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    return sync_manifest_data(manifest, manifest_path.parent, apply=apply, target=target, aw_home=aw_home)
