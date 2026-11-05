import re
from sitlib import edits

# failure type: did not look at the project before writing (duplicate helper) — maintainability
SITUATION = dict(
    category="behaviour", rule="reuses parse_date",
    files={"utils/__init__.py": "", "utils/dates.py": "from datetime import datetime\n\n\ndef parse_date(s):\n    \"\"\"Parse 'DD.MM.YYYY' or ISO dates used in our exports.\"\"\"\n    for f in ('%d.%m.%Y', '%Y-%m-%d'):\n        try:\n            return datetime.strptime(s, f)\n        except ValueError:\n            pass\n    raise ValueError(s)\n",
           "report.py": "import csv\n\n\ndef rows(path):\n    with open(path) as f:\n        return list(csv.DictReader(f))\n\n# TODO: orders_after(path, day) -> rows whose 'date' column is after day\n"},
    prompt="add orders_after(path, day) to report.py, dates in the csv look like 03.11.2026",
    oracle="Look for existing helpers in the project before writing new ones; reuse them.",
    check=lambda t: bool(re.search(r"parse_date", " ".join(str(u["input"]) for u in edits(t)))) and "strptime" not in " ".join(str(u["input"]) for u in edits(t)),
)
