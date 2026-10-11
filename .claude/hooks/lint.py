#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write|MultiEdit): cheap deterministic check after each edit of code or of the
agentic layer. .py → py_compile · .json → json.load · .xml → ElementTree · .sh → bash -n · .yaml/.yml →
PyYAML if available. Failure → exit 2 with the error (the agent fixes it right away).
Disable with "lint": false in harness.json.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import is_code, is_harness, load, relative  # noqa: E402


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
    if not rel or not (is_code(rel, cfg) or is_harness(rel)):
        return 0
    ext = os.path.splitext(fp)[1].lower()
    try:
        if ext == ".py":
            r = subprocess.run([sys.executable, "-m", "py_compile", fp], capture_output=True, text=True, timeout=20)
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
