#!/usr/bin/env bash
# make adopt DEST=<existing repo> [FLAVOR=development|content] [NAME=…] [AUTHOR=…] [EMAIL=…] [OWNER=…]
# Brings the harness INTO an existing project (brownfield) without touching its code:
#   - copies the agentic layer (.agents/, .claude/, .cursor/, .github/hooks + copilot-instructions, scripts/)
#   - harness docs go to docs/harness/ (your docs/ is left alone)
#   - AGENTS.md / CLAUDE.md: created if missing; if they exist, a short block between <!-- harness:rules --> markers is
#     APPENDED pointing to docs/harness/AGENTS.md (your rules stay first)
#   - Makefile: created if missing; if it exists, the recipes land in harness.mk and you add `include harness.mk`
#   - harness.json with code=[] (fill it with /codebase-context), memory/ seeded, changes/ created
#   - never overwrites an existing file; never runs git commands other than reading the config
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:?missing DEST (path to the existing repo)}"; FLAVOR="${2:-development}"; NAME="${3:-}"; AUTHOR="${4:-}"; EMAIL="${5:-}"; OWNER="${6:-}"
[ -d "$DEST" ] || { echo "✗ $DEST is not a directory" >&2; exit 1; }
DEST="$(cd "$DEST" && pwd)"
[ "$DEST" != "$ROOT" ] || { echo "✗ DEST is the harness itself" >&2; exit 1; }
case "$FLAVOR" in development|content) ;; *) echo "FLAVOR must be development or content" >&2; exit 1;; esac
NAME="${NAME:-$(basename "$DEST")}"
AUTHOR="${AUTHOR:-$(git -C "$DEST" config user.name 2>/dev/null || echo "")}"
EMAIL="${EMAIL:-$(git -C "$DEST" config user.email 2>/dev/null || echo "")}"
OWNER="${OWNER:-$NAME}"
T="$ROOT/.agents/skills/epe-0-new/templates/common"; TODAY="$(date +%F)"
created=(); skipped=()
put() { # put <src> <dest-relative>
  if [ -e "$DEST/$2" ]; then skipped+=("$2"); else mkdir -p "$(dirname "$DEST/$2")"; cp -R "$1" "$DEST/$2"; created+=("$2"); fi
}

# 1. Agentic layer (directories copied only if absent; files inside existing dirs are added, never replaced)
for d in .agents .cursor scripts; do
  if [ -d "$DEST/$d" ]; then
    (cd "$ROOT/$d" && find . -type f) | while read -r f; do f="${f#./}"; [ -e "$DEST/$d/$f" ] || { mkdir -p "$(dirname "$DEST/$d/$f")"; cp "$ROOT/$d/$f" "$DEST/$d/$f"; echo "  + $d/$f"; }; done
    skipped+=("$d/ (merged, nothing replaced)")
  else cp -R "$ROOT/$d" "$DEST/$d"; created+=("$d/"); fi
done
mkdir -p "$DEST/.claude"
for f in hooks agents settings.json profile.env.example; do put "$ROOT/.claude/$f" ".claude/$f"; done
rm -rf "$DEST/.claude/skills" 2>/dev/null || true; bash "$DEST/scripts/skills-link.sh" >/dev/null
mkdir -p "$DEST/.github/hooks"
put "$ROOT/.github/hooks/guardrails.json" ".github/hooks/guardrails.json"
put "$ROOT/.github/copilot-instructions.md" ".github/copilot-instructions.md"
put "$T/pull_request_template.md" ".github/pull_request_template.md"
[ -d "$DEST/.vscode" ] || put "$ROOT/.vscode" ".vscode"

# 2. Docs → docs/harness/
mkdir -p "$DEST/docs/harness"
for f in "$ROOT"/docs/*.md; do put "$f" "docs/harness/$(basename "$f")"; done
put "$ROOT/AGENTS.md" "docs/harness/AGENTS.md"

# 3. AGENTS.md / CLAUDE.md: create or append a marked block
BLOCK_AGENTS="
<!-- harness:rules -->
## Harness rules (adopted ${TODAY})
This repo uses the harness: memory in the repo (\`memory/\`), the EPE cycle with a human gate (\`changes/\`), profiles and
hooks. The full rules are in [docs/harness/AGENTS.md](docs/harness/AGENTS.md) (imported below); configuration in \`harness.json\`. Read
\`memory/README.md\`, \`memory/decisions.md\` and \`memory/inbox.md\` at the start of every session. Run \`/codebase-context\`
once to fill the verified context block below and \`harness.json\` → \`code\`.

@docs/harness/AGENTS.md
<!-- /harness:rules -->
"
if [ -f "$DEST/AGENTS.md" ]; then
  grep -q "<!-- harness:rules -->" "$DEST/AGENTS.md" || { printf '%s' "$BLOCK_AGENTS" >> "$DEST/AGENTS.md"; created+=("AGENTS.md (block appended)"); }
else
  { cat "$ROOT/AGENTS.md"; } > "$DEST/AGENTS.md"; created+=("AGENTS.md")
fi
if [ -f "$DEST/CLAUDE.md" ]; then
  grep -q "harness:rules" "$DEST/CLAUDE.md" || { printf '\n<!-- harness:rules -->\n@AGENTS.md\n\nThe line above imports the repo rules (section "Harness rules" of AGENTS.md, which imports docs/harness/AGENTS.md); Claude-specific notes in docs/harness/CLAUDE.md.\n<!-- /harness:rules -->\n' >> "$DEST/CLAUDE.md"; created+=("CLAUDE.md (block appended)"); }
  put "$ROOT/CLAUDE.md" "docs/harness/CLAUDE.md"
else
  put "$ROOT/CLAUDE.md" "CLAUDE.md"
fi

# 4. Makefile
if [ -f "$DEST/Makefile" ]; then
  put "$ROOT/Makefile" "harness.mk"
  grep -q "include harness.mk" "$DEST/Makefile" || echo "  ! add this line to your Makefile:  include harness.mk"
else put "$ROOT/Makefile" "Makefile"; fi

# 5. harness.json, memory, changes
if [ ! -f "$DEST/harness.json" ]; then
python3 - "$DEST" "$FLAVOR" "$NAME" "$AUTHOR" "$EMAIL" "$OWNER" "$TODAY" <<'PY'
import json, sys
dest, flavor, name, author, email, owner, today = sys.argv[1:8]
hints = [
  {"skill": "triage", "pattern": "\\b(build|add|implement|create|fix|refactor|migrate|write|design|set ?up|integrate|quiero|necesito|agrega\\w*|implementa\\w*|crea\\w*|arregla\\w*|escrib\\w*|dise[ñn]a\\w*)\\b", "only_without_active": True},
  {"skill": "codebase-context", "pattern": "existing (codebase|project|repo)|brownfield|legacy|inherited (code|repo)|onboard"},
  {"skill": "epe-1-explore", "pattern": "user story|acceptance criteria|\\bAC\\d\\b|as an? .* i want .* so that|brief|historia de usuario|criterios? de aceptaci"},
  {"skill": "epe-4-review", "pattern": "\\b(review\\w*|pull request|\\bpr\\b|adversarial|revisa\\w*)\\b"},
  {"skill": "epe-memory", "pattern": "compact\\w*|save (the )?memor|note this for next time|close (the )?session|guarda (las )?memorias|apunta esto"},
  {"skill": "product-tech-brief", "pattern": "which (stack|framework|language)|tech(nical)? brief|non-functional|\\bnfrs?\\b|architecture decision"},
]
if flavor == "content":
    hints.insert(1, {"skill": "produce-content", "pattern": "\\b(post|article|lesson|script|thread|newsletter|linkedin|publish|draft\\w*|write\\w*)\\b"})
cfg = {"name": name, "description": f"Existing {flavor} project; harness adopted on {today}. Fill `code` with /codebase-context.",
       "flavor": flavor, "author": author, "email": email, "owner": owner, "changes_dir": "changes",
       "code": [], "tests": [],
       "exempt": ["memory/", "docs/", "product/", ".claude/", ".agents/", ".github/", ".cursor/", ".vscode/"],
       "protected_branches": ["main", "master", "release", "production", "prod"],
       "blocked_commands": [], "skill_hints": hints, "lint": True}
with open(f"{dest}/harness.json", "w") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2); f.write("\n")
PY
created+=("harness.json")
else skipped+=("harness.json"); fi
mkdir -p "$DEST/memory/journal" "$DEST/changes"
put "$T/memory-README.md" "memory/README.md"; put "$T/research.md" "memory/research.md"; put "$T/inbox.md" "memory/inbox.md"
put "$T/closed.md" "memory/closed.md"; put "$T/meta-improvements.md" "memory/meta-improvements.md"
put "$T/journal-README.md" "memory/journal/README.md"; put "$T/changes-README.md" "changes/README.md"
if [ ! -f "$DEST/memory/decisions.md" ]; then
cat > "$DEST/memory/decisions.md" <<MD
# Project decisions (lightweight ADR)

States: Accepted · Revised · Proposed · Discarded. Never deleted; when they change, mark them Revised with a date and
link the new one.

## D1 — The harness is adopted into an existing codebase
- **Status:** Accepted · ${TODAY} · decided by: ${AUTHOR:-<name (role)>}
- **Decision:** "${NAME}" adopts the harness (flavor **${FLAVOR}**) on top of its existing code. Nothing of the code was
  touched; the harness lives in \`.agents/\`, \`.claude/\`, \`memory/\`, \`changes/\`, \`docs/harness/\` and \`harness.json\`.
- **Why:** brownfield entry per \`docs/harness/brownfield.md\`: verify context, don't document the system; one bounded
  first change.
- **Next:** \`/codebase-context\` fills the \`AGENTS.md\` context block and \`harness.json\` → \`code\`.
MD
created+=("memory/decisions.md")
fi
cat > "$DEST/memory/journal/${TODAY}-harness-adopted.md" <<MD
# ${TODAY} — Harness adopted into an existing codebase

**Who:** ${AUTHOR:-<name (role)>} with Claude.

## Intent
Bring the harness into "${NAME}" without touching its code.

## What was done
\`make adopt\` from the harness: agentic layer added (nothing replaced), docs in \`docs/harness/\`, AGENTS.md/CLAUDE.md
created or extended with a marked block, \`harness.json\` with \`code=[]\`, memory seeded.

## Next
\`/codebase-context\` → verified context block, \`code\`, \`blocked_commands\`; then one bounded first change.

## Declared debt
- \`code=[]\`: the plan gate watches nothing until /codebase-context fills it.
MD
# .gitignore additions (append only)
for line in ".claude/profile.env" ".claude/settings.local.json" ".epe/"; do
  grep -qxF "$line" "$DEST/.gitignore" 2>/dev/null || echo "$line" >> "$DEST/.gitignore"
done

python3 "$ROOT/scripts/harness-sync.py" manifest --root "$DEST" --src "$ROOT" --mode adopt | sed 's/^/  /'
echo "✓ Harness adopted into $DEST (${NAME}, ${FLAVOR})"
printf '  created: %s\n' "${created[@]}" | head -40
[ ${#skipped[@]} -eq 0 ] || printf '  kept as they were: %s\n' "${skipped[@]}"
echo "  next: cd $DEST && make profile && make doctor; then in the agent: /codebase-context"
