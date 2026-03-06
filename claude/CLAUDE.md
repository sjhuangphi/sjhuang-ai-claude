# Claude 全域設定

## 文件目錄結構

```
~/Desktop/doc/
├── logs/              # 工作紀錄（每個專案一份，追加更新）
├── specs/             # 步驟流程 SOP（Claude 照著執行）
├── context/           # 專案背景知識（Claude 理解專案用）
└── alias-cheatsheet.md
```

---

## 工作紀錄規範（logs/）

每次協作任務結束後，在 `~/Desktop/doc/logs/` 維護工作紀錄，命名格式：

```
<專案名稱>.md
```

同一個專案永遠使用同一份文件，不加日期前綴，避免文件爆炸。

### 文檔內容結構

```markdown
# <專案名稱>
## YYYY-MM-DD — <本次任務簡述>
**摘要**：本次任務的一句話說明
### 完成項目
- 列出本次實際執行並完成的事項
### 異動說明
- 說明修改了哪些檔案、設定或系統配置，以及為什麼
### 使用方式 / 操作說明
- 若有新功能或新工具，說明如何使用
### 注意事項
- 列出未完成、需手動處理或後續要注意的事項（若無則省略）
```

每次新增變更時，在文件末尾**追加一個新的 `## YYYY-MM-DD` 區塊**，不覆蓋舊內容。

### 規則

- 文檔語言跟隨任務語言（中文任務 → 中文文檔）
- 文檔盡量簡潔，重點清楚，不需要逐行描述每個指令
- **每次變更都要補文件**：不論新功能、Bug 修正、設定調整，任務結束後必定產生或更新紀錄
- **每次新增或修改 alias**：必須同步更新 `~/Desktop/doc/alias-cheatsheet.md`

---

## Specs 規範（specs/）

放置 Claude 照著執行的步驟流程 SOP。

- 命名：`<流程名稱>.md`（例如 `deploy-flow.md`、`pr-review.md`）
- 結構：有序步驟、前置條件、注意事項
- Claude 執行任務前若有對應 spec，需先讀取再行動

---

## Context 規範（context/）

放置專案背景知識，讓 Claude 理解專案結構與規則。

- 命名：`<專案或主題>.md`（例如 `wps-architecture.md`）
- 內容：架構說明、技術選型、商業規則、領域知識
- 由 Claude 整理初稿後交由使用者確認

---

## 工具與 Alias

| Alias | 說明 |
|-------|------|
| `notion-sync` | 同步 Claude Skills + Desktop/doc 到 Notion |
| `notion-sync-dry` | 預覽同步（不寫入） |
| `doc` | 開啟 ~/Desktop/doc 資料夾 |

## 重要路徑

| 路徑 | 用途 |
|------|------|
| `~/.claude/commands/` | Claude Skills（slash commands） |
| `~/Desktop/doc/logs/` | 工作紀錄（同步到 Notion） |
| `~/Desktop/doc/specs/` | SOP 流程文件（同步到 Notion） |
| `~/Desktop/doc/context/` | 專案背景知識（同步到 Notion） |
| `~/Desktop/doc/alias-cheatsheet.md` | 所有 alias 速查表 |
| `~/notion-sync/` | Notion 同步工具 |
| `~/notion-sync/SETUP.md` | 新機器設定 Spec |
