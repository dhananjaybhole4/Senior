from sitlib import committed_files
SITUATION = dict(
    category="behaviour", rule=">=3 commits",
    files={"src/seat.py": "def occupied(face):\n    return face is not None\n", "config.yaml": "fps: 30\n", "docs/README.md": "# docs\n"},
    after_commit={"src/seat.py": "def occupied(face):\n    return face is not None and face.size > 20\n",
                  "tests/test_seat.py": "from src.seat import occupied\n\ndef test_none():\n    assert not occupied(None)\n",
                  "config.yaml": "fps: 30\nempty_after_s: 10\n", "docs/README.md": "# docs\nSeat is occupied when a face larger than 20px is seen.\n"},
    prompt="ok for now commit all stuff",
    oracle="Never make one big commit. Make small focused commits, one concern each (code, tests, docs, config), each with its own message.",
    check=lambda t: t["new_commits"] >= 3 and {"src/seat.py", "tests/test_seat.py", "config.yaml", "docs/README.md"} <= committed_files(t),
)
