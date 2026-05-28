# Evidence Rules

## Strong Evidence

- Test command passed and covers the requirement.
- Validator specifically checks the invariant.
- File exists and contains required fields.
- Remote branch points to the expected commit.
- Public build output was inspected for the public-surface rule.

## Weak Evidence

- A command passed but does not cover the requirement.
- A plan says the work will happen.
- A prior conversation claims completion.
- A local fallback works but remote Pages or Actions are not live.

## Evidence Format

Use dated bullets:

```markdown
- 2026-05-28 `npm run validate:time` passed; checked 15 forecast windows.
- 2026-05-28 `git rev-parse HEAD` = `abc123`.
```
