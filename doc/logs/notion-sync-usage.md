# Notion Sync 使用說明

## 工具位置

```
~/notion-sync/
├── sync_to_notion.py      # 主程式
├── config.yaml            # 設定（含 token，勿上傳 git）
├── config.yaml.example    # 設定範本
├── SETUP.md               # 新機器設定 spec
└── requirements.txt
```

---

## 常用指令

```bash
# 預覽模式（不實際寫入 Notion）
notion-sync-dry

# 正式同步
notion-sync
```

---

## 同步來源

| 本機路徑 | 同步目標 |
|---------|---------|
| `~/.claude/commands/*.md` | Notion → Claude Skills |
| `~/knowledge-base/*.md` | Notion → Knowledge Base |

---

## 新增 Claude Skill

1. 在 `~/.claude/commands/` 新增 `my-skill.md`
2. 執行 `notion-sync`
3. Notion 的 Claude Skills 會自動新增一筆

## 新增知識庫文檔

1. 在 `~/knowledge-base/` 新增 `my-doc.md`
2. 執行 `notion-sync`
3. Notion 的 Knowledge Base 會自動新增一筆

---

## 同步規則

- 標題（檔名）相同 → **更新**現有 Notion 頁面
- 標題不存在 → **新增**頁面
- 本機刪除檔案 → Notion 不會自動刪除（手動處理）
- `LastSynced` 欄位會自動更新為最後同步時間

---

## Notion 頁面

- 根頁面：Claude Knowledge Base
- Claude Skills Database ID：`31b1500a-4b9d-81bd-931e-d348fd2a31ed`
- Knowledge Base Database ID：`31b1500a-4b9d-8127-815b-de53703e328e`

---

## 注意事項

- `config.yaml` 含有 Notion token，**不要** commit 到公開 git repo
- token 可到 https://www.notion.so/my-integrations 重新生成
- 每次 `notion-sync` 會清空並重寫 Notion 頁面內容
