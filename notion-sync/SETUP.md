# Claude + Notion Sync — 新機器設定 Spec

## 概述

本文件描述如何在新電腦上還原完整的 Claude 設定與 Notion 同步工具。

---

## 一、前置需求

```bash
# 確認已安裝
python3 --version   # >= 3.10
pip3 --version
git --version
```

---

## 二、Git Dotfiles（Claude Skills 同步）

### 首次設定（主機）

```bash
# 1. 建立 dotfiles repo
mkdir -p ~/dotfiles/claude
git init ~/dotfiles
cd ~/dotfiles
git remote add origin git@github.com:<YOUR_USERNAME>/dotfiles.git

# 2. 將 Claude commands 移入 dotfiles
cp -r ~/.claude/commands ~/dotfiles/claude/
cp ~/.claude/settings.json ~/dotfiles/claude/settings.json

# 3. 建立 symlink
rm -rf ~/.claude/commands
ln -sf ~/dotfiles/claude/commands ~/.claude/commands
ln -sf ~/dotfiles/claude/settings.json ~/.claude/settings.json

# 4. 推上 GitHub
cd ~/dotfiles && git add . && git commit -m "init: claude dotfiles" && git push -u origin main
```

### 新機器還原

```bash
# 1. Clone dotfiles
git clone git@github.com:<YOUR_USERNAME>/dotfiles.git ~/dotfiles

# 2. 建立 symlinks
mkdir -p ~/.claude
ln -sf ~/dotfiles/claude/commands ~/.claude/commands
ln -sf ~/dotfiles/claude/settings.json ~/.claude/settings.json

# 3. 之後更新只需
cd ~/dotfiles && git pull
```

---

## 三、Notion Sync 工具設定

### 複製工具到新機器

```bash
# 方法 A：如果 notion-sync 也在 dotfiles 裡
ln -sf ~/dotfiles/notion-sync ~/notion-sync

# 方法 B：直接複製目錄
cp -r ~/notion-sync ~/notion-sync
```

### 安裝依賴

```bash
pip3 install requests PyYAML
```

> 注意：不需要 notion-client SDK，工具直接使用 requests 呼叫 REST API

### 設定 config.yaml

```bash
cd ~/notion-sync
cp config.yaml.example config.yaml
```

編輯 `config.yaml`，填入：

```yaml
notion_token: "ntn_xxxxxxxxxxxx"   # 從 notion.so/my-integrations 取得

databases:
  claude_skills: "31b1500a-4b9d-81bd-931e-d348fd2a31ed"
  knowledge_base: "31b1500a-4b9d-8127-815b-de53703e328e"

sources:
  claude_commands: "~/.claude/commands"
  knowledge_base: "~/knowledge-base"
```

> Notion Database IDs 是固定的，直接填上面的值即可（已建立完成）

### Notion Integration 設定

1. 前往 https://www.notion.so/my-integrations
2. 找到 `Claude Sync` integration
3. 複製 token（`ntn_` 開頭）
4. 貼到 `config.yaml` 的 `notion_token`
5. 確認 Notion 的 `Claude Knowledge Base` page 已連接此 integration

---

## 四、Shell Aliases

在 `~/.zshrc` 加入：

```bash
# Notion Sync
alias notion-sync="python3 ~/notion-sync/sync_to_notion.py"
alias notion-sync-dry="python3 ~/notion-sync/sync_to_notion.py --dry-run"
```

```bash
source ~/.zshrc
```

---

## 五、Knowledge Base 目錄

```bash
mkdir -p ~/knowledge-base
```

所有放入此目錄的 `.md` 檔案都會在執行 `notion-sync` 時同步到 Notion。

---

## 六、Notion 頁面位置

| 項目 | URL |
|------|-----|
| 根頁面 | https://www.notion.so/Claude-Knowledge-Base-31b1500a4b9d802a94bfffefbb879371 |
| Claude Skills DB | database id: `31b1500a-4b9d-81bd-931e-d348fd2a31ed` |
| Knowledge Base DB | database id: `31b1500a-4b9d-8127-815b-de53703e328e` |

---

## 七、完整還原 Checklist

```
[ ] git clone dotfiles repo
[ ] 建立 ~/.claude/commands symlink
[ ] 建立 ~/.claude/settings.json symlink
[ ] 複製或 clone notion-sync 工具
[ ] pip3 install requests PyYAML
[ ] 設定 config.yaml（填入 notion_token）
[ ] 加入 aliases 到 ~/.zshrc
[ ] mkdir ~/knowledge-base
[ ] 執行 notion-sync-dry 驗證
[ ] 執行 notion-sync 正式同步
```
