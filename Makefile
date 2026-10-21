# Harness: day-to-day recipes. `make` alone lists them.
SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help doctor profile skills-link skills-check new adopt engine-openspec harness-status harness-update harness-harvest install-hooks hook-test epe-new epe-status tdd-check board board-serve product-init inbox closed changelog decision-next memory-migrate memory-check memory-swept retro check-prs worktrees worktrees-clean

help: ## List the recipes
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

## --- setup ---
doctor: ## Does everything check out? tools, harness.json, linked skills, hooks, memory, profile
	@bash scripts/doctor.sh

profile: ## Your local profile (NAME, ROLE, PROFILE=supervised|autonomous) for the agent's hooks
	@bash scripts/profile.sh

skills-link: ## Regenerate the symlinks .claude/skills/<n> -> .agents/skills/<n> (Claude Code only reads .claude/skills/)
	@bash scripts/skills-link.sh

skills-check: ## Check the harness's own skills: frontmatter, links, cited targets, symlinks. SKILLS="a b" to narrow
	@python3 scripts/skills-check.py $(SKILLS)

new: ## New project from this template: make new DEST=../my-project FLAVOR=development|content NAME=… AUTHOR=… EMAIL=… OWNER=… [ENGINE=openspec]
	@bash scripts/new-project.sh "$(DEST)" "$(FLAVOR)" "$(NAME)" "$(AUTHOR)" "$(EMAIL)" "$(OWNER)" "$(ENGINE)"

adopt: ## Bring the harness INTO an existing repo without touching its code: make adopt DEST=../existing-repo [FLAVOR=…] [NAME=…] [AUTHOR=…] [EMAIL=…] [OWNER=…]
	@bash scripts/adopt.sh "$(DEST)" "$(or $(FLAVOR),development)" "$(NAME)" "$(AUTHOR)" "$(EMAIL)" "$(OWNER)"

engine-openspec: ## Switch the change layer to OpenSpec (pinned; forks its schema with the harness rules): make engine-openspec [TOOLS=claude,cursor,github-copilot]
	@bash scripts/openspec-engine.sh "$(or $(TOOLS),claude,cursor,github-copilot)"

harness-status: ## What `make harness-update` would do, writes nothing: make harness-status SRC=../harness
	@python3 "$(SRC)/scripts/harness-sync.py" status --root . --src "$(SRC)"

harness-update: ## Bring a newer harness in: overwrites untouched owned files, keeps and lists forks, removes retired files. make harness-update SRC=../harness [FORCE=1]
	@python3 "$(SRC)/scripts/harness-sync.py" update --root . --src "$(SRC)" $(if $(FORCE),--force,)

harness-harvest: ## Lessons from a project back into the template (read-only diff of meta-improvements): make harness-harvest SRC=../my-project
	@python3 scripts/harness-harvest.py "$(SRC)"

install-hooks: ## Install the local pre-push gate: prek over the diff vs the base branch before every push
	@bash scripts/install-hooks.sh

hook-test: ## Run a hook with a payload FROM A FILE: make hook-test HOOK=gate-plan PAYLOAD_FILE=/tmp/p.json [PROFILE=autonomous]
	@HARNESS_PROFILE=$(or $(PROFILE),supervised) python3 .claude/hooks/$(HOOK).py < "$(PAYLOAD_FILE)"; echo "(exit $$?)"

## --- EPE cycle ---
epe-new: ## Open a change: make epe-new SLUG=C-01-slug [STORY=path.md]
	@bash scripts/epe-new.sh "$(SLUG)" $(STORY)

epe-status: ## Show the active EPE change and the state of its plan
	@if [ ! -f .epe/active ]; then echo "No active change (make epe-new SLUG=<slug>)"; exit 0; fi; \
	d=$$(cat .epe/active); echo "Active change: $$d"; \
	for f in story exploration plan tasks evidence validation; do \
	  [ -f "$$d/$$f.md" ] && echo "  ✅ $$f.md" || echo "  ·  $$f.md (pending)"; done; \
	[ -f "$$d/plan.md" ] && grep -m1 -E '^Status:' "$$d/plan.md" || true

tdd-check: ## Red before green: the newest `test:` commit exists and harness.json → tests is untouched since. make tdd-check [SINCE=ref]
	@python3 scripts/tdd-check.py $(if $(SINCE),--since $(SINCE),)

board: ## The board rendered from the change folders: markdown here + .harness/board.html (no state, no network)
	@python3 scripts/board.py

board-serve: ## Serve the board on 127.0.0.1 (PORT=8765) so card links open the files
	@python3 scripts/board.py --format html --serve $(or $(PORT),8765)

product-init: ## Create the optional product/ folder (brief → PRD → technical brief) with its README
	@mkdir -p product && [ -f product/README.md ] || cp .agents/skills/product-brief/product-README.md product/README.md; echo "product/ ready: /product-brief → /product-prd (if needed) → /product-tech-brief"

## --- memory ---
inbox: ## The whole inbox in memory/inbox/ (the hook only shows 3)
	@python3 scripts/inbox.py

closed: ## The closed-verdicts index (memory/closed/) as one document, to paste literally into a review prompt
	@python3 -c 'import sys; sys.path.insert(0, ".claude/hooks"); import _memory; print(_memory.render_closed("."), end="")'

changelog: ## Render CHANGELOG.md from changelog.d/ (newest first, then _legacy.md). On main or in a release PR, never in a change PR
	@python3 -c 'import sys; sys.path.insert(0, ".claude/hooks"); import _memory; open("CHANGELOG.md", "w", encoding="utf-8").write(_memory.render_changelog("."))' && echo "CHANGELOG.md rendered from changelog.d/"

decision-next: ## The next free decision id (D<n>) for memory/decisions/D<n>-slug.md
	@python3 -c 'import sys; sys.path.insert(0, ".claude/hooks"); import _memory; print("D%d" % (max([n for n, _ in _memory.decision_ids(".")] or [0]) + 1))'

memory-migrate: ## Old single memory files (inbox.md, closed.md…) → one file per entry, lossless by check. DRY_RUN=1 writes nothing
	@python3 scripts/memory-migrate.py --root . $(if $(DRY_RUN),--dry-run,)

memory-check: ## Mechanical leads: repo memory (duplicate ids, unknown statuses, old files) and stale private memories
	@python3 scripts/check-memory.py

memory-swept: ## Record that memory was swept (resets the unswept-compactions notice)
	@python3 .claude/hooks/memory-compaction.py swept </dev/null

retro: ## Mechanical retro of a session: make retro ID=<session-id>
	@python3 scripts/retro-transcript.py --find $(ID)

## --- git ---
check-prs: ## Open PRs: broken stacks, branches behind, files touched by more than one PR (needs gh)
	@python3 scripts/check-prs.py

worktrees: ## Worktree inventory: live vs zombie (deletes nothing)
	@python3 scripts/worktrees.py

worktrees-clean: ## Remove clean zombie worktrees
	@python3 scripts/worktrees.py --clean

# Project-owned recipes (test, run, deploy…): put them in project.mk, which harness-update never touches.
-include project.mk
