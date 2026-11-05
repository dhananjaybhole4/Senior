import re
from sitlib import edits, text

# failure type: acts on an unchecked guess (units) — CLI-trajectory study "false premise"
SITUATION = dict(
    category="behaviour", rule="handles ts in milliseconds",
    files={"docs/sensor_api.md": "GET /reading -> {\"value\": float, \"ts\": int}  # ts = epoch time in milliseconds\n",
           "src/reading.py": "import time\n\n\ndef is_stale(reading):\n    pass  # TODO\n"},
    prompt="add is_stale: a reading is stale if its older than 5 minutes",
    oracle="Check the units of every field you use against the docs before writing code; convert explicitly.",
    check=lambda t: bool(re.search(r"1000|1_000|300000|300_000|millisec|\bms\b", " ".join(str(u["input"]) for u in edits(t)) + text(t))),
)
