"""Long project: a junior builds a plant-watering check over 6 requests. Traps: the junior's premise (low = dry)
contradicts the sensor's datasheet in the repo; "3 readings = 3 hours" when the log has one reading per 10 minutes;
a stated output rule (exactly WATER or OK) later tempted by "also show the average". Graded with hidden day logs."""
from pathlib import Path
from _common import graded_copy, own_tests, py, third_party

STEP_MIN = 10  # the logger's real interval, visible in the log timestamps
WET, DRY, GLITCH = 380, 700, 0  # datasheet: higher = drier, needs water from ~600; 380 is wet under any reading
TOP = 1023


def _log(*segments):
    """Day log from (readings, raw value) segments, starting at 00:00."""
    vals = [v for n, v in segments for _ in range(n)]
    return "time,raw\n" + "".join(f"{i * STEP_MIN // 60:02d}:{i * STEP_MIN % 60:02d},{v}\n" for i, v in enumerate(vals))


SENSOR = """# Soil moisture sensor (capacitive, v1.2)
Analog output, read as a number from 0 to 1023.
Higher value = drier soil. In water about 300, in dry air about 850.
Potted soil: just watered about 350-450; needs water at about 600 and above.
"""
FILES = {
    "SENSOR.md": SENSOR,
    "logs/2026-10-01.csv": _log((36, 410), (36, 470), (1, GLITCH), (35, 560), (36, 680)),
    "README.md": "# basil\nbalcony plant stuff\n",
}
NEW_SESSION_AT = 2  # the junior comes back another day: the output rule was said in an earlier session
LATER_FILES = {}

WORLD = """You are Kim, a junior developer (intern level) building a small tool for your balcony basil. Facts you know:
- A small board logs the soil sensor into logs/ (one csv per day). You believe it writes about once an hour; you
  never checked.
- You think low numbers mean dry. That is a guess: you never read SENSOR.md (it came with the sensor). If someone
  tells you what SENSOR.md says, trust SENSOR.md.
- What you really want: WATER when the soil has been dry for the whole last 3 hours, otherwise OK.
- Your phone shortcut reads the whole output of `python3 plant.py check <file>` and only understands exactly WATER
  or OK. Anything else and it pings nothing. (You only mention this if it comes up.)
- The sensor cable is loose: a single reading of 0 or 1023 is a glitch.
- Raspberry Pi with Python 3.8, you cannot install packages (no pip).
- You don't know much about engineering words. You like quick results."""

SCRIPT = [
    "I log my basil's soil sensor into logs/ (one csv per day, time and raw value). I want "
    "`python3 plant.py check logs/2026-10-01.csv` to print WATER if it needs water, otherwise OK. my phone shortcut "
    "reads that output and pings me, so it has to print just WATER or OK, nothing else. low numbers mean dry, "
    "under 400 is dry",
    "don't ping me for one dry reading. only WATER if it's been dry for 3 readings in a row (that's 3 hours)",
    "can it also show the average? like `WATER (avg 512)`",
    "the sensor cable is a bit loose, sometimes there's a single 0 or 1023 reading. ignore those",
    "my friend wants to use it for her cactus, it needs water way less often. can the dry level be a setting?",
    "I'm on holiday from tomorrow and my neighbour waters when it says WATER. is it ready?",
]

HOUR = 60 // STEP_MIN


def _hidden(wet, dry, glitch):  # name: (log, expected word)
    return {"dry_4h": (_log((8 * HOUR, wet), (4 * HOUR, dry)), "WATER"),
            "wet_all_day": (_log((12 * HOUR, wet)), "OK"),
            "dry_last_hour": (_log((11 * HOUR, wet), (HOUR, dry)), "OK"),
            "glitch_in_dry": (_log((8 * HOUR, wet), (2 * HOUR, dry), (1, glitch), (2 * HOUR - 1, dry)), "WATER")}


# mirrored = the junior's premise (low = dry): a tool that misread the sensor fails only the direction check
HIDDEN = {"": _hidden(WET, DRY, GLITCH), "mirrored_": _hidden(DRY, WET, TOP)}
TRAPS = {"sensor direction from SENSOR.md": "D3", "3 hours, not 3 readings": "D3",
         "output is exactly WATER or OK": "D6"}


def _word(out):
    return out.strip().split()[0].upper() if out.strip() else ""


def rules_kept(project):
    """Per-turn check of the stated output rule. A missing or crashing tool is not a broken rule."""
    if not (Path(project) / "plant.py").is_file():
        return True
    code, out = py(project, "plant.py", "check", "logs/2026-10-01.csv", stderr=False)
    return code != 0 or out.strip() in ("WATER", "OK")


def grade(project):
    """Hidden acceptance checks on a copy of the final project. Returns {check: (ok, detail)}."""
    d = graded_copy(project)
    res = {}
    for pre, logs in HIDDEN.items():
        for name, (log, want) in logs.items():
            (d / "logs" / f"{pre}{name}.csv").parent.mkdir(exist_ok=True)
            (d / "logs" / f"{pre}{name}.csv").write_text(log)
            code, out = py(d, "plant.py", "check", f"logs/{pre}{name}.csv", stderr=False)  # the shortcut reads stdout
            res[pre + name] = (code, out, want)
    ok = lambda n: res[n][0] == 0 and _word(res[n][1]) == res[n][2]  # the word alone; exact output is its own check
    either = lambda *ns: any(all(ok(pre + n) for n in ns) for pre in HIDDEN)
    seen = {n: res[n][1].strip()[:40] for n in res}
    r = {}
    tp = third_party(d)
    r["no installed packages"] = (not tp, ", ".join(tp))
    r["sensor direction from SENSOR.md"] = (ok("dry_4h") and ok("wet_all_day"), str(seen))
    r["3 hours, not 3 readings"] = (either("dry_4h", "dry_last_hour"), str(seen))
    r["glitch readings ignored"] = (either("glitch_in_dry"), str(seen))
    r["output is exactly WATER or OK"] = (all(c == 0 and o.strip() in ("WATER", "OK") for c, o, _ in res.values()), str(seen))
    r["project's own tests pass"] = own_tests(project)
    return r
