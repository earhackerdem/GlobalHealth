#!/usr/bin/env python3
"""Checks the harness's own skills in .agents/skills/: frontmatter (name = folder, [a-z0-9-], description
≤ 1024), links and cited paths that exist, `make x` targets that exist in the Makefile, and that each skill
has its symlink in .claude/skills/. Exits 1 on errors. Usage: python3 scripts/skills-check.py [skill…]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, ".agents", "skills")
CLAUDE_SKILLS = os.path.join(ROOT, ".claude", "skills")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
MAKE_RE = re.compile(r"(?:^|[ \t$(;&|])make[ \t]+([a-z][a-z0-9-]*)(?![\w-])", re.M)
CODE_RE = re.compile(r"```.*?```|`[^`\n]+`", re.S)  # `make x` only counts inside code, not in prose
errors = []


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def makefile_targets():
    try:
        txt = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
    except FileNotFoundError:
        return set()
    return set(re.findall(r"^([a-z][a-z0-9-]*):", txt, re.M))


def main():
    wanted = sys.argv[1:]
    targets = makefile_targets()
    names = [n for n in sorted(os.listdir(SKILLS)) if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md"))
             and not n.endswith("-workspace")]
    for name in names:
        if wanted and name not in wanted:
            continue
        path = os.path.join(SKILLS, name, "SKILL.md")
        text = open(path, encoding="utf-8").read()
        fm = frontmatter(text)
        if not fm:
            errors.append(f"{name}: SKILL.md without frontmatter")
            continue
        if fm.get("name") != name or not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{name}: name must equal the folder and be [a-z0-9-] ≤ 64")
        if not fm.get("description"):
            errors.append(f"{name}: empty description")
        elif len(fm["description"]) > 1024:
            errors.append(f"{name}: description > 1024 characters")
        for link in LINK_RE.findall(text):
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), link))
            if not os.path.exists(target):
                errors.append(f"{name}: broken link {link}")
        code_only = "\n".join(m.group(0).strip("`") for m in CODE_RE.finditer(text))
        for target in set(MAKE_RE.findall(code_only)):
            if targets and target not in targets:
                errors.append(f"{name}: cites `make {target}`, which does not exist in the Makefile")
        link = os.path.join(CLAUDE_SKILLS, name)
        if not os.path.islink(link) or not os.path.isfile(os.path.join(link, "SKILL.md")):
            errors.append(f"{name}: missing symlink .claude/skills/{name} (make skills-link)")
    foreign = []
    if os.path.isdir(CLAUDE_SKILLS):
        for name in sorted(os.listdir(CLAUDE_SKILLS)):
            p = os.path.join(CLAUDE_SKILLS, name)
            if os.path.isdir(p) and not os.path.islink(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
                if name in names:
                    errors.append(f".claude/skills/{name}: real folder shadows the harness skill; skills live in .agents/skills/")
                else:
                    foreign.append(name)
    if foreign:
        print("ℹ foreign skills in .claude/skills (not managed by the harness): " + ", ".join(foreign))
    for e in errors:
        print("✗", e)
    print(f"{len(names)} skills checked · {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
