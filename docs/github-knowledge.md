# GitHub 知识管理

AgentWorkOS 把 GitHub 当作 agent 知识源，而不是只当代码托管。

## 推荐仓库分层

| 仓库 | 用途 | 典型文件 |
| --- | --- | --- |
| `AgentWorkOS-Stack` | 个人总环境入口 | `agentworkos.toml`, `agentworkos.lock.json`, `TERMS.md` |
| Skill repos | 可复用技能包 | `SKILL.md`, `agentpkg.toml`, docs, tests |
| Agent repos | 角色卡和分发规则 | role cards, `AGENTS.md`, `CLAUDE.md` adapters |
| SOP repos | 可复用流程 | checklists, prompts, scripts |

## 同步关系

```text
GitHub source repo
  -> aw install / aw sync
  -> ~/.agentworkos/sources cache
  -> ~/.codex and ~/.claude runtime targets
```

`aw install github:OWNER/REPO` 更像 `pip install git+...`。

`agentworkos.toml` 更像 `requirements.txt`：它声明这个环境要哪些包、从哪里来、装到哪里。

`agentworkos.lock.json` 更像 `uv.lock`：它记录当时解析到的 source、commit、hash 和 target 信息。

## 什么时候必须上传 GitHub

本机单次实验可以只用本地路径：

```toml
source = "./skills/readme-design"
```

跨电脑、团队共享、长期维护时，应该把 Stack Repo 和可复用 Package Repo 推到 GitHub：

```toml
source = "github:OWNER/readme-design"
ref = "main"
```

然后在新机器执行：

```powershell
aw install github:OWNER/AgentWorkOS-Stack --target all --apply
```

## 三端同步

在 AgentWorkOS 语境里，三端同步指：

| 端 | 例子 | 验证 |
| --- | --- | --- |
| Runtime copy | `~/.codex`, `~/.claude` | `aw scan`, `aw sync` dry-run |
| Local source repo | `D:/.../AgentWorkOS-Stack` | `git status`, `aw doctor` |
| Remote GitHub repo | `github.com/OWNER/AgentWorkOS-Stack` | `git push`, lockfile commit |

规则：只改 runtime 不算完成，只改本地 repo 不算完成，只推 GitHub 但 runtime 没同步也不算完成。

## 包源选择

| Source | 适合场景 |
| --- | --- |
| `github:OWNER/REPO` | 推荐写法，最短 |
| `https://github.com/OWNER/REPO` | 兼容直链 |
| `git+https://github.com/OWNER/REPO.git` | 类 pip 的 git source 写法 |
| `./local/path` | 本机开发和调试 |

## 最小可迁移闭环

```powershell
aw lock
aw doctor
git add .
git commit -m "Update AgentWorkOS stack"
git push

# on another machine
aw install github:OWNER/AgentWorkOS-Stack --target all --apply
aw scan
```
