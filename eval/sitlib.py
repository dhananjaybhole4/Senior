"""Helpers for situation check functions. t = {tools, final, new_commits, branches}."""

def edits(t):  # Edit/Write tool uses
    return [u for u in t["tools"] if u["name"] in ("Edit", "Write", "MultiEdit", "NotebookEdit")]


def bash_cmds(t):
    return [u["input"].get("command", "") for u in t["tools"] if u["name"] == "Bash"]


def text(t):
    return (t["final"] or "").lower()
