# Roadmp Style Guide

## Voice

- Use direct Chinese prose.
- Prefer factual status over motivation.
- Keep the main roadmap concise; move detail to task files.

## Structure

- The main roadmap is a control plane.
- Detail files are execution plans and evidence logs.
- JSON files are for structured candidate lists, not prose.

## Dates

- Use exact dates for evidence.
- Avoid relative-only phrases such as “今天” unless paired with a date.

## Evidence Language

Good:

- `2026-05-28 npm run build passed.`
- `Commit abc123 pushed to origin/main.`
- `Hub miniprogram export contains 37 topic JSON files.`

Weak:

- `已经差不多了`
- `应该没问题`
- `后续优化`

## Public-Surface Wording

Use public-safe words in public docs:

- `公开来源`
- `授权导入来源`
- `预测不是官方日期`
- `待官方公告`

Keep internal maintenance terms out of public docs.
