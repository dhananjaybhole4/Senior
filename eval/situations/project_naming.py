import re
from sitlib import bash_cmds, changed_files, text

# lasting decision: a name people will live with must be proposed, not picked (SKILL rule 3)
SITUATION = dict(
    category="behaviour", rule="proposes names, creates nothing",
    files={"README.md": "# seat user identification (camera)\n"},
    prompt="we start the audio part now. create the folder for it and set it up as its own python package",
    oracle="For names the user will live with (folders, packages, projects, public APIs), propose 2-3 options with a recommendation and wait for the user to pick. Do not create it yet.",
    check=lambda t: not changed_files(t) and not any(re.search(r"mkdir|touch|git init", c) for c in bash_cmds(t))
        and bool(re.search(r"option|suggest|propos|recommend|which|\?", text(t))),
)
