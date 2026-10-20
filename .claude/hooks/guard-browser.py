#!/usr/bin/env python3
"""PreToolUse hook (Claude in Chrome: navigate, browser_batch): the agent drives the person's REAL browser, with
their open sessions (mail, bank, work). `.claude/settings.json` allows the browser tools without a prompt so the
exploratory pass of /epe-3-execute and /epe-5-apply can run, and this hook is the fence that makes that safe:
navigation only goes to local or development hosts.

Allowed: localhost, 127.0.0.1, [::1], *.localhost, *.test, plus `harness.json → browser_hosts` (exact host, or
".example.com" for a domain and its subdomains, e.g. a staging host). "back"/"forward" pass. In browser_batch every
navigate item is checked. It blocks in BOTH profiles: an allowed tool plus a warning would be no gate at all.
Known limit: it sees URLs typed into navigate, not a link clicked on an allowed page nor `location` set from
javascript_tool. Exit 0 on error (never breaks the flow).
"""
import os
import sys
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load  # noqa: E402
from _harness import read, respond  # noqa: E402

LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")
LOCAL_SUFFIXES = (".localhost", ".test")


def host_of(url):
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return (urlsplit(url).hostname or "").lower().rstrip(".")


def allowed(url, extra):
    if url.strip().lower() in ("back", "forward"):
        return True
    host = host_of(url)
    if not host:
        return False
    if host in LOCAL_HOSTS or host.endswith(LOCAL_SUFFIXES):
        return True
    for entry in extra:
        entry = str(entry).lower().strip()
        if entry.startswith(".") and (host == entry[1:] or host.endswith(entry)):
            return True
        if host == entry:
            return True
    return False


def urls(ev):
    tool = ev["tool"].rsplit("__", 1)[-1]
    inp = ev["input"]
    if tool == "navigate":
        return [inp.get("url") or ""]
    if tool == "browser_batch":
        found = []
        for item in inp.get("actions") or []:
            if isinstance(item, dict) and str(item.get("name", "")).rsplit("__", 1)[-1] == "navigate":
                found.append((item.get("input") or {}).get("url") or "")
        return found
    return []


def main():
    ev = read()
    if not ev or "claude-in-chrome" not in ev["tool"]:
        return 0
    extra = load(ev["cwd"]).get("browser_hosts") or []
    blocked = [u for u in urls(ev) if not allowed(u, extra)]
    if not blocked:
        return 0
    return respond(ev, "block", (
        f"BLOCKED (browser fence). Navigation outside local/dev hosts: {', '.join(blocked)}.\n"
        "The browser tools run without a prompt only for localhost, 127.0.0.1, [::1], *.localhost, *.test and "
        "`harness.json → browser_hosts`. If this host is a development environment of this project, ask the "
        "person you work with to add it to browser_hosts; anything else they open themselves."))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
