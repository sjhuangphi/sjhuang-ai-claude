# claude-notion-sync

## 2026-03-06 — 建立 Claude 設定同步與 Notion 知識庫工具

**摘要**：建立 Git Dotfiles 同步方案與 notion-sync 工具，讓 Claude Skills 和知識庫文檔能同步到 Notion，並可在多台電腦還原。

### 完成項目

- 建立 `~/notion-sync/` 同步工具（直接使用 requests 呼叫 Notion REST API）
- 在 Notion 建立 `Claude Knowledge Base` 根頁面，內含兩個 Database
- 成功同步 4 個 Claude Skills 與 1 份知識庫文檔到 Notion
- 建立 `~/notion-sync/SETUP.md` — 新機器完整還原 spec
- 建立 `~/knowledge-base/notion-sync-usage.md` — 工具使用說明
- 建立 `~/.claude/CLAUDE.md` — 全域工作紀錄規範
- 新增 aliases：`notion-sync`、`notion-sync-dry`、`kb`

### 異動說明

| 檔案 | 異動 |
|------|------|
| `~/notion-sync/sync_to_notion.py` | 主程式，使用 requests 避免 notion-client SDK 版本問題 |
| `~/notion-sync/config.yaml` | Notion token + database IDs 設定 |
| `~/notion-sync/SETUP.md` | 新機器還原 checklist |
| `~/knowledge-base/notion-sync-usage.md` | 工具使用說明（已同步到 Notion） |
| `~/.claude/CLAUDE.md` | 新建，定義工作紀錄規範 |
| `~/.zshrc` | 新增 notion-sync、notion-sync-dry、kb alias |

### 使用方式 / 操作說明

```bash
notion-sync        # 同步 ~/.claude/commands/ 和 ~/knowledge-base/ 到 Notion
notion-sync-dry    # 預覽，不寫入
kb                 # 開啟 ~/knowledge-base 資料夾
```

Notion 頁面：https://www.notion.so/Claude-Knowledge-Base-31b1500a4b9d802a94bfffefbb879371

### 注意事項

- `config.yaml` 含有 Notion token，不要 commit 到公開 repo
- ~~Git Dotfiles repo 尚未實際建立~~ → 已完成，見下方紀錄
- `notion-client` SDK v3 移除了 `databases.query`，工具改用 `requests` 直接呼叫 API

## 2026-03-06 — 重構文件目錄結構 + 調整同步來源

**摘要**：將 `~/Desktop/doc/` 統一作為文件根目錄，建立三層子目錄分類，並更新同步來源與 CLAUDE.md 規範。

### 完成項目

- 建立 `logs/`、`specs/`、`context/` 三個子目錄
- 將既有文件移入 `logs/`
- 同步來源改為 `~/Desktop/doc/`（取代 `~/knowledge-base/`）
- Update 策略改為 archive 舊 page + 建新 page（避免逐 block 刪除的效能問題）
- FilePath 欄位改為 `~/...` 格式（不含機器 username）
- 更新 `CLAUDE.md`，加入三種文件類型的規範
- alias `kb` 改為 `doc`

### 異動說明

| 檔案 | 異動 |
|------|------|
| `~/notion-sync/config.yaml` | knowledge_base 來源改為 `~/Desktop/doc` |
| `~/notion-sync/sync_to_notion.py` | FilePath 改 `~/` 格式；update 改 archive+create 策略 |
| `~/.claude/CLAUDE.md` | 加入 specs/context 規範，更新路徑表 |
| `~/.zshrc` | `kb` 改為 `doc`（指向 ~/Desktop/doc） |

### 使用方式 / 操作說明

```bash
notion-sync     # 同步 ~/.claude/commands/ + ~/Desktop/doc/ 到 Notion
doc             # 開啟 ~/Desktop/doc/
```

文件放置規則：
- 工作紀錄 → `logs/<專案>.md`
- 步驟 SOP → `specs/<流程>.md`
- 背景知識 → `context/<主題>.md`

## 2026-03-06 — 建立 Git Dotfiles repo 並推上 GitHub

**摘要**：將 Claude 設定與 notion-sync 工具備份到 GitHub private repo，建立 symlink 架構，新機器可一鍵還原。

### 完成項目

- 建立 `~/dotfiles/` 目錄結構並推上 `sjhuangphi/sjhuang-ai-claude`
- 建立 `setup.sh` — 新機器一鍵建立 symlinks
- 建立 `.gitignore` — 排除含 token 的 `config.yaml`
- 將 `~/.claude/commands/`、`CLAUDE.md`、`settings.json`、`~/notion-sync/` 改為 symlink 指向 dotfiles

### 異動說明

| 項目 | 說明 |
|------|------|
| `~/dotfiles/` | 新建，git repo 實體位置 |
| `~/.claude/commands` | symlink → `~/dotfiles/claude/commands` |
| `~/.claude/CLAUDE.md` | symlink → `~/dotfiles/claude/CLAUDE.md` |
| `~/.claude/settings.json` | symlink → `~/dotfiles/claude/settings.json` |
| `~/notion-sync` | symlink → `~/dotfiles/notion-sync` |

### 使用方式 / 操作說明

```bash
# Skills 或設定有變動後 push
cd ~/dotfiles && git add . && git commit -m "update: ..." && git push
```

新機器還原：參考 `specs/dotfiles-setup.md`
