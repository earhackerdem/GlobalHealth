"""Repo memory, one file per entry, read by directory. Imported by the hooks and (through sys.path) the scripts.

Layout:
  memory/inbox/YYYY-MM-DD-slug.md               status: open | snoozed [YYYY-MM-DD] | done | discarded
  memory/closed/YYYY-MM-DD-slug.md              state: frozen | reopenable | deferred | partial
  memory/decisions/D<n>-slug.md                 id: D<n> · status: accepted | revised | superseded | proposed | discarded
  memory/meta-improvements/YYYY-MM-DD-slug.md   status: proposed | accepted | rejected | applied
  memory/research/<topic>.md                    no frontmatter; the file name is the old `research.md#<topic>` anchor
  memory/<kind>/README.md                       what the kind is and how to write an entry (never an entry)
  changelog.d/YYYY-MM-DD-slug.md                one fragment per archived change; `_legacy.md` holds the old body

Why: two branches that each append a row to the same file conflict on merge; two branches that each add a file
never do. Indexes are rendered on demand (`make inbox`, `make closed`, `make changelog`), never committed.

Frontmatter is plain `key: value` lines between two `---` lines (no YAML dependency). The first non-empty line of
the body is the entry's title. While a project still has the old single files (`memory/inbox.md`…), entries()
parses them as well, so every reader works before and after `make memory-migrate`.
"""
import datetime
import os
import re
import unicodedata

KINDS = ("inbox", "closed", "decisions", "meta-improvements", "research")
STATUSES = {
    "inbox": ("open", "snoozed", "done", "discarded"),
    "closed": ("frozen", "reopenable", "deferred", "partial"),
    "decisions": ("accepted", "revised", "superseded", "proposed", "discarded"),
    "meta-improvements": ("proposed", "accepted", "rejected", "applied"),
}
STATUS_KEY = {"closed": "state"}
STATE_ICON = {"frozen": "🔒", "reopenable": "↩️", "deferred": "⏸️", "partial": "🧩"}
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FRONT = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
SEP_ROW = re.compile(r"^\|[\s\-:|]+\|$")
BULLET = re.compile(r"^- \[(\d{4}-\d{2}-\d{2})([^\]]*)\]")
DEFAULT_HEADERS = {
    "inbox": ["Date", "What", "Why it matters", "Status"],
    "closed": ["Date", "Finding", "Verdict and why", "State", "Anchor (journal: date · title)"],
    "meta-improvements": ["Date", "Proposal", "Verdict", "Why", "Where it lives (PR, file)"],
}


class Entry:
    """One memory record. `units` are the source fragments (lines or table cells) it carries, for the
    migration's line-coverage check; `note` says how a status was inferred, for the dry run."""

    def __init__(self, kind, meta, body, path=None, stem=None, units=None, note=""):
        self.kind, self.meta, self.body, self.path = kind, meta, body, path
        self.stem, self.units, self.note = stem, units or [], note

    @property
    def date(self):
        return self.meta.get("date", "")

    @property
    def status(self):
        raw = self.meta.get(STATUS_KEY.get(self.kind, "status"), "").strip()
        return raw.split()[0].lower() if raw else ""

    @property
    def title(self):
        for line in self.body.splitlines():
            s = line.strip()
            if s:
                s = re.sub(r"^#+\s*", "", s)
                s = re.sub(r"^-\s+", "", s)
                return re.sub(r"^\[\d{4}-\d{2}-\d{2}[^\]]*\]\s*", "", s)
        return ""

    def text(self):
        return dump(self.meta, self.body)


# ---------- files ----------

def parse(text):
    """(meta, body) of an entry file."""
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip():
            meta[k.strip()] = v.strip()
    return meta, text[m.end():].lstrip("\n")


def dump(meta, body):
    body = body.strip("\n") + "\n"
    if not meta:
        return body
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in meta.items()) + "---\n\n" + body


def memory_dir(root):
    return os.path.join(root, "memory")


def monolith(root, kind):
    return os.path.join(root, "memory", f"{kind}.md")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def slugify(text, words=6, limit=50):
    text = re.sub(r"\*\*|`|\[\[|\]\]|<[^>]+>", "", text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    parts = re.findall(r"[a-z0-9]+", text)[:words]
    return "-".join(parts)[:limit].strip("-") or "entry"


def load_dir(root, kind):
    d = os.path.join(memory_dir(root), kind)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md") or name == "README.md" or name.startswith(("_", ".")):
            continue
        path = os.path.join(d, name)
        meta, body = parse(read(path))
        out.append(Entry(kind, meta, body, path=path, stem=name[:-3]))
    return out


def key(entry):
    """Identity of a record across layouts: its date plus its normalised title."""
    return entry.date + "|" + re.sub(r"\W+", "", entry.title.lower())[:90]


def entries(root, kind):
    """Every entry of a kind: the directory's, plus the old single file's while it still exists."""
    have = load_dir(root, kind)
    path = monolith(root, kind)
    if os.path.isfile(path):
        seen = {key(e) for e in have}
        _, old = parse_monolith(read(path), kind)
        have += [e for e in old if key(e) not in seen]
    return have


# ---------- the old single files ----------

def _cells(line):
    s = line.strip()[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", s)]


def inbox_status(text, section, bullet):
    if "✅" in text:
        return "done"
    if "❌" in text:
        return "discarded"
    if "💤" in text:
        m = DATE.search(text.split("💤", 1)[1])
        if m and section == "closed" and m.group(0) <= datetime.date.today().isoformat():
            return "snoozed"  # under Closed a past date is when it was parked, not when it comes back
        return f"snoozed {m.group(0)}" if m else "snoozed"
    if section == "closed" and not bullet:
        return "done"
    return "open"


def closed_state(text):
    for icon, state in (("🔒", "frozen"), ("↩", "reopenable"), ("⏸", "deferred"), ("🧩", "partial")):
        if icon in text:
            return state
    low = text.lower()
    for state in STATUSES["closed"]:
        if state in low:
            return state
    return (re.findall(r"[a-z]+", low) or ["unknown"])[0]


def meta_status(text):
    low = text.lower()
    for needle, status in (("❌", "rejected"), ("reject", "rejected"), ("rechaz", "rejected"),
                           ("descart", "rejected"), ("appli", "applied"), ("aplicad", "applied"),
                           ("accept", "accepted"), ("aceptad", "accepted"), ("propos", "proposed"),
                           ("propuest", "proposed")):
        if needle in low:
            return status
    return "proposed"


def _row_entry(kind, section, header, cells):
    date, title = cells[0], cells[1] if len(cells) > 1 else ""
    lines = [title]
    for i, value in enumerate(cells[2:], start=2):
        if value:
            label = header[i] if i < len(header) else ""
            lines += ["", f"**{label}:** {value}" if label else value]
    status_text = " ".join(c for h, c in zip(header, cells)
                           if re.search(r"status|state|closure|verdict|estado|cierre|veredicto", h, re.I)) \
        or (cells[-1] if len(cells) > 2 else "")
    meta, note = {"date": date}, ""
    if kind == "inbox":
        meta["status"] = inbox_status(status_text, section, False)
    elif kind == "closed":
        meta["state"] = closed_state(status_text)
        anchor = cells[4] if len(cells) > 4 else ""
        if anchor:
            meta["anchor"] = anchor.replace("\n", " ")
    elif kind == "meta-improvements":
        meta["status"] = meta_status(status_text)
    return Entry(kind, meta, "\n".join(lines), units=[c for c in cells if c], note=note)


def _bullet_entry(kind, section, block, m):
    body = [block[0][2:]] + [ln[2:] if ln.startswith("  ") else ln.strip() for ln in block[1:]]
    text = "\n".join(body)
    meta, note = {"date": m.group(1)}, ""
    if kind == "inbox":
        meta["status"] = inbox_status(text, section, True)
        if section == "closed" and meta["status"] == "open":
            note = "a bullet under `## Closed` with no ✅/❌/💤: kept open (the old hook never showed it)"
    elif kind == "closed":
        meta["state"] = closed_state(text)
    elif kind == "meta-improvements":
        meta["status"] = meta_status(m.group(2) or text)
    return Entry(kind, meta, text, units=[ln for ln in block if ln.strip()], note=note)


def _parse_rows(text, kind):
    readme, out = [], []
    lines = text.splitlines()
    section, header, legend, prev_table = "", None, False, False
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        is_table = s.startswith("|")
        if line.startswith("## "):
            name = s[3:].strip().lower()
            if name in ("open", "closed", "abierto", "abiertos", "cerrado", "cerrados"):
                section = "closed" if name.startswith(("closed", "cerrad")) else "open"
            else:
                readme.append(line)
            i += 1
            prev_table = False
            continue
        if is_table:
            if SEP_ROW.match(s):
                if legend:
                    readme.append(line)
            else:
                cells = _cells(s)
                if DATE.fullmatch(cells[0]):
                    out.append(_row_entry(kind, section, header or DEFAULT_HEADERS.get(kind, []), cells))
                    legend = False
                elif cells[0].lower() in ("date", "fecha"):
                    header, legend = cells, False
                else:
                    if not prev_table:
                        legend = True
                    readme.append(line)
            prev_table = True
            i += 1
            continue
        prev_table = False
        m = BULLET.match(line)
        if m:
            block = [line]
            i += 1
            while i < len(lines) and lines[i][:1] in (" ", "\t") and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append(_bullet_entry(kind, section, block, m))
            continue
        legend = False
        readme.append(line)
        i += 1
    return readme, out


def _parse_sections(text, kind):
    readme, out, cur = [], [], None
    for line in text.splitlines():
        start = None
        if kind == "decisions":
            m = re.match(r"^## (D\d+)\b\s*[—–-]*\s*(.*)", line)
            if m:
                start = (m.group(1), slugify(m.group(2)))
        else:
            m = re.match(r"^(##|###) (.*)", line)
            if m and not m.group(2).strip().startswith("<"):
                anchor = re.search(r'<a id="([^"]+)"', m.group(2))
                if anchor:
                    start = (None, anchor.group(1))
                elif m.group(1) == "##":
                    start = (None, slugify(m.group(2)))
        if start:
            cur = {"id": start[0], "slug": start[1], "lines": [line]}
            out.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
        else:
            readme.append(line)
    entries_ = []
    for sec in out:
        body = "\n".join(sec["lines"]).strip("\n")
        meta, stem = {}, sec["slug"]
        if kind == "decisions":
            head = "\n".join(sec["lines"][:6])
            st = re.search(r"\*\*Status:\*\*\s*([A-Za-z]+)", head)
            dt = DATE.search(head)
            meta = {"id": sec["id"], "date": dt.group(0) if dt else "",
                    "status": st.group(1).lower() if st else "accepted"}
            stem = f"{sec['id']}-{sec['slug']}"
        entries_.append(Entry(kind, meta, body, stem=stem, units=[ln for ln in sec["lines"] if ln.strip()]))
    return readme, entries_


def parse_monolith(text, kind):
    """(readme_lines, entries) of an old single file. Lines that are neither an entry nor table structure
    (the title, the legend, stray prose) come back as readme_lines, so nothing is lost."""
    if kind in ("decisions", "research"):
        return _parse_sections(text, kind)
    return _parse_rows(text, kind)


# ---------- readers ----------

def clean(s, n=None):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\[\[(.+?)\]\]", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s if n is None or len(s) <= n else s[: n - 1] + "…"


def inbox(root, today=None):
    """{'open': [...], 'snoozed': [...], 'closed': [...]}: (date, title, until, entry); open oldest first."""
    today = today or datetime.date.today()
    out = {"open": [], "snoozed": [], "closed": []}
    for e in entries(root, "inbox"):
        st = e.status or "open"
        raw = e.meta.get("status", "")
        if st in ("done", "discarded"):
            out["closed"].append((e.date, e.title, None, e))
            continue
        if st == "snoozed":
            m = DATE.search(raw)
            until = None
            if m:
                try:
                    until = datetime.date.fromisoformat(m.group(0))
                except ValueError:
                    until = None
            if until is None or until > today:
                out["snoozed"].append((e.date, e.title, until, e))
                continue
            out["open"].append((e.date, e.title, until, e))
            continue
        out["open"].append((e.date, e.title, None, e))
    out["open"].sort(key=lambda r: r[0])
    out["snoozed"].sort(key=lambda r: str(r[2] or "9999"))
    return out


def readme_title(root, kind):
    path = os.path.join(memory_dir(root), kind, "README.md")
    if os.path.isfile(path):
        for line in read(path).splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return ""


def render_closed(root):
    """The closed-verdicts index as one document, to paste literally into a review prompt."""
    readme = os.path.join(memory_dir(root), "closed", "README.md")
    parts = [read(readme).strip()] if os.path.isfile(readme) else ["# Closed — review verdicts already triaged"]
    for e in entries(root, "closed"):
        rest = e.body.split("\n", 1)[1].strip() if "\n" in e.body else ""
        head = f"### {e.title}\n{STATE_ICON.get(e.status, '')} {e.status} · {e.date}".rstrip()
        if e.meta.get("anchor"):
            head += f" · {e.meta['anchor']}"
        parts.append(head + ("\n\n" + rest if rest else ""))
    return "\n\n".join(parts) + "\n"


def closed_markers(root):
    """What a review prompt must contain (any one of them) to prove it carries the index: the index's title
    and the first frozen verdict's title. Empty when there are no verdicts yet."""
    marks = []
    title = readme_title(root, "closed")
    if title:
        marks.append(title)
    elif os.path.isfile(monolith(root, "closed")):
        for line in read(monolith(root, "closed")).splitlines():
            if line.startswith("# "):
                marks.append(line[2:].strip())
                break
    found = entries(root, "closed")
    if not found:
        return []
    frozen = [e for e in found if e.status == "frozen"]
    if frozen:
        marks.append(frozen[0].title)
    return [m for m in marks if m]


def render_changelog(root):
    d = os.path.join(root, "changelog.d")
    legacy = os.path.join(d, "_legacy.md")
    title, rest = "# Changelog", ""
    if os.path.isfile(legacy):
        lines = read(legacy).splitlines()
        if lines and lines[0].startswith("# "):
            title, lines = lines[0], lines[1:]
        rest = "\n".join(lines).strip("\n")
    frags = sorted((f for f in os.listdir(d) if f.endswith(".md") and f not in ("README.md", "_legacy.md")),
                   reverse=True) if os.path.isdir(d) else []
    parts = [title] + [read(os.path.join(d, f)).strip("\n") for f in frags] + ([rest] if rest else [])
    return "\n\n".join(parts) + "\n"


def decision_ids(root):
    """[(n, where)] for every decision id, duplicates included."""
    out = []
    for e in entries(root, "decisions"):
        m = re.match(r"D(\d+)$", e.meta.get("id", "")) or re.match(r"D(\d+)\b", e.stem or "")
        if m:
            out.append((int(m.group(1)), e.path or "memory/decisions.md"))
    return out


def problems(root):
    """[(path, message)]: duplicate decision ids, unknown statuses, missing dates, monoliths left over."""
    out = []
    seen = {}
    for n, where in decision_ids(root):
        if n in seen:
            out.append((where, f"D{n} also in {os.path.relpath(seen[n], root)}: two branches took the same id "
                               f"(`make decision-next` gives the next free one)"))
        else:
            seen[n] = where
    for kind, allowed in STATUSES.items():
        for e in load_dir(root, kind):
            rel = os.path.relpath(e.path, root)
            if e.status not in allowed:
                out.append((rel, f"unknown {STATUS_KEY.get(kind, 'status')} `{e.status or '(none)'}` "
                                 f"(allowed: {' | '.join(allowed)})"))
            if kind != "decisions" and not DATE.fullmatch(e.date):
                out.append((rel, "frontmatter without `date: YYYY-MM-DD`"))
    for kind in KINDS:
        if os.path.isfile(monolith(root, kind)):
            out.append((f"memory/{kind}.md", "old single file: run `make memory-migrate` (one file per entry)"))
    return out
