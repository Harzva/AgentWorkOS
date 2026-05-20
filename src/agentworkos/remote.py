from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .util import default_aw_home, run_git


@dataclass(frozen=True)
class RemoteSource:
    original: str
    url: str
    host: str
    owner: str
    repo: str

    @property
    def display(self) -> str:
        return f"{self.host}/{self.owner}/{self.repo}"


def is_remote_source(source: str) -> bool:
    return source.startswith(("github:", "git+https://", "https://", "http://", "git+file://", "file://"))


def _github_base_url() -> str:
    return os.environ.get("AW_GITHUB_BASE_URL", "https://github.com").rstrip("/")


def _strip_git_suffix(repo: str) -> str:
    return repo[:-4] if repo.endswith(".git") else repo


def _from_github_shorthand(source: str) -> RemoteSource:
    value = source.removeprefix("github:").strip("/")
    parts = value.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("github source must look like github:OWNER/REPO")
    owner = parts[0]
    repo = _strip_git_suffix(parts[1])
    base = _github_base_url()
    if base.startswith("file://"):
        url = f"{base}/{owner}/{repo}.git"
    else:
        url = f"{base}/{owner}/{repo}.git"
    return RemoteSource(original=source, url=url, host="github.com", owner=owner, repo=repo)


def _from_url(source: str) -> RemoteSource:
    original = source
    if source.startswith("git+"):
        source = source.removeprefix("git+")
    parsed = urlparse(source)
    if parsed.scheme not in {"https", "http", "file"}:
        raise ValueError(f"unsupported remote source: {original}")
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(path_parts) < 2:
        raise ValueError(f"remote source must include OWNER/REPO: {original}")
    owner = path_parts[-2]
    repo = _strip_git_suffix(path_parts[-1])
    host = parsed.netloc or "local"
    return RemoteSource(original=original, url=source, host=host, owner=owner, repo=repo)


def resolve_remote_source(source: str) -> RemoteSource:
    if source.startswith("github:"):
        return _from_github_shorthand(source)
    if is_remote_source(source):
        return _from_url(source)
    raise ValueError(f"unsupported remote source: {source}")


def remote_cache_path(remote: RemoteSource, aw_home: Path | None = None) -> Path:
    root = (aw_home or default_aw_home()).expanduser()
    return root / "sources" / remote.host / remote.owner / remote.repo


def clone_or_fetch(remote: RemoteSource, checkout: Path, ref: str, apply: bool) -> list[str]:
    if not apply:
        verb = "fetch" if checkout.exists() else "clone"
        return [f"would {verb} {remote.url} -> {checkout}", f"would checkout {remote.display}@{ref}"]

    if checkout.exists() and not (checkout / ".git").exists():
        raise RuntimeError(f"remote cache path exists but is not a git checkout: {checkout}")
    if checkout.exists():
        run_git(["fetch", "--all", "--tags", "--prune"], cwd=checkout)
        actions = [f"fetched {remote.url} in {checkout}"]
    else:
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", remote.url, str(checkout)])
        actions = [f"cloned {remote.url} -> {checkout}"]
    run_git(["checkout", ref], cwd=checkout)
    actions.append(f"checked out {remote.display}@{ref}")
    return actions


def inspect_remote_checkout(remote: RemoteSource, ref: str, cache: Path, apply: bool, temp_root: Path) -> tuple[Path, list[str]]:
    if apply:
        actions = clone_or_fetch(remote, cache, ref, apply=True)
        return cache, actions

    if cache.exists():
        return cache, [f"using existing cache for dry-run: {cache}"]

    temp_checkout = temp_root / remote.host / remote.owner / remote.repo
    if temp_checkout.exists():
        shutil.rmtree(temp_checkout)
    temp_checkout.parent.mkdir(parents=True, exist_ok=True)
    run_git(["clone", "--depth", "1", "--branch", ref, remote.url, str(temp_checkout)])
    return temp_checkout, [f"inspected temporary clone {remote.url}"]
