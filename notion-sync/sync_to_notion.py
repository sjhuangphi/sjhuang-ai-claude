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

    page_id = find_page(notion, database_id, title)

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

    sync_directory(
        notion,
        database_id=config["databases"]["claude_skills"],
        source_dir=Path(config["sources"]["claude_commands"]).expanduser(),
        label="Claude Skills",
        dry_run=args.dry_run,
    )

    sync_directory(
        notion,
        database_id=config["databases"]["knowledge_base"],
        source_dir=Path(config["sources"]["knowledge_base"]).expanduser(),
        label="Knowledge Base",
        dry_run=args.dry_run,
    )

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"\n{prefix}✅ Done")


if __name__ == "__main__":
    main()
