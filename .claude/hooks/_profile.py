"""Shared reader of the local profile (.claude/profile.env). Imported by the hooks.

PROFILE=supervised  -> guardrails BLOCK (no code edits without an approved plan; no push to protected
                       branches, no force, no merge). Delivery ends at the PR.
PROFILE=autonomous  -> the same guardrails only WARN.
Without the file, supervised is assumed (the safe mode). HARNESS_PROFILE in the environment overrides
the file (for tests and CI). The names describe the session's working mode, not the person's level.
"""
import os

from _config import root

BLOCKS = "supervised"
WARNS = "autonomous"


def read_profile(cwd):
    """dict with NAME, ROLE, PROFILE. Empty (except PROFILE) if there is no file."""
    forced = (os.environ.get("HARNESS_PROFILE") or "").strip().lower()
    if forced in (BLOCKS, WARNS):
        return {"PROFILE": forced}
    path = os.path.join(root(cwd), ".claude", "profile.env")
    data = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    data[k.strip().upper()] = v.strip().strip('"').strip("'")
        except Exception:
            data = {}
    profile = (data.get("PROFILE") or BLOCKS).lower()
    data["PROFILE"] = profile if profile in (BLOCKS, WARNS) else BLOCKS
    return data


def blocks(profile):
    return profile != WARNS
