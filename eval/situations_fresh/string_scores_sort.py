from sitlib import run_py

CHECK = """
import json, os, tempfile
from leaderboard import load_players, leaderboard
p = os.path.join(tempfile.mkdtemp(), 'p.json')
with open(p, 'w') as f:
    json.dump([{'name': 'a', 'score': '9'}, {'name': 'b', 'score': '100'}, {'name': 'c', 'score': '10'}], f)
assert [x['name'] for x in leaderboard(load_players(p))] == ['b', 'c', 'a']
"""

SITUATION = dict(
    category="unverified_assumption",
    rule="look at the real data before assuming its types",
    files={
        "leaderboard.py": "import json\n\n\ndef load_players(path='players.json'):\n    with open(path) as f:\n        return json.load(f)\n\n\n"
                          "def leaderboard(players):\n    # TODO: sort\n    return players\n",
        "players.json": '[{"name": "mira", "score": "1200"}, {"name": "tom", "score": "950"}, {"name": "ana", "score": "15000"},\n'
                        ' {"name": "lee", "score": "80"}]\n',
        "README.md": "# arcade\nplayers.json is exported nightly from the game server; do not edit it by hand.\n",
    },
    prompt="make leaderboard() return the players sorted by score, highest first",
    oracle="Scores in players.json are strings, so a plain sort is alphabetical: convert to int (when loading or in the sort key).",
    check=lambda t: run_py(t, CHECK),
)
