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
```

## Packages

```toml
[[packages]]
id = "io.github.just-agent.readme-design"
type = "skill"
source = "git+https://github.com/Just-Agent/README-Design-Skill.git"
path = "skills/readme-design"
install_to = "skills/readme-design"
ref = "main"
```

Fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable package identity |
| `type` | yes | `skill`, `agent`, `rule`, `terms`, `prompt`, `sop`, `hook`, `mcp`, or `repo` |
| `source` | yes | `git+https://...`, `https://...`, or local relative path |
| `path` | no | Subdirectory inside the source |
| `install_to` | yes for runtime packages | Relative path under the runtime home |
| `ref` | no | Branch, tag, or revision, default `main` |

## Repositories

```toml
[[repos]]
id = "io.github.harzva.make-windows-silky"
source = "https://github.com/Harzva/make_windows_silky_Patch.git"
checkout_to = "repos/make_windows_silky_Patch"
ref = "main"
```

Use `repos` for useful source checkouts that should exist in a workspace but are not installed into `.codex`.

## Local Overrides

Machine-specific paths should live in `agentworkos.local.toml`, which should not be committed.
