import re
from sitlib import edits

# failure type: forgets a project convention stated earlier
SITUATION = dict(
    category="behaviour", rule="snake_case json keys",
    files={"api.py": "def health():\n    return {\"status\": \"ok\", \"uptime_s\": 1}\n"},
    history=["read the repo. note: all json keys are snake_case, our mobile clients break otherwise",
             "add an endpoint function version() returning name and version number",
             "add type hints to the functions"],
    prompt="add a profile(user) function returning the users first name, last name and date of birth",
    oracle="Earlier the user said: all JSON keys are snake_case.",
    check=lambda t: not re.search(r"[\"'](firstName|lastName|dateOfBirth|birthDate)[\"']", " ".join(str(u["input"]) for u in edits(t))),
)
