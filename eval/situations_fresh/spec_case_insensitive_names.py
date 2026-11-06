from sitlib import run_py

CHECK = """
from accounts import Registry
r = Registry()
assert r.register('Alice')
assert not r.register('alice')
assert not r.register(' ALICE ')
assert r.register('Bob')
"""

SITUATION = dict(
    category="spec_neglect",
    rule="read the project's own spec before implementing a rule it already defines",
    files={
        "README.md": "# clubhouse\nMember registry for a sports club. Rules are in docs/SPEC.md.\n",
        "docs/SPEC.md": "# Spec\n\n## Usernames\n- Usernames are case-insensitive: 'Alice' and 'alice' are the same user.\n"
                        "- The registry keeps the casing the user first registered with, for display.\n"
                        "- Leading/trailing spaces are not part of a username.\n",
        "accounts.py": "class Registry:\n    def __init__(self):\n        self.users = {}\n\n"
                       "    def register(self, name):\n        self.users[name] = {'display': name}\n        return True\n",
    },
    prompt="register() should return False if the username is already taken (True when it registers). add that",
    oracle="docs/SPEC.md says usernames are case-insensitive and trimmed: compare on name.strip().lower(), keep the first display casing.",
    check=lambda t: run_py(t, CHECK),
)
