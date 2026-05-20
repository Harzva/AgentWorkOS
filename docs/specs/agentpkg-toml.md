# `agentpkg.toml` Spec

`agentpkg.toml` describes one AgentWorkOS Package.

## Example

```toml
[package]
id = "io.github.just-agent.readme-design"
name = "readme-design"
type = "skill"
version = "0.1.0"
description = "Design and polish GitHub README homepages."
license = "MIT"

[source]
repo = "github:Just-Agent/README-Design-Skill"
path = "skills/readme-design"

[install]
target = "skills/readme-design"

[[targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"

[verify]
entrypoint = "SKILL.md"
```

## Package Types

- `skill`
- `agent`
- `rule`
- `terms`
- `prompt`
- `sop`
- `hook`
- `mcp`
- `repo`

## Minimum Quality Bar

Every package should have:

- stable ID;
- package type;
- source URL or local source;
- install target;
- verification entrypoint;
- license;
- README or usage notes;
- no secrets or private raw logs.

## Runtime Targets

`targets` are optional runtime projections. They let one canonical package declare different install paths for Codex, Claude Code, and future agent runtimes.

AgentWorkOS should not pretend all runtimes are identical. It should preserve one canonical source and adapt it carefully.

## Installing From GitHub

A repository with `agentpkg.toml` can be installed directly:

```powershell
aw install github:OWNER/REPO --target codex --apply
```

AgentWorkOS reads `[source].path`, `[install].target`, and optional `[[targets]]` entries, then projects the package into the requested runtime.
