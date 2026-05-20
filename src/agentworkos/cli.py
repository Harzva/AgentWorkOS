from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .doctor import render_doctor, run_doctor
from .install import install_source
from .lockfile import write_lock
from .manifest import write_sample_stack, write_sample_terms
from .scan import render_audit, scan_environment
from .sync import sync_manifest
from .terms import explain
from .util import default_codex_home, json_dump


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest = root / "agentworkos.toml"
    terms = root / "TERMS.md"
    if manifest.exists() and not args.force:
        print(f"exists: {manifest}")
    else:
        write_sample_stack(manifest, codex_home=Path(args.codex_home).expanduser() if args.codex_home else None)
        print(f"wrote: {manifest}")
    if terms.exists() and not args.force:
        print(f"exists: {terms}")
    else:
        write_sample_terms(terms)
        print(f"wrote: {terms}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    state = scan_environment(
        codex_home=Path(args.codex_home).expanduser() if args.codex_home else None,
        claude_home=Path(args.claude_home).expanduser() if args.claude_home else None,
        workspace=Path(args.workspace).expanduser() if args.workspace else None,
    )
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    json_dump(output_json, state)
    output_md.write_text(render_audit(state), encoding="utf-8")
    print(f"wrote: {output_json}")
    print(f"wrote: {output_md}")
    print(
        " ".join(
            [
                f"codex_skills={state['summary']['skills']}",
                f"codex_agents={state['summary']['agents']}",
                f"claude_skills={state['summary']['claude_skills']}",
                f"claude_agents={state['summary']['claude_agents']}",
                f"repos={state['summary']['repos']}",
            ]
        )
    )
    return 0


def cmd_lock(args: argparse.Namespace) -> int:
    payload = write_lock(Path(args.manifest), Path(args.output), offline=args.offline)
    print(f"wrote: {args.output}")
    print(f"packages={len(payload['packages'])} repos={len(payload['repos'])}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    report = run_doctor(Path(args.manifest))
    print(render_doctor(report), end="")
    return 0 if report["ok"] else 1


def cmd_sync(args: argparse.Namespace) -> int:
    report = sync_manifest(
        Path(args.manifest),
        apply=args.apply,
        target=args.target,
        aw_home=Path(args.aw_home).expanduser() if args.aw_home else None,
    )
    for action in report["actions"]:
        print(action)
    if not args.apply:
        print("dry-run only; pass --apply to write runtime files")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    report = install_source(
        args.source,
        ref=args.ref,
        target=args.target,
        apply=args.apply,
        aw_home=Path(args.aw_home).expanduser() if args.aw_home else None,
    )
    for action in report["actions"]:
        print(action)
    if not args.apply:
        print("dry-run only; pass --apply to write cache and runtime files")
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    paths = [Path(path) for path in args.terms]
    if not paths:
        paths = [Path.cwd() / "TERMS.md", default_codex_home() / "agents" / "TERMS.md"]
    print(explain(args.term, paths), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aw", description="AgentWorkOS package manager")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create an agentworkos.toml and TERMS.md")
    init.add_argument("--root", default=".")
    init.add_argument("--codex-home", default="")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    scan = sub.add_parser("scan", help="scan local AgentWorkOS runtime and workspace")
    scan.add_argument("--codex-home", default="")
    scan.add_argument("--claude-home", default="")
    scan.add_argument("--workspace", default=".")
    scan.add_argument("--output-json", default="agentworkos.state.json")
    scan.add_argument("--output-md", default="AGENTWORKOS_AUDIT.md")
    scan.set_defaults(func=cmd_scan)

    lock = sub.add_parser("lock", help="create agentworkos.lock.json")
    lock.add_argument("--manifest", default="agentworkos.toml")
    lock.add_argument("--output", default="agentworkos.lock.json")
    lock.add_argument("--offline", action="store_true")
    lock.set_defaults(func=cmd_lock)

    doctor = sub.add_parser("doctor", help="check manifest health")
    doctor.add_argument("--manifest", default="agentworkos.toml")
    doctor.set_defaults(func=cmd_doctor)

    sync = sub.add_parser("sync", help="sync local packages into runtime; dry-run by default")
    sync.add_argument("--manifest", default="agentworkos.toml")
    sync.add_argument("--target", choices=["codex", "claude", "claude-code", "all"], default="codex")
    sync.add_argument("--aw-home", default="")
    sync.add_argument("--apply", action="store_true")
    sync.set_defaults(func=cmd_sync)

    install = sub.add_parser("install", help="install an AgentWorkOS stack or package from GitHub")
    install.add_argument("source")
    install.add_argument("--ref", default="main")
    install.add_argument("--target", choices=["codex", "claude", "claude-code", "all"], default="codex")
    install.add_argument("--aw-home", default="")
    install.add_argument("--apply", action="store_true")
    install.set_defaults(func=cmd_install)

    explain_parser = sub.add_parser("explain", help="explain a local shorthand term")
    explain_parser.add_argument("term")
    explain_parser.add_argument("--terms", action="append", default=[])
    explain_parser.set_defaults(func=cmd_explain)

    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI needs concise user-facing errors.
        print(f"aw: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
