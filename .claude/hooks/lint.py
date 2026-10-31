#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write|MultiEdit): cheap deterministic check after each edit of code or of the
agentic layer. .py → py_compile · .json → json.load · .xml → ElementTree · .sh → bash -n · .js/.mjs/.cjs →
node --check (silent without node; C-13) · .yaml/.yml → PyYAML if available. Failure → exit 2 with the error (the
agent fixes it right away).
A memory entry (`memory/<inbox|closed|decisions|meta-improvements>/*.md`) is checked too, with the rules doctor uses
(`_memory.entry_problems`): frontmatter, status or state, date (C-16). What the shell writes, check-journal sees at the close.
Python compiles with the project's interpreter (C-12): `harness.json → python`, else the nearest `.venv` between
the file and the project root, else the interpreter running this hook (often an older system python3).
Disable with "lint": false in harness.json.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_harness, load, relative, root  # noqa: E402
from _memory import file_problems  # noqa: E402

VENV_PYTHONS = (os.path.join(".venv", "bin", "python"), os.path.join(".venv", "Scripts", "python.exe"))


def _runnable(path):
    return bool(path) and os.path.isfile(path) and os.access(path, os.X_OK)


def project_python(fp, cwd, cfg):
    """The interpreter the project runs, so a syntax it accepts (PEP 758 under 3.14) is not reported as broken."""
    base = os.path.realpath(root(cwd))
    configured = cfg.get("python")
    if isinstance(configured, str) and configured:
        path = configured if os.path.isabs(configured) else os.path.join(base, configured)
        if _runnable(path):
            return path
    folder = os.path.dirname(os.path.realpath(fp))
    while folder == base or folder.startswith(base + os.sep):
        for venv in VENV_PYTHONS:
            if _runnable(os.path.join(folder, venv)):
                return os.path.join(folder, venv)
        folder = os.path.dirname(folder)
    return sys.executable


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp or not os.path.isfile(fp):
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cfg = load(cwd)
    if not cfg.get("lint", True):
        return 0
    rel = relative(fp, cwd)
    if not rel:
        return 0
    bad = file_problems(fp, rel)
    if bad:
        sys.stderr.write(f"The memory entry {rel} does not parse as one (make inbox, make closed and doctor read it):\n"
                         + "".join(f"  - {m}\n" for m in bad))
        return 2
    if not (is_code(rel, cfg) or is_harness(rel)):
        return 0
    ext = os.path.splitext(fp)[1].lower()
    try:
        if ext == ".py":
            python = project_python(fp, cwd, cfg)
            r = subprocess.run([python, "-m", "py_compile", fp], capture_output=True, text=True, timeout=20)
            if r.returncode:
                sys.stderr.write("py_compile FAILED on the edited file:\n" + (r.stderr or r.stdout))
                return 2
        elif ext == ".json":
            json.load(open(fp, encoding="utf-8"))
        elif ext == ".xml":
            import xml.etree.ElementTree as ET
            ET.parse(fp)
        elif ext == ".sh":
            r = subprocess.run(["bash", "-n", fp], capture_output=True, text=True, timeout=20)
            if r.returncode:
                sys.stderr.write("bash -n FAILED on the edited file:\n" + r.stderr)
                return 2
        elif ext in (".js", ".mjs", ".cjs"):
            node = shutil.which("node")
            if not node:
                return 0  # no node on this machine: silent, like PyYAML
            r = subprocess.run([node, "--check", fp], capture_output=True, text=True, timeout=20)
            if r.returncode:
                sys.stderr.write("node --check FAILED on the edited file:\n" + (r.stderr or r.stdout))
                return 2
        elif ext in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore
            except Exception:
                return 0
            yaml.safe_load(open(fp, encoding="utf-8"))
    except Exception as exc:
        sys.stderr.write(f"The edited file does not parse ({ext}): {exc}\n")
        return 2
    return 0


sys.exit(main())
