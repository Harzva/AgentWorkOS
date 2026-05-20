from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import load_toml


def run_doctor(manifest_path: Path) -> dict[str, Any]:
    manifest = load_toml(manifest_path)
    base = manifest_path.parent
    findings: list[dict[str, str]] = []
    seen: set[str] = set()

    for package in manifest.get("packages", []):
        package_id = package.get("id", "")
        if not package_id:
            findings.append({"severity": "error", "message": "package missing id"})
        elif package_id in seen:
            findings.append({"severity": "error", "message": f"duplicate package id: {package_id}"})
        seen.add(package_id)

        source = package.get("source", "")
        if source and not source.startswith(("git+", "https://")):
            if not (base / source).exists():
                findings.append({"severity": "warning", "message": f"local source missing for {package_id}: {source}"})

        if not package.get("install_to"):
            findings.append({"severity": "warning", "message": f"package has no install_to: {package_id}"})

    stack = manifest.get("stack", {})
    codex_home = stack.get("codex_home", "")
    if codex_home and not Path(codex_home).expanduser().exists():
        findings.append({"severity": "warning", "message": f"codex_home does not exist: {codex_home}"})

    return {
        "schema": "agentworkos.doctor.v1",
        "manifest": str(manifest_path),
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
