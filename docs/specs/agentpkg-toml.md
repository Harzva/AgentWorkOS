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
repo = "https://github.com/Just-Agent/README-Design-Skill.git"
path = "skills/readme-design"

[install]
target = "skills/readme-design"

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
