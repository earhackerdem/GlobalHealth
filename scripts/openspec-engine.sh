#!/usr/bin/env bash
# make engine-openspec [TOOLS=claude,cursor,github-copilot] — switch this project's change layer to OpenSpec:
#   openspec init (pinned version from harness.json → openspec_version), fork the spec-driven schema as `harness-epe`,
#   install the harness's design/tasks templates and rules (Status gate, interface contract, Execution per group,
#   one red per group), set harness.json → engine=openspec, plan_file=design.md. Idempotent; never touches changes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
TOOLS="${1:-claude,cursor,github-copilot}"
VER="$(python3 -c "import json; print(json.load(open('harness.json')).get('openspec_version') or '1.14.1')")"
T=".agents/skills/epe-0-new/templates/openspec"
command -v npx >/dev/null || { echo "✗ npx (Node.js) is required for the OpenSpec engine" >&2; exit 1; }
echo "→ openspec@$VER init (tools: $TOOLS)"
npx -y "@fission-ai/openspec@$VER" init --tools "$TOOLS" --no-animation --force . >/dev/null
echo "→ schema fork spec-driven → harness-epe"
npx -y "@fission-ai/openspec@$VER" schema fork spec-driven harness-epe --force >/dev/null
cp "$T/design.md" openspec/schemas/harness-epe/templates/design.md
cp "$T/tasks.md" openspec/schemas/harness-epe/templates/tasks.md
python3 - <<'PY'
import re, pathlib
p = pathlib.Path("openspec/schemas/harness-epe/schema.yaml"); s = p.read_text()
s = s.replace("description: Default OpenSpec workflow - proposal → specs → design → tasks",
              "description: harness EPE on OpenSpec - proposal → specs → design (Status gate, interface contract) → tasks (Execution per group)")
def inject(s, art_id, extra):
    m = re.search(r"(  - id: %s\n(?:.*\n)*?    instruction: \|\n)" % art_id, s)
    if not m or extra.strip().splitlines()[0] in s:
        return s
    return s[:m.end()] + "".join("      " + l + "\n" for l in extra.strip().splitlines()) + "\n" + s[m.end():]
s = inject(s, "design", "HARNESS: the first line after the title is `Status: DRAFT`; the person you work with turns it into\n`Status: APPROVED` by writing \"plan approved\". Fill the Interface contract and one test per scenario. Always create\ndesign.md in this schema: it is the harness's gated plan, even for small changes.")
s = inject(s, "tasks", "HARNESS: every group heading ends with `· single`, `· test→impl` or `· parallel` (see the template's rule);\nthe tests of a group are committed alone as `test:` before its implementation; `make tdd-check` checks one red per\ntest→impl group.")
p.write_text(s)
c = pathlib.Path("openspec/config.yaml"); t = c.read_text()
t = re.sub(r"^schema:.*$", "schema: harness-epe", t, count=1, flags=re.M)
marker = "# --- harness rules"
if marker in t:
    t = t[:t.index(marker)].rstrip("\n") + "\n"
t = t.rstrip("\n") + "\n" + pathlib.Path(".agents/skills/epe-0-new/templates/openspec/config-rules.yaml").read_text()
c.write_text(t)
h = pathlib.Path("harness.json"); import json
d = json.load(open(h)); d["engine"] = "openspec"; d["plan_file"] = "design.md"; d.setdefault("openspec_version", "1.14.1")
h.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
PY
bash scripts/skills-link.sh >/dev/null
echo "✓ engine: openspec · schema harness-epe · plan_file design.md"
echo "  next: make epe-new SLUG=<id> (openspec new change) → /opsx:propose or /epe-1-explore; design.md carries the gate"
