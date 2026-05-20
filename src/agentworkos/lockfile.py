from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml
from .remote import is_remote_source, resolve_remote_source
from .util import git_commit, git_remote, is_git_repo, json_dump, run_git, sha256_file, sha256_tree


def normalize_git_source(source: str) -> str:
    return source.removeprefix("git+")


def resolve_git_remote(source: str, ref: str) -> str:
    remote = resolve_remote_source(source).url if is_remote_source(source) else normalize_git_source(source)
    output = run_git(["ls-remote", remote, ref])
    first = output.splitlines()[0] if output else ""
    return first.split()[0] if first else ""


def lock_local_source(source: Path) -> dict[str, Any]:
    if source.is_file():
        return {"content_hash": sha256_file(source), "source_kind": "file"}
    if is_git_repo(source):
        return {
            "source_kind": "git-local",
            "remote": git_remote(source),
            "commit": git_commit(source),
            "content_hash": sha256_tree(source),
        }
    return {"source_kind": "directory", "content_hash": sha256_tree(source)}


def create_lock(manifest_path: Path, offline: bool = False) -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    base = manifest_path.parent
    entries: list[dict[str, Any]] = []

    for package in manifest.get("packages", []):
        source = package.get("source", "")
        ref = package.get("ref", "main")
        entry: dict[str, Any] = {
            "id": package.get("id"),
            "type": package.get("type"),
            "source": source,
            "path": package.get("path", ""),
            "install_to": package.get("install_to", ""),
            "targets": package.get("targets", []),
            "ref": ref,
        }
        if is_remote_source(source):
            entry["source_kind"] = "git-remote"
            if not offline:
                try:
                    entry["commit"] = resolve_git_remote(source, ref)
                except Exception as exc:  # noqa: BLE001 - lock records best-effort diagnostics.
                    entry["warning"] = str(exc)
        else:
            source_path = (base / source).resolve()
            entry["resolved_path"] = source
            if source_path.exists():
                entry.update(lock_local_source(source_path))
            else:
                entry["warning"] = "local source does not exist"
        entries.append(entry)

    repo_entries: list[dict[str, Any]] = []
    for repo in manifest.get("repos", []):
        source = repo.get("source", "")
        ref = repo.get("ref", "main")
        entry = {"id": repo.get("id"), "source": source, "checkout_to": repo.get("checkout_to", ""), "ref": ref}
        if source and not offline:
            try:
                entry["commit"] = resolve_git_remote(source, ref)
            except Exception as exc:  # noqa: BLE001
                entry["warning"] = str(exc)
        repo_entries.append(entry)

    return {
        "schema": "agentworkos.lock.v1",
        "manifest": str(manifest_path),
        "stack": manifest.get("stack", {}),
        "packages": entries,
        "repos": repo_entries,
    }


def write_lock(manifest_path: Path, output: Path, offline: bool = False) -> dict[str, Any]:
    payload = create_lock(manifest_path, offline=offline)
    json_dump(output, payload)
    return payload
