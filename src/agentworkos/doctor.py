from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml, profile_map, resolve_profile
from .remote import is_remote_source, resolve_remote_source


def run_doctor(manifest_path: Path, profile: str | None = None) -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    base = manifest_path.parent
    findings: list[dict[str, str]] = []
    try:
        profile_map(manifest)
        manifest = resolve_profile(manifest, profile)
        selected_profile = manifest.get("_selected_profile", profile)
    except ValueError as exc:
        findings.append({"severity": "error", "message": str(exc)})
        selected_profile = profile
    seen: set[str] = set()

    for package in manifest.get("packages", []):
        package_id = package.get("id", "")
        if not package_id:
            findings.append({"severity": "error", "message": "package missing id"})
        elif package_id in seen:
            findings.append({"severity": "error", "message": f"duplicate package id: {package_id}"})
        seen.add(package_id)

        source = package.get("source", "")
        if source and is_remote_source(source):
            try:
                resolve_remote_source(source)
            except ValueError as exc:
                findings.append({"severity": "warning", "message": f"invalid remote source for {package_id}: {exc}"})
        elif source:
            if not (base / source).exists():
                findings.append({"severity": "warning", "message": f"local source missing for {package_id}: {source}"})

        if not package.get("install_to"):
            findings.append({"severity": "warning", "message": f"package has no install_to: {package_id}"})

        for target in package.get("targets", []):
            runtime = target.get("runtime", "")
            install_to = target.get("install_to", "")
            if runtime not in {"codex", "claude", "claude-code"}:
                findings.append({"severity": "warning", "message": f"unknown target runtime for {package_id}: {runtime}"})
            if not install_to:
                findings.append({"severity": "warning", "message": f"target has no install_to for {package_id}: {runtime}"})

    stack = manifest.get("stack", {})
    codex_home = stack.get("codex_home", "")
    if codex_home and not Path(codex_home).expanduser().exists():
        findings.append({"severity": "warning", "message": f"codex_home does not exist: {codex_home}"})
    claude_home = stack.get("claude_home", "")
    if claude_home and not Path(claude_home).expanduser().exists():
        findings.append({"severity": "warning", "message": f"claude_home does not exist: {claude_home}"})

    repo_seen: set[str] = set()
    for repo in manifest.get("repos", []):
        repo_id = repo.get("id", "")
        if not repo_id:
            findings.append({"severity": "error", "message": "repo missing id"})
        elif repo_id in repo_seen:
            findings.append({"severity": "error", "message": f"duplicate repo id: {repo_id}"})
        repo_seen.add(repo_id)
        source = repo.get("source", "")
        checkout_to = repo.get("checkout_to", "")
        if not source:
            findings.append({"severity": "warning", "message": f"repo has no source: {repo_id}"})
        elif not is_remote_source(source):
            findings.append({"severity": "warning", "message": f"repo source is not remote for {repo_id}: {source}"})
        if not checkout_to:
            findings.append({"severity": "warning", "message": f"repo has no checkout_to: {repo_id}"})

    return {
        "schema": "agentworkos.doctor.v1",
        "manifest": str(manifest_path),
        "profile": selected_profile,
        "ok": not any(item["severity"] == "error" for item in findings),
        "findings": findings,
    }


def render_doctor(report: dict[str, Any]) -> str:
    if not report["findings"]:
        return "AgentWorkOS doctor passed.\n"
    lines = ["AgentWorkOS doctor findings:"]
    for item in report["findings"]:
        lines.append(f"- [{item['severity']}] {item['message']}")
    return "\n".join(lines) + "\n"
