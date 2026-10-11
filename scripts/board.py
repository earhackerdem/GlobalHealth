#!/usr/bin/env python3
"""A board rendered from the change folders. No state of its own: the repo is the source of truth.

  python3 scripts/board.py [--root .] [--format md|html|both] [--out .harness/board.html] [--serve PORT]

Column per change, by what exists (never by a status someone must maintain):
  Done        under <changes_dir>/_archive/
  Validating  all tasks ticked, evidence.md and validation.md present
  Executing   plan.md with `Status: APPROVED`, tasks not all ticked
  Planning    plan.md present, not approved
  Exploring   exploration.md present, no plan
  Backlog     story only (or an empty folder, flagged)
The active change (.epe/active) is marked. --serve binds 127.0.0.1 only and serves the repo root so card links
open the files. Python ≥ 3.8, stdlib only, no network, HTML self-contained.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys

FILES = ("story", "exploration", "plan", "tasks", "evidence", "validation")
COLUMNS = ("Backlog", "Exploring", "Planning", "Executing", "Validating", "Done")
EXEC_RE = re.compile(r"·\s*(single|test→impl|parallel)\b")


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def first(pattern, text, flags=re.M):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


def parse_change(folder, slug, archived, active):
    story = read(os.path.join(folder, "story.md"))
    plan = read(os.path.join(folder, "plan.md"))
    tasks = read(os.path.join(folder, "tasks.md"))
    present = {f: os.path.isfile(os.path.join(folder, f + ".md")) for f in FILES}
    done = len(re.findall(r"^\s*- \[x\]", tasks, re.M | re.I))
    todo = len(re.findall(r"^\s*- \[ \]", tasks, re.M))
    status = first(r"^Status:\s*(\w+)", plan).upper()
    c = {
        "slug": slug, "archived": archived, "active": active, "files": present,
        "title": first(r"^##\s+(?:[A-Za-z]-?\d+\s*[:—-]\s*)?(.+)$", story) or ("(no story.md)" if not present["story"] else slug),
        "origin": first(r"^\*\*Origin:\*\*\s*(.+)$", story), "triage": first(r"^\*\*Triage:\*\*\s*(.+)$", story),
        "ac": len(re.findall(r"^\*\*AC\d+", story, re.M)),
        "plan_status": status, "approver": first(r"Approved by:\s*([^\n]+?)(?:\s+on\s|\s*$)", plan),
        "done": done, "total": done + todo, "exec": sorted(set(EXEC_RE.findall(tasks))),
    }
    if archived:
        col = "Done"
    elif present["tasks"] and c["total"] and done == c["total"] and present["evidence"] and present["validation"]:
        col = "Validating"
    elif status == "APPROVED":
        col = "Executing"
    elif present["plan"]:
        col = "Planning"
    elif present["exploration"]:
        col = "Exploring"
    else:
        col = "Backlog"
    c["column"] = col
    return c


def parse_openspec(folder, slug, archived, active):
    """A change under openspec/changes/: proposal + specs → contract, design → plan, tasks, evidence, validation."""
    proposal = read(os.path.join(folder, "proposal.md"))
    design = read(os.path.join(folder, "design.md"))
    tasks = read(os.path.join(folder, "tasks.md"))
    specs = ""
    for dp, _, fn in os.walk(os.path.join(folder, "specs")):
        for f in fn:
            if f.endswith(".md"):
                specs += read(os.path.join(dp, f))
    present = {"story": os.path.isfile(os.path.join(folder, "proposal.md")) or bool(specs),
               "exploration": os.path.isfile(os.path.join(folder, "exploration.md")),
               "plan": os.path.isfile(os.path.join(folder, "design.md")),
               "tasks": os.path.isfile(os.path.join(folder, "tasks.md")),
               "evidence": os.path.isfile(os.path.join(folder, "evidence.md")),
               "validation": os.path.isfile(os.path.join(folder, "validation.md"))}
    done = len(re.findall(r"^\s*- \[x\]", tasks, re.M | re.I)); todo = len(re.findall(r"^\s*- \[ \]", tasks, re.M))
    status = first(r"^Status:\s*(\w+)", design).upper()
    c = {"slug": slug, "archived": archived, "active": active, "files": present,
         "title": first(r"^#\s+(?:Proposal:\s*)?(.+)$", proposal) or slug,
         "origin": first(r"^\*?\*?Origin:\*?\*?\s*(.+)$", proposal), "triage": first(r"^\*?\*?Triage:\*?\*?\s*(.+)$", proposal),
         "ac": len(re.findall(r"^####\s*Scenario:", specs, re.M)),
         "plan_status": status, "approver": first(r"Approved by:\s*([^\n]+?)(?:\s+on\s|\s*$)", design),
         "done": done, "total": done + todo, "exec": sorted(set(EXEC_RE.findall(tasks)))}
    if archived:
        col = "Done"
    elif present["tasks"] and c["total"] and done == c["total"] and present["evidence"] and present["validation"]:
        col = "Validating"
    elif status == "APPROVED":
        col = "Executing"
    elif present["plan"] or present["tasks"]:
        col = "Planning"
    elif present["exploration"] or bool(specs):
        col = "Exploring"
    else:
        col = "Backlog"
    c["column"] = col
    return c


def collect(root):
    cfg = {}
    try:
        cfg = json.load(open(os.path.join(root, "harness.json"), encoding="utf-8"))
    except Exception:
        pass
    if (cfg.get("engine") or "epe") == "openspec":
        base = os.path.join(root, "openspec", "changes")
        active = read(os.path.join(root, ".epe", "active")).strip().rstrip("/")
        out = []
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                p = os.path.join(base, name)
                if name.startswith(".") or name == "archive" or not os.path.isdir(p):
                    continue
                out.append(parse_openspec(p, name, False, active == f"openspec/changes/{name}"))
            arch = os.path.join(base, "archive")
            if os.path.isdir(arch):
                for name in sorted(os.listdir(arch)):
                    p = os.path.join(arch, name)
                    if os.path.isdir(p) and not name.startswith("."):
                        out.append(parse_openspec(p, name, True, False))
        return cfg, "openspec/changes", out
    changes_dir = (cfg.get("changes_dir") or "changes").strip("/")
    base = os.path.join(root, changes_dir)
    active = read(os.path.join(root, ".epe", "active")).strip().rstrip("/")
    out = []
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            p = os.path.join(base, name)
            if name.startswith((".", "_")) or not os.path.isdir(p):
                continue
            out.append(parse_change(p, name, False, active == f"{changes_dir}/{name}"))
        arch = os.path.join(base, "_archive")
        if os.path.isdir(arch):
            for name in sorted(os.listdir(arch)):
                p = os.path.join(arch, name)
                if os.path.isdir(p) and not name.startswith("."):
                    out.append(parse_change(p, name, True, False))
    return cfg, changes_dir, out


def render_md(cfg, changes_dir, changes):
    name = cfg.get("name") or os.path.basename(os.getcwd())
    lines = [f"# Board — {name} · {datetime.date.today().isoformat()} · rendered from `{changes_dir}/`", ""]
    if not changes:
        lines.append(f"(no change folders yet: `make epe-new SLUG=C-01-<slug>` opens the first one)")
        return "\n".join(lines) + "\n"
    counts = " · ".join(f"{c} {sum(1 for x in changes if x['column'] == c)}" for c in COLUMNS)
    lines += [counts, "", "| Column | Change | Title | AC | Tasks | Plan | Exec | Files |", "|---|---|---|---|---|---|---|---|"]
    for col in COLUMNS:
        for c in [x for x in changes if x["column"] == col]:
            files = "".join("●" if c["files"][f] else "○" for f in FILES)
            plan = (c["plan_status"] or "—") + (f" ({c['approver']})" if c["approver"] else "")
            tasks = f"{c['done']}/{c['total']}" if c["total"] else "—"
            lines.append(f"| {col} | {'▶ ' if c['active'] else ''}{c['slug']} | {c['title']} | {c['ac'] or '—'} | {tasks} | {plan} | {', '.join(c['exec']) or '—'} | {files} |")
    lines += ["", "Files: story · exploration · plan · tasks · evidence · validation (● present ○ missing) · ▶ active change"]
    return "\n".join(lines) + "\n"


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c1e24;--muted:#6b7280;--line:#e3e6ea;--accent:#2563eb;--ok:#16a34a;--warn:#d97706;--col:#eef0f3}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1115;--card:#171a21;--ink:#e6e8ec;--muted:#9aa3b2;--line:#262b35;--accent:#60a5fa;--ok:#4ade80;--warn:#fbbf24;--col:#13161c}}
:root[data-theme="dark"]{--bg:#0f1115;--card:#171a21;--ink:#e6e8ec;--muted:#9aa3b2;--line:#262b35;--accent:#60a5fa;--ok:#4ade80;--warn:#fbbf24;--col:#13161c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:20px 16px 8px}h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--muted);font-size:13px}
.board{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(260px,1fr);gap:12px;padding:12px 16px 24px;overflow-x:auto}
@media (max-width:720px){.board{grid-auto-flow:row;grid-auto-columns:auto}}
.col{background:var(--col);border:1px solid var(--line);border-radius:10px;padding:10px;min-height:120px}
.col h2{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-bottom:10px}
.card.active{border-color:var(--accent);box-shadow:0 0 0 2px color-mix(in srgb,var(--accent) 30%,transparent)}
.card .slug{font-size:12px;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.card .title{font-weight:600;margin:2px 0 6px}.card .title a{color:inherit;text-decoration:none}.card .title a:hover{text-decoration:underline}
.meta{font-size:12px;color:var(--muted);margin:2px 0}.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:6px 0 4px}
.bar i{display:block;height:100%;background:var(--ok)}.chips{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.chip{font-size:11px;border:1px solid var(--line);border-radius:999px;padding:1px 7px;color:var(--muted)}.chip.on{color:var(--ink);border-color:var(--accent)}
.chip.ok{color:var(--ok);border-color:var(--ok)}.chip.warn{color:var(--warn);border-color:var(--warn)}
.empty{padding:40px 16px;color:var(--muted)}footer{padding:8px 16px 24px;color:var(--muted);font-size:12px}
"""


def render_html(cfg, changes_dir, changes):
    e = html.escape
    name = cfg.get("name") or "harness project"
    today = datetime.date.today().isoformat()
    cols = []
    for col in COLUMNS:
        cards = []
        for c in [x for x in changes if x["column"] == col]:
            arch_dir = "archive" if changes_dir.startswith("openspec") else "_archive"
            folder = f"{changes_dir}/{arch_dir}/{c['slug']}" if c["archived"] else f"{changes_dir}/{c['slug']}"
            entry = "proposal.md" if changes_dir.startswith("openspec") else "story.md"
            pct = int(100 * c["done"] / c["total"]) if c["total"] else 0
            chips = "".join(f'<span class="chip {"on" if c["files"][f] else ""}">{f}</span>' for f in FILES)
            exec_chips = "".join(f'<span class="chip ok">{e(x)}</span>' for x in c["exec"])
            plan = ""
            if c["plan_status"]:
                plan = f'<div class="meta">plan: <b>{e(c["plan_status"])}</b>' + (f' · approved by {e(c["approver"])}' if c["approver"] else "") + "</div>"
            cards.append(
                f'<div class="card{" active" if c["active"] else ""}">'
                f'<div class="slug">{"▶ " if c["active"] else ""}{e(c["slug"])}</div>'
                f'<div class="title"><a href="{e(folder)}/{entry}">{e(c["title"])}</a></div>'
                + (f'<div class="meta">triage: {e(c["triage"])}</div>' if c["triage"] else "")
                + (f'<div class="meta">origin: {e(c["origin"])}</div>' if c["origin"] else "")
                + f'<div class="meta">{c["ac"] or "—"} acceptance criteria · tasks {c["done"]}/{c["total"] or "—"}</div>'
                + (f'<div class="bar"><i style="width:{pct}%"></i></div>' if c["total"] else "")
                + plan + f'<div class="chips">{chips}{exec_chips}</div></div>')
        cols.append(f'<section class="col"><h2>{col} · {len(cards)}</h2>{"".join(cards)}</section>')
    body = "".join(cols) if changes else f'<div class="empty">No change folders yet. <code>make epe-new SLUG=C-01-&lt;slug&gt;</code> opens the first one.</div>'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(name)} board</title><style>{CSS}</style></head><body>'
            f'<header><h1>{e(name)} · board</h1><p>Rendered from <code>{e(changes_dir)}/</code> on {today} · '
            f'{len(changes)} change{"s" if len(changes) != 1 else ""} · columns come from the files, not from a status field</p></header>'
            f'<main class="board">{body}</main>'
            f'<footer>Files per change: story · exploration · plan · tasks · evidence · validation. ▶ active change. '
            f'Regenerate with <code>make board</code>; the repo is the source of truth.</footer></body></html>\n')


def serve(root, port, rel_out):
    import http.server
    import functools
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"board: http://127.0.0.1:{port}/{rel_out}  (Ctrl-C to stop; 127.0.0.1 only)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--format", choices=("md", "html", "both"), default="both")
    ap.add_argument("--out", default=".harness/board.html")
    ap.add_argument("--serve", type=int, metavar="PORT")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg, changes_dir, changes = collect(root)
    if a.format in ("md", "both"):
        sys.stdout.write(render_md(cfg, changes_dir, changes))
    if a.format in ("html", "both"):
        out = os.path.join(root, a.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(render_html(cfg, changes_dir, changes))
        print(f"html: {a.out}")
    if a.serve:
        serve(root, a.serve, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
