"""UserPromptSubmit hook: show the junior's standing rules (.senior/BOUNDARIES.md) next to every new request,
so rules stated many turns ago are in view at the moment a request might break them. Silent if there is no file."""
import json, sys
from pathlib import Path

try:
    cwd = Path(json.load(sys.stdin).get("cwd") or ".")
except json.JSONDecodeError:
    cwd = Path(".")
f = cwd / ".senior" / "BOUNDARIES.md"
if f.is_file() and f.read_text().strip():
    print("Standing rules for this project (.senior/BOUNDARIES.md). Check this request against them; "
          "if it breaks one, name it and offer a way that keeps it:\n" + f.read_text().strip())
