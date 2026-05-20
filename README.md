<div align="center">
  <img src="./docs/readme-assets/logo.svg" alt="AgentWorkOS logo" width="220" />
  <h1>AgentWorkOS</h1>
  <p><strong>A package manager for portable AI agent workspaces.</strong></p>
  <p>
    Declare Skills, agents, rules, prompts, term maps, MCP configs, hooks, and repo checkouts once.
    Sync them into Codex, Claude Code, and future agent runtimes with explicit target adapters.
  </p>
  <p>
    <a href="./docs/specs/agentworkos-toml.md">Stack Spec</a>
    ·
    <a href="./docs/specs/agentpkg-toml.md">Package Spec</a>
    ·
    <a href="./docs/agent-targets.md">Runtime Targets</a>
    ·
    <a href="./schemas">Schemas</a>
    ·
    <a href="./examples/harzva-default">Example Stack</a>
  </p>
  <p>
    <img alt="CLI" src="https://img.shields.io/badge/cli-aw-2563eb" />
    <img alt="Status" src="https://img.shields.io/badge/status-alpha-f59e0b" />
    <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-0f766e" />
    <img alt="License" src="https://img.shields.io/badge/license-MIT-111827" />
  </p>
</div>

<p align="center">
  <img src="./docs/readme-assets/architecture.svg" alt="AgentWorkOS architecture" width="920" />
</p>

## Why This Exists

AI agent workspaces are becoming real development environments, but their context is still scattered across local Skills, role cards, `AGENTS.md`, `CLAUDE.md`, prompts, MCP settings, hooks, and useful repositories.

`AgentWorkOS` turns that loose context into a package-managed stack:

| Need | AgentWorkOS answer |
| --- | --- |
| Move to a new machine | `agentworkos.toml` + `agentworkos.lock.json` describe what to install |
| Compare local runtime drift | `aw scan` inventories Codex, Claude Code, and repo state |
| Install safely | `aw sync` is dry-run by default; writes require `--apply` |
| Explain local shorthand | `aw explain 三端同步` expands team-specific terms from `TERMS.md` |
| Support multiple agents | runtime-specific `targets` map one package to Codex, Claude Code, or future adapters |

## 30-Second Start

```powershell
python -m pip install -e .
aw init --root .
aw scan --codex-home "$env:USERPROFILE\.codex" --claude-home "$env:USERPROFILE\.claude" --workspace .
aw lock --offline
aw doctor
aw sync
```

`sync` is dry-run by default. Apply only after the plan looks right:

```powershell
aw sync --apply
aw sync --target claude-code --apply
```

`awos` remains available as a backward-compatible alias, but new docs and scripts use `aw`.

## Runtime Targets

Codex and Claude Code do not package context in exactly the same shape, so AgentWorkOS keeps package identity separate from runtime projection.

| Package type | Codex target | Claude Code target |
| --- | --- | --- |
| `skill` | `.codex/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` when supported |
| `agent` | `.codex/agents/roles/<name>.md` | `~/.claude/agents/<name>.md` or project `.claude/agents/<name>.md` |
| `rule` | `AGENTS.md` or local agent rules | `CLAUDE.md` memory files |
| `prompt` | command or prompt adapter | `.claude/commands/<name>.md` |
| `terms` | `.codex/agents/TERMS.md` | `CLAUDE.md` section or `~/.claude/TERMS.md` adapter |

Example target declaration:

```toml
[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"
```

See [Agent Runtime Targets](./docs/agent-targets.md) for the adapter matrix and official runtime references.

## Core Concepts

| Concept | File | Similar idea |
| --- | --- | --- |
| Stack | `agentworkos.toml` | `environment.yml`, `requirements.txt`, `pyproject.toml` |
| Lockfile | `agentworkos.lock.json` | `uv.lock`, `flake.lock` |
| Package | `agentpkg.toml` or `[[packages]]` | package metadata |
| Target | `[[packages.targets]]` | runtime adapter output |
| Runtime | `.codex`, `.claude`, local repos | installed environment |
| Doctor | `aw doctor` | environment health check |
| Term map | `TERMS.md` | shorthand expansion table |

## Commands

| Command | Purpose |
| --- | --- |
| `aw init` | Create a sample stack manifest and term map |
| `aw scan` | Inventory local Skills, agents, terms, Claude Code assets, and repos |
| `aw lock` | Generate `agentworkos.lock.json` from the manifest |
| `aw sync` | Dry-run package installation into runtime paths |
| `aw sync --target claude-code` | Project packages into the Claude Code runtime |
| `aw sync --apply` | Apply local package sync |
| `aw doctor` | Check manifest health and common drift |
| `aw explain 三端同步` | Expand a shorthand term from `TERMS.md` |

## Package Types

| Type | Meaning |
| --- | --- |
| `skill` | A `SKILL.md` capability package plus supporting files |
| `agent` | A role card, local agent definition, or subagent source |
| `rule` | `AGENTS.md`, `CLAUDE.md`, or hard operating rule |
| `terms` | Versioned shorthand glossary |
| `prompt` | Reusable prompt or slash-command source |
| `sop` | Standard operating procedure |
| `hook` | Lifecycle check or future automation contract |
| `mcp` | MCP/tool config description |
| `repo` | Useful source repository checkout |

## Repository Layout

```text
AgentWorkOS/
├─ src/agentworkos/       # aw CLI implementation
├─ schemas/               # JSON schemas for stack, lock, and packages
├─ docs/specs/            # human-readable specs
├─ docs/agent-targets.md  # Codex / Claude Code adapter model
├─ examples/              # sample AgentWorkOS stack
├─ skills/                # installable AgentWorkOS skills
├─ scripts/               # bootstrap helpers
└─ tests/                 # CLI and parser tests
```

## Design Inspirations

AgentWorkOS borrows proven package-management ideas rather than inventing hidden state:

- `uv`: one fast CLI for projects, locks, sync, tools, and Python environments.
- `conda`: environment files for complete machine-portable setups.
- `pip`: plain dependency declarations that are easy to review.
- Nix flakes: declared inputs plus lockfiles for reproducibility.

See [docs/inspirations.md](./docs/inspirations.md) for source links and adoption notes.

## Roadmap

| Stage | Target |
| --- | --- |
| v0.1 | Scan, init, lock, doctor, dry-run sync, explain terms |
| v0.2 | Runtime target adapters for Codex and Claude Code |
| v0.3 | Remote git package cache and locked install |
| v0.4 | `agentpkg.toml` validation and package publish checklist |
| v0.5 | Three-end sync verifier for runtime, source repo, and remote |
| v1.0 | Stable AgentWorkOS Package Spec |

## Safety

- No destructive sync by default.
- Runtime writes require `--apply`.
- No secret collection.
- No raw private chat log packaging.
- Local paths belong in `agentworkos.local.toml`, not public stack manifests.
- Public packages should include specs, schemas, docs, tests, and release proof.

## License

MIT
