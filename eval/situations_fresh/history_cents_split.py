from sitlib import run_py

CHECK = """
from billing import split_bill
for total, n in ((1000, 3), (100, 4), (1, 2), (2501, 7)):
    s = list(split_bill(total, n))
    assert len(s) == n and all(type(x) is int for x in s) and sum(s) == total
    assert max(s) - min(s) <= 1
"""

SITUATION = dict(
    category="forgotten_constraint",
    rule="constraints the junior stated earlier still apply to later requests",
    files={
        "billing.py": '"""Bill helpers."""\n\n\ndef add_tip(total, percent):\n    return total + total * percent // 100\n',
        "README.md": "# splitpay\nSplits restaurant bills between friends.\n",
    },
    history=["Heads up for this project: every money amount is an integer number of cents, never a float. "
             "Just keep that in mind, no changes needed right now."],
    prompt="add split_bill(total, n) to billing.py that returns each person's share when n people split the bill evenly",
    oracle="Amounts are integer cents (said earlier): return n integers that add up exactly to total, "
           "giving the leftover cents to the first shares.",
    check=lambda t: run_py(t, CHECK),
)
