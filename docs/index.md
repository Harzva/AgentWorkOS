# AgentWorkOS

AgentWorkOS 是 AI agent 工作环境的包管理层。

它把 Skills、Agent roles、Rules、Prompts、Terms、MCP 配置、Hooks 和常用仓库放进一个可声明、可锁定、可同步、可验证的 GitHub 知识系统。

![AgentWorkOS architecture](readme-assets/architecture.svg)

## 现在支持哪些智能体

| Runtime | Status | Skills | Agents / Subagents | Rules / Memory | Commands / Prompts | Terms | MCP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | ✅ supported | ✅ | ✅ | ✅ | adapter | ✅ | adapter |
| Claude Code | ✅ supported | ✅ | ✅ | ✅ | ✅ | ✅ | adapter |
| Cursor | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| Windsurf | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| Gemini CLI | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |
| OpenCode | 🚧 planned | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |

第一版只给 Codex 和 Claude Code 打支持标记。其他 runtime 进入 adapter roadmap，不做超前承诺。

## 一句话模型

```text
GitHub Stack Repo -> agentworkos.toml -> agentworkos.lock.json -> aw install/sync -> .codex / .claude
```

类比传统开发工具：

| AgentWorkOS | 类比 |
| --- | --- |
| `agentworkos.toml` | `requirements.txt` / `environment.yml` |
| `agentworkos.lock.json` | `uv.lock` / `flake.lock` |
| GitHub Stack Repo | 可迁移的知识源仓库 |
| `aw install github:OWNER/REPO` | `pip install git+...` |
| `aw sync` | 把声明的知识包安装到 agent runtime |

## 最短路径

```powershell
python -m pip install -e .
aw install github:Harzva/AgentWorkOS --target all
aw doctor
aw scan
```

`install` 和 `sync` 默认都是 dry-run。确认计划无误后再加 `--apply`。

```powershell
aw install github:Harzva/AgentWorkOS --target all --apply
```

下一步阅读：[快速上手](getting-started.md)。
