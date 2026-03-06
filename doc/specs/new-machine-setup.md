# 新機器環境還原 SOP

本文件供 Claude 在新電腦上自動執行，完整還原開發環境。

---

## 前置條件

- macOS（Apple Silicon 或 Intel）
- 已安裝 Homebrew（`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- 已有 GitHub SSH 金鑰（`~/.ssh/sjhuang.phi` + `~/.ssh/sjhuang.phi.pub`）
- 已有 TCG 內網金鑰（`~/.ssh/id_rsa`、`~/.ssh/dev.root.tc168`，如需要）

---

## 步驟 1：安裝基礎工具

```bash
# oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Homebrew 套件（從 Brewfile）
brew bundle --file=~/dotfiles/Brewfile
```

---

## 步驟 2：SSH 金鑰設定

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# 確認以下金鑰已複製到 ~/.ssh/
#   - sjhuang.phi（GitHub 私鑰）
#   - sjhuang.phi.pub（GitHub 公鑰）
#   - id_rsa（TCG 內網，如需要）
#   - dev.root.tc168（TCG 開發機，如需要）

chmod 600 ~/.ssh/sjhuang.phi ~/.ssh/id_rsa ~/.ssh/dev.root.tc168 2>/dev/null
chmod 644 ~/.ssh/sjhuang.phi.pub 2>/dev/null

# SSH config（從 dotfiles 複製）
cp ~/dotfiles/ssh/config ~/.ssh/config

# 測試 GitHub 連線
ssh -T git@github.com
```

---

## 步驟 3：Git 設定

```bash
cp ~/dotfiles/gitconfig ~/.gitconfig
```

驗證：
```bash
git config user.name   # → chris.h.tcg
git config user.email  # → sjhuang.phi@gmail.com
```

---

## 步驟 4：Clone dotfiles 並執行 setup

```bash
git clone git@github.com:sjhuangphi/sjhuang-ai-claude.git ~/dotfiles
cd ~/dotfiles && bash setup.sh
```

`setup.sh` 會自動：
- 建立 `~/.claude/` symlinks（CLAUDE.md, settings.json, commands/）
- 建立 `~/notion-sync` symlink
- 將 `zshrc-custom.sh` source 加入 `~/.zshrc`
- 建立 `~/Desktop/doc/` 目錄結構（logs, specs, context, skills-spec）
- 安裝 Python 依賴（requests, PyYAML）
- 從 template 建立 `config.yaml`

---

## 步驟 5：Notion Sync 設定

```bash
# 編輯 config.yaml，填入 Notion token
# Token 取得方式：https://www.notion.so/my-integrations → "Claude Sync"
vim ~/notion-sync/config.yaml
```

填入 `notion_token` 後，DB ID 可以留空。sync 會自動：
1. 搜尋 workspace 中同名的 DB
2. 找到 → 使用該 ID
3. 找不到 → 自動新建

```bash
# 驗證
notion-sync-dry

# 正式同步
notion-sync
```

---

## 步驟 6：驗證

```bash
# 確認 aliases 生效
source ~/.zshrc
which notion-sync   # → alias
which sync-all      # → function

# 確認 Claude commands 正確連結
ls -la ~/.claude/commands/

# 完整同步測試
sync-all "init: new machine setup"
```

---

## 目錄結構總覽

```
~/
├── dotfiles/                  # Git repo（版控中心）
│   ├── setup.sh               # 一鍵安裝腳本
│   ├── Brewfile               # Homebrew 套件清單
│   ├── zshrc-custom.sh        # Shell aliases + functions
│   ├── gitconfig              # Git 設定
│   ├── ssh/config             # SSH 設定（不含私鑰）
│   ├── CHANGELOG.md           # 主變更紀錄
│   ├── claude/                # Claude Code 設定
│   │   ├── CLAUDE.md          # 全域指令
│   │   ├── settings.json      # Claude 設定
│   │   └── commands/          # Claude Skills（slash commands）
│   └── notion-sync/           # Notion 同步工具
│       ├── sync_to_notion.py  # 主程式
│       ├── config.yaml.example# 設定模板
│       └── requirements.txt   # Python 依賴
├── .claude/                   # Claude Code（symlinks → dotfiles）
├── .ssh/                      # SSH 金鑰（手動複製）
├── .gitconfig                 # Git 設定（手動複製）
├── notion-sync/               # symlink → dotfiles/notion-sync
└── Desktop/doc/               # 工作文件（同步到 Notion）
    ├── logs/                  # 工作紀錄
    ├── specs/                 # SOP 流程
    ├── context/               # 專案背景
    ├── skills-spec/           # Skill 整合參考
    ├── alias-cheatsheet.md    # Alias 速查表
    └── CHANGELOG.md           # 從 dotfiles 複製
```

---

## 機密資料清單（不進版控）

| 檔案 | 說明 | 來源 |
|------|------|------|
| `~/.ssh/sjhuang.phi` | GitHub SSH 私鑰 | 手動複製 |
| `~/.ssh/id_rsa` | TCG 內網私鑰 | 手動複製 |
| `~/.ssh/dev.root.tc168` | TCG 開發機私鑰 | 手動複製 |
| `~/notion-sync/config.yaml` | Notion token + DB IDs | 手動填入 token，DB ID 自動產生 |

---

## Homebrew 套件（Brewfile 內容）

| 套件 | 用途 |
|------|------|
| git | 版本控制 |
| gh | GitHub CLI |
| nvm | Node.js 版本管理 |
| yarn | Node.js 套件管理 |
| go | Go 語言 |
| ffmpeg | 影音處理 |
| imagemagick | 圖片處理 |
| pandoc | 文件轉換 |
| mysql-client | MySQL 客戶端 |
| nginx | Web server |
| cloudflared | Cloudflare tunnel |
| iterm2 | 終端機（cask） |
| warp | 終端機（cask） |

---

## 故障排除

### SSH 連線失敗
```bash
ssh -vT git@github.com   # 查看詳細連線資訊
ssh-add ~/.ssh/sjhuang.phi
```

### Notion sync 404
DB 被刪除時，sync 會自動搜尋或重建。確認：
1. `config.yaml` 有 `parent_page_id`
2. Notion integration 有連接到 parent page

### zshrc-custom.sh 沒生效
```bash
grep "zshrc-custom" ~/.zshrc   # 確認有 source 行
source ~/.zshrc
```
