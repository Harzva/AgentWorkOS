# Design Inspirations

AgentWorkOS borrows from mature package and environment managers.

| System | What AgentWorkOS borrows | Source |
| --- | --- | --- |
| uv | One CLI for init, lock, sync, tool-style workflows, and fast environment operations | [uv docs](https://docs.astral.sh/uv/) |
| conda | A portable environment declaration file | [environment.yml spec](https://conda.org/learn/specifications/exchange/environment-yml/) |
| pip | Simple dependency declaration and requirements-style portability | [requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/) |
| Nix flakes | Declared inputs plus a lockfile for reproducible environments | [Nix flakes](https://nix.dev/concepts/flakes) |

## Design Translation

| Existing ecosystem idea | AgentWorkOS equivalent |
| --- | --- |
| `pyproject.toml` | `agentworkos.toml` |
| `requirements.txt` | package list inside `agentworkos.toml` |
| `environment.yml` | complete AgentWorkOS stack |
| `uv.lock` / `flake.lock` | `agentworkos.lock.json` |
| virtual environment | `.codex` runtime plus checked-out source repos |
| package metadata | `agentpkg.toml` |
| environment doctor | `aw doctor` |

## Boundary

AgentWorkOS is not a replacement for Python, Node, Nix, or Conda package managers.

It manages the agent layer:

- skills;
- role cards;
- rules;
- terminology;
- prompts;
- SOPs;
- MCP configs;
- hooks;
- source repositories;
- local runtime copies.
