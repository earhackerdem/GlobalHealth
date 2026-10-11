#!/usr/bin/env python3
"""Metrics extractor for a session transcript, for `/session-retro`.

Why: a retro done "from memory" measures what the agent remembers, which is exactly what it remembers worst
(the loops it ran). This pulls the MECHANICAL signals out of the transcript (repeated commands, re-read files,
user interruptions, hook blocks, gates run) and leaves JUDGEMENT to the skill. The script measures, the
person decides. It does not say whether anything was good or bad, proposes nothing, and does not read the
content of the answers. It counts.

Usage:
    python3 scripts/retro-transcript.py <path-to-.jsonl>
    python3 scripts/retro-transcript.py --find <session-id>   # resolves the path

How the transcript is located (and why NOT "the most recent"): projects live in
~/.claude/projects/<cwd-with-slashes-as-dashes>/<session-id>.jsonl. Taking the newest .jsonl is a real race
condition: measured in origin, two concurrent sessions swapped first place within 10 seconds. The session id is
the reliable anchor.
"""
import json
import os
import re
import sys
from collections import Counter

# Read-only commands: repeating them is exploring, not looping.
LECTURA = re.compile(r"^\s*(ls|cat|head|tail|wc|grep|rg|find|git (log|show|status|diff|branch))\b")

# A REAL gate invocation: at the start of the command or after a shell separator. Otherwise the `make …`
# travelling inside a heredoc that writes documentation gets counted, and the tally lies.
GATE = re.compile(r"(?:^|[;&|]\s*|\n\s*)(?:make|just)\s+([a-z][a-z-]+)")


def eventos(ruta):
    with open(ruta, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                yield json.loads(linea)
            except Exception:
                continue


def bloques(evento, tipo):
    msg = evento.get("message") or evento
    contenido = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(contenido, list):
        for b in contenido:
            if isinstance(b, dict) and b.get("type") == tipo:
                yield b


def texto_usuario(evento):
    msg = evento.get("message") or {}
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return None
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return None


def analizar(ruta):
    herramientas = Counter()
    comandos = Counter()
    leidos = Counter()
    escritos = Counter()
    skills = []
    gates = []
    interrupciones = 0
    bloqueos_hook = []
    mensajes_usuario = 0

    for ev in eventos(ruta):
        for tu in bloques(ev, "tool_use"):
            nombre = tu.get("name") or "?"
            entrada = tu.get("input") or {}
            herramientas[nombre] += 1
            if nombre == "Bash":
                cmd = (entrada.get("command") or "").strip()
                if cmd:
                    comandos[cmd] += 1
                    for g in GATE.findall(cmd):
                        gates.append(g)
            elif nombre == "Skill":
                s = entrada.get("skill")
                if s:
                    skills.append(s)
            elif nombre == "Read":
                p = entrada.get("file_path")
                if p:
                    leidos[os.path.basename(p)] += 1
            elif nombre in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                p = entrada.get("file_path")
                if p:
                    escritos[os.path.basename(p)] += 1

        t = texto_usuario(ev)
        if t:
            mensajes_usuario += 1
            if "[Request interrupted by user]" in t:
                interrupciones += 1
            if "Stop hook feedback" in t or "hook blocking error" in t:
                bloqueos_hook.append(t.strip().splitlines()[0][:120])

    return {
        "herramientas": herramientas,
        "comandos": comandos,
        "leidos": leidos,
        "escritos": escritos,
        "skills": skills,
        "gates": gates,
        "interrupciones": interrupciones,
        "bloqueos_hook": bloqueos_hook,
        "mensajes_usuario": mensajes_usuario,
    }


def resolver(id_sesion):
    """Path of the .jsonl from the session id, searching every project."""
    base = os.path.expanduser("~/.claude/projects")
    for proyecto in os.listdir(base):
        cand = os.path.join(base, proyecto, f"{id_sesion}.jsonl")
        if os.path.exists(cand):
            return cand
    return None


# Why this function exists: the report LIED, silently and in green. Measured in origin: it printed
# "Files edited: none" with 20 files changed on the branch, because the counters look at Edit|Write and Read,
# and that session made 107 Bash calls and zero Edit/Write (bypass mode writes with cat/sed/heredocs).
# Two of the five retro lenses come from those counters, so a retro could conclude "clean session" from a
# structurally blind report. Deliberately NOT fixed by parsing the Bash command (each unforeseen way of writing
# would be a false negative). It does the only honest thing: declares that it cannot see, and says where the
# data is.
UMBRAL_BASH = 10


def avisa_punto_ciego(d) -> None:
    bash = d["herramientas"].get("Bash", 0)
    if d["escritos"] or bash < UMBRAL_BASH:
        return
    print(
        f"\n  ⚠ BLIND SPOT: \"none\" here does NOT mean nothing was edited.\n"
        f"    This session made {bash} Bash calls and 0 Edit/Write, so if it wrote files it did so\n"
        f"    with `cat`/`sed`/heredoc, which the transcript does not record.\n"
        f"    Same for \"files re-read\": a `cat` does not count as Read.\n"
        f"    The real data is in git, not here:  git diff --name-only <base>...HEAD"
    )


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip().split("Uso:")[1].strip(), file=sys.stderr)
        return 2
    if args[0] == "--find":
        ruta = resolver(args[1]) if len(args) > 1 else None
        if not ruta:
            print(f"✗ no transcript found for session {args[1] if len(args) > 1 else ''}", file=sys.stderr)
            return 1
    else:
        ruta = args[0]
    if not os.path.exists(ruta):
        print(f"✗ does not exist: {ruta}", file=sys.stderr)
        return 1

    d = analizar(ruta)
    print(f"# Mechanical retro of {os.path.basename(ruta)}")
    print(f"\nUser messages: {d['mensajes_usuario']} · interruptions: {d['interrupciones']}")

    print("\n## Tools")
    for n, c in d["herramientas"].most_common():
        print(f"  {c:4d}  {n}")

    print("\n## Skills loaded")
    print("  " + (", ".join(dict.fromkeys(d["skills"])) if d["skills"] else "NONE ← strong signal if code or content was edited"))

    print("\n## Gates run")
    g = Counter(d["gates"])
    print("  " + (", ".join(f"{k}×{v}" for k, v in g.most_common()) if g else "none"))

    print("\n## Possible loops — NON-trivial repeated commands")
    repes = [(n, c) for n, c in d["comandos"].most_common() if c > 1 and not LECTURA.match(n)]
    if not repes:
        print("  none")
    for n, c in repes[:10]:
        print(f"  ×{c}  {n[:110]}")

    print("\n## Possible loops — files re-read 3+ times")
    rel = [(f, c) for f, c in d["leidos"].most_common() if c >= 3]
    print("  " + ("none" if not rel else ", ".join(f"{f}×{c}" for f, c in rel)))

    print("\n## Files edited (times)")
    print("  " + (", ".join(f"{f}×{c}" for f, c in d["escritos"].most_common(12)) if d["escritos"] else "none"))
    avisa_punto_ciego(d)

    print("\n## Hook blocks received")
    if not d["bloqueos_hook"]:
        print("  none")
    for b in d["bloqueos_hook"]:
        print(f"  · {b}")
    if len(d["bloqueos_hook"]) >= 2:
        print("  ⚠ two or more blocks: check whether the gate was right or whether it is friction that teaches to ignore it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
