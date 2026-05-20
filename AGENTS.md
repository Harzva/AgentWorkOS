# AgentWorkOS Agent Rules

## Mission

AgentWorkOS makes AI agent workspaces package-managed: scannable, lockable, installable, syncable, and verifiable.

## Package Manager Safety

- `aw sync` must be dry-run by default.
- Runtime writes require an explicit `--apply` flag.
- Do not commit secrets, cookies, tokens, raw private chat logs, or local credential files.
- Prefer manifests, lockfiles, schemas, and doctor checks over undocumented local state.

## Vocabulary

- `AgentWorkOS` is the operating layer and ecosystem.
- `AgentWorkOS Package` is one installable capability unit: Skill, Agent role, Rule, Term map, Prompt, SOP, Hook, MCP config, or Repo.
- `AgentWorkOS Stack` is a complete environment declaration, similar to a conda environment or requirements file.
- `aw` is the CLI package manager.

## Completion Gate

Every feature must include at least one of:

- CLI command;
- schema/spec update;
- test fixture;
- example stack;
- doctor/verify rule;
- README or docs update.

Public claims must point to files, commands, schemas, tests, or repository URLs.
