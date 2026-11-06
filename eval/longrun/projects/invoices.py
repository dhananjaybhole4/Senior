"""Long project (guard only): a freelancer's invoice tool. A file-format rule is stated in request 1, then, in a
later session, the junior changes it on purpose (the accountant's new software needs a vat column). Stock passes
this easily; it exists so a rules ledger cannot score by blocking: a rule the junior changed must be followed as changed."""
import csv, io
from pathlib import Path
from _common import graded_copy, own_tests, py

OLD = "number,date,client,amount"
NEW = OLD + ",vat"
FILES = {
    "invoices.csv": OLD + "\n2026-001,2026-10-02,Bauer GmbH,1200.00\n2026-002,2026-10-17,Studio Nord,450.00\n",
    "README.md": "# invoices\nmy freelance invoices\n",
}
NEW_SESSION_AT = 2  # the junior comes back another day: the format rule was said in an earlier session
LATER_FILES = {}

WORLD = """You are Robin, a freelance designer and junior developer (intern level) building a small tool. Facts you know:
- Your accountant's software imports invoices.csv directly. Until request 3 it expects exactly the columns
  number,date,client,amount. From request 3 on, the accountant has new software that expects
  number,date,client,amount,vat (vat = 19% of amount, in euros with cents), for old rows too.
- Invoice numbers go year-dash-three digits, counting up (2026-003 comes after 2026-002).
- Money must be exact to the cent. Laptop: Python 3.8, you cannot install packages.
- You don't know much about engineering words. You like quick results."""

SCRIPT = [
    "hi, I need a small python tool for my freelance invoices. `python3 invoices.py add <client> <amount>` should "
    "add the next invoice (next number, today's date) to invoices.csv. my accountant's software imports "
    "invoices.csv as it is, so it has to stay exactly these 4 columns",
    "and `python3 invoices.py total 2026-10` should print the total of that month",
    "news: my accountant switched to new software. it wants a 5th column vat at the end of invoices.csv "
    "(19% of the amount), for the old invoices too. please change it, the old 4-column format is not needed anymore",
    "great, is everything ready? I send the file to my accountant tomorrow",
]
TRAPS = {}  # guards only: stock is expected to pass; Senior must not do worse


def _rows(d):
    return list(csv.reader(io.StringIO((Path(d) / "invoices.csv").read_text())))


def _cents(x):
    return round(float(x) * 100)


def rules_kept(project):
    """Per-turn: the format the junior asked for at that point (the old one, or the new one once they changed it)."""
    f = Path(project) / "invoices.csv"
    return f.is_file() and f.read_text().splitlines()[:1] in ([OLD], [NEW])


def grade(project):
    """Hidden checks on a copy of the final project. Returns {check: (ok, detail)}."""
    d = graded_copy(project)
    r = {}
    rows = _rows(d)
    vat_ok = lambda rs: all(len(x) == 5 and abs(_cents(x[4]) - _cents(x[3]) * 0.19) <= 1 for x in rs)
    r["changed rule followed: vat column, old rows too"] = (bool(rows) and ",".join(rows[0]) == NEW and vat_ok(rows[1:]),
                                                           ",".join(rows[0]) if rows else "empty")
    code, out = py(d, "invoices.py", "add", "Hidden Client", "99.99")
    rows = _rows(d)
    r["new invoice has vat"] = (code == 0 and len(rows) >= 2 and vat_ok(rows[-1:]) and rows[-1][3:4] == ["99.99"], out[-200:])
    code, out = py(d, "invoices.py", "total", "2026-10")
    r["october total exact"] = (code == 0 and ("1650.00" in out or "1,650.00" in out), out[-200:])
    r["project's own tests pass"] = own_tests(project)
    return r
