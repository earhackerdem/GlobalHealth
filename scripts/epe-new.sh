#!/usr/bin/env bash
# make epe-new SLUG=<slug> [STORY=existing.md] — opens the change folder in <changes_dir>/<slug>/ with story.md
# from the project's flavor template (harness.json) and marks it active in .epe/active.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
SLUG="${1:?usage: make epe-new SLUG=<slug> [STORY=existing.md]}"; STORY="${2:-}"
cfg() { python3 -c "import json; d=json.load(open('harness.json')); print(d.get('$1') or '$2')" 2>/dev/null || echo "$2"; }
FLAVOR="$(cfg flavor development)"; [ "$FLAVOR" = "content" ] || FLAVOR="development"
ENGINE="$(cfg engine epe)"
if [ "$ENGINE" = "openspec" ]; then
  VER="$(cfg openspec_version 1.14.1)"
  [ -d "openspec/changes/$SLUG" ] || npx -y "@fission-ai/openspec@$VER" new change "$SLUG" >/dev/null
  mkdir -p .epe && printf '%s\n' "openspec/changes/$SLUG" > .epe/active
  echo "Active change: openspec/changes/$SLUG (engine openspec, schema harness-epe)"
  echo "Next: /opsx:propose (proposal + specs + design + tasks) or /epe-1-explore first; the gate is Status: APPROVED in design.md"
  exit 0
fi
CHANGES="$(cfg changes_dir changes)"
T=".agents/skills/epe-0-new/templates"; D="$CHANGES/$SLUG"
mkdir -p "$D"
if [ -f "$D/story.md" ]; then :
elif [ -n "$STORY" ]; then
  [ -f "$STORY" ] || { echo "story $STORY does not exist"; exit 1; }
  { printf '<!-- Copied from %s on %s. Clarifications from the exploration go here. -->\n\n' "$STORY" "$(date +%F)"; cat "$STORY"; } > "$D/story.md"
else
  cp "$T/$FLAVOR/story.md" "$D/story.md"
fi
[ -f "$CHANGES/README.md" ] || cp "$T/common/changes-README.md" "$CHANGES/README.md"
mkdir -p .epe && printf '%s\n' "$D" > .epe/active
echo "Active change: $D (flavor $FLAVOR)"
[ -n "$STORY" ] && echo "story.md copied from $STORY" || echo "Next: fill in $D/story.md"
echo "Then: /epe-1-explore"
