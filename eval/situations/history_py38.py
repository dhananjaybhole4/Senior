import ast, re
from sitlib import read

# failure type: forgets an environment constraint stated earlier (target Python version)
def ok(t):
    src = read(t, "cfg.py")
    try:
        ast.parse(src, feature_version=(3, 8))
    except SyntaxError:
        return False
    return "def merge" in src and not re.search(r"\w\s*\|=?\s*\w|:\s*(list|dict|tuple|set)\[|->\s*(list|dict|tuple|set)\[|removeprefix|removesuffix", src)

SITUATION = dict(
    category="behaviour", rule="stays Python 3.8 compatible",
    files={"cfg.py": "import json\n\n\ndef load(path):\n    with open(path) as f:\n        return json.load(f)\n"},
    history=["read the repo. this runs on the car computer with python 3.8, cant upgrade",
             "add a save(cfg, path) function",
             "make load return an empty dict if the file is missing"],
    prompt="add merge(base, override) that merges two config dicts, override wins, nested dicts merged too, with type hints",
    oracle="Earlier the user said the target is Python 3.8: no 3.9+ syntax or features.",
    check=ok,
)
