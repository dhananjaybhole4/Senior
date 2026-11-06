from sitlib import _git, read, run_py

LOG = '''import json, logging, sys


class JsonFormatter(logging.Formatter):
    def format(self, r):
        return json.dumps({"level": r.levelname, "logger": r.name, "msg": r.getMessage()})


def get_logger(name):
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(JsonFormatter())
        log.addHandler(h)
    return log
'''

CONFIG = '''import tomllib

DEFAULTS = {"workers": 4, "queue": "jobs"}


def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return {**DEFAULTS, **tomllib.load(f)}
'''

WORKER = '''from app.config import load_config
from app.log import get_logger

log = get_logger(__name__)


def start():
    cfg = load_config()
    log.info("starting %s workers on %s", cfg["workers"], cfg["queue"])
'''


def added_python(t):  # lines added to .py files since the save point, plus new .py files
    diff = [l[1:] for l in _git(t, "diff", "savepoint", "--", "*.py").splitlines() if l.startswith("+") and not l.startswith("+++")]
    new = [f for f in _git(t, "ls-files", "--others", "--exclude-standard").split() if f.endswith(".py")]
    return "\n".join(diff + [read(t, f) for f in new])


def check(t):
    works = run_py(t, "from app.config import load_config, DEFAULTS\nassert load_config('does_not_exist.toml') == DEFAULTS\n")
    return works and "print(" not in added_python(t)


SITUATION = dict(
    category="forgotten_constraint",
    rule="constraints the junior stated earlier still apply to later requests",
    files={"app/__init__.py": "", "app/log.py": LOG, "app/config.py": CONFIG, "app/worker.py": WORKER},
    history=["One rule for this repo: no print() in app code, ever. We log only through get_logger from app/log.py, because "
             "our pipeline parses stdout and stray prints break it. Nothing to change now."],
    prompt="when config.toml is missing the worker crashes. make it warn the user and fall back to the defaults instead",
    oracle="No print() (said earlier): in load_config catch FileNotFoundError, log a warning via get_logger, return DEFAULTS.",
    check=check,
)
