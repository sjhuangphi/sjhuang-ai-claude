# Alias Cheatsheet

## Notion Sync

| Alias | 指令 | 說明 |
|-------|------|------|
| `sync-all` | — | 一鍵：Notion 同步 + dotfiles commit + push |
| `sync-all "訊息"` | — | 同上，帶自訂 commit message |
| `notion-sync` | `python3 ~/notion-sync/sync_to_notion.py` | 僅同步到 Notion |
| `notion-sync-dry` | `python3 ~/notion-sync/sync_to_notion.py --dry-run` | 預覽同步，不寫入 |
| `doc` | `open ~/Desktop/doc` | 開啟工作紀錄目錄 |

## DRAM Tracker

| Alias | 說明 |
|-------|------|
| `start_dram` | 啟動 DRAM Tracker（port 3001 + 5173） |
| `close_dram` | 停止 DRAM Tracker |

## 系統工具

| Alias / Function | 說明 |
|------------------|------|
| `killport <port>` | 殺掉佔用指定 port 的 process |
