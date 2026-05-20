from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .manifest import load_toml
from .remote import inspect_remote_checkout, remote_cache_path, resolve_remote_source
from .sync import sync_manifest_data


def manifest_from_agentpkg(package_root: Path, agentpkg_path: Path) -> dict[str, Any]:
    package_manifest = load_toml(agentpkg_path)
    package = package_manifest.get("package", {})
    source = package_manifest.get("source", {})
    install = package_manifest.get("install", {})
    return {
        "stack": {"name": package.get("name", package.get("id", "agentworkos-package")), "version": package.get("version", "0.1.0")},
        "packages": [
            {
                "id": package.get("id", package.get("name", package_root.name)),
                "type": package.get("type", "skill"),
                "source": ".",
                "path": source.get("path", "."),
                "install_to": install.get("target", ""),
                "targets": package_manifest.get("targets", []),
            }
        ],
    }


def detect_install_manifest(repo_root: Path) -> tuple[str, dict[str, Any], Path]:
    stack_manifest = repo_root / "agentworkos.toml"
    if stack_manifest.exists():
        return "stack", load_toml(stack_manifest), repo_root
    agentpkg_manifest = repo_root / "agentpkg.toml"
    if agentpkg_manifest.exists():
        return "package", manifest_from_agentpkg(repo_root, agentpkg_manifest), repo_root
    raise RuntimeError(f"remote repository does not contain agentworkos.toml or agentpkg.toml: {repo_root}")


def install_source(
    source: str,
    ref: str = "main",
    target: str = "codex",
    apply: bool = False,
    aw_home: Path | None = None,
) -> dict[str, Any]:
    remote = resolve_remote_source(source)
    cache = remote_cache_path(remote, aw_home)
    actions: list[str] = []

    with tempfile.TemporaryDirectory(prefix="agentworkos-install-") as tmp:
        repo_root, inspect_actions = inspect_remote_checkout(remote, ref, cache, apply=apply, temp_root=Path(tmp))
        actions.extend(inspect_actions)
        kind, manifest, base = detect_install_manifest(repo_root)
        actions.append(f"detected {kind} repo: {remote.display}")
        sync = sync_manifest_data(manifest, base, apply=apply, target=target, aw_home=aw_home)
        actions.extend(sync["actions"])

    return {
        "schema": "agentworkos.install.v1",
        "source": source,
        "ref": ref,
        "target": target,
        "apply": apply,
        "actions": actions,
    }
