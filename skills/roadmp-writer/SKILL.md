---
name: roadmp-writer
description: "Use when writing, normalizing, splitting, auditing, or updating roadmp/roadmap Markdown files in the Just-DDL roadmpxx.md style: structured milestones, task files, checkbox governance, evidence-based completion, staged audits, candidate tables, assumptions, blockers, and Chinese production-roadmap prose."
---

# Roadmp Writer

## Purpose

Use this skill to write or normalize roadmap documents in the `roadmpxx.md` style.

This skill is for documentation structure and task governance. It does not execute a roadmap by itself. If the task is to implement Just-DDL work, combine it with `just-ddl-roadmap`.

## Fast Path

1. Read the existing main roadmap and the directly relevant task file.
2. Decide whether the change belongs in the main file, a detail file, or structured JSON.
3. Add the smallest evidence-backed update.
4. Keep broad completion criteria open until release evidence proves them.
5. Run the local roadmap audit script when available.

For Just-DDL, resolve paths from the checked-out project root:

- Main roadmap: `roadmpxx.md`
- Detail folder: `roadmpxx-tasks/`

## Naming

Preserve the project spelling already in use:

- Main file: `roadmpxx.md`
- Detail folder: `roadmpxx-tasks/`
- Detail files: `NN-short-topic-name.md`
- Candidate data: `topic-candidates.json` or another clear JSON file

Do not rename existing files just to correct spelling.

## Standard Roadmap Shape

A production roadmap should contain:

1. Title and one-sentence objective.
2. Usage rules for checkboxes, detail files, regression, and evidence.
3. Safety rules: no destructive rewrites, fake completion, or private notes in public surfaces.
4. Current baseline: repos, topics, counts, constraints, and working directories.
5. Key decisions: in scope, deferred, and must-not-change items.
6. Overall completion standards.
7. Phases with links to detail files.
8. Test plan and staged audit standards.
9. Assumptions and items needing user input.

Move dense implementation detail to `roadmpxx-tasks/*.md`.

## Checkbox Rules

- `[x]` means current evidence proves the item is complete.
- `[ ]` means not done, not verified, blocked, deferred, or still needs input.
- Never mark an item complete because it is planned, partially done, or likely true.
- If only a subset is done, rewrite the item to name the subset or keep the broader item open.
- Put evidence next to the checked item or in a dated evidence section.

Good:

```markdown
- [x] Hub `validate:time` blocks forecast windows from becoming next official DDL.
  - Evidence: 2026-05-26 `npm run validate:time` passed with 15 forecast windows checked.
- [ ] P2 anime sources still need more official pages before production expansion.
```

Bad:

```markdown
- [x] All topics are production ready.
```

unless a complete release audit proves every topic.

## Detail File Template

Use `templates/task-detail.md` for new detail files. Default structure:

- `目标`
- `范围`
- `Key Decisions`
- `Task List`
- `Evidence / 已完成证据`
- `Open Questions`
- `Test Plan`
- `Assumptions`

Use `templates/release-audit.md` before claiming production readiness.

## Writing Style

- Default to Chinese for project roadmap prose.
- Use short declarative sentences.
- Prefer concrete nouns: repo, topic, data source, validator, Action, Hub, miniprogram export.
- Separate decisions from evidence.
- Separate future work from completed work.
- Use exact dates such as `2026-05-28` for evidence and incidents.
- Avoid vague claims such as “基本完成”, “应该可以”, or “后续优化” unless followed by a concrete open task.

For detailed style rules, read `references/style-guide.md`.

## Governance Rules

- Do not shrink a broad goal into a convenient small task.
- Do not erase unfinished tasks to make progress look cleaner.
- Do not hide blockers; record them as open tasks or questions.
- Do not duplicate the same task across many sections unless one is a summary and the other is the source of truth.
- Do not rewrite large sections unless the user asks for reorganization.

For checkbox and evidence edge cases, read:

- `references/checkbox-rules.md`
- `references/evidence-rules.md`

## Public / Private Boundary

If the roadmap controls a public product, avoid normalizing private maintenance leakage into future work.

Use public-safe wording:

- `公开来源`
- `授权导入来源`
- `预测不是官方日期`
- `人工核验入口`
- `贡献机会`

Do not publish raw internal terms in READMEs, Pages, miniprogram exports, or contributor docs:

- `apiUrl`
- `parser`
- `forecastBasis`
- `releaseCadence`
- raw crawl errors
- token paths
- import file paths
- developer or maintainer notes

Private roadmap docs may mention these as internal validation concerns, but public-facing docs must rewrite them into user-safe language.

## Scripts

Use bundled scripts when practical:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/audit-roadmp.ps1 -Roadmap path\to\roadmpxx.md
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/new-roadmp-task.ps1 -TasksDir path\to\roadmpxx-tasks -Number 14 -Slug example-task -Title "Example Task"
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/summarize-roadmp-state.ps1 -Roadmap path\to\roadmpxx.md
```

The scripts are guardrails, not proof of completion. Evidence still needs human review.

## Relationship To AgentWorkOS

This skill should live in the AgentWorkOS source repository under `skills/roadmp-writer/`, then be projected into local runtimes by:

```powershell
aw sync --target codex --profile codex --apply
```

Direct edits under `.codex/skills/roadmp-writer` are runtime hotfixes only; they are not the source of truth.
