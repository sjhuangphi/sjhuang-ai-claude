# Dotfiles & Notion Sync — 新機器設定 Spec

## 前置需求

- macOS + zsh
- git + SSH key 已設定（能 clone GitHub private repo）
- Python 3.10+

---

## Step 1 — Clone dotfiles repo

```bash
git clone git@github.com:sjhuangphi/sjhuang-ai-claude.git ~/dotfiles
```

---

## Step 2 — 執行 setup.sh（建立 symlinks）

```bash
bash ~/dotfiles/setup.sh
```

建立的 symlinks：

| symlink | 指向 |
|---------|------|
| `~/.claude/CLAUDE.md` | `~/dotfiles/claude/CLAUDE.md` |
| `~/.claude/settings.json` | `~/dotfiles/claude/settings.json` |
| `~/.claude/commands/` | `~/dotfiles/claude/commands/` |
| `~/notion-sync/` | `~/dotfiles/notion-sync/` |

---

## Step 3 — 設定 Notion token

```bash
cp ~/notion-sync/config.yaml.example ~/notion-sync/config.yaml
```

編輯 `~/notion-sync/config.yaml`，填入：

```yaml
notion_token: "ntn_xxxxxxxxxxxx"   # 從 notion.so/my-integrations 取得

databases:
  claude_skills: "31b1500a-4b9d-81d9-aa4d-fc6b5106238f"
  knowledge_base: "31b1500a-4b9d-816d-ae5b-cdc791e6601e"

sources:
  claude_commands: "~/.claude/commands"
  knowledge_base: "~/Desktop/doc"
```

> Database IDs 固定不變，直接用上面的值

---

## Step 4 — 安裝 Python 依賴

```bash
pip3 install requests PyYAML
```

---

## Step 5 — 加入 aliases

在 `~/.zshrc` 加入：

```bash
# Notion Sync
alias notion-sync="python3 ~/notion-sync/sync_to_notion.py"
alias notion-sync-dry="python3 ~/notion-sync/sync_to_notion.py --dry-run"
alias doc="open ~/Desktop/doc"
```

```bash
source ~/.zshrc
```

---

## Step 6 — 建立文件目錄

```bash
mkdir -p ~/Desktop/doc/logs ~/Desktop/doc/specs ~/Desktop/doc/context
```

---

## Step 7 — 驗證

```bash
notion-sync-dry   # 預覽同步清單
notion-sync       # 正式同步
```

---

## Notion 相關資訊

| 項目 | 值 |
|------|-----|
| Integration | notion.so/my-integrations → Claude Sync |
| 根頁面 | Claude Knowledge Base |
| Claude Skills DB | `31b1500a-4b9d-81d9-aa4d-fc6b5106238f` |
| Knowledge Base DB | `31b1500a-4b9d-816d-ae5b-cdc791e6601e` |

---

## 日常維護

```bash
# Skills 或 CLAUDE.md 有變動時 push
cd ~/dotfiles && git add . && git commit -m "update: ..." && git push

# 文件有變動時同步到 Notion
notion-sync
```
