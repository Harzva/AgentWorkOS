# Agent Runtime Targets

AgentWorkOS packages are canonical. Agent runtimes are adapters.

This matters because Codex and Claude Code do not distribute context in exactly the same shape.

## Target Matrix

| Capability | Canonical AgentWorkOS type | Codex target | Claude Code target |
| --- | --- | --- | --- |
| Project/global rules | `rule` | `AGENTS.md` and local agent rules | `CLAUDE.md` memory files |
| Skill package | `skill` | `.codex/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md` or project `.claude/skills` when supported |
| Role card / subagent | `agent` | `.codex/agents/roles/<name>.md` or Codex subagent adapter | `~/.claude/agents/<name>.md` or `.claude/agents/<name>.md` |
| Slash command | `prompt` | Codex command adapter | `.claude/commands/<name>.md` or `~/.claude/commands/<name>.md` |
| Term map | `terms` | `.codex/agents/TERMS.md` | `CLAUDE.md` section or `~/.claude/TERMS.md` adapter |
| MCP config | `mcp` | Codex MCP config adapter | Claude Code MCP settings adapter |

## Why Adapters Exist

Codex and Claude Code both support persistent context, but their distribution details differ:

- Codex uses `AGENTS.md` as a custom-instructions mechanism, with documented configuration areas for AGENTS.md, rules, hooks, MCP, skills, and subagents.
- Claude Code subagents are Markdown files with YAML frontmatter under project `.claude/agents/` or user `~/.claude/agents/`.
- Claude Code custom slash commands are Markdown files under `.claude/commands/` or `~/.claude/commands/`.
- Claude Code also uses `CLAUDE.md` memory files and settings.

Sources:

- [OpenAI Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Anthropic Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Anthropic Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
- [Anthropic Claude Code settings](https://docs.anthropic.com/en/docs/claude-code/settings)

## Adapter Contract

Every adapter should be explicit about:

- `runtime`: `codex`, `claude-code`, or future target;
- `install_to`: runtime-relative target path;
- `adapter`: conversion strategy name;
- `lossiness`: whether conversion drops metadata;
- `verify`: how the target install is checked.

Example:

```toml
[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"
```

## Rule

Never flatten runtime-specific behavior into the package identity.

The package identity is stable. The target adapter is allowed to vary.
