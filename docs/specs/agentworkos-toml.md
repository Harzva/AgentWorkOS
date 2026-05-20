# `agentworkos.toml` Spec

`agentworkos.toml` declares a desired AgentWorkOS Stack.

It is intentionally human-editable and lockfile-backed.

## Required Top-Level Tables

```toml
[stack]
name = "default-agentworkos"
version = "0.1.0"
platforms = ["windows-x64"]
codex_home = "C:/Users/example/.codex"
claude_home = "~/.claude"
```

## Packages

```toml
[[packages]]
id = "io.github.just-agent.readme-design"
type = "skill"
source = "github:Just-Agent/README-Design-Skill"
path = "skills/readme-design"
install_to = "skills/readme-design"
ref = "main"

[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"
```

Fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable package identity |
| `type` | yes | `skill`, `agent`, `rule`, `terms`, `prompt`, `sop`, `hook`, `mcp`, or `repo` |
| `source` | yes | `github:OWNER/REPO`, `git+https://...`, `https://...`, or local relative path |
| `path` | no | Subdirectory inside the source |
| `install_to` | yes for runtime packages | Relative path under the runtime home |
| `ref` | no | Branch, tag, or revision, default `main` |
| `targets` | no | Runtime-specific install targets for Codex, Claude Code, or future adapters |

## Target Adapters

Different agent runtimes do not share the same filesystem layout or metadata rules.

Use `[[packages.targets]]` when a package must be projected into more than one runtime:

```toml
[[packages.targets]]
runtime = "codex"
install_to = "skills/readme-design"

[[packages.targets]]
runtime = "claude-code"
install_to = "skills/readme-design"
adapter = "skill-to-claude-skill"
```

The canonical package stays the same. The target adapter decides where and how it is installed.

## Remote Sources

Remote package sources are cached under `AW_HOME`, defaulting to `~/.agentworkos`:

```text
~/.agentworkos/sources/github.com/OWNER/REPO
```

`aw sync --apply` clones or fetches remote sources before installing them into the selected runtime target. Without `--apply`, it prints the planned clone/fetch and copy actions.

## Repositories

```toml
[[repos]]
id = "io.github.harzva.make-windows-silky"
source = "https://github.com/Harzva/make_windows_silky_Patch.git"
checkout_to = "repos/make_windows_silky_Patch"
ref = "main"
```

Use `repos` for useful source checkouts that should exist in a workspace but are not installed into an agent runtime.

## Local Overrides

Machine-specific paths should live in `agentworkos.local.toml`, which should not be committed.
