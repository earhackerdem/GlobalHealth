#!/usr/bin/env python3
"""Open-PR health check: broken stacks and collisions between sessions. On demand (`make check-prs`), not a
blocking gate.

Why (two real precedents of the same failure in origin): PRs marked MERGED whose content was NOT on main
because they merged into their base branch; and a PR still pointing at an already-merged base. The cause is
always the same and counter-intuitive: **GitHub only re-targets a stacked PR to `main` if its base branch is
DELETED when merged.** If the base stays alive, "Merge" puts the upper PR into the base, nobody warns, and the
work is stranded with the PR marked merged.

The fourth check is different: two open PRs touching the SAME file. With several sessions at once, two of them
wrote contradictory statements in the same file on the same day; a person caught it by asking, not a gate.

NEVER blocks: it needs network and an authenticated `gh`, and a gate that depends on the network teaches people
to skip it. Without `gh`, network or permissions, it warns and exits 0.

Usage:  python3 scripts/check-prs.py   ·   make check-prs
"""
import json
import subprocess
import sys
from collections import defaultdict

PRINCIPAL = "main"


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=kw.get("timeout", 30))


def prs_abiertos():
    r = sh("gh", "pr", "list", "--state", "open", "--limit", "50",
           "--json", "number,title,baseRefName,headRefName,files")
    if r.returncode != 0:
        return None, (r.stderr or "").strip().splitlines()[-1:] or ["gh failed"]
    try:
        return json.loads(r.stdout), None
    except Exception:
        return None, ["unreadable gh response"]


def rama_remota_existe(rama):
    return sh("git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{rama}").returncode == 0


def commits_por_detras(rama):
    """How many commits of origin/main are missing from origin/<branch>. None if unknown."""
    r = sh("git", "rev-list", "--count", f"origin/{rama}..origin/{PRINCIPAL}")
    if r.returncode != 0:
        return None
    try:
        return int(r.stdout.strip())
    except ValueError:
        return None


def main():
    if sh("git", "rev-parse", "--is-inside-work-tree").returncode != 0:
        print("ℹ not inside a git repo — nothing to check")
        return 0
    if sh("which", "gh").returncode != 0:
        print("ℹ `gh` not found: this check needs the GitHub CLI. Skipped (does not block).")
        return 0

    # Without a fetch, "behind main" measures against a stale snapshot and lies.
    if sh("git", "fetch", "--quiet", "--prune", "origin", timeout=60).returncode != 0:
        print("ℹ fetch failed (no network?). Skipped (does not block).")
        return 0

    prs, error = prs_abiertos()
    if prs is None:
        print(f"ℹ could not query GitHub ({'; '.join(error)}). Skipped (does not block).")
        return 0
    if not prs:
        print("✓ no open PRs")
        return 0

    avisos = []
    graves = []

    for pr in prs:
        n, base, head = pr["number"], pr["baseRefName"], pr["headRefName"]
        titulo = (pr.get("title") or "")[:60]

        if base != PRINCIPAL:
            # Stacked. Stacking is not the problem: a dead base is.
            if not rama_remota_existe(base):
                graves.append(
                    f"#{n} targets `{base}`, which NO LONGER EXISTS on the remote. "
                    f"Merging it would send it to a dead branch and strand the work.\n"
                    f"       → fix it with:  gh pr edit {n} --base {PRINCIPAL}"
                )
            else:
                base_fusionada = sh(
                    "git", "merge-base", "--is-ancestor",
                    f"origin/{base}", f"origin/{PRINCIPAL}"
                ).returncode == 0
                if base_fusionada:
                    graves.append(
                        f"#{n} is stacked on `{base}`, which is already MERGED into {PRINCIPAL} "
                        f"(but its branch is still alive, so GitHub did not re-target it).\n"
                        f"       → fix it with:  gh pr edit {n} --base {PRINCIPAL}"
                    )
                else:
                    avisos.append(
                        f"#{n} is stacked on `{base}` (not merged yet). "
                        f"When you merge the base, DELETE it so this one re-targets itself. — {titulo}"
                    )

        detras = commits_por_detras(head) if rama_remota_existe(head) else None
        if detras:
            avisos.append(f"#{n} is {detras} commit(s) behind {PRINCIPAL}: what you see is not what gets merged. — {titulo}")

    # Collisions: two open PRs touching the same file.
    por_archivo = defaultdict(list)
    for pr in prs:
        for f in pr.get("files") or []:
            ruta = f.get("path") if isinstance(f, dict) else f
            if ruta:
                por_archivo[ruta].append(pr["number"])
    colisiones = {ruta: nums for ruta, nums in por_archivo.items() if len(set(nums)) > 1}

    print(f"Checked {len(prs)} open PR(s).\n")

    for g in graves:
        print(f"  ✗ {g}")
    for a in avisos:
        print(f"  ⚠ {a}")
    if colisiones:
        print("\n  ⚠ Files touched by MORE THAN ONE open PR (possible collision between sessions):")
        for ruta, nums in sorted(colisiones.items()):
            print(f"      {ruta} → {', '.join('#' + str(x) for x in sorted(set(nums)))}")
        print("      Check whether they contradict each other BEFORE merging; merge order does not solve it.")

    if not graves and not avisos and not colisiones:
        print("  ✓ nothing to flag: none stacked on a dead branch, none behind, no collisions")

    print("\nThis check looks at branch STATE and file overlaps, not PR CONTENT: "
          "two PRs touching the same file does not mean they contradict each other.")
    return 1 if graves else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ℹ the PR check failed ({e}). Skipped (does not block).")
        sys.exit(0)
