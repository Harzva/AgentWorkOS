---
name: agentworkos-inventory
description: Scan and package-manage a local AgentWorkOS environment, including Codex skills, agent role cards, TERMS.md, AGENTS.md rules, local repositories, lockfiles, and sync drift. Use when the user asks to migrate machines, restore AI workspace context, package skills, or verify three-end sync.
---

# AgentWorkOS Inventory

Use this skill to turn a local AI agent workspace into a package-managed environment.

## Workflow

1. Scan the runtime.

   ```powershell
   aw scan --codex-home "$env:USERPROFILE\.codex" --workspace .
   ```

2. Inspect `AGENTWORKOS_AUDIT.md`.

3. Create or update `agentworkos.toml`.

4. Generate a lockfile.

   ```powershell
   aw lock
   ```

5. Run doctor.

   ```powershell
   aw doctor
   ```

6. Sync safely.

   ```powershell
   aw sync
   aw sync --apply
   ```

## Three-End Sync

When the user says `三端同步`, verify:

- installed runtime copy;
- local source repository;
- remote GitHub repository.

Do not call sync complete until local status is clean and the remote commit matches the local source commit.

## Output Contract

- Scan summary.
- Drift findings.
- Manifest or lockfile updates.
- Commands run.
- Remaining risks.

## Safety

Do not copy secrets, raw chat logs, token files, cookies, or local credential dumps into public manifests.
