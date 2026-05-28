# Checkbox Rules

## Completion

`[x]` requires evidence. Evidence can be:

- command output,
- file path and content inspection,
- commit hash,
- CI run,
- screenshot,
- deployed URL,
- user acceptance,
- explicit deferral decision for a scoped item.

## Partial Completion

Do not check a broad item when only part is done.

Instead:

```markdown
- [x] Sports subtopics include basketball, football, and marathon.
- [ ] Sports still needs official-source expansion for more leagues.
```

## Blocked Work

Blocked work stays unchecked:

```markdown
- [ ] CAS quartile history needs authorized import data.
  - Blocker: source workbook does not contain quartile columns.
```
