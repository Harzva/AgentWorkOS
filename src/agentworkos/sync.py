from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml
from .util import copy_file, copy_tree, default_codex_home


def sync_manifest(manifest_path: Path, apply: bool = False) -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    base = manifest_path.parent
    stack = manifest.get("stack", {})
    codex_home = Path(stack.get("codex_home") or default_codex_home()).expanduser()
    actions: list[str] = []

    for package in manifest.get("packages", []):
        source = package.get("source", "")
        install_to = package.get("install_to", "")
        path_inside = package.get("path", "")
        if not source or not install_to:
            actions.append(f"skip {package.get('id', '<unknown>')}: missing source or install_to")
            continue
        if source.startswith(("git+", "https://")):
            actions.append(f"skip {package.get('id')}: remote package sync requires checkout cache (planned)")
            continue
        source_path = (base / source).resolve()
        if path_inside:
            candidate = source_path / path_inside
            if candidate.exists():
                source_path = candidate
        target_path = codex_home / install_to
        if source_path.is_dir():
            actions.append(copy_tree(source_path, target_path, apply=apply))
        elif source_path.is_file():
            actions.append(copy_file(source_path, target_path, apply=apply))
        else:
            actions.append(f"missing source: {source_path}")

    return {"schema": "agentworkos.sync.v1", "apply": apply, "actions": actions}
