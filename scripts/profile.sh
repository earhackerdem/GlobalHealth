#!/usr/bin/env bash
# LOCAL profile of the person working with the agent: NAME, ROLE and PROFILE (supervised|autonomous), in
# .claude/profile.env (ignored by git). Read by the SessionStart hook profile.py.
# No email on purpose: the agent doesn't need it; a versioned roster would expose the team's.
# Anchored to the MAIN worktree: the file doesn't travel through git, so a new worktree wouldn't have it.
#   scripts/profile.sh                     interactive
#   scripts/profile.sh check               ✓ / ⚠, never fails (used by make doctor)
#   NAME=… ROLE=… PROFILE=… scripts/profile.sh   non-interactive
set -euo pipefail
if GIT_COMMON=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null); then
  REPO_ROOT=$(dirname "$GIT_COMMON")
else
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
FILE="$REPO_ROOT/.claude/profile.env"

if [ "${1:-}" = "check" ]; then
  if [ -f "$FILE" ] && grep -q '^NAME=.' "$FILE" && grep -q '^ROLE=.' "$FILE"; then
    echo "✓ profile: $(grep '^NAME=' "$FILE" | cut -d= -f2-) ($(grep '^ROLE=' "$FILE" | cut -d= -f2-)) · PROFILE=$(grep '^PROFILE=' "$FILE" | cut -d= -f2- || echo supervised)"
  else
    echo "⚠ No local profile: run 'make profile'. Hooks assume PROFILE=supervised."
  fi
  exit 0
fi

NAME="${NAME:-}"; ROLE="${ROLE:-}"; PROFILE="${PROFILE:-}"
[ -n "$NAME" ] || read -r -p "Your name (as the record should call you): " NAME
[ -n "$ROLE" ] || read -r -p "Your role in the project (author, developer, reviewer, mentor…): " ROLE
[ -n "$PROFILE" ] || read -r -p "Profile [supervised/autonomous] (supervised = guardrails block; autonomous = they warn): " PROFILE
PROFILE="$(echo "${PROFILE:-supervised}" | tr '[:upper:]' '[:lower:]')"
case "$PROFILE" in supervised|autonomous) ;; *) echo "✗ PROFILE must be supervised or autonomous" >&2; exit 1;; esac
if [ -z "$NAME" ] || [ -z "$ROLE" ]; then echo "✗ Name and role are both required." >&2; exit 1; fi
mkdir -p "$(dirname "$FILE")"
printf 'NAME=%s\nROLE=%s\nPROFILE=%s\n' "$NAME" "$ROLE" "$PROFILE" >"$FILE"
echo "✓ Profile saved to $FILE (ignored by git). It applies when the next session opens."
