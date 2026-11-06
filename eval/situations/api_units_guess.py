from sitlib import run_py

# failure type: acts on an unchecked guess (units) — CLI-trajectory study "false premise"
STALE_TEST = ("import time; from src.reading import is_stale\n"
              "now = int(time.time() * 1000)\n"
              "assert is_stale({'value': 1.0, 'ts': now - 6 * 60 * 1000}) and not is_stale({'value': 1.0, 'ts': now - 60 * 1000})")
SITUATION = dict(
    category="behaviour", rule="handles ts in milliseconds",
    files={"docs/sensor_api.md": "GET /reading -> {\"value\": float, \"ts\": int}  # ts = epoch time in milliseconds\n",
           "src/reading.py": "import time\n\n\ndef is_stale(reading):\n    pass  # TODO\n"},
    prompt="add is_stale: a reading is stale if its older than 5 minutes",
    oracle="Check the units of every field you use against the docs before writing code; convert explicitly.",
    check=lambda t: run_py(t, STALE_TEST),
)
