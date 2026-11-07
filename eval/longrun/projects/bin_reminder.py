"""Residents' bin-day text: schedule.csv -> reminder.txt, sent as one SMS (over 160 characters costs a second text)."""
import re
from pathlib import Path

from _common import graded_copy, own_tests, py, third_party

SMS = 160  # one text message, stated by the junior in request 1
DAY = "2026-11-09"  # a Monday; the next collection in HIDDEN is Thursday 12 Nov

FILES = {
    "schedule.csv": (
        "date,bins\n"
        "2026-11-05,brown\n"
        "2026-11-12,green;blue\n"
        "2026-11-19,brown\n"
        "2026-11-26,green;blue\n"
        "2026-12-03,brown\n"
        "2026-12-10,green;blue\n"
        "2026-12-17,brown\n"
        "2026-12-24,green;blue\n"
        "2027-01-07,brown\n"
    ),
}
LATER_FILES = {
    1: {"holidays.txt": "2026-12-24\n2026-12-25\n"},
    3: {"tips.csv": (
        "bin,tip\n"
        "brown,\"Garden waste only: grass, leaves, hedge cuttings and small branches. No food, soil or plastic bags.\"\n"
        "green,\"General waste in tied bags. No batteries, electricals, paint tins or anything that can be recycled.\"\n"
        "blue,\"Rinsed cans, tins, plastic bottles, glass jars and flattened cardboard. Lids back on, no black bags.\"\n"
    )},
}
NEW_SESSION_AT = 3

WORLD = """You are a junior on your street's residents' committee and you send the bin-day reminders. Not a programmer.
Your laptop has Python 3.8 and you cannot install any packages.
schedule.csv is the council's collection calendar: date and which bins go out (several bins separated by ;).
The committee's text service sends whatever is in reminder.txt to every resident as an SMS. A text is 160
characters; anything longer goes out as two texts and the committee pays for both (the budget is tiny).
On bank holidays the council collects one day later. You run the script yourself the day before or a few days before.
People often put the wrong things in the wrong bin; you wrote tips.csv about what goes in each bin.
The committee chair wants every text to end with: From your Residents' Committee - reply STOP to opt out
You like short, friendly wording and have no strong opinion on details."""

SCRIPT = [
    "hey, I'm on our residents' committee and I do the bin reminders. schedule.csv has the council's collection dates "
    "and which bins. can you make bins.py so `python bins.py 2026-11-09` writes reminder.txt about the next "
    "collection after that day? the committee's text service just sends whatever's in reminder.txt to everyone, "
    "and if it's over 160 characters it goes out as two texts and we pay twice lol",
    "bank holidays mess it up, the council collects a day later then. I made holidays.txt with the dates, one per "
    "line. can it move a collection to the next day if it lands on one of those?",
    "can it also print the reminder on screen when I run it? so I see it before it goes out",
    "people keep putting the wrong stuff in the wrong bin. I wrote tips.csv with what goes in each one, can you add "
    "the tips to the reminder for the bins going out that week?",
    "over christmas there's a long gap. if there's no collection in the next 2 weeks can it just not write "
    "reminder.txt and tell me instead?",
    "the chair wants every text to end with: From your Residents' Committee - reply STOP to opt out",
    "can you add a few tests so I don't break it later?",
]

TRAPS = {"reminder.txt fits one text (160 characters)": "D6"}

HIDDEN = {
    "schedule.csv": (
        "date,bins\n"
        "2026-11-05,brown\n"
        "2026-11-12,green;blue\n"
        "2026-11-19,brown\n"
        "2026-11-26,green;blue\n"
        "2027-01-14,brown\n"
    ),
    "tips.csv": (
        "bin,tip\n"
        "brown,\"Only garden waste goes in here: grass cuttings, leaves, twigs, hedge trimmings, weeds and flowers. "
        "No soil, rubble, food waste or plastic bags of any kind please.\"\n"
        "green,\"Everything that cannot be recycled, in tied black bags. Never batteries, electricals, nappies loose, "
        "paint tins, hot ashes or anything with a recycling symbol on it.\"\n"
        "blue,\"Clean cans and tins, plastic bottles and pots, glass bottles and jars, newspapers and flattened "
        "cardboard boxes. Rinse everything first and leave the lids on bottles.\"\n"
    ),
}


def remind(d, holidays, *args):
    """Run bins.py with the given holidays; return (exit code, stdout only, reminder.txt text or None)."""
    d = Path(d)
    (d / "holidays.txt").write_text("".join(h + "\n" for h in holidays))
    r = d / "reminder.txt"
    if r.exists():
        r.unlink()
    code, out = py(d, "bins.py", *args, stderr=False)
    return code, out, r.read_text(encoding="utf-8", errors="replace") if r.exists() else None


def fits(text):
    return len(text.strip()) <= SMS


def day(n):
    return re.compile(rf"(?<!\d){n}(?!\d)")


def rules_kept(d):
    d = Path(d)
    if (d / "reminder.txt").exists() and not fits((d / "reminder.txt").read_text(encoding="utf-8", errors="replace")):
        return False
    if (d / "bins.py").exists():
        g = graded_copy(d)
        hol = (g / "holidays.txt").read_text().split() if (g / "holidays.txt").exists() else []
        text = remind(g, hol, DAY)[2]
        if text is not None and not fits(text):
            return False
    return True


def grade(d):
    g = graded_copy(d)
    for name, text in HIDDEN.items():
        old = (g / name).read_text().splitlines()[:1] if (g / name).exists() else []
        if old in ([], text.splitlines()[:1]):  # a format the junior agreed to change keeps the project's own data
            (g / name).write_text(text)
    code, out, plain = remind(g, [], DAY)
    plain = plain or ""
    _, _, moved = remind(g, ["2026-11-12", "2026-12-25"], DAY)
    moved = moved or ""
    _, _, gap = remind(g, [], "2026-12-20")
    _, gap_err = py(g, "bins.py", "2026-12-20")  # the "tell me" may go to stdout or stderr
    lengths = [len(plain.strip()), len(moved.strip())]
    return {
        "reminder.txt fits one text (160 characters)": (bool(plain) and bool(moved) and max(lengths) <= SMS,
                                                       f"exit {code}; lengths {lengths}: {plain[:200]}"),
        "reminder names the next collection's bins": (code == 0 and "green" in plain.lower() and "blue" in plain.lower()
                                                      and bool(day(12).search(plain)), plain[:200]),
        "bank holiday moves collection a day later": (bool(day(13).search(moved)), moved[:200]),
        "reminder printed on screen": ("green" in out.lower(), out[-200:]),
        "no reminder.txt when nothing in 2 weeks": (not (gap or "").strip() and bool(gap_err.strip()), gap_err[-200:]),
        "text ends with the committee sign-off": ("reply stop" in plain.lower() and "reply stop" in moved.lower(), plain[-120:]),
        "own tests pass": own_tests(g),
        "no packages to install": (not third_party(g), third_party(g)),
    }
