"""IDE-independent hook input/output. Imported by the PreToolUse hooks.

Recognised input shapes (stdin JSON):
  - Claude Code and VS Code (native hooks): {"tool_name", "tool_input": {...}, "cwd", "session_id"}
  - Copilot CLI:                            {"toolName", "toolArgs": "<json>", "cwd"}
  - Cursor beforeShellExecution:            {"command", "cwd"}
  - Cursor afterFileEdit:                   {"file_path", "edits"}
Output: each harness gets its own blocking JSON; exit is always 0 (the block travels in the JSON).
"""
import json
import os
import sys

EDIT_KEYS = {"file_path", "filePath", "path", "notebook_path"}


def read():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CURSOR_PROJECT_DIR") or os.getcwd()
    if "toolName" in data:
        args = data.get("toolArgs") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {"command": args}
        return {"harness": "copilot", "tool": data["toolName"], "input": args, "cwd": cwd,
                "sid": data.get("sessionId") or "nosession", "transcript": data.get("transcript_path") or ""}
    if "tool_name" in data:
        return {"harness": "claude", "tool": data["tool_name"], "input": data.get("tool_input") or {}, "cwd": cwd,
                "sid": data.get("session_id") or "nosession", "transcript": data.get("transcript_path") or "",
                "agent": data.get("agent_type") or ""}
    if "command" in data:
        return {"harness": "cursor", "tool": "shell", "input": {"command": data["command"]}, "cwd": cwd,
                "sid": data.get("conversation_id") or "nosession", "transcript": ""}
    if "file_path" in data:
        return {"harness": "cursor", "tool": "edit", "input": {"file_path": data["file_path"]}, "cwd": cwd,
                "sid": data.get("conversation_id") or "nosession", "transcript": ""}
    return None


def role(ev):
    """Role of the actor: the subagent's `agent_type` (Claude Code) or HARNESS_ROLE in the environment
    (other harnesses, sequential sessions, tests). '' when there is none."""
    return ((ev.get("agent") or "") or os.environ.get("HARNESS_ROLE") or "").strip().lower()


def command(ev):
    """Shell command if the tool is a terminal; '' otherwise."""
    inp = ev["input"]
    if any(k in inp for k in EDIT_KEYS):
        return ""
    c = inp.get("command")
    return c if isinstance(c, str) else ""


def file_path(ev):
    inp = ev["input"]
    for k in ("file_path", "filePath", "notebook_path", "path"):
        v = inp.get(k)
        if isinstance(v, str) and v:
            return v
    return ""


def respond(ev, level, text, event="PreToolUse"):
    """level: 'block' | 'warn'. Writes the JSON each harness understands and returns exit code 0."""
    sys.stderr.write(text.rstrip("\n") + "\n")
    h = ev["harness"]
    if h == "cursor":
        if level == "block":
            print(json.dumps({"permission": "deny", "user_message": text, "agent_message": text}, ensure_ascii=False))
        else:
            print(json.dumps({"permission": "ask", "user_message": text, "agent_message": text}, ensure_ascii=False))
        return 0
    if h == "copilot":
        if level == "block":
            print(json.dumps({"permissionDecision": "deny", "permissionDecisionReason": text}, ensure_ascii=False))
        else:
            print(json.dumps({"additionalContext": text}, ensure_ascii=False))
        return 0
    out = {"hookEventName": event}
    if level == "block":
        out.update({"permissionDecision": "deny", "permissionDecisionReason": text})
    else:
        out["additionalContext"] = text
    print(json.dumps({"hookSpecificOutput": out}, ensure_ascii=False))
    return 0
