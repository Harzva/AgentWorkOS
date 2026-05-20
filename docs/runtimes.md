# 支持的智能体

AgentWorkOS 的原则是：已验证的 runtime 才打勾，计划中的 adapter 不冒充已支持。

## Support Matrix

| Runtime | Status | Skills | Agents / Subagents | Rules / Memory | Commands / Prompts | Terms | MCP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | ✅ supported | ✅ | ✅ | ✅ | adapter | ✅ | adapter |
| Claude Code | ✅ supported | ✅ | ✅ | ✅ | ✅ | ✅ | adapter |
| Cursor | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| Windsurf | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| Gemini CLI | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| OpenCode | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |

## 当前支持范围

### Codex

Codex target 当前支持：

- `.codex/skills/<name>/SKILL.md`
- `.codex/agents/roles/<name>.md`
- `.codex/agents/TERMS.md`
- `AGENTS.md` 项目规则
- MCP config adapter 作为计划项

### Claude Code

Claude Code target 当前支持：

- `~/.claude/skills/<name>/SKILL.md`
- `~/.claude/agents/<name>.md`
- `.claude/agents/<name>.md`
- `~/.claude/commands/<name>.md`
- `CLAUDE.md` / `~/.claude/TERMS.md` memory adapter

## 为什么不是所有 agent 都打勾

不同 agent runtime 的文件布局、metadata、命令机制、memory 机制都不一样。

AgentWorkOS 使用 `[[packages.targets]]` 显式声明 adapter：

```toml
[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"
```

这保证 package identity 稳定，runtime projection 可以单独演化。

## 状态含义

| Status | 含义 |
| --- | --- |
| supported | 已有 CLI 路径、manifest target、测试或文档验收 |
| adapter | 能声明目标，但需要 runtime-specific 转换增强 |
| planned | 只进入路线图，不承诺当前可用 |
