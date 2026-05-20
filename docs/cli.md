# CLI

AgentWorkOS 的 CLI 叫 `aw`。

`awos` 仍保留为兼容别名，新文档和脚本统一使用 `aw`。

## Commands

| Command | Purpose |
| --- | --- |
| `aw init` | 创建 `agentworkos.toml` 和 `TERMS.md` |
| `aw scan` | 扫描 Codex、Claude Code 和 workspace repo |
| `aw lock` | 生成 `agentworkos.lock.json` |
| `aw sync` | 将 manifest 中的包同步到 runtime，默认 dry-run |
| `aw install` | 从 GitHub 安装 Stack Repo 或 Package Repo |
| `aw doctor` | 检查 manifest 健康状态 |
| `aw explain` | 展开 `TERMS.md` 里的本地术语 |

## `aw install`

```powershell
aw install <source> [--ref main] [--target codex|claude-code|all] [--apply]
```

支持 source：

```text
github:OWNER/REPO
https://github.com/OWNER/REPO
git+https://github.com/OWNER/REPO.git
```

识别规则：

| Remote file | Repo type | Behavior |
| --- | --- | --- |
| `agentworkos.toml` | Stack Repo | 同步整个 stack |
| `agentpkg.toml` | Package Repo | 安装单个 package |
| neither | invalid | 退出并提示缺少 manifest |

默认只 dry-run：

```powershell
aw install github:OWNER/AgentWorkOS-Stack --target all
```

确认计划正确后：

```powershell
aw install github:OWNER/AgentWorkOS-Stack --target all --apply
```

## Cache

远程 repo cache 默认在：

```text
~/.agentworkos/sources/github.com/OWNER/REPO
```

可以用 `AW_HOME` 覆盖：

```powershell
$env:AW_HOME = "D:\AgentWorkOS"
aw install github:OWNER/AgentWorkOS-Stack --apply
```

## `aw sync`

```powershell
aw sync --manifest agentworkos.toml --target codex
aw sync --manifest agentworkos.toml --target claude-code
aw sync --manifest agentworkos.toml --target all
```

如果 `source` 是远程 GitHub repo，`--apply` 会先 clone/fetch 到 `AW_HOME` cache，再安装到 runtime。

## Safety

- `install` 和 `sync` 默认 dry-run。
- `--apply` 才会写 cache 或 runtime。
- remote cache 与 runtime target 分离。
- 本地私密覆盖应放在不提交的 `agentworkos.local.toml`。
