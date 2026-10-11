#!/usr/bin/env bash
# make doctor — checks that the harness is consistent: tools, harness.json, skill symlinks, hooks, memory, profile.
# Changes nothing. Exits 1 on ❌.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'; fails=0
ok(){ echo -e "  ${G}✅${N} $1"; }; warn(){ echo -e "  ${Y}⚠️ ${N} $1"; }; bad(){ echo -e "  ${R}❌${N} $1"; fails=$((fails+1)); }

echo "== Tools"
for t in git python3 make; do command -v "$t" >/dev/null && ok "$t" || bad "$t is not in PATH"; done
command -v gh >/dev/null && ok "gh (PRs, check-prs)" || warn "no gh: check-prs and PR comments are skipped"
pv=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])'); ok "python $pv (hooks need ≥ 3.8)"

echo "== harness.json"
if [ -f harness.json ]; then
  python3 - <<'PY' || fails=$((fails+1))
import json, sys
d = json.load(open("harness.json"))
flavor = d.get("flavor"); code = d.get("code") or []
print(f"  ✅ name={d.get('name')!r} flavor={flavor!r} owner={d.get('owner')!r}")
if flavor not in ("development", "content", "mixed"):
    print("  ❌ flavor must be development | content | mixed"); sys.exit(1)
if not code:
    print("  ⚠️  code=[]: the plan gate watches no path (edit harness.json → code)")
else:
    print(f"  ✅ code={code} requires an approved plan")
ver = d.get("harness_version") or "?"
import os
man = os.path.isfile(".agents/harness-manifest.json")
tpl = open("VERSION").read().strip() if os.path.isfile("VERSION") else ""
if tpl:
    print(f"  ✅ harness template VERSION {tpl}" + ("" if ver in (tpl, "?") else f"  ⚠️ harness.json says {ver}"))
else:
    print(f"  ✅ harness_version={ver} · manifest {'present' if man else 'MISSING (make harness-update cannot run; see docs/updating.md)'}")
engine = d.get("engine") or "epe"
if engine == "openspec":
    okc = os.path.isfile("openspec/config.yaml") and "harness-epe" in open("openspec/config.yaml").read()
    print(f"  {'✅' if okc else '❌'} engine=openspec · schema harness-epe {'present' if okc else 'MISSING (make engine-openspec)'} · plan_file={d.get('plan_file')}")
    if not okc: sys.exit(1)
else:
    print(f"  ✅ engine={engine} (changes in {d.get('changes_dir') or 'changes'}/)")
tests = d.get("tests") or []
print(f"  ✅ tests={tests}: tester/implementer barrier on" if tests else "  ·  tests=[]: tester/implementer barrier off (development projects fill it)")
PY
else bad "harness.json is missing"; fi

echo "== Skills"
n=0; broken=0
for d in .agents/skills/*/; do [ -f "$d/SKILL.md" ] || continue; s=$(basename "$d"); n=$((n+1))
  [ -L ".claude/skills/$s" ] && [ -f ".claude/skills/$s/SKILL.md" ] || broken=$((broken+1))
done
[ "$broken" = 0 ] && ok "$n skills in .agents/skills/, all linked in .claude/skills/" || bad "$broken skill(s) without symlink in .claude/skills/ (make skills-link)"

echo "== Hooks"
for h in .claude/hooks/*.py; do python3 -m py_compile "$h" 2>/dev/null || bad "$h does not compile"; done
reg=$(grep -o 'hooks/[a-z_-]*\.py' .claude/settings.json | sort -u | wc -l | tr -d ' '); ok "$reg hooks registered in .claude/settings.json"
for h in .claude/hooks/[a-z]*.py; do b=$(basename "$h"); grep -q "$b" .claude/settings.json || warn "$b exists but is not registered in settings.json"; done

echo "== Memory"
for f in memory/README.md memory/decisions.md memory/inbox.md memory/closed.md; do [ -f "$f" ] && ok "$f" || bad "missing $f"; done
[ -d memory/journal ] && ok "memory/journal/" || bad "missing memory/journal/"

echo "== Profile"; bash scripts/profile.sh check | sed 's/^/  /'

echo "== Active EPE change"
if [ -f .epe/active ]; then d=$(cat .epe/active); echo "  active: $d"; [ -f "$d/plan.md" ] && grep -m1 -E '^Status:' "$d/plan.md" | sed 's/^/  plan: /' || echo "  (no plan.md)"; else echo "  none (make epe-new SLUG=<slug>)"; fi

echo; [ "$fails" = 0 ] && echo -e "${G}doctor: everything checks out${N}" || { echo -e "${R}doctor: $fails problem(s)${N}"; exit 1; }
