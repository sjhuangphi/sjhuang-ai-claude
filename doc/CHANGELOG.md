# Dotfiles & Claude 工具 Changelog

每次異動都在此追加一個 `## YYYY-MM-DD` 區塊，說明變更內容與使用方式。

---

## 2026-03-06 — 初始化整套 Claude + Notion 同步架構

### 變更內容

**notion-sync 工具（`~/notion-sync/` → symlink `~/dotfiles/notion-sync/`）**
- 建立 `sync_to_notion.py`：使用 requests 直接呼叫 Notion REST API
- 同步來源：`~/.claude/commands/`（Claude Skills）+ `~/Desktop/doc/`（知識庫）
- Update 策略：archive 舊 page + 建新 page（避免逐 block 刪除慢速問題）
- FilePath 欄位改為 `~/...` 格式，不含機器 username
- 修正：code block 語言白名單驗證；文字超過 1990 字自動截斷

**Claude 設定（`~/.claude/` → symlink `~/dotfiles/claude/`）**
- `CLAUDE.md`：定義工作紀錄規範、文件目錄結構、Alias 說明
- `commands/`：Skills — git-release, java-codegen, pr, references/conventions
- `settings.json`：Claude Code 全域設定

**文件目錄結構（`~/Desktop/doc/`）**
```
~/Desktop/doc/
├── logs/          # 工作紀錄（每專案一份，追加更新）
├── specs/         # 步驟 SOP（Claude 照著執行）
├── skills-spec/   # Claude skill 參考文件（整合說明、API 端點）
├── context/       # 專案背景知識
└── alias-cheatsheet.md
```

**Notion 資料庫（`Claude Knowledge Base`）**
- Claude Skills DB ID：`31b1500a-4b9d-81d9-aa4d-fc6b5106238f`
- Knowledge Base DB ID：`31b1500a-4b9d-816d-ae5b-cdc791e6601e`

**Aliases（`~/.zshrc`）**
| Alias | 說明 |
|-------|------|
| `sync-all` | Notion 同步 + dotfiles commit + push 一次完成 |
| `sync-all "msg"` | 同上，帶自訂 commit message |
| `notion-sync` | 僅同步到 Notion |
| `notion-sync-dry` | 預覽同步，不寫入 |
| `doc` | 開啟 ~/Desktop/doc/ |

### 使用方式

```bash
# 日常同步（文件有更新時）
sync-all
sync-all "update: 新增 xxx skill"

# 僅同步 Notion
notion-sync

# 預覽
notion-sync-dry

# 開啟文件目錄
doc
```

### Symlink 架構

```
~/.claude/CLAUDE.md      → ~/dotfiles/claude/CLAUDE.md
~/.claude/settings.json  → ~/dotfiles/claude/settings.json
~/.claude/commands/      → ~/dotfiles/claude/commands/
~/notion-sync/           → ~/dotfiles/notion-sync/
```

### 新機器還原

```bash
git clone git@github.com:sjhuangphi/sjhuang-ai-claude.git ~/dotfiles
bash ~/dotfiles/setup.sh
cp ~/notion-sync/config.yaml.example ~/notion-sync/config.yaml
# 填入 notion_token，然後：
sync-all
```

---

## 2026-03-06 — 新增 skills-spec 文件分類

### 變更內容

- 新增 `~/Desktop/doc/skills-spec/` 資料夾，放置 Claude skill 整合參考文件
- 更新 `CLAUDE.md`，說明 `skills-spec/` 用途與命名規則
- 更新 `CHANGELOG.md`（本檔案）加入此分類說明

### skills-spec 已有文件

| 檔案 | 說明 |
|------|------|
| `skills-sms-otp-expert.md` | OTP Expert SMS Provider（Provider ID 190）整合文件 |
| `skills-sms-tsms.md` | TSMS SMS Provider（Provider ID 191）整合文件，HMAC-SHA256 簽名 |

### skills-spec 使用方式

Claude 執行 SMS provider 對接任務時，先讀取對應的 skills-spec 文件：
- 包含 Provider 概要、API 端點、BO 參數、簽名規則、快速 debug 指令
- 命名規則：`skills-<類別>-<provider>.md`

