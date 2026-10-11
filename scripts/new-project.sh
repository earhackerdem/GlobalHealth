#!/usr/bin/env bash
# make new DEST=… FLAVOR=development|content NAME=… AUTHOR=… EMAIL=… OWNER=…
# Creates a new project from this template: copies the agentic layer (without this template's memory), writes
# harness.json with the given identity, seeds memory/ from the templates with an origin D1, prepares the changes
# folder and (if missing) a git repo with the local identity. Does NOT commit and does NOT touch remotes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:?missing DEST}"; FLAVOR="${2:?missing FLAVOR (development|content)}"; NAME="${3:?missing NAME}"
AUTHOR="${4:?missing AUTHOR}"; EMAIL="${5:?missing EMAIL}"; OWNER="${6:?missing OWNER}"; ENGINE="${7:-epe}"
case "$FLAVOR" in development|content) ;; *) echo "FLAVOR must be development or content" >&2; exit 1;; esac
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then echo "✗ $DEST exists and is not empty" >&2; exit 1; fi
mkdir -p "$DEST"; DEST="$(cd "$DEST" && pwd)"
T="$ROOT/.agents/skills/epe-0-new/templates/common"; TODAY="$(date +%F)"

# 1. Agentic layer (no memory, no changes, no local state, no git)
rsync -a --exclude '.git' --exclude 'memory' --exclude 'changes' --exclude '.epe' --exclude '.claude/profile.env' \
  --exclude '.claude/settings.local.json' --exclude '.claude/skills' --exclude '__pycache__' --exclude '.DS_Store' \
  --exclude '/README.md' --exclude '/harness.json' --exclude '/VERSION' --exclude '/CHANGELOG.md' "$ROOT/" "$DEST/"
bash "$DEST/scripts/skills-link.sh" >/dev/null

# 2. harness.json with identity and flavor defaults
if [ "$FLAVOR" = "development" ]; then CODE='["src/", "app/", "lib/", "packages/"]'; TESTS='["tests/", "test/", "spec/", "__tests__/"]'; else CODE='["content/"]'; TESTS='[]'; fi
python3 - "$DEST" "$FLAVOR" "$NAME" "$AUTHOR" "$EMAIL" "$OWNER" "$CODE" "$TESTS" <<'PY'
import datetime, json, sys
dest, flavor, name, author, email, owner, code, tests = sys.argv[1:9]
hints = [
  {"skill": "triage", "pattern": "\\b(build|add|implement|create|fix|refactor|migrate|write|design|set ?up|integrate|quiero|necesito|agrega\\w*|implementa\\w*|crea\\w*|arregla\\w*|escrib\\w*|dise[ñn]a\\w*)\\b", "only_without_active": True},
  {"skill": "epe-1-explore", "pattern": "user story|acceptance criteria|\\bAC\\d\\b|as an? .* i want .* so that|brief|historia de usuario|criterios? de aceptaci"},
  {"skill": "epe-4-review", "pattern": "\\b(review\\w*|pull request|\\bpr\\b|adversarial|revisa\\w*)\\b"},
  {"skill": "epe-memory", "pattern": "compact\\w*|save (the )?memor|note this for next time|close (the )?session|guarda (las )?memorias|apunta esto"},
  {"skill": "product-prd", "pattern": "\\bprd\\b|product requirements|epics?\\b|roadmap"},
  {"skill": "product-tech-brief", "pattern": "which (stack|framework|language)|tech(nical)? brief|non-functional|\\bnfrs?\\b|architecture decision"},
  {"skill": "codebase-context", "pattern": "existing (codebase|project|repo)|brownfield|legacy|inherited (code|repo)|onboard"},
]
if flavor == "content":
    hints.insert(0, {"skill": "produce-content", "pattern": "\\b(post|article|lesson|script|thread|newsletter|linkedin|publish|draft\\w*|write\\w*|art[ií]culo|lecci[oó]n|guion|publicar|redacta\\w*|escrib\\w*)\\b"})
cfg = {"name": name, "description": f"{flavor} project generated from the harness template on {datetime.date.today().isoformat()}.",
       "flavor": flavor, "author": author, "email": email, "owner": owner, "changes_dir": "changes",
       "code": json.loads(code), "tests": json.loads(tests),
       "exempt": ["memory/", "docs/", "product/", ".claude/", ".agents/", ".github/", ".cursor/", ".vscode/"],
       "protected_branches": ["main", "master", "release", "production", "prod"],
       "blocked_commands": [], "skill_hints": hints, "lint": True}
with open(f"{dest}/harness.json", "w") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2); f.write("\n")
PY

# 3. Seeded memory
mkdir -p "$DEST/memory/journal" "$DEST/changes"
cp "$T/memory-README.md" "$DEST/memory/README.md"; cp "$T/research.md" "$DEST/memory/research.md"
cp "$T/inbox.md" "$DEST/memory/inbox.md"; cp "$T/closed.md" "$DEST/memory/closed.md"
cp "$T/meta-improvements.md" "$DEST/memory/meta-improvements.md"; cp "$T/journal-README.md" "$DEST/memory/journal/README.md"
cp "$T/changes-README.md" "$DEST/changes/README.md"; cp "$T/pull_request_template.md" "$DEST/.github/pull_request_template.md"
cat > "$DEST/memory/decisions.md" <<MD
# Project decisions (lightweight ADR)

States: Accepted · Revised · Proposed · Discarded. Never deleted; when they change, mark them Revised with a date and
link the new one. Order: from most structural to most tactical.

## D1 — Origin, owner and identity of the project
- **Status:** Accepted · ${TODAY} · decided by: ${AUTHOR}
- **Decision:** "${NAME}" is born from the mother template \`harness\` (flavor **${FLAVOR}**). Owner: **${OWNER}**. Author:
  ${AUTHOR} (${EMAIL}), which is this repo's local git identity.
- **Why:** the harness brings memory in the repo, an EPE cycle with a human gate, profiles and deterministic hooks
  already measured in two projects; what is specific to this project is decided here, not in the template.
- **Consequence:** \`harness.json\` → \`code\` marks which paths require an approved plan; adjust it in the first change.
MD
cat > "$DEST/memory/journal/${TODAY}-project-born.md" <<MD
# ${TODAY} — The project is born from the harness template

**Who:** ${AUTHOR} with Claude.

## Intent
Start "${NAME}" (flavor ${FLAVOR}, owner ${OWNER}) with the agentic layer of the mother template.

## What was done
\`make new\` from the harness template: agentic layer copied, \`harness.json\` with identity, memory seeded (origin D1),
\`changes/\` folder, local git repo with identity ${EMAIL}. No commit, no remote.

## Verification
\`make doctor\` in the destination.

## Declared debt
- First commit pending. No remote: nothing is pushed anywhere until ${AUTHOR} authorises it.
- \`harness.json\` → \`code\` has the flavor defaults; review it in the first change.
MD

# 4. Project README
cat > "$DEST/README.md" <<MD
# ${NAME}

A **${FLAVOR}** project of ${OWNER}, with the agentic layer of the \`harness\` template: memory in the repo, EPE cycle with a
human gate, profiles and hooks. Rules in [AGENTS.md](AGENTS.md); the cycle in [docs/epe-cycle.md](docs/epe-cycle.md).

\`\`\`bash
make profile     # who the agent works with (supervised blocks / autonomous warns)
make doctor      # does everything check out?
make epe-new SLUG=C-01-my-first-change   # then, in the agent: /epe-1-explore → /epe-2-plan → /epe-3-execute
\`\`\`
MD

# 4b. Change engine
if [ "$ENGINE" = "openspec" ]; then (cd "$DEST" && bash scripts/openspec-engine.sh claude,cursor,github-copilot | sed 's/^/  /'); fi

# 5. Ownership manifest + version (what the harness placed; make harness-update uses it)
python3 "$ROOT/scripts/harness-sync.py" manifest --root "$DEST" --src "$ROOT" --mode new | sed 's/^/  /'

# 6. Local git (no commit, no remote)
if [ ! -d "$DEST/.git" ]; then
  git -C "$DEST" init -q -b main 2>/dev/null || { git -C "$DEST" init -q && git -C "$DEST" checkout -q -b main 2>/dev/null || true; }
fi
git -C "$DEST" config user.name "$AUTHOR"; git -C "$DEST" config user.email "$EMAIL"

echo "✓ Project \"${NAME}\" (${FLAVOR}) created at ${DEST}"
echo "  local git identity: ${AUTHOR} <${EMAIL}> · owner: ${OWNER}"
echo "  next: cd ${DEST} && make profile && make doctor; first commit when you decide. No remote."
