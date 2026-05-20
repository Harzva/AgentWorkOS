from __future__ import annotations

from pathlib import Path


def read_markdown_table_terms(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    terms: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "Term" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 3 and cells[0]:
            terms[cells[0]] = {"expanded": cells[1], "behavior": cells[2]}
    return terms


def explain(term: str, paths: list[Path]) -> str:
    for path in paths:
        entries = read_markdown_table_terms(path)
        if term in entries:
            item = entries[term]
            return f"{term}\nExpanded: {item['expanded']}\nBehavior: {item['behavior']}\nSource: {path}\n"
    searched = ", ".join(str(path) for path in paths)
    return f"Term not found: {term}\nSearched: {searched}\n"
