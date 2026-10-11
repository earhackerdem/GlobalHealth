#!/usr/bin/env python3
"""The harness layer inside a project as a vendored dependency.

  manifest --root P --src T --mode new|adopt   record what the harness placed (after make new / make adopt)
  status   --root P --src T                    what an update would do; writes nothing
  update   --root P --src T [--force]          apply it

Ownership: a file is harness-owned when the harness placed it and, at install, its content equalled the source.
Everything else (memory/, changes/, product/, harness.json, README, code, files adopt skipped) is never touched.
Per file the states are: up-to-date · update · add · remove · forked (local edit, upstream unchanged) ·
conflict (local edit AND upstream change: kept, listed) · unmanaged (exists locally, never owned: skipped).
--force overwrites forked/conflict files and leaves <file>.harness-bak. A file with both
<!-- harness:context --> markers is compared with its block body blanked and keeps the project's block on update.
Always content-compares (a version-only check lies when the template moved). Runs from the TEMPLATE
(`make harness-update SRC=…` calls $(SRC)/scripts/harness-sync.py) so the updater is as new as the layer.
Exit 0 clean (forks are fine) · 1 conflicts remain · 2 misuse. Python ≥ 3.8, stdlib only, no git writes.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

MANIFEST = ".agents/harness-manifest.json"
OWNED_DIRS = (".agents", ".claude/hooks", ".claude/agents", ".cursor", ".github/hooks", ".vscode", "scripts")
OWNED_FILES = (".claude/settings.json", ".claude/profile.env.example", ".github/copilot-instructions.md",
               "Makefile", "AGENTS.md", "CLAUDE.md")
SKIP_PARTS = ("__pycache__", ".DS_Store", "harness-manifest.json")
BLOCK = re.compile(r"(<!-- harness:context -->)(.*?)(<!-- /harness:context -->)", re.S)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    with open(path, "rb") as f:
        return f.read()


def normalised(data):
    """Bytes with the context block body blanked, if the file has both markers."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    if "<!-- harness:context -->" in text and "<!-- /harness:context -->" in text:
        return BLOCK.sub(r"\1\3", text).encode("utf-8")
    return data


def splice_block(new_data, old_data):
    """New content with the project's context block body."""
    try:
        new, old = new_data.decode("utf-8"), old_data.decode("utf-8")
    except UnicodeDecodeError:
        return new_data
    m_old, m_new = BLOCK.search(old), BLOCK.search(new)
    if not (m_old and m_new):
        return new_data
    return (new[:m_new.start(2)] + m_old.group(2) + new[m_new.end(2):]).encode("utf-8")


def template_files(src):
    """Harness-owned files in the template, relative paths, sorted."""
    out = []
    for d in OWNED_DIRS:
        base = os.path.join(src, d)
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if not x.endswith("-workspace") and x not in SKIP_PARTS]
            for f in files:
                p = os.path.relpath(os.path.join(root, f), src).replace(os.sep, "/")
                if not any(s in p for s in SKIP_PARTS):
                    out.append(p)
    for f in OWNED_FILES:
        if os.path.isfile(os.path.join(src, f)):
            out.append(f)
    for f in sorted(os.listdir(os.path.join(src, "docs"))) if os.path.isdir(os.path.join(src, "docs")) else []:
        if f.endswith(".md"):
            out.append("docs/" + f)
    return sorted(set(out))


def dest_for(rel, mode, root):
    """Where a template file lives in the project. adopt: docs/harness/, harness.mk, docs/harness/CLAUDE.md."""
    if mode != "adopt":
        return rel
    if rel.startswith("docs/"):
        return "docs/harness/" + rel[len("docs/"):]
    if rel == "AGENTS.md":
        return "docs/harness/AGENTS.md"
    if rel == "CLAUDE.md":
        return "docs/harness/CLAUDE.md" if os.path.isfile(os.path.join(root, "docs/harness/CLAUDE.md")) else "CLAUDE.md"
    if rel == "Makefile":
        return "harness.mk" if os.path.isfile(os.path.join(root, "harness.mk")) else "Makefile"
    return rel


def version_of(src):
    try:
        return open(os.path.join(src, "VERSION"), encoding="utf-8").read().strip()
    except FileNotFoundError:
        return ""


def load_manifest(root):
    try:
        return json.load(open(os.path.join(root, MANIFEST), encoding="utf-8"))
    except FileNotFoundError:
        return None


def save_manifest(root, data):
    path = os.path.join(root, MANIFEST)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def set_version(root, version):
    path = os.path.join(root, "harness.json")
    try:
        cfg = json.load(open(path, encoding="utf-8"))
    except Exception:
        return
    cfg["harness_version"] = version
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")


def relink_skills(root):
    script = os.path.join(root, "scripts", "skills-link.sh")
    if os.path.isfile(script):
        subprocess.run(["bash", script], cwd=root, capture_output=True)


def cmd_manifest(a):
    files = {}
    for rel in template_files(a.src):
        dest = dest_for(rel, a.mode, a.root)
        dp = os.path.join(a.root, dest)
        if os.path.islink(dp) or not os.path.isfile(dp):
            continue
        s_hash, d_hash = sha(normalised(read(os.path.join(a.src, rel)))), sha(normalised(read(dp)))
        if s_hash == d_hash:  # placed by the harness, untouched: owned
            files[dest] = {"src": rel, "sha256": s_hash}
    import datetime
    data = {"harness_version": version_of(a.src), "mode": a.mode, "installed": datetime.date.today().isoformat(),
            "files": files}
    save_manifest(a.root, data)
    set_version(a.root, data["harness_version"])
    print(f"harness manifest: {len(files)} owned files · version {data['harness_version'] or '?'} · mode {a.mode}")
    return 0


def plan(a, man):
    """List of (state, dest, rel, detail)."""
    mode = man.get("mode", "new")
    recorded = man.get("files", {})
    by_src = {v["src"]: d for d, v in recorded.items()}
    rows = []
    seen = set()
    for rel in template_files(a.src):
        dest = by_src.get(rel) or dest_for(rel, mode, a.root)
        seen.add(dest)
        dp = os.path.join(a.root, dest)
        t_hash = sha(normalised(read(os.path.join(a.src, rel))))
        entry = recorded.get(dest)
        exists = os.path.isfile(dp) and not os.path.islink(dp)
        p_hash = sha(normalised(read(dp))) if exists else None
        if entry is None:
            if not exists:
                rows.append(("add", dest, rel, ""))
            elif p_hash == t_hash:
                rows.append(("adopt", dest, rel, "identical to upstream; now owned"))
            else:
                rows.append(("unmanaged", dest, rel, "exists locally and was never owned: skipped"))
            continue
        m_hash = entry["sha256"]
        if not exists:
            rows.append(("forked", dest, rel, "deleted locally; not restored"))
        elif p_hash == m_hash:
            rows.append(("up-to-date" if t_hash == m_hash else "update", dest, rel, ""))
        elif t_hash == m_hash:
            rows.append(("forked", dest, rel, "local edit, upstream unchanged"))
        elif p_hash == t_hash:
            rows.append(("adopt", dest, rel, "already equal to upstream"))
        else:
            rows.append(("conflict", dest, rel, f"local edit AND upstream change: kept. diff {dest} {a.src}/{rel}"))
    for dest, entry in sorted(recorded.items()):
        if dest in seen:
            continue
        dp = os.path.join(a.root, dest)
        if not os.path.isfile(dp):
            rows.append(("gone", dest, entry["src"], "already removed locally"))
        elif sha(normalised(read(dp))) == entry["sha256"]:
            rows.append(("remove", dest, entry["src"], "retired upstream"))
        else:
            rows.append(("forked", dest, entry["src"], "retired upstream but edited locally: kept"))
    return rows


def report(rows, version_from, version_to, dry):
    order = ("update", "add", "remove", "adopt", "conflict", "forked", "unmanaged", "gone", "up-to-date")
    counts = {k: sum(1 for r in rows if r[0] == k) for k in order}
    head = "harness-sync (dry run)" if dry else "harness-sync"
    print(f"{head}: {version_from or '?'} → {version_to or '?'} · " + " · ".join(f"{k} {v}" for k, v in counts.items() if v))
    for state in order:
        if state == "up-to-date":
            continue
        for s, dest, rel, detail in rows:
            if s == state:
                mark = {"update": "↻", "add": "+", "remove": "−", "adopt": "=", "conflict": "✗", "forked": "⑂",
                        "unmanaged": "·", "gone": "·"}[s]
                print(f"  {mark} {s:10} {dest}" + (f"  ({detail})" if detail else ""))
    return counts


def cmd_status(a, apply=False):
    man = load_manifest(a.root)
    if man is None:
        print(f"no {MANIFEST}: this project was not installed by a harness with manifests. "
              "Run `harness-sync.py manifest --mode new|adopt` once (it only records files identical to the template).")
        return 2
    rows = plan(a, man)
    counts = report(rows, man.get("harness_version"), version_of(a.src), dry=not apply)
    if not apply:
        return 0
    recorded = man.get("files", {})
    backups = []
    for state, dest, rel, _ in rows:
        dp, sp = os.path.join(a.root, dest), os.path.join(a.src, rel)
        if state in ("update", "add", "adopt") or (a.force and state in ("forked", "conflict") and os.path.isfile(sp)):
            if a.force and state in ("forked", "conflict") and os.path.isfile(dp):
                os.replace(dp, dp + ".harness-bak"); backups.append(dest + ".harness-bak")
            new = read(sp)
            if state != "add" and os.path.isfile(dp + ".harness-bak" if a.force and state in ("forked", "conflict") else dp):
                old = read(dp + ".harness-bak" if a.force and state in ("forked", "conflict") else dp)
                new = splice_block(new, old)
            os.makedirs(os.path.dirname(dp) or ".", exist_ok=True)
            with open(dp, "wb") as f:
                f.write(new)
            if os.access(sp, os.X_OK):
                os.chmod(dp, os.stat(dp).st_mode | 0o111)
            recorded[dest] = {"src": rel, "sha256": sha(normalised(read(sp)))}
        elif state in ("remove", "gone"):
            if os.path.isfile(dp):
                os.remove(dp)
                d = os.path.dirname(dp)
                while d and d != a.root and os.path.isdir(d) and not os.listdir(d):
                    os.rmdir(d); d = os.path.dirname(d)
            recorded.pop(dest, None)
    man["files"] = recorded
    man["harness_version"] = version_of(a.src)
    import datetime
    man["updated"] = datetime.date.today().isoformat()
    save_manifest(a.root, man)
    set_version(a.root, man["harness_version"])
    relink_skills(a.root)
    left = 0 if a.force else counts["conflict"]  # forks are a legitimate steady state; conflicts are not
    if backups:
        print("  backups: " + ", ".join(backups))
    print(f"  manifest and harness.json → harness_version {man['harness_version'] or '?'} rewritten; skills relinked.")
    print("  next: `make doctor`, then record the update as one small change folder + journal entry (it is a change to this repo).")
    return 1 if left else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("manifest", "status", "update"):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True, help="the project")
        p.add_argument("--src", required=True, help="the harness template")
        if name == "manifest":
            p.add_argument("--mode", choices=("new", "adopt"), required=True)
        if name == "update":
            p.add_argument("--force", action="store_true")
    a = ap.parse_args()
    a.root, a.src = os.path.abspath(a.root), os.path.abspath(a.src)
    if not os.path.isdir(a.src) or not os.path.isdir(os.path.join(a.src, ".agents")):
        print(f"--src {a.src} is not a harness template (no .agents/)"); return 2
    if os.path.realpath(a.root) == os.path.realpath(a.src):
        print("--root is the template itself"); return 2
    if not os.path.isdir(a.root):
        print(f"--root {a.root} is not a directory"); return 2
    if a.cmd == "manifest":
        return cmd_manifest(a)
    return cmd_status(a, apply=(a.cmd == "update"))


if __name__ == "__main__":
    sys.exit(main())
