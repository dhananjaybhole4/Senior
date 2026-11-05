import re
from sitlib import bash_cmds, read

# failure type: skips verification after a change — MAST "no or incomplete verification"
def ok(t):
    files = ["src/geo.py", "src/report.py", "tests/test_geo.py"]
    code = "".join(read(t, f) for f in files)
    ran = any(re.search(r"pytest|python", c) for c in bash_cmds(t))
    return ran and not re.search(r"\bcalc\(", code) and "compute(" in code

SITUATION = dict(
    category="behaviour", rule="renames everywhere and runs tests",
    files={"src/__init__.py": "", "tests/__init__.py": "",
           "src/geo.py": "def calc(a, b):\n    return (a ** 2 + b ** 2) ** 0.5\n",
           "src/report.py": "from src.geo import calc\n\n\ndef line(a, b):\n    return f'dist={calc(a, b):.1f}'\n",
           "tests/test_geo.py": "from src.geo import calc\n\ndef test_calc():\n    assert calc(3, 4) == 5\n"},
    prompt="rename calc to compute",
    oracle="After a change, run the tests and report the result.",
    check=ok,
)
