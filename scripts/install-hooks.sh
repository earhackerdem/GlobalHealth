#!/usr/bin/env bash
# make install-hooks — installs the local pre-push gate: prek over the diff vs the base branch.
# Lesson from origin (GlobalHealth 2026-10): three CI pre-commit failures were pushes without a local prek pass.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
HOOK="$ROOT/.git/hooks/pre-push"
BASE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
BASE="${BASE:-main}"
cat > "$HOOK" <<EOF
#!/usr/bin/env bash
# Installed by 'make install-hooks'. Runs prek over the diff vs the base branch. Bypass: git push --no-verify
set -euo pipefail
base="origin/$BASE"
git rev-parse --verify -q "\$base" >/dev/null 2>&1 || base="$BASE"
files=\$(git diff --name-only "\$base"...HEAD | tr '\n' ' ')
[ -z "\${files// /}" ] && exit 0
uvx prek run --files \$files
EOF
chmod +x "$HOOK"
echo "✓ pre-push gate installed at .git/hooks/pre-push (prek over the diff vs $BASE; bypass with --no-verify)"
echo "  After a red gate: hooks auto-fix the working tree — run 'git status' and commit the fixes BEFORE retrying."
