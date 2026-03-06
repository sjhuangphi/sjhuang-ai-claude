#!/bin/bash
# setup.sh - 新機器還原完整開發環境
set -e

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "🔧 Setting up dotfiles..."

# ── 1. Claude symlinks ────────────────────────────────────────
mkdir -p "$CLAUDE_DIR"

for item in CLAUDE.md settings.json commands; do
  target="$CLAUDE_DIR/$item"
  source="$DOTFILES/claude/$item"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "  Backing up existing $target → $target.bak"
    mv "$target" "$target.bak"
  fi
  ln -sf "$source" "$target"
  echo "  ✓ $target → $source"
done

# ── 2. notion-sync symlink ────────────────────────────────────
if [ -e "$HOME/notion-sync" ] && [ ! -L "$HOME/notion-sync" ]; then
  mv "$HOME/notion-sync" "$HOME/notion-sync.bak"
fi
ln -sf "$DOTFILES/notion-sync" "$HOME/notion-sync"
echo "  ✓ ~/notion-sync → $DOTFILES/notion-sync"

# ── 3. Shell config ──────────────────────────────────────────
ZSHRC="$HOME/.zshrc"
SOURCE_LINE='[ -f ~/dotfiles/zshrc-custom.sh ] && source ~/dotfiles/zshrc-custom.sh'
if ! grep -qF "zshrc-custom.sh" "$ZSHRC" 2>/dev/null; then
  echo "" >> "$ZSHRC"
  echo "# Dotfiles custom config" >> "$ZSHRC"
  echo "$SOURCE_LINE" >> "$ZSHRC"
  echo "  ✓ Added zshrc-custom.sh source to ~/.zshrc"
else
  echo "  ✓ zshrc-custom.sh already sourced in ~/.zshrc"
fi

# ── 4. Clone doc repo ─────────────────────────────────────────
if [ ! -d "$HOME/Desktop/doc/.git" ]; then
  echo "  Cloning doc repo..."
  git clone git@github.com:sjhuangphi/claude-doc.git "$HOME/Desktop/doc" 2>/dev/null \
    && echo "  ✓ ~/Desktop/doc cloned from GitHub" \
    || echo "  ⚠️  Failed to clone doc repo — run: git clone git@github.com:sjhuangphi/claude-doc.git ~/Desktop/doc"
else
  echo "  ✓ ~/Desktop/doc already exists"
fi

# ── 5. Python 依賴 ───────────────────────────────────────────
if command -v pip3 &>/dev/null; then
  pip3 install -q requests PyYAML
  echo "  ✓ Python dependencies installed"
else
  echo "  ⚠️  pip3 not found — install Python first, then run: pip3 install requests PyYAML"
fi

# ── 6. Notion config ─────────────────────────────────────────
if [ ! -f "$HOME/notion-sync/config.yaml" ]; then
  cp "$DOTFILES/notion-sync/config.yaml.example" "$HOME/notion-sync/config.yaml"
  echo "  ✓ Created ~/notion-sync/config.yaml from template"
fi

echo ""
echo "✅ Done! Remaining manual steps:"
echo "  1. 填入 ~/notion-sync/config.yaml 的 notion_token"
echo "  2. 複製 SSH 金鑰到 ~/.ssh/"
echo "  3. 複製 .gitconfig 到 ~/.gitconfig"
echo "  4. source ~/.zshrc"
echo "  5. notion-sync-dry  # 驗證"
