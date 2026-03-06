# ── Custom Shell Config ────────────────────────────────────────
# Source this file from ~/.zshrc:
#   [ -f ~/dotfiles/zshrc-custom.sh ] && source ~/dotfiles/zshrc-custom.sh

# ── PATH ──────────────────────────────────────────────────────
export PATH="$HOME/.local/bin:$PATH"

# ── Functions ─────────────────────────────────────────────────

# Kill process by port
killport() {
  if [ -z "$1" ]; then
    echo "Usage: killport <port>"
    return 1
  fi
  local pids=($(lsof -t -i:"$1"))
  if [ ${#pids[@]} -eq 0 ]; then
    echo "No process found on port $1"
    return 1
  fi
  kill -9 "${pids[@]}" && echo "Killed ${#pids[@]} process(es) on port $1"
}

# Notion sync + dotfiles commit + doc commit + push
sync-all() {
  cp ~/dotfiles/CHANGELOG.md ~/Desktop/doc/CHANGELOG.md

  echo "🔄 Syncing to Notion..."
  python3 ~/notion-sync/sync_to_notion.py || { echo "❌ Notion sync failed"; return 1; }

  echo ""
  echo "📦 Committing dotfiles..."
  cd ~/dotfiles && git add . && \
  git diff --cached --quiet && echo "  (nothing to commit)" || \
  git commit -m "${1:-sync: update skills and docs}" && git push

  echo ""
  echo "📄 Committing doc..."
  cd ~/Desktop/doc && git add -A && \
  git diff --cached --quiet && echo "  (nothing to commit)" || \
  git commit -m "${1:-sync: update docs}" && git push

  echo ""
  echo "✅ All done"
}

# Pull latest doc from remote
doc-pull() {
  cd ~/Desktop/doc && git pull
}

# Commit and push doc (includes additions, modifications, and deletions)
doc-push() {
  cd ~/Desktop/doc && git add -A && \
  git diff --cached --quiet && echo "(nothing to commit)" || \
  git commit -m "${1:-update docs}" && git push
}

# ── Aliases ───────────────────────────────────────────────────
alias notion-sync="python3 ~/notion-sync/sync_to_notion.py"
alias notion-sync-dry="python3 ~/notion-sync/sync_to_notion.py --dry-run"
alias doc="open ~/Desktop/doc"
