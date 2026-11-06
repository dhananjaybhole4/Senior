"""SessionStart hook: print Senior's every-turn rules so they apply without the junior typing /senior.
One source of truth: the "Rules (every turn)" section of skills/senior/SKILL.md."""
import re
from pathlib import Path

skill = (Path(__file__).resolve().parent.parent / "skills" / "senior" / "SKILL.md").read_text()
m = re.search(r"^## Rules \(every turn\)\n(.*?)(?=^## )", skill, re.S | re.M)
if not m:
    raise SystemExit("primer: 'Rules (every turn)' section not found in SKILL.md")
print("Senior is active. Apply these rules to every request in this session:\n" + m.group(1).strip())
