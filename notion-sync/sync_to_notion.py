#!/usr/bin/env python3
"""
sync_to_notion.py - Sync markdown files to Notion databases

Sources:
  - ~/.claude/commands/*.md  →  Claude Skills database
  - ~/knowledge-base/*.md    →  Knowledge Base database

Usage:
  python3 sync_to_notion.py
  python3 sync_to_notion.py --dry-run
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

import yaml
import requests

NOTION_VERSION = "2022-06-28"


# ---------------------------------------------------------------------------
# Notion REST client (direct HTTP, no SDK version issues)
# ---------------------------------------------------------------------------

class Notion:
    def __init__(self, token: str):
        self.base = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _get(self, path: str) -> dict:
        r = requests.get(f"{self.base}{path}", headers=self.headers)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        r = requests.post(f"{self.base}{path}", headers=self.headers, json=body)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, body: dict) -> dict:
        r = requests.patch(f"{self.base}{path}", headers=self.headers, json=body)
        r.raise_for_status()
        return r.json()

    def query_database(self, database_id: str, filter_body: dict = None) -> list:
        body = filter_body or {}
        data = self._post(f"/databases/{database_id}/query", body)
        return data.get("results", [])

    def create_page(self, parent_db_id: str, properties: dict, children: list) -> dict:
        return self._post("/pages", {
            "parent": {"database_id": parent_db_id},
            "properties": properties,
            "children": children,
        })

    def update_page(self, page_id: str, properties: dict) -> dict:
        return self._patch(f"/pages/{page_id}", {"properties": properties})

    def append_blocks(self, block_id: str, children: list) -> dict:
        return self._patch(f"/blocks/{block_id}/children", {"children": children})


# ---------------------------------------------------------------------------
# Markdown → Notion block converter
# ---------------------------------------------------------------------------

NOTION_TEXT_LIMIT = 1990  # Notion rich_text max is 2000 chars

def _rich_text(text: str) -> list:
    return [{"type": "text", "text": {"content": text[:NOTION_TEXT_LIMIT]}}]

NOTION_SUPPORTED_LANGS = {
    "abap","arduino","bash","basic","c","clojure","coffeescript","c++","c#",
    "css","dart","diff","docker","elixir","elm","erlang","flow","fortran",
    "f#","gherkin","glsl","go","graphql","groovy","haskell","html","java",
    "javascript","json","julia","kotlin","latex","less","lisp","livescript",
    "lua","makefile","markdown","markup","mermaid","nix","objective-c","ocaml",
    "pascal","perl","php","plain text","powershell","prolog","protobuf","python",
    "r","reason","ruby","rust","sass","scala","scheme","scss","shell","sql",
    "swift","toml","typescript","vb.net","verilog","vhdl","visual basic",
    "webassembly","xml","yaml","java/c/c++/c#"
}

def _safe_lang(lang: str) -> str:
    lang = lang.lower().strip()
    return lang if lang in NOTION_SUPPORTED_LANGS else "plain text"


def _parse_table_cells(line: str) -> list:
    """Parse a markdown table row into a list of cell strings."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_table_separator(cells: list) -> bool:
    """Check if row is a markdown table separator (|---|---|)."""
    return all(c.strip("-").strip(":").strip() == "" for c in cells if c.strip())


def _markdown_table_to_notion(table_lines: list) -> dict | None:
    """Convert markdown table lines to a Notion table block with row children."""
    rows = [_parse_table_cells(line) for line in table_lines]
    data_rows = [r for r in rows if not _is_table_separator(r)]
    if not data_rows:
        return None

    table_width = max(len(r) for r in data_rows)

    notion_rows = []
    for row in data_rows:
        padded = row + [""] * (table_width - len(row))
        notion_rows.append({
            "type": "table_row",
            "table_row": {
                "cells": [
                    [{"type": "text", "text": {"content": cell[:NOTION_TEXT_LIMIT]}}]
                    for cell in padded
                ]
            },
        })

    return {
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": True,
            "has_row_header": False,
            "children": notion_rows,
        },
    }


def parse_markdown_to_blocks(content: str) -> list:
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            lang = _safe_lang(line[3:].strip() or "plain text")
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "type": "code",
                "code": {"rich_text": _rich_text("\n".join(code_lines)), "language": lang},
            })
        elif line.strip() in ("---", "***", "___"):
            blocks.append({"type": "divider", "divider": {}})
        elif line.startswith("### "):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": _rich_text(line[4:])}})
        elif line.startswith("## "):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": _rich_text(line[3:])}})
        elif line.startswith("# "):
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": _rich_text(line[2:])}})
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": _rich_text(line[2:])},
            })
        elif len(line) > 2 and line[0].isdigit() and line[1:3] in (". ", ") "):
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": _rich_text(line[3:].strip())},
            })
        elif line.startswith("> "):
            blocks.append({"type": "quote", "quote": {"rich_text": _rich_text(line[2:])}})
        elif line.strip().startswith("|"):
            # Markdown table — collect all consecutive table lines
            table_lines = [line]
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                i += 1
                table_lines.append(lines[i])
            table_block = _markdown_table_to_notion(table_lines)
            if table_block:
                blocks.append(table_block)
        elif line.strip():
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": _rich_text(line)}})

        i += 1

    return blocks[:100]  # Notion limit per append


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _relative_path(file_path: Path) -> str:
    """Return ~/... style path instead of /Users/username/..."""
    try:
        return "~/" + str(file_path.relative_to(Path.home()))
    except ValueError:
        return str(file_path)


def build_properties(title: str, category: str, file_path: Path) -> dict:
    return {
        "Name": {"title": _rich_text(title)},
        "Category": {"select": {"name": category}},
        "FilePath": {"rich_text": _rich_text(_relative_path(file_path))},
        "LastSynced": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
    }


def find_page(notion: Notion, database_id: str, title: str) -> str | None:
    results = notion.query_database(database_id, {
        "filter": {"property": "Name", "title": {"equals": title}}
    })
    return results[0]["id"] if results else None


def sync_file(notion: Notion, database_id: str, file_path: Path, category: str, dry_run: bool):
    content = file_path.read_text(encoding="utf-8")
    title = file_path.stem
    properties = build_properties(title, category, file_path)
    blocks = parse_markdown_to_blocks(content)

    try:
        page_id = find_page(notion, database_id, title)
    except requests.HTTPError as e:
        print(f"  ✗ Failed [{title}]: {e}")
        return

    if dry_run:
        action = "UPDATE" if page_id else "CREATE"
        print(f"  [dry-run] {action}: {title}  ({len(blocks)} blocks)")
        return

    try:
        if page_id:
            # Archive old page (fast: 1 API call) then create fresh (avoids slow block-by-block deletion)
            notion._patch(f"/pages/{page_id}", {"archived": True})
            notion.create_page(database_id, properties, blocks)
            print(f"  ✓ Updated: {title}")
        else:
            notion.create_page(database_id, properties, blocks)
            print(f"  + Created: {title}")
    except requests.HTTPError as e:
        print(f"  ✗ Failed [{title}]: {e}")


def sync_directory(notion: Notion, database_id: str, source_dir: Path, label: str, dry_run: bool):
    if not source_dir.exists():
        print(f"  ⚠️  Not found, skipping: {source_dir}")
        return

    md_files = sorted(source_dir.rglob("*.md"))
    if not md_files:
        print(f"  ⚠️  No .md files in: {source_dir}")
        return

    prefix = "[dry-run] " if dry_run else ""
    print(f"\n{prefix}📂 {label}  ({len(md_files)} files)")

    for md_file in md_files:
        rel = md_file.relative_to(source_dir)
        category = str(rel.parent) if str(rel.parent) != "." else label.lower().replace(" ", "-")
        sync_file(notion, database_id, md_file, category, dry_run)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def sync_file_single(notion: Notion, database_id: str, file_path: Path, dry_run: bool):
    """Sync a single root-level file (not inside a subdirectory)."""
    if not file_path.exists():
        print(f"  ⚠️  Not found, skipping: {file_path}")
        return
    category = file_path.parent.name
    sync_file(notion, database_id, file_path, category, dry_run)


def main():
    parser = argparse.ArgumentParser(description="Sync markdown files to Notion")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        print("   Run: cp config.yaml.example config.yaml")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    notion = Notion(token=config["notion_token"])
    src = config["sources"]
    dbs = config["databases"]
    dry = args.dry_run

    # ── Claude Skills ──────────────────────────────────────────────
    sync_directory(notion, dbs["claude_skills"],
                   Path(src["claude_skills"]).expanduser(), "Claude Skills", dry)

    # ── Knowledge Base ─────────────────────────────────────────────
    kb_db = dbs.get("knowledge_base", "").strip()
    if not kb_db:
        print("\n⚠️  Knowledge Base: no database ID — skipping")
    else:
        kb_count = sum(
            len(list(Path(d).expanduser().rglob("*.md")))
            for d in src.get("knowledge_base_dirs", [])
            if Path(d).expanduser().exists()
        )
        print(f"\n{'[dry-run] ' if dry else ''}📂 Knowledge Base  ({kb_count} files)")

        for d in src.get("knowledge_base_dirs", []):
            p = Path(d).expanduser()
            if p.exists():
                for md_file in sorted(p.rglob("*.md")):
                    rel = md_file.relative_to(p)
                    category = str(rel.parent) if str(rel.parent) != "." else p.name
                    sync_file(notion, kb_db, md_file, category, dry)

    # ── Specs ──────────────────────────────────────────────────────
    def _sync_dirs(db_key: str, dirs_key: str, label: str):
        db_id = dbs.get(db_key, "").strip()
        dirs = src.get(dirs_key, [])
        if not dirs:
            return
        if not db_id:
            print(f"\n⚠️  {label}: no database ID — skipping (add {db_key} to config.yaml)")
            return
        count = sum(
            len(list(Path(d).expanduser().rglob("*.md")))
            for d in dirs if Path(d).expanduser().exists()
        )
        print(f"\n{'[dry-run] ' if dry else ''}📂 {label}  ({count} files)")
        for d in dirs:
            p = Path(d).expanduser()
            if p.exists():
                for md_file in sorted(p.rglob("*.md")):
                    sync_file(notion, db_id, md_file, p.name, dry)

    _sync_dirs("specs", "specs_dirs", "Specs")
    _sync_dirs("context", "context_dirs", "Context")

    # ── Docs ───────────────────────────────────────────────────────
    docs_db = dbs.get("docs", "").strip()
    docs_files = src.get("docs_files", [])
    if docs_files:
        if docs_db:
            print(f"\n{'[dry-run] ' if dry else ''}📂 Docs  ({len(docs_files)} files)")
            for f in docs_files:
                sync_file_single(notion, docs_db, Path(f).expanduser(), dry)
        else:
            print(f"\n⚠️  Docs: no database ID — skipping (add docs to config.yaml)")

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"\n{prefix}✅ Done")


if __name__ == "__main__":
    main()
