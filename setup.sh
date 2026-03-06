#!/bin/bash
# setup.sh - 新機器還原 Claude 設定
set -e

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "🔧 Setting up Claude dotfiles..."

mkdir -p "$CLAUDE_DIR"

# Symlinks for Claude settings
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

# Symlink notion-sync tool
if [ -e "$HOME/notion-sync" ] && [ ! -L "$HOME/notion-sync" ]; then
  mv "$HOME/notion-sync" "$HOME/notion-sync.bak"
fi
ln -sf "$DOTFILES/notion-sync" "$HOME/notion-sync"
echo "  ✓ ~/notion-sync → $DOTFILES/notion-sync"

echo ""
echo "✅ Done! Next steps:"
echo "  1. cp ~/notion-sync/config.yaml.example ~/notion-sync/config.yaml"
echo "  2. 填入 notion_token"
echo "  3. notion-sync"
