#!/usr/bin/env bash
# make skills-link — ensures .claude/skills/<n> -> ../../.agents/skills/<n> for EVERY skill in .agents/skills/
# (folder with SKILL.md). Claude Code only discovers .claude/skills/; Cursor, VS Code (Copilot) and Antigravity
# read .agents/skills/ directly. Idempotent; never overwrites real folders.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/.claude/skills"; cd "$ROOT/.claude/skills"
n=0; broken=0
for d in "$ROOT"/.agents/skills/*/; do
  s="$(basename "$d")"; [ -f "$d/SKILL.md" ] || continue
  if [ -e "$s" ] && [ ! -L "$s" ]; then echo "WARNING: .claude/skills/$s is a real folder, not a symlink; move it to .agents/skills/"; continue; fi
  ln -sfn "../../.agents/skills/$s" "$s"; n=$((n+1))
done
for l in *; do
  [ -L "$l" ] && [ ! -f "$l/SKILL.md" ] && { echo "broken symlink removed: .claude/skills/$l"; rm "$l"; broken=$((broken+1)); }
done
echo "skills linked in .claude/skills/: $n (broken symlinks removed: $broken)"
